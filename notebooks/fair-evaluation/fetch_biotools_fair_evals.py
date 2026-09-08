"""
Fetches all bio.tools entries from the public bio.tools API, runs FAIR-Checker
assessments via the public API, and writes results to a CSV file.

Usage:
    python fetch_biotools_fair_evals.py [--output biotools-fc_evals-2026.csv]
                                         [--cache biotools_ids.json]
                                         [--limit 100]

Resume: if the output CSV already exists, already-evaluated URLs are skipped.
"""

import argparse
import csv
import json
import logging
import random
import time
from pathlib import Path

import pandas as pd
import requests
from tqdm import tqdm


class TqdmLoggingHandler(logging.Handler):
    """Routes log records through tqdm.write so they don't clobber the progress bar."""

    def emit(self, record):
        tqdm.write(self.format(record))


# use the custom handler instead of the default StreamHandler, which would
# write straight to stderr and garble the in-place progress bar redraws
logging.basicConfig(
    level=logging.INFO, format="%(message)s", handlers=[TqdmLoggingHandler()]
)
logger = logging.getLogger(__name__)

BIOTOOLS_API_URL = "https://bio.tools/api/tool/"
FC_API_URL = (
    "https://fair-checker.france-bioinformatique.fr/api/check/legacy/metrics_all"
)

METRIC_COLS = [
    "F1A",
    "F1B",
    "F2A",
    "F2B",
    "A1.1",
    "A1.2",
    "I1",
    "I2",
    "I3",
    "R1.1",
    "R1.2",
    "R1.3",
]


def fetch_tool_ids(cache_path: Path) -> list[str]:
    if cache_path.exists():
        print(f"Using cached bio.tools ID list: {cache_path}")
        return json.loads(cache_path.read_text())

    print(f"Fetching bio.tools entries → {cache_path}")
    ids: list[str] = []
    page = 1
    total = None
    progress = tqdm(desc="Listing bio.tools entries", unit="tool")
    while True:
        r = requests.get(
            BIOTOOLS_API_URL, params={"format": "json", "page": page}, timeout=30
        )
        r.raise_for_status()
        data = r.json()
        if total is None:
            total = data.get("count")
            progress.total = total
        for entry in data.get("list", []):
            biotools_id = entry.get("biotoolsID")
            if biotools_id:
                ids.append(biotools_id)
        progress.update(len(data.get("list", [])))
        if not data.get("next"):
            break
        page += 1
    progress.close()

    cache_path.write_text(json.dumps(ids))
    return ids


def compute_scores(row: dict) -> dict:
    def safe(key):
        return int(row.get(key, 0) or 0)

    row["F_score"] = round(
        (safe("F1A") + safe("F1B") + safe("F2A") + safe("F2B")) * 100 / 8, 1
    )
    row["A_score"] = round((safe("A1.1") + safe("A1.2")) * 100 / 4, 1)
    row["I_score"] = round((safe("I1") + safe("I2") + safe("I3")) * 100 / 6, 1)
    row["R_score"] = round((safe("R1.1") + safe("R1.2") + safe("R1.3")) * 100 / 6, 1)
    row["FAIR_score"] = round(sum(safe(m) for m in METRIC_COLS) * 100 / 24, 1)
    return row


def evaluate(url: str, retries: int = 3, backoff: float = 5.0) -> dict | None:
    for attempt in range(retries):
        try:
            r = requests.get(FC_API_URL, params={"url": url}, timeout=60)
            r.raise_for_status()
            evaluations = r.json()
            row = {"URL": url}
            for i, e in enumerate(evaluations):
                metric = e["metric"]
                # some entries return null metric names — fall back to positional mapping
                if metric is None and i < len(METRIC_COLS):
                    metric = METRIC_COLS[i]
                if metric in METRIC_COLS:
                    row[metric] = int(e["score"])

            missing = [m for m in METRIC_COLS if m not in row]
            if missing and attempt < retries - 1:
                # incomplete response — retry rather than defaulting to 0
                time.sleep(backoff * (attempt + 1))
                continue

            # after all retries, any still-missing metric genuinely scores 0
            for m in missing:
                row[m] = 0

            return compute_scores(row)
        except Exception as exc:
            if attempt < retries - 1:
                time.sleep(backoff * (attempt + 1))
            else:
                tqdm.write(f"[WARN] Failed {url}: {exc}")
                return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="biotools-fc_evals-2026.csv")
    parser.add_argument("--cache", default="biotools_ids.json")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Only process N randomly sampled entries (useful for testing)",
    )
    args = parser.parse_args()

    output_path = Path(args.output)
    cache_path = Path(args.cache)

    tool_ids = fetch_tool_ids(cache_path)
    print(f"Total bio.tools entries: {len(tool_ids)}")
    if args.limit:
        tool_ids = random.sample(tool_ids, min(args.limit, len(tool_ids)))
        print(
            f"--limit {args.limit}: processing {len(tool_ids)} randomly sampled entries"
        )

    all_urls = [f"https://bio.tools/{tool_id}" for tool_id in tool_ids]

    fieldnames = (
        ["URL"]
        + METRIC_COLS
        + ["F_score", "A_score", "I_score", "R_score", "FAIR_score"]
    )
    # flush every 10 rows rather than only at the end, so a crash/interrupt mid-run
    # still leaves progress on disk for the resume logic above to pick up
    BATCH_SIZE = 10
    success = 0
    failed = 0
    batch: list[dict] = []

    # load already-evaluated URLs to skip them without hitting the API
    saved_urls: set[str] = (
        set(pd.read_csv(output_path, usecols=["URL"])["URL"].tolist())
        if output_path.exists()
        else set()
    )

    remaining = [u for u in all_urls if u not in saved_urls]
    logger.info(f"{len(saved_urls)} already evaluated, {len(remaining)} remaining")
    if not remaining:
        print("Nothing to do.")
        return

    def flush_batch(batch: list[dict]) -> None:
        if not batch:
            return
        # only write the header on the very first flush of a fresh file —
        # subsequent flushes append rows to the same CSV
        write_header = not output_path.exists() or output_path.stat().st_size == 0
        with output_path.open("a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            if write_header:
                writer.writeheader()
            writer.writerows(batch)

    progress = tqdm(remaining, unit="tool", desc="FAIR assessment")
    for url in progress:
        row = evaluate(url)
        if row:
            batch.append(row)
            saved_urls.add(url)
            success += 1
            logger.info("%s -> FAIR_score=%s", url, row["FAIR_score"])
            if len(batch) >= BATCH_SIZE:
                flush_batch(batch)
                batch.clear()
        else:
            failed += 1
        progress.set_postfix(success=success, failed=failed)

    flush_batch(batch)  # write any remaining rows
    print(f"\nDone — {success} evaluated, {failed} failed → {output_path}")


if __name__ == "__main__":
    main()

# Metric Detail Content Negotiation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add HTTP content negotiation to `/test/<tag>` so clients sending `Accept: text/turtle`, `Accept: application/ld+json`, or `Accept: application/rdf+xml` (or a `?format=` query param) receive the metric's metadata as linked data; browsers continue to get the existing HTML page.

**Architecture:** One new helper `_build_metric_kg(metric, subject_uri)` is added to `metrics/util.py`; it builds a `ConjunctiveGraph` using `schema:` + `dcterms:` triples. The existing `_negotiate_rdf_response`, `_ACCEPT_MAP`, and `_FORMAT_PARAM` from the same file handle all serialisation and MIME-type selection. The route in `app.py` checks the `Accept` header (and `?format=` param) before deciding whether to call the helper or fall through to the existing `render_template` call.

**Tech Stack:** Python 3, Flask, rdflib, pytest

---

## File Map

| File | Change |
|---|---|
| `metrics/util.py` | Add `_build_metric_kg(metric, subject_uri)` after `_assessment_to_rdf` |
| `app.py` | Extend the `from metrics.util import …` line; add Accept/format check inside `metric_detail` |
| `tests/test_metric_detail_page.py` | Append 5 new tests (written first, TDD) |

---

## Task 1: Write the five failing tests

**Files:**
- Modify: `tests/test_metric_detail_page.py`

These tests must be written **before** any implementation. They will fail because content negotiation does not exist yet.

- [ ] **Step 1.1 — Append the five tests to the test file**

Open `tests/test_metric_detail_page.py` and append the following after the last existing test:

```python
def test_metric_detail_returns_turtle_when_accept_turtle(client):
    response = client.get("/test/F1A", headers={"Accept": "text/turtle"})
    assert response.status_code == 200
    assert response.content_type == "text/turtle"
    from rdflib import ConjunctiveGraph
    g = ConjunctiveGraph()
    g.parse(data=response.data, format="turtle")
    assert len(g) > 0


def test_metric_detail_returns_jsonld_when_accept_jsonld(client):
    response = client.get(
        "/test/F1A", headers={"Accept": "application/ld+json"}
    )
    assert response.status_code == 200
    assert "application/ld+json" in response.content_type
    from rdflib import ConjunctiveGraph
    g = ConjunctiveGraph()
    g.parse(data=response.data, format="json-ld")
    assert len(g) > 0


def test_metric_detail_returns_rdfxml_when_accept_rdfxml(client):
    response = client.get(
        "/test/F1A", headers={"Accept": "application/rdf+xml"}
    )
    assert response.status_code == 200
    assert "application/rdf+xml" in response.content_type
    from rdflib import ConjunctiveGraph
    g = ConjunctiveGraph()
    g.parse(data=response.data, format="xml")
    assert len(g) > 0


def test_metric_detail_returns_turtle_via_format_param(client):
    response = client.get("/test/F1A?format=turtle")
    assert response.status_code == 200
    assert response.content_type == "text/turtle"
    from rdflib import ConjunctiveGraph
    g = ConjunctiveGraph()
    g.parse(data=response.data, format="turtle")
    assert len(g) > 0


def test_metric_detail_still_returns_html_by_default(client):
    response = client.get("/test/F1A")
    assert response.status_code == 200
    assert "text/html" in response.content_type
```

- [ ] **Step 1.2 — Run the new tests, confirm they all fail**

```bash
cd /Users/gaignard-a/Documents/Dev/fair-checker
python -m pytest tests/test_metric_detail_page.py -v -k "turtle or jsonld or rdfxml or format_param or html_by_default"
```

Expected: 5 FAILED (the route returns HTML for all requests; RDF parse will fail or content-type will be wrong).

---

## Task 2: Add `_build_metric_kg` to `util.py`

**Files:**
- Modify: `metrics/util.py` — insert after line ~820 (after `_assessment_to_rdf`, before `_negotiate_rdf_response`)

- [ ] **Step 2.1 — Add the necessary rdflib imports to `util.py`**

`util.py` already imports `from rdflib import ConjunctiveGraph, URIRef, RDF`. Add `Literal` and `Namespace` to that same import if they are not already there:

```python
from rdflib import ConjunctiveGraph, URIRef, RDF, Literal, Namespace
from rdflib.namespace import DCTERMS
```

Check the current import line (line 3) and update it to:

```python
from rdflib import ConjunctiveGraph, URIRef, RDF, Literal, Namespace
from rdflib.namespace import DCTERMS
```

- [ ] **Step 2.2 — Insert `_build_metric_kg` into `util.py`**

Add the following function **between** `_assessment_to_rdf` and `_negotiate_rdf_response` (i.e. after the closing of `_assessment_to_rdf` at line ~820):

```python
def _build_metric_kg(metric, subject_uri: str) -> ConjunctiveGraph:
    """Build a ConjunctiveGraph describing a FAIR metric using schema: + dcterms:."""
    SCHEMA = Namespace("https://schema.org/")
    tag = metric.get_principle_tag()
    # Strip HTML tags from description so it is a plain-text literal
    plain_desc = re.sub(r"<[^>]+>", "", metric.get_desc()).strip()
    github_url = (
        "https://github.com/IFB-ElixirFr/FAIR-checker/blob/master/metrics/"
        f"{tag}_Impl.py"
    )
    kg = ConjunctiveGraph()
    kg.bind("schema", SCHEMA)
    kg.bind("dcterms", DCTERMS)
    subj = URIRef(subject_uri)
    kg.add((subj, RDF.type, SCHEMA.Thing))
    kg.add((subj, SCHEMA.name, Literal(metric.get_name())))
    kg.add((subj, DCTERMS.description, Literal(plain_desc)))
    kg.add((subj, DCTERMS.identifier, Literal(tag)))
    kg.add((subj, SCHEMA.isPartOf, URIRef(metric.get_principle())))
    kg.add((subj, SCHEMA.codeRepository, URIRef(github_url)))
    updated = metric.get_update_date()
    if updated and updated != "My update date":
        kg.add((subj, DCTERMS.modified, Literal(updated)))
    return kg
```

- [ ] **Step 2.3 — Confirm `util.py` is importable (no syntax errors)**

```bash
cd /Users/gaignard-a/Documents/Dev/fair-checker
python -c "from metrics.util import _build_metric_kg; print('OK')"
```

Expected output: `OK`

---

## Task 3: Update `metric_detail` in `app.py`

**Files:**
- Modify: `app.py` — line 55 (import) and lines 369–390 (`metric_detail` function)

- [ ] **Step 3.1 — Extend the util import in `app.py`**

Find this line in `app.py` (around line 55):

```python
from metrics.util import _turtle_to_html, _assessment_to_rdf, _negotiate_rdf_response
```

Replace it with:

```python
from metrics.util import (
    _turtle_to_html,
    _assessment_to_rdf,
    _negotiate_rdf_response,
    _build_metric_kg,
    _ACCEPT_MAP,
    _FORMAT_PARAM,
)
```

- [ ] **Step 3.2 — Add content negotiation to `metric_detail`**

Find the current `metric_detail` function (around line 369):

```python
@app.route("/test/<tag>")
def metric_detail(tag):
    tag = tag.upper()
    metrics_by_tag = {
        m.get_principle_tag(): m for m in FAIRMetricsFactory.get_FC_impl()
    }
    metric = metrics_by_tag.get(tag)
    if metric is None:
        from flask import abort

        abort(404)
    return render_template(
        "metric_detail.html",
        title=metric.get_principle_tag(),
        subtitle=metric.get_name(),
        tag=metric.get_principle_tag(),
        name=metric.get_name(),
        desc=metric.get_desc(),
        principle=metric.get_principle(),
        implem=metric.get_implem(),
        updated_at=metric.get_update_date(),
    )
```

Replace it with:

```python
@app.route("/test/<tag>")
def metric_detail(tag):
    tag = tag.upper()
    metrics_by_tag = {
        m.get_principle_tag(): m for m in FAIRMetricsFactory.get_FC_impl()
    }
    metric = metrics_by_tag.get(tag)
    if metric is None:
        from flask import abort

        abort(404)

    best = request.accept_mimetypes.best_match(
        ["text/html"] + list(_ACCEPT_MAP.keys()),
        default="text/html",
    )
    fmt_param = request.args.get("format", "").lower()

    if best != "text/html" or fmt_param in _FORMAT_PARAM:
        kg = _build_metric_kg(metric, request.url)
        return _negotiate_rdf_response(kg, tag, request.url, "test")

    return render_template(
        "metric_detail.html",
        title=metric.get_principle_tag(),
        subtitle=metric.get_name(),
        tag=metric.get_principle_tag(),
        name=metric.get_name(),
        desc=metric.get_desc(),
        principle=metric.get_principle(),
        implem=metric.get_implem(),
        updated_at=metric.get_update_date(),
    )
```

- [ ] **Step 3.3 — Run the full test suite for the metric detail page**

```bash
cd /Users/gaignard-a/Documents/Dev/fair-checker
python -m pytest tests/test_metric_detail_page.py -v
```

Expected: **10 passed** (5 pre-existing + 5 new).

- [ ] **Step 3.4 — Commit**

```bash
git add metrics/util.py app.py tests/test_metric_detail_page.py
git commit -m "feat: add RDF content negotiation to /test/<tag> route

- Add _build_metric_kg helper in metrics/util.py (schema: + dcterms:)
- /test/<tag> returns Turtle/JSON-LD/RDF-XML on matching Accept header
- ?format=turtle|json-ld|rdf-xml query param also supported
- HTML behaviour unchanged for browser requests

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Self-Review

**Spec coverage:**
- ✅ `_build_metric_kg` helper in `util.py` — Task 2
- ✅ Content negotiation via `Accept` header — Task 3
- ✅ `?format=` query param support — Task 3 (delegated to `_negotiate_rdf_response`)
- ✅ HTML fallback unchanged — Task 3 + test in Task 1
- ✅ TDD (tests written before implementation, fail verified) — Tasks 1 → 3
- ✅ All five test cases from spec — Task 1

**Placeholder scan:** None found.

**Type consistency:**
- `_build_metric_kg(metric, subject_uri: str)` defined in Task 2, called in Task 3 ✅
- `_ACCEPT_MAP`, `_FORMAT_PARAM` used in Task 3, imported from `util.py` ✅
- `_negotiate_rdf_response(kg, tag, request.url, "test")` signature matches definition in `util.py` ✅

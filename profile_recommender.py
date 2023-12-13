import eventlet

eventlet.monkey_patch(select=False)

from rdflib import ConjunctiveGraph, RDF
from rich.console import Console
from rich.table import Table

# from rich.text import Text
from argparse import ArgumentParser, RawTextHelpFormatter
from profiles.ProfileFactory import ProfileFactory, load_profiles

import sys
import time


parser = ArgumentParser(
    description="""
profile_recommender helps you in finding the most relevant Bioschemas profile.   

Usage examples :
    python profile_recommender.py -url http://bio.tools/jaspar
    
Please report any issue to alban.gaignard@univ-nantes.fr
""",
    formatter_class=RawTextHelpFormatter,
)

# parser.add_argument(
#     "-u",
#     "--update",
#     help="download or update the EDAM ontology",
# )

parser.add_argument(
    "-u",
    "--urls",
    metavar="urls",
    type=str,
    nargs="+",
    help="input urls",
)

parser.add_argument(
    "-f",
    "--files",
    metavar="files",
    type=str,
    nargs="+",
    help="input files",
)


def list_all_instances(kg):
    subjects = []
    for s, p, o in kg.triples((None, RDF.type, None)):
        # print(f"{s} is a {o}")
        subjects.append(s)
    return subjects


if __name__ == "__main__":
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    console = Console()

    s1 = time.time()
    profiles = ProfileFactory.create_all_profiles_from_specifications()
    ts1 = round((time.time() - s1), 2)
    console.print(f"{len(profiles)} Bioschemas profiles loaded in {ts1} s")

    if args.urls:
        from metrics.WebResource import WebResource

        for url in args.urls:
            results = {}

            console.print(f"Which profile is relevant for {url} ?")
            web_res = WebResource(url)
            kg = web_res.get_rdf()
            console.print(f"{len(kg)} loaded RDF triples")
            entities = list_all_instances(kg)

            console.print(f"Iterating over {entities} typed entities")
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Entity", justify="left")
            table.add_column("Profile name", justify="left")
            table.add_column("Similarity score", justify="right")
            table.add_column("Profile URI", justify="right", style="green")

            for e in entities:
                # print(e)
                # print(type(e))
                sub_kg = ConjunctiveGraph()
                for s, p, o in kg.triples((e, None, None)):
                    sub_kg.add((s, p, o))

                has_matching_profile = False
                for p_name in profiles.keys():
                    profile = profiles[p_name]
                    sim = profile.compute_similarity(sub_kg)
                    # sim = profile.compute_loose_similarity(kg)
                    results[p_name] = {"score": sim, "ref": profile.get_name()}
                    if sim > 0:
                        has_matching_profile = True

                    sorted_results = dict(
                        sorted(
                            results.items(),
                            key=lambda item: item[1]["score"],
                            reverse=True,
                        )
                    )

                final_results = []
                if has_matching_profile:
                    for hit in sorted_results.keys():
                        if sorted_results[hit]["score"] > 0:
                            final_results.append(
                                (
                                    str(str(e)),
                                    f"[link={sorted_results[hit]['ref']}]{sorted_results[hit]['ref']}[/link]",
                                    str(sorted_results[hit]["score"]),
                                    str(hit),
                                )
                            )
                            table.add_row(
                                str(str(e)),
                                f"[link={sorted_results[hit]['ref']}]{sorted_results[hit]['ref']}[/link]",
                                str(sorted_results[hit]["score"]),
                                str(hit),
                            )

            # table.add_row(
            #     str(str(e)),
            #     f"[link={sorted_results[hit]['ref']}]{sorted_results[hit]['ref']}[/link]",
            #     str(sorted_results[hit]["score"]),
            #     str(hit),
            # )

            console.rule(f"[bold red]Relevent Bioschemas profile for {url}")
            console.print(table)
            console.print()

    if args.files:
        for file in args.files:
            console.print(f"Which profile is relevant for {file} ?")

            kg = ConjunctiveGraph()
            # kg.parse(file, format="turtle")
            kg.parse(file)
            console.print(f"{len(kg)} loaded RDF triples")

            results = {}

            for p_name in profiles.keys():
                profile = profiles[p_name]
                sim = profile.compute_similarity(kg)
                # sim = profile.compute_loose_similarity(kg)
                results[p_name] = {"score": sim, "ref": ""}

            sorted_results = dict(
                sorted(results.items(), key=lambda item: item[1]["score"], reverse=True)
            )
            # print(sorted_results)

            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Profile", justify="left")
            table.add_column("Similarity score", justify="right")
            table.add_column("Profile URI", justify="right", style="green")

            for hit in sorted_results.keys():
                table.add_row(
                    str(hit),
                    str(sorted_results[hit]["score"]),
                    # str({sorted_results[hit]["ref"]})
                    f"[link={sorted_results[hit]['ref']}]{sorted_results[hit]['ref']}[/link]",
                )

            console.rule(f"[bold red]Relevent Bioschemas profile for {file}")
            console.print(table)
            console.print()

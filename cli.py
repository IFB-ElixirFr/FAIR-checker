import sys
import eventlet
from os import path
from rdflib import ConjunctiveGraph
import logging
import click
import time
import uuid
from pathlib import Path
import itertools
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.progress import track

logging.getLogger("WDM").setLevel("CRITICAL")

eventlet.monkey_patch()

basedir = path.abspath(path.dirname(__file__))

LOGGER = logging.getLogger()
if not LOGGER.handlers:
    LOGGER.addHandler(logging.StreamHandler(sys.stdout))
LOGGER.propagate = False


def pourcentage(x, count_sum):
    return x * 100 / count_sum


def get_suffix(x):
    return str(x).split(sep="/")[-1]


def get_prefix(x):
    if len(str(x).split("//")) > 1:
        return str(x).split("//")[1].split(sep="/")[0]
    else:
        return x


def get_dataframe_from_query_results(res):
    return pd.DataFrame(res.bindings)


def print_valid_report(eval_results, conforms_to):
    console = Console()
    for r in eval_results:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Required missing properties", justify="right")
        table.add_column("Improvements", justify="right")
        # print(r)
        # print(json.dumps(eval_results[r], indent=True))
        # print(eval_results[r]["errors"])
        # print(eval_results[r]["warnings"])
        rows = itertools.zip_longest(
            list(set(eval_results[r]["errors"])), list(set(eval_results[r]["warnings"]))
        )
        for row in rows:
            if not row[0]:
                table.add_row(Text(""), Text(str(row[1]), style="orange"))
            elif not row[1]:
                table.add_row(Text(str(row[0]), style="red"), Text(""))
            else:
                table.add_row(
                    Text(str(row[0]), style="red"), Text(str(row[1]), style="orange")
                )

        console.print()
        console.print(Text(f"Validating {r} typed {eval_results[r]['type']}"))
        if conforms_to:
            console.print(
                Text(f"against specified profile {eval_results[r]['ref_profile']}")
            )
        else:
            console.print(Text(f"against profile {eval_results[r]['ref_profile']}"))
        console.print(table)


@click.command("validate_bioschemas", short_help="...")
@click.option("-u", "--url", "urls", multiple=True)
def cmd_validate_bioschemas(urls):
    from metrics.WebResource import WebResource
    from profiles.ProfileFactory import (
        evaluate_profile_from_type,
        dyn_evaluate_profile_with_conformsto,
    )

    for u in urls:
        res_conforms_to = {}
        res_type = {}
        web_resource = WebResource(u)
        kg = web_resource.get_rdf()
        res_conforms_to = dyn_evaluate_profile_with_conformsto(kg)
        print_valid_report(res_conforms_to, conforms_to=True)
        if len(res_conforms_to) < 1:
            res_type = evaluate_profile_from_type(kg)
            print_valid_report(res_type, conforms_to=False)


@click.command("evaluate", short_help="...")
@click.option("-f", "--file", "rdf_files", multiple=True)
@click.option("-u", "--url", "urls", multiple=True)
@click.option(
    "-d",
    "--debug",
    is_flag=True,
    show_default=True,
    default=False,
    help="for debugging purpose",
)
def cmd_evaluate(rdf_files, urls, debug):

    from metrics.FAIRMetricsFactory import FAIRMetricsFactory
    from metrics.WebResource import WebResource
    from app import get_result_style

    if debug:
        # print("DEBUG ACTIVATED")
        logging.basicConfig(
            level=logging.DEBUG,
            format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)-8s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        logging.debug("DEBUG ACTIVATED")
    else:
        logging.basicConfig(
            level=logging.INFO,
            format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)-8s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        logging.info("DEBUG NOT ACTIVATED")

    if rdf_files:

        console = Console()
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Findable", justify="right")
        table.add_column("Accessible", justify="right")
        table.add_column("Interoperable", justify="right")
        table.add_column("Reusable", justify="right")

        for file in rdf_files:
            start_time = time.time()
            logging.debug(f"Testing local file {file}")
            file_KG = ConjunctiveGraph()
            # file_KG.parse(file, format="turtle")
            file_KG.parse(file)
            web_res = WebResource(
                "local.file",
                rdf_graph=file_KG,
            )
            console.print(f"Loaded {len(web_res.get_rdf())} triples")

            metrics_collection = []
            metrics_collection.append(FAIRMetricsFactory.get_F1A(web_res))
            metrics_collection.append(FAIRMetricsFactory.get_F1B(web_res))
            metrics_collection.append(FAIRMetricsFactory.get_F2A(web_res))
            metrics_collection.append(FAIRMetricsFactory.get_F2B(web_res))
            metrics_collection.append(FAIRMetricsFactory.get_I1(web_res))
            metrics_collection.append(FAIRMetricsFactory.get_I1A(web_res))
            metrics_collection.append(FAIRMetricsFactory.get_I1B(web_res))
            metrics_collection.append(FAIRMetricsFactory.get_I2(web_res))
            metrics_collection.append(FAIRMetricsFactory.get_I2A(web_res))
            metrics_collection.append(FAIRMetricsFactory.get_I2B(web_res))
            metrics_collection.append(FAIRMetricsFactory.get_I3(web_res))
            metrics_collection.append(FAIRMetricsFactory.get_R11(web_res))
            metrics_collection.append(FAIRMetricsFactory.get_R12(web_res))
            metrics_collection.append(FAIRMetricsFactory.get_R13(web_res))

            # metrics_collection.append(FAIRMetricsFactory.get_A11(web_res))

            F_norm = 0
            A_norm = 0
            I_norm = 0
            R_norm = 0

            for m in track(metrics_collection, "Processing FAIR metrics ..."):
                logging.info(m.get_principle_tag())
                logging.info(m.get_name())
                res = m.evaluate()
                if m.get_principle_tag().startswith("F"):
                    F_norm += int(res.get_score())
                    table.add_row(
                        Text(
                            m.get_name() + " " + str(res.get_score()),
                            style=get_result_style(res),
                        ),
                        "",
                        "",
                        "",
                    )
                elif m.get_principle_tag().startswith("I"):
                    I_norm += int(res.get_score())
                    table.add_row(
                        "",
                        "",
                        Text(
                            m.get_name() + " " + str(res.get_score()),
                            style=get_result_style(res),
                        ),
                        "",
                    )
                elif m.get_principle_tag().startswith("R"):
                    R_norm += int(res.get_score())
                    table.add_row(
                        "",
                        "",
                        "",
                        Text(
                            f"{m.get_name()} {str(res.get_score())}",
                            style=get_result_style(res),
                        ),
                    )

            console.rule(f"[bold red]FAIRness evaluation for file {file}")
            console.print(table)
            console.print(
                Text("F normalized score: " + str(round(F_norm / 8 * 100, 1)) + "%")
            )
            console.print(Text("A normalized score: " + str(round(0, 1)) + "%"))
            console.print(
                Text("I normalized score: " + str(round(I_norm / 14 * 100, 1)) + "%")
            )
            console.print(
                Text("R normalized score: " + str(round(R_norm / 6 * 100, 1)) + "%")
            )
            console.print(
                Text(
                    "FAIR normalized score: "
                    + str(round((F_norm + A_norm + I_norm + R_norm) / 28 * 100, 1))
                    + "%"
                )
            )
            elapsed_time = round((time.time() - start_time), 2)
            console.print(f"FAIR metrics evaluated in {elapsed_time} s")

    elif urls:
        console = Console()

        for url in urls:
            start_time = time.time()

            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Findable", justify="right")
            table.add_column("Accessible", justify="right")
            table.add_column("Interoperable", justify="right")
            table.add_column("Reusable", justify="right")

            logging.debug(f"Testing URL {url}")
            web_res = WebResource(url)

            metrics_collection = []
            metrics_collection.append(FAIRMetricsFactory.get_F1A(web_res))
            metrics_collection.append(FAIRMetricsFactory.get_F1B(web_res))
            metrics_collection.append(FAIRMetricsFactory.get_F2A(web_res))
            metrics_collection.append(FAIRMetricsFactory.get_F2B(web_res))
            metrics_collection.append(FAIRMetricsFactory.get_A11(web_res))
            metrics_collection.append(FAIRMetricsFactory.get_I1(web_res))
            metrics_collection.append(FAIRMetricsFactory.get_I1A(web_res))
            metrics_collection.append(FAIRMetricsFactory.get_I1B(web_res))
            metrics_collection.append(FAIRMetricsFactory.get_I2(web_res))
            metrics_collection.append(FAIRMetricsFactory.get_I2A(web_res))
            metrics_collection.append(FAIRMetricsFactory.get_I2B(web_res))
            metrics_collection.append(FAIRMetricsFactory.get_I3(web_res))
            metrics_collection.append(FAIRMetricsFactory.get_R11(web_res))
            metrics_collection.append(FAIRMetricsFactory.get_R12(web_res))
            metrics_collection.append(FAIRMetricsFactory.get_R13(web_res))

            for m in track(metrics_collection, "Processing FAIR metrics ..."):
                logging.debug(m.get_name())
                res = m.evaluate()
                if m.get_principle_tag().startswith("F"):
                    table.add_row(
                        Text(
                            m.get_name() + " " + str(res.get_score()),
                            style=get_result_style(res),
                        ),
                        "",
                        "",
                        "",
                    )
                elif m.get_principle_tag().startswith("A"):
                    table.add_row(
                        "",
                        Text(
                            m.get_name() + " " + str(res.get_score()),
                            style=get_result_style(res),
                        ),
                        "",
                        "",
                    )
                elif m.get_principle_tag().startswith("I"):
                    table.add_row(
                        "",
                        "",
                        Text(
                            m.get_name() + " " + str(res.get_score()),
                            style=get_result_style(res),
                        ),
                        "",
                    )
                elif m.get_principle_tag().startswith("R"):
                    table.add_row(
                        "",
                        "",
                        "",
                        Text(
                            f"{m.get_name()} {str(res.get_score())}",
                            style=get_result_style(res),
                        ),
                    )

            console.rule(f"[bold red]FAIRness evaluation for URL {url}")
            console.print(table)
            elapsed_time = round((time.time() - start_time), 2)
            console.print(f"FAIR metrics evaluated in {elapsed_time} s")


@click.command("extract_metadata", short_help="...")
@click.option("-u", "--url", "urls", multiple=True)
@click.option("-uc", "--url-collection")
@click.option("-o", "--out-dir")
def cmd_extract_metadata(urls, url_collection, out_dir):
    # FAIR-Checker as a metadata crawler

    # import metrics.util as util
    # import metrics.statistics as stats
    # from metrics import test_metric
    # from metrics.FAIRMetricsFactory import FAIRMetricsFactory
    from metrics.WebResource import WebResource

    # from metrics.Evaluation import Result
    # from profiles.bioschemas_shape_gen import validate_any_from_KG
    # from profiles.bioschemas_shape_gen import validate_any_from_microdata
    # from metrics.util import SOURCE
    # from app import get_result_style, app_logger

    start_time = time.time()

    # if url_collection:
    #     file = args.url_collection[0]
    #     mydoc = open(file, "r")
    #     urls = mydoc.readlines()
    # else:
    #     logging.warning(
    #         "There is no valid argument after --extract-metadata. Please add --urls or --url-collection."
    #     )
    #     sys.exit(1)

    if len(urls) > 0:
        for url in urls:
            console = Console()
            table_classes = Table(show_header=True, header_style="bold magenta")
            table_classes.add_column("Classes", justify="right")
            table_classes.add_column("Count", justify="right")

            table_props = Table(show_header=True, header_style="bold magenta")
            table_props.add_column("Properties", justify="right")
            table_props.add_column("Count", justify="right")

            logging.debug(f"Testing URL {url}")
            web_res = WebResource(url)
            KG = ConjunctiveGraph()
            KG = web_res.get_rdf()

            KG2 = ConjunctiveGraph(
                identifier=url,
            )

            print()

            for s, p, o in KG:
                KG2.add((s, p, o))

            classes_counts = """
            SELECT ?c (count(?c) as ?count) WHERE {
                ?s rdf:type ?c .
            }
            GROUP BY ?c
            ORDER BY DESC(?count)
            """

            property_counts = """
            SELECT ?p (count(?p) as ?count) WHERE {
                ?s ?p ?o .
            }
            GROUP BY ?p
            ORDER BY DESC(?count)
            """

            # Classes
            res_classes = KG.query(classes_counts)

            df_classes = pd.DataFrame(res_classes, columns=["class", "count"])

            df_classes["class"] = df_classes["class"].astype("str")
            df_classes["count"] = df_classes["count"].astype("int")

            sum_classes = 0
            for c in df_classes["count"]:
                sum_classes += c

            df_classes_copy = df_classes.copy()
            df_classes_copy["%"] = df_classes_copy["count"].apply(
                lambda x: x * 100 / sum_classes
            )
            # df_classes_copy["label"] = df_classes_copy["class"].apply(get_suffix)
            df_classes_copy["label"] = df_classes_copy["class"]
            # df_classes_copy["onlology"] = df_classes_copy["class"].apply(get_prefix)
            df_classes_copy["onlology"] = df_classes_copy["class"]

            # Properties
            res_props = KG.query(property_counts)
            # df_props = get_dataframe_from_query_results(res_props)

            df_props = pd.DataFrame(res_props, columns=["prop", "count"])

            df_props["prop"] = df_props["prop"].astype("str")
            df_props["count"] = df_props["count"].astype("int")

            sum_props = 0
            for c in df_props["count"]:
                sum_props += c

            df_props_copy = df_props.copy()
            df_props_copy["%"] = df_props_copy["count"].apply(
                lambda x: x * 100 / sum_props
            )
            # df_props_copy["label"] = df_props_copy["prop"].apply(get_suffix)
            df_props_copy["label"] = df_props_copy["prop"]
            # df_props_copy["onlology"] = df_props_copy["prop"].apply(get_prefix)
            df_props_copy["onlology"] = df_props_copy["prop"]

            props = df_props_copy
            classes = df_classes_copy

            # Classes Table
            for index, row in classes.iterrows():
                table_classes.add_row(Text(row[3]), Text(str(row[1])))
            # Props Table
            for index, row in props.iterrows():
                table_props.add_row(Text(row[3]), Text(str(row[1])))

            console.rule(f"Metadata found at URL {url}")
            console.print(table_classes)
            console.print(table_props)

            if out_dir:
                if not path.exists(out_dir):
                    Path(out_dir).mkdir(parents=True, exist_ok=True)

                KG2.serialize(
                    destination=out_file,
                    # format="trig",
                    format="nquads",
                )
                console.print(
                    f"Loaded {len(KG2)} triples from {url}, and saved in {out_file}"
                )
            else:
                if not path.exists("dumps"):
                    Path("dumps").mkdir(parents=True, exist_ok=True)
                out_file = f"dumps/{uuid.uuid4()}.nq"
                KG2.serialize(
                    out_file,
                    format="nquads",
                )
                console.print(
                    f"Loaded {len(KG2)} triples from {url}, and saved in {out_file}"
                )

            elapsed_time = round((time.time() - start_time), 2)
            console.print(f"{url} crawled in {elapsed_time} s")


@click.group(
    help="""
    \b
    A python tool to retrieve RDF metadata from web pages and evaluate FAIR-ness.

    \b
    Usage examples :
        python cli.py evaluate --url http://bio.tools/bwa --url http://bio.tools/jaspar
        python cli.py extract_metadata --url http://bio.tools/bwa -o metadata_dump
        python cli.py extract_metadata --url-collection input_urls.txt
        python cli.py validate_bioschemas --url http://bio.tools/bwa
        python cli.py validate_bioschemas --url https://doi.org/10.57745/B3WUEG"""
)
@click.version_option(version="1.0.0")
def cli():
    pass


cli.add_command(cmd_evaluate)
cli.add_command(cmd_validate_bioschemas)
cli.add_command(cmd_extract_metadata)

if __name__ == "__main__":
    cli()

# if __name__ == "__main__":

#     if args.debug:
#         logging.basicConfig(
#             level=logging.DEBUG,
#             format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)-8s %(message)s",
#             datefmt="%Y-%m-%d %H:%M:%S",
#         )

#     else:
#         logging.basicConfig(
#             level=logging.INFO,
#             format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)-8s %(message)s",
#             datefmt="%Y-%m-%d %H:%M:%S",
#         )
#     LOGGER = logging.getLogger()
#     if not LOGGER.handlers:
#         LOGGER.addHandler(logging.StreamHandler(sys.stdout))
#     LOGGER.propagate = False

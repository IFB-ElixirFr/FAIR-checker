import requests
from os import path
from tqdm import tqdm
import pandas as pd
import time
import random

from metrics.WebResource import WebResource
from metrics.FAIRMetricsFactory import FAIRMetricsFactory
from metrics.AbstractFAIRMetrics import AbstractFAIRMetrics

from rdflib import ConjunctiveGraph, Namespace, URIRef
from rdflib.namespace import RDF, RDFS

import pprofile

profiler = pprofile.Profile()

random.seed(10)


def index_dump():
    for i in tqdm(index.keys()):
        sub_graph = ConjunctiveGraph()
        for s, p, o in KG.triples((URIRef(i), None, None)):
            sub_graph.add((s, p, o))
        index[i] = sub_graph


def get_RDF_sparql(bio_tools_Id):
    q = f"CONSTRUCT {{<{bio_tools_Id}> ?p ?o}} WHERE {{<{bio_tools_Id}> rdf:type schema:SoftwareApplication . <{bio_tools_Id}> ?p ?o .}}"
    res = KG.query(q)
    print(res.serialize(format="turtle"))


def get_RDF(bio_tools_Id):
    sub_graph = ConjunctiveGraph()
    for s, p, o in KG.triples((URIRef(bio_tools_Id), None, None)):
        sub_graph.add((s, p, o))
    print(sub_graph.serialize(format="turtle"))


def eval_metrics(web_res):
    metrics_collection = []
    metrics_collection.append(FAIRMetricsFactory.get_F1A(web_res))
    metrics_collection.append(FAIRMetricsFactory.get_F1B(web_res))
    metrics_collection.append(FAIRMetricsFactory.get_F2A(web_res))
    #    metrics_collection.append(FAIRMetricsFactory.get_F2B_weak(web_res))
    metrics_collection.append(FAIRMetricsFactory.get_I1A(web_res))
    metrics_collection.append(FAIRMetricsFactory.get_I1B(web_res))
    metrics_collection.append(FAIRMetricsFactory.get_I2A(web_res))
    metrics_collection.append(FAIRMetricsFactory.get_I2B(web_res))
    metrics_collection.append(FAIRMetricsFactory.get_I3(web_res))
    metrics_collection.append(FAIRMetricsFactory.get_R11(web_res))
    metrics_collection.append(FAIRMetricsFactory.get_R12(web_res))
    #    metrics_collection.append(FAIRMetricsFactory.get_R13(web_res))

    row = {"ID": web_res.get_url()}
    row_time = {"ID": web_res.get_url()}
    for m in metrics_collection:
        ts1 = time.time()
        e = m.evaluate()
        duration = round((time.time() - ts1), 2)
        if e is not None:
            row[m.get_principle_tag()] = e.get_score()
            row_time[m.get_principle_tag()] = duration

    return row, row_time


def mass_eval():
    evals = []
    exec_time = []

    for sample in tqdm(samples):
        wr = WebResource(url=sample[0], rdf_graph=sample[1])
        row, row_time = eval_metrics(wr)
        evals.append(row)
        exec_time.append(row_time)
    return evals, exec_time


if __name__ == "__main__":
    print("Stress test")

    dump = "bioschemas-dump.ttl"
    if not path.isfile(dump):
        r = requests.get(
            "https://github.com/bio-tools/content/raw/master/datasets/bioschemas-dump.ttl"
        )
        assert r.status_code == 200
        with open(dump, "wb") as f:
            f.write(r.content)

    assert path.isfile(dump)

    schema = Namespace("http://schema.org/")
    KG = ConjunctiveGraph()
    KG.parse(dump, format="turtle")
    print(f"{len(KG)} loaded triples")

    index = {}
    for s, p, o in KG.triples((None, RDF.type, schema.SoftwareApplication)):
        index[str(s)] = None
    print(print(f"{len(index)} software applications"))

    index_dump()

    samples = random.sample(list(index.items()), 20)

    with profiler:
        evals, exec_time = mass_eval()

    profiler.print_stats()

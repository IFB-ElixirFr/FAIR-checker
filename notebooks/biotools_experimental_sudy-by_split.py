#!/usr/bin/env python
# coding: utf-8

# In[5]:


import sys

parentdir = ".."
sys.path.insert(0, parentdir)

import requests
from os import path
from tqdm import tqdm
import pandas as pd
import time
import glob
import logging

logging.getLogger().setLevel(logging.ERROR)

from rdflib import ConjunctiveGraph, Namespace, URIRef
from rdflib.namespace import RDF, RDFS

schema = Namespace("http://schema.org/")

from metrics.WebResource import WebResource
from metrics.FAIRMetricsFactory import FAIRMetricsFactory
from metrics.AbstractFAIRMetrics import AbstractFAIRMetrics

filename = sys.argv[1]


def eval_metrics(web_res):
    metrics_collection = []
    metrics_collection.append(FAIRMetricsFactory.get_F1A(web_res))
    metrics_collection.append(FAIRMetricsFactory.get_F1B(web_res))
    metrics_collection.append(FAIRMetricsFactory.get_F2A(web_res))
    metrics_collection.append(FAIRMetricsFactory.get_I1(web_res))
    #   metrics_collection.append(FAIRMetricsFactory.get_I2(web_res))
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


def mass_eval(samples):
    evals = []
    exec_time = []

    for url, graph in tqdm(samples.items()):
        wr = WebResource(url=url, rdf_graph=graph)
        row, row_time = eval_metrics(wr)
        evals.append(row)
        exec_time.append(row_time)

    return evals, exec_time


# In[7]:


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


# # Iterate over splits


# import glob

# input_files = glob.glob("./split_*.ttl")


KG = ConjunctiveGraph()
KG.parse(filename, format="turtle")

# index of biotools {IDs: rdf KG}
index = {}
for s, p, o in KG.triples((None, RDF.type, schema.SoftwareApplication)):
    index[str(s)] = None

for bio_tools_Id in tqdm(index.keys()):
    sub_graph = ConjunctiveGraph()
    for s, p, o in KG.triples((URIRef(bio_tools_Id), None, None)):
        sub_graph.add((s, p, o))
    index[bio_tools_Id] = sub_graph

# for each index, FAIR evaluation of all entries
df = pd.DataFrame()
df_time = pd.DataFrame()

evals, exec_time = mass_eval(index)
df = pd.concat([df, pd.DataFrame.from_records(evals)])
df_time = pd.concat([df_time, pd.DataFrame.from_records(exec_time)])

df.to_csv("results/biotools/FC_results_" + filename + ".csv")
df_time.to_csv("results/biotools/exec_time_" + filename + ".csv")

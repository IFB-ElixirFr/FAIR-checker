import eventlet
eventlet.monkey_patch()

from flask import Flask, redirect, url_for, request, render_template, session, send_file, send_from_directory
from flask_socketio import SocketIO
from flask_socketio import send, emit
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import secrets

import threading

import time
import random
import re
import os
import io
import uuid
from datetime import datetime
import json

from rdflib import ConjunctiveGraph
import json
import requests

import rdflib
from rdflib import ConjunctiveGraph
from rdflib.compare import to_isomorphic, graph_diff
import pyshacl

import extruct
#from extruct.jsonld import JsonLdExtractor


import metrics.util  as util


import sys



# sys.path.append('../fairmetrics_interface_tests')
# import metrics.test_metric
from metrics import test_metric

# Command line exec
import subprocess
from subprocess import Popen
from subprocess import PIPE
from subprocess import run

app = Flask(__name__)

# app.config.from_envvar('FLASK_CONFIG')

if app.config["ENV"] == "production":
    app.config.from_object("config.ProductionConfig")
else:
    app.config.from_object("config.DevelopmentConfig")

print(f'ENV is set to: {app.config["ENV"]}')

#socketio = SocketIO(app, cors_allowed_origins="*")
socketio = SocketIO(app,async_mode = 'eventlet')
app.secret_key = secrets.token_urlsafe(16)
#socketio = SocketIO(app)
sample_resources = {
    'input_data': [
        "",
        "https://data.inra.fr/dataset.xhtml?persistentId=doi:10.15454/TKMGCQ", # dataset INRA Dataverse
        "https://doi.pangaea.de/10.1594/PANGAEA.914331", # dataset in PANGAEA
    ],
    'input_software' : [
        "",
        "https://zenodo.org/record/3349821#.Xp7m9SNR2Uk", # VM image in zenodo
        "https://explore.openaire.eu/search/software?softwareId=r37b0ad08687::275ecd99e516ed1b863e2a7586063a64", # same VM image in OpenAir
        "https://data.inra.fr/dataset.xhtml?persistentId=doi:10.15454/5K9HCS", # code in INRA Dataverse
        "https://bio.tools/rsat_peak-motifs", # Tool in biotools
        "https://workflowhub.eu/workflows/18", # Workflow in WorkflowHub
        "http://tara-oceans.mio.osupytheas.fr/ocean-gene-atlas/", # OGA Main page of webtool
    ],
    'input_database' : [
        "",
        "https://fairsharing.org/FAIRsharing.ZPRtfG", # knowledge base in FAIRsharing (AgroLD)
        "http://remap.univ-amu.fr" # Database of transcriptional regulators
    ],
    'input_ontology' : [
        "",
        "https://bioportal.bioontology.org/ontologies/OCRE", # Ontology in bioportal
        "https://www.ebi.ac.uk/ols/ontologies/ncit/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FNCIT_C2985" # OLS entry
    ],
    'input_publication' : [
        "",
        "https://doi.org/10.1145/1614320.1614332", # Paper from lod.openair
        "https://search.datacite.org/works/10.7892/boris.108387", # Publication in Datacite
        "https://doi.org/10.6084/m9.figshare.c.3607916_d7.v1", # Publication figure in FigShare
        "https://search.datacite.org/works/10.6084/m9.figshare.c.3607916_d7.v1", # Publication figure in Datacite (same as previous)
        "https://api.datacite.org/dois/application/ld+json/10.6084/m9.figshare.c.3607916_d7.v1" # Publication figure with Datacite API
    ],
    'input_training' : [
        "",
        "https://tess.elixir-europe.org/materials/train-the-trainer", # Training material in TeSS
        "https://tess.elixir-europe.org/materials/bioccheck-a-thon-check-in"
    ],
    # 'input_ifb' : [
    #     "https://www.orpha.net/consor/cgi-bin/Drugs_Search.php?lng=FR&data_id=2679&Substance=Benznidazole&search=Drugs_Search_Disease&data_type=Product&diseaseType=Drug&Typ=Sub&title=&diseaseGroup=Chagas"
    # ]
}

metrics = [{'name':'f1', 'category':'F', 'description': 'F1 verifies that ...  '},
           {'name':'f2', 'category':'F', 'description': 'F2 verifies that ...  '},
           {'name':'f3', 'category':'F', 'description': 'F3 verifies that ...  '},
           {'name':'a1', 'category':'A'},
           {'name':'a2', 'category':'A'}]

    ###### A DEPLACER AU LANCEMENT DU SERVEUR ######
METRICS_RES = test_metric.getMetrics()

kgs = {}

FILE_UUID = ""

DICT_TEMP_RES = {}




@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                          'favicon.ico',mimetype='image/vnd.microsoft.icon')

@socketio.on('evaluate_metric')
def handle_metric(json):
    """
    socketio Handler for a metric calculation requests, calling FAIRMetrics API.
    emit the result of the test

    @param json dict Contains the necessary informations to execute evaluate a metric.
    """

    url = json['url']
    api_url = json['api_url']
    id = json['id']
    principle = json['principle']
    print('RUNNING ' + principle + ' for '+str(url))
    emit('running_f')
    data = '{"subject": "' + url + '"}'
    print(data)

    print(session)

    content_uuid = json['uuid']


    # evaluate metric
    start_time = test_metric.getCurrentTime()
    res = test_metric.testMetric(api_url, data)
    # print(res)
    end_time = test_metric.getCurrentTime()
    evaluation_time = end_time - start_time
    print(evaluation_time)

    # get the score
    score = test_metric.requestResultSparql(res, "ss:SIO_000300")
    score = str(int(float(score)))

    # get comment
    comment = test_metric.requestResultSparql(res, "schema:comment")
    # remove empty lines from the comment
    comment = test_metric.cleanComment(comment)
    all_comment = comment
    # select only success and failure
    comment = test_metric.filterComment(comment, "sf")

    json_result = {
        "url": url,
        "api_url": api_url,
        "principle": principle,
        "id": id,
        "score": score,
        "exec_time": str(evaluation_time),
        "date": str(datetime.now().isoformat())
    }


    # might be removed
    write_temp_metric_res_file(principle, api_url, res, evaluation_time, score, comment, content_uuid)

    principle = principle.split("/")[-1]
    api_url = api_url.split("/")[-1].lstrip("gen2_")
    name = principle + "_" + api_url
    csv_line = '"{}"\t"{}"\t"{}"\t"{}"'.format(name, score, str(evaluation_time), comment)
    emit_json = {
        "score": score,
        "comment": comment,
        "time": str(evaluation_time),
        "name": name,
        "csv_line": csv_line
    }
    print(emit_json)

    emit('done_' + id, emit_json)
    print('DONE ' + principle)


def write_temp_metric_res_file(principle, api_url, json_res, time, score, comment, content_uuid):
    global DICT_TEMP_RES
    sid = request.sid
    temp_file_path = "./temp/" + sid

    principle = principle.split("/")[-1]
    api_url = api_url.split("/")[-1].lstrip("gen2_")
    name = principle + "_" + api_url
    print(name)

    line = '"{}"\t"{}"\t"{}"\t"{}"\n'.format(name, score, str(time), comment)
    # write csv file
    if os.path.exists(temp_file_path):
        with open(temp_file_path, 'a') as fp:
            fp.write(line)
            print("success written")


    if content_uuid in DICT_TEMP_RES.keys():
        DICT_TEMP_RES[content_uuid] += line
    else:
        DICT_TEMP_RES[content_uuid] = line


@socketio.on('download_csv')
def handle_csv_download():


    temp_file_path = "./temp/" + FILE_UUID

    print("Received download request from " + FILE_UUID)
    # csv_download(temp_file_path)

@app.route('/test_asynch/csv-download/<uuid>')
def csv_download(uuid):
    print("downloading !")
    print(uuid)

    output = io.StringIO()
    output.write(DICT_TEMP_RES[uuid])
    # write file object in BytesIO from StringIO
    content = output.getvalue().encode('utf-8')
    mem = io.BytesIO()
    mem.write(content)
    mem.seek(0)

    print(json.dumps(DICT_TEMP_RES, sort_keys=True, indent=4))

    try:
        return send_file(
            mem,
            as_attachment=True,
            attachment_filename='results.csv',
            mimetype='text/csv',
            cache_timeout=-1,
        )
        # return send_from_directory(
        #     "./temp/" + sid,
        #     as_attachment=True,
        #     attachment_filename='metrics_results.csv',
        #     mimetype='text/csv'
        # )
    except Exception as e:
        return str(e)

# not working
@socketio.on('connected')
def handle_connected(json):

    print(request.namespace.socket.sessid)
    print(request.namespace)

@socketio.on('connect')
def handle_connect():
    global FILE_UUID
    print ("The random id using uuid() is : ",end="")
    FILE_UUID = str(uuid.uuid1())
    print (FILE_UUID)
    print (request)

    sid = request.sid

    print("Connected with SID " + sid)

    # Creates a new temp file
    # with open("./temp/" + sid, 'w') as fp:
    #     pass

@socketio.on('disconnect')
def handle_disconnected():



    print("Disconnected")


    sid = request.sid

    time.sleep(5)
    print("Cleaning temp file after disconnect: " + sid)
    if os.path.exists("./temp/" + sid):
        os.remove("./temp/" + sid)


@socketio.on('hello')
def handle_hello(json):
    print(request.sid)


    print('received hello from client: ' + str(json))
    #socketio.emit('ack', 'everything is fine', broadcast=True)
    #emit('ack', 'everything is fine', broadcast=True)
    emit('ack', 'everything is fine')

@socketio.on('slow')
def handle_slow():
    print('received slow from client: ' + str(request.sid))
    #socketio.emit('ack', 'everything is fine', broadcast=True)
    #emit('ack', 'everything is fine', broadcast=True)
    for i in range(0,100):
        time.sleep(0.5)
        emit('slow', i)
        i+=10
    emit('slow', 'done')

@socketio.on('fast')
def handle_fast():
    print('received fast client: ' + str(request.sid))
    #socketio.emit('ack', 'everything is fine', broadcast=True)
    #emit('ack', 'everything is fine', broadcast=True)
    for i in range(0,100):
        time.sleep(0.01)
        emit('fast', i)
    emit('fast', 'done')


#######################################
#######################################
@socketio.on('retrieve_embedded_annot')
def handle_embedded_annot(data):
    """
    socketio Handler to aggregate original page metadata with sparql endpoints.
    emit the result of sparql requests

    @param data dict Contains the data needed to aggregate (url, etc).
    """
    step = 0
    sid = request.sid
    print(sid)
    uri = str(data['url'])
    print('retrieving embedded annotations for '+uri)
    print("Retrieve KG for uri: " + uri)
    page = requests.get(uri)
    html = page.content
    d = extruct.extract(html, syntaxes=['microdata', 'rdfa', 'json-ld'], errors='ignore')

    print(d)
    kg = ConjunctiveGraph()

    for md in d['json-ld']:
        if '@context' in md.keys():
            print(md['@context'])
            if ('https://schema.org' in md['@context']) or ('http://schema.org' in md['@context']) :
                md['@context'] = 'https://schema.org/docs/jsonldcontext.json'
        kg.parse(data=json.dumps(md, ensure_ascii=False), format="json-ld")
    for md in d['rdfa']:
        if '@context' in md.keys():
            if ('https://schema.org' in md['@context']) or ('http://schema.org' in md['@context']) :
                md['@context'] = 'https://schema.org/docs/jsonldcontext.json'
        kg.parse(data=json.dumps(md, ensure_ascii=False), format="json-ld")
    for md in d['microdata']:
        if '@context' in md.keys():
            if ('https://schema.org' in md['@context']) or ('http://schema.org' in md['@context']) :
                md['@context'] = 'https://schema.org/docs/jsonldcontext.json'
        kg.parse(data=json.dumps(md, ensure_ascii=False), format="json-ld")

    kgs[sid] = kg

    step += 1
    emit('update_annot', step)
    emit('send_annot', str(kg.serialize(format='turtle').decode()))
    print(len(kg))

    #check if id or doi in uri
    if util.is_DOI(uri):
        uri = util.get_DOI(uri)
        print(f'FOUND DOI: {uri}')
        # describe on lod.openair

    kg = util.describe_loa(uri, kg)
    step += 1
    emit('update_annot', step)
    emit('send_annot', str(kg.serialize(format='turtle').decode()))
    print(len(kg))

    kg = util.describe_opencitation(uri, kg)
    step += 1
    emit('update_annot', step)
    emit('send_annot', str(kg.serialize(format='turtle').decode()))
    print(len(kg))

    kg = util.describe_wikidata(uri, kg)
    step += 1
    emit('update_annot', step)
    emit('send_annot', str(kg.serialize(format='turtle').decode()))
    print(len(kg))

    kg = util.describe_biotools(uri, kg)
    step += 1
    emit('update_annot', step)
    emit('send_annot', str(kg.serialize(format='turtle').decode()))
    print(f'ended with step {step}')
    print(len(kg))
    print(step)

@socketio.on('complete_kg')
def handle_complete_kg(json):
    print('completing KG for ' + str(json['url']))

@socketio.on('check_kg')
def check_kg(data):
    step = 0
    sid = request.sid
    print(sid)
    uri = str(data['url'])
    if (not sid in kgs.keys()) :
        handle_embedded_annot(data)
    elif (not kgs[sid]):
        handle_embedded_annot(data)
    kg = kgs[sid]

    query_classes = """
        SELECT DISTINCT ?class { ?s rdf:type ?class } ORDER BY ?class
    """
    query_properties = """
        SELECT DISTINCT ?prop { ?s ?prop ?o } ORDER BY ?prop
    """

    table_content = {'classes':[], 'properties':[]}
    qres = kg.query(query_classes)
    for row in qres:
        table_content['classes'].append({'name': row["class"], 'tag':[]})
        print(f'{row["class"]}')

    qres = kg.query(query_properties)
    for row in qres:
        table_content['properties'].append({'name': row["prop"], 'tag':[]})
        print(f'{row["prop"]}')

    emit('done_check', table_content)

    for c in table_content['classes']:
        if util.ask_OLS(c['name']):
            c['tag'].append('OLS')
            emit('done_check', table_content)
        if util.ask_LOV(c['name']):
            c['tag'].append('LOV')
            emit('done_check', table_content)

    for p in table_content['properties']:
        if util.ask_OLS(p['name']):
            p['tag'].append('OLS')
            emit('done_check', table_content)
        if util.ask_LOV(p['name']):
            p['tag'].append('LOV')
            emit('done_check', table_content)

@socketio.on('check_kg_shape')
def check_kg_shape(data):
    step = 0
    sid = request.sid
    print(sid)
    uri = str(data['url'])
    if (not sid in kgs.keys()):
        handle_embedded_annot(data)
    elif (not kgs[sid]):
        handle_embedded_annot(data)
    kg = kgs[sid]

    warnings, errors = util.shape_checks(kg)
    data = {'errors': errors, 'warnings': warnings}
    emit('done_check_shape', data)



#######################################
#######################################

@app.route('/')
def index():
    return render_template('index.html')

def cb():
    print("received message originating from server")

def buidJSONLD():
    """
    Create the Advanced page JSON-LD annotation using schema.org

    @return str
    """
    jld = {
        "@context": "https://schema.org/",
        "@type": "WebApplication",
        "@id": "https://github.com/IFB-ElixirFr/interop-wg/tree/master/linked-data-webapp",
        "name": "FAIR playground",
        "applicationCategory": "FAIR Test",
        "applicationSubCategory": "Demonstrator",
        "operatingSystem": "Any",
        "description": """This demo is based on the FAIRMetrics framework [Wilkinson, Dumontier et al., Scientific Data 6:174] that is composed of Maturity Indicators (MI), compliance tests and the evaluator application itself.
                        For now, few efforts have been done so far to take advantage from their concrete implementation, in the process of improving FAIRness of users/community resources.
                        Furthermore, this does not provide concrete help or guidelines to developers for better sharing their published works. In this work we propose a web demonstrator, leveraging existing web APIs, aimed at i) evaluating FAIR maturity indicators and ii) providing hints to progress in the FAIRification process.""",
        "citation": "https://dx.doi.org/10.1038%2Fsdata.2018.118",

    }
    print(jld)
    raw_jld = json.dumps(jld)
    return raw_jld

@app.route('/test_asynch')
def test_asynch():
    """
    Load the Advanced page elements loading informations from FAIRMetrics API.
    Generate a page allowing test of independent metrics.

    @return render_template
    """
    # unique id to retrieve content results of tests
    content_uuid = str(uuid.uuid1())
    DICT_TEMP_RES[content_uuid] = ""


    print(str(session.items()))
    # sid = request.sid
    #return render_template('test_asynch.html')
    metrics = []

    metrics_res = METRICS_RES

    for metric in metrics_res:
        # remove "FAIR Metrics Gen2" from metric name
        name = metric["name"].replace('FAIR Metrics Gen2- ','')
        # same but other syntax because of typo
        name = name.replace('FAIR Metrics Gen2 - ','')
        metrics.append({
            "name": name,
            "description": metric["description"],
            "api_url": metric["smarturl"],
            "id": "metric_" + metric["@id"].rsplit('/', 1)[-1],
            "principle": metric["principle"],
            "principle_tag": metric["principle"].rsplit('/', 1)[-1],
            "principle_category": metric["principle"].rsplit('/', 1)[-1][0],
        })

    raw_jld = buidJSONLD()
    print(app.config)

    return render_template('metrics_summary.html', f_metrics=metrics, sample_data=sample_resources, jld=raw_jld, uuid=content_uuid)

@app.route('/kg_metrics')
def kg_metrics():
    # m = [{  "name": "i1",
    #         "description": "desc i1",
    #         "id": "metric_i1",
    #         "principle": "principle for i1" }]
    m = []
    return render_template('kg_metrics.html', f_metrics=m, sample_data=sample_resources)

@app.route('/is_it_fair')
def is_it_fair():
    return render_template('is_it_fair.html', )

@app.route('/test_url', methods=['POST'])
def testUrl():
    test_url = request.form.get('url')

    number = test_metric.getMetrics()
    # socketio.emit('newnumber', {'number': number}, namespace='/test')
    socketio.emit('my response', {'data': 'got it!'}, namespace='/test')

    headers_list, descriptions_list, test_score_list, time_list, comments_list = test_metric.webTestMetrics(test_url)

    results_list = []
    for i, elem in enumerate(headers_list):
        if i != 0:
            res_dict = {}
            res_dict["header"] = headers_list[i]
            res_dict["score"] = test_score_list[i]
            res_dict["time"] = time_list[i]
            try:
                res_dict["comments"] = comments_list[i].replace('\n', '<br>')
                res_dict["descriptions"] = descriptions_list[i]
            except IndexError:
                res_dict["comments"] = ""
                res_dict["descriptions"] = ""
            results_list.append(res_dict)
        if i == 4:
            print(res_dict)

    return render_template('result.html', test_url=test_url,
                                            results_list=results_list,)


if __name__ == "__main__":
    # context = ('server.crt', 'server.key')
    # app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=context)
    socketio.run(app,  host="0.0.0.0", port=5000, debug=True)
    #app.run(host='0.0.0.0', port=5000, debug=True)

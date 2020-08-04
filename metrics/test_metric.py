#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os

import urllib
import urllib.request
import json
import requests
from requests.exceptions import SSLError
import rdflib
from rdflib import Graph, plugin
from rdflib.serializer import Serializer
import argparse
import termcolor
from string import Template

import itertools
import threading
import time
import sys
from datetime import datetime, timedelta

#import joblib
#from joblib import Parallel, delayed
import multiprocessing
from multiprocessing import Pool

from tqdm import *

#!!!!! fait bugguer enumerate()
# from threading import *

import random

# from reprint import output

import subprocess


# timeout (connect, read) in secondes
TIMEOUT = (10, 3600)
PRINT_DETAILS = False
OUTPUT_DIR = "para_doi_test_output"
OUTPUT_PREF = "ptest"

parser = argparse.ArgumentParser(description='A FAIRMetrics tester',
                                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
# parser.add_argument("guid", help="The GUID to be tested (DOI, etc)")
parser.add_argument("-n","--name",
                        help="Print metric name to STDOUT",
                        action="store_true")
parser.add_argument("-p","--principle",
                        help="Print principle number to STDOUT",
                        action="store_true")
parser.add_argument("-d","--description",
                        help="Print description of the metrics to STDOUT",
                        action="store_true")
parser.add_argument("-c","--comment",
                        help="Zero or more letters from [iwfsc] (none=print all). Print comment messages for INFO, WARN, FAIL, SUCC, CRIT to STDOUT",
                        # default='all',
                        const='iwfsc',
                        nargs='?',)
parser.add_argument("-wc","--write_comment",
                        help="Zero or more letters from [iwfsc] (none=print all). Filter comment messages for INFO, WARN, FAIL, SUCC, CRIT in output comment file",
                        # default='all',
                        const='iwfsc',
                        nargs='?',)
parser.add_argument("-s","--score",
                        help="Print scores of the metrics to STDOUT",
                        action="store_true")
parser.add_argument("-t","--time",
                        help="Print metric test time to STDOUT",
                        action="store_true")
parser.add_argument("-i","--input",
                        help="The input GUID (Globally Unique Identifier: DOI, URL, etc...)",)
parser.add_argument("-D","--directory",
                        help="Output directory",
                        default=OUTPUT_DIR,)
parser.add_argument("-o","--output",
                        help="Output prefix filenames",
                        default=OUTPUT_PREF)
parser.add_argument("-tn", "--thread_num",
                        help="Number of threads to use. Max available: " + str(multiprocessing.cpu_count()),
                        type=int,
                        choices=range(1, multiprocessing.cpu_count()+1),
                        default=1)



def animated_loading(message):
    """
    Add an animated character to show loading at the end of a message.

    @param message String The message to be displayed
    """

    # string of char the will be displayed in a loop
    chars = "/—\|"

    # the loop over the chars
    for char in chars:
        sys.stdout.write('\r' + message + char)
        time.sleep(.1)
        sys.stdout.flush()

def processFunction(function, args, message):
    """
    The function that execute another function through a wrapper allowing for an animated message while executed.

    @param function Method A python function to be executed
    @param args List The arguments of the function to be executed
    @param message String The message to be displayed
    """

    # List that will contains the results of the input function
    res = []
    # Initialize and start the process
    the_process = threading.Thread(target=wrapper, args=(function, args, res))
    the_process.start()

    # Execute the animated message as long as the process is alive (executing the input function)
    if PRINT_DETAILS:
        while the_process.isAlive():
            animated_loading(message)

    the_process.join()

    # print('test')
    sys.stdout.write('\r\033[K')
    sys.stdout.flush()

    return res[0]

def wrapper(func, args, res):
    """
    The wrapper that execute the input function.

    @param func Method The python function to be executed
    @param args List The arguments of the function to be executed
    @param res List The list of results from the input function
    """
    res.append(func(*args))

def testMetric(metric_api_url, data):
    """
    Send a request to the URL api that will test the metric.

    @param metric_api_url String The URL of one metric to test the data against
    @param data dict Contain the GUID to be tested

    @return String Result returned by the request that is JSON-LD formated
    """

    ##### BRICOLAGE A MODIFIER QUAND FAIRMETRICS SERA A JOUR
    # base_url = "http://linkeddata.systems/cgi-bin/FAIR_Tests/"
    # sub_url = metric_api_url.split('/')[5]
    # metric_api_url = base_url + sub_url
    print(metric_api_url)

    while True:
        try:
            response = requests.request(method='POST', url=metric_api_url, data=data, timeout=TIMEOUT)
            result = response.text
            break
        except requests.exceptions.Timeout:
            print("Timeout, retrying...")
            time.sleep(5)
        except requests.exceptions.ReadTimeout:
            print("ReadTimeout, retrying...")
            time.sleep(20)
        except SSLError:
            print("SSLError, retrying...")
            time.sleep(10)

    return result


def testMetrics(GUID):
    """
    Call multiples time "testMetric" to test each metric against one GUID.

    @param GUID String The GUID to be tested

    @return tuple (headers_list, descriptions_list, test_score_list, time_list, comments_list)
    """

    if args.directory: OUTPUT_DIR = args.directory
    if args.output: OUTPUT_PREF = args.output

    # Create the data dict containing the GUID
    data = '{"subject": "' + GUID + '"}'
    data = data.encode("utf-8")

    # Retrieve all the metrics general info and api urls
    metrics = getMetrics()

    metric_test_results = [{
        "@id": "metric",
        "score": GUID,
        "principle": "GUID",
        "test_time": GUID,
        "comment": '"' + GUID + '"',
        "description": "Description"
    }]

    if args.thread_num > 1:
        metrics_list = []
        for metric in metrics:
            metric_test_results.append({
                "@id": metric["@id"],
                "principle": metric["principle"].rsplit('/', 1)[-1]
            })
            metrics_list.append((metric, data))
        # initialize parallelized
        num_cores = multiprocessing.cpu_count()
        p = Pool(num_cores)
        list_results = []
        # starting metrics test
        for result in tqdm(p.imap_unordered(pTestMetric, metrics_list), total=len(metrics_list), dynamic_ncols=True):
            list_results.append(result)

        p.close()
        p.join()

        # append res to lists
        for result in list_results:
            for i, test in enumerate(metric_test_results):
                if result:
                    if result["@id"] == test["@id"]:
                        metric_test_results[i]["score"] = result["score"]
                        metric_test_results[i]["test_time"] = result["test_time"]
                        metric_test_results[i]["comment"] = result["comment"]
                        metric_test_results[i]["description"] = result["description"]


    else:
        n = 0
        # iterate over each metric
        for metric in metrics:
            n += 1

            # retrieve more specific info about each metric
            metric_info = processFunction(getMetricInfo, [metric["@id"]], 'Retrieving metric informations... ')
            # retrieve the name (principle) of each metric (F1, A1, I2, etc)
            principle = metric_info["principle"].rsplit('/', 1)[-1]
            # principle = metric_info["principle"]
            # get the description on the metric
            description = '"' + metric_info["description"] + '"'

            if True:
            # if principle[0:2] != 'I2':
            # if principle[0:2] == 'I2':
                if PRINT_DETAILS:
                    # print informations related to the metric
                    printMetricInfo(metric_info)
                # evaluate the metric
                start_time = getCurrentTime()
                metric_evaluation_result_text = processFunction(testMetric, [metric["smarturl"], data], 'Evaluating metric ' + principle +'... ')
                end_time = getCurrentTime()
                # print(metric_evaluation_result_text)
                metric_evaluation_result = json.loads(metric_evaluation_result_text)
                test_time = end_time - start_time

                if PRINT_DETAILS:
                    #print results of the evaluation
                    printTestMetricResult(metric_evaluation_result_text, test_time)

                # get comment
                # REQUETE SPARQL !!!!!
                comment = requestResultSparql(metric_evaluation_result_text, "schema:comment")
                # remove empty lines from the comment
                comment = cleanComment(comment)
                # filter comment based on args
                if args.write_comment:
                    comment = filterComment(comment, args.write_comment)
                comment = '"' + comment + '"'


                # get the score
                score = requestResultSparql(metric_evaluation_result_text, "ss:SIO_000300")
                score = str(int(float(score)))

                # add score, principle, time, comment and description

                metric_test_results.append({
                    "@id": metric["@id"],
                    "principle": principle,
                    "score": score,
                    "test_time": test_time,
                    "comment": comment,
                    "description": description,
                })

    # list that will contains the score for each metric test
    test_score_list = []
    # list that will contains the name of each (principle) metric test (F1, A1, I2, etc)
    headers_list = []
    # list that will contains the executation time for each metric test
    time_list = []
    # list that will contains the comment for each metric test
    comments_list = []
    # ist that will contains the description for each metric test
    descriptions_list = []

    for test_result in metric_test_results:
        test_score_list.append(test_result["score"])
        headers_list.append(test_result["principle"])
        time_list.append(test_result["test_time"])
        comments_list.append(test_result["comment"])
        descriptions_list.append(test_result["description"])

    sumScoresTimes(headers_list, test_score_list, time_list)

    # write the list of score (and header if file doesnt exists yet) to a result file
    writeScoreFile("\t".join(headers_list), "\t".join(test_score_list), OUTPUT_DIR, "/" + OUTPUT_PREF + "_score.tsv")

    # write a new line to the time file or create it
    writeTimeFile("\t".join(headers_list), "\t".join(map(str, time_list)), OUTPUT_DIR, "/" + OUTPUT_PREF + "_time.tsv")

    # write a new line to the comment file or create it
    writeCommentFile("\t".join(headers_list), "\t".join(comments_list), "\t".join(descriptions_list), OUTPUT_DIR, "/" + OUTPUT_PREF + "_comment.tsv")

    ### RAJOUT SOMME SCORES et temps dans stdout
    # if args.score:
    # if args.time:
    return (headers_list, descriptions_list, test_score_list, list(map(str, time_list)), comments_list)

def asyncTestMetric(metric):
    global args
    args = parser.parse_args()
    args.write_comment = False
    return pTestMetric(metric)

def pTestMetric(metric):
    # retrieve more specific info about each metric
    metric_info = getMetricInfo(metric[0]["@id"])
    # retrieve the name (principle) of each metric (F1, A1, I2, etc)
    principle = metric_info["principle"].rsplit('/', 1)[-1]
    # get the description on the metric
    description = '"' + metric_info["description"] + '"'


    # if principle[0:2] != 'I2':
    # if principle[0] == 'F':
    if True:
        start_time = getCurrentTime()
        metric_evaluation_result_text = testMetric(metric[0]["smarturl"], metric[1])
        end_time = getCurrentTime()
        # print(metric_evaluation_result_text)
        metric_evaluation_result = json.loads(metric_evaluation_result_text)
        test_time = end_time - start_time

        # get comment
        # REQUETE SPARQL !!!!!
        comment = requestResultSparql(metric_evaluation_result_text, "schema:comment")
        # remove empty lines from the comment
        comment = cleanComment(comment)
        # filter comment based on args
        if args.write_comment:
            comment = filterComment(comment, args.write_comment)
        comment = '"' + comment + '"'


        # get the score
        score = requestResultSparql(metric_evaluation_result_text, "ss:SIO_000300")
        score = str(int(float(score)))

        dict_result = {
            "@id": metric[0]["@id"],
            "score": score,
            "principle": principle,
            "test_time": test_time,
            "comment": comment,
            "description": description,
        }
        return dict_result

    return False

def requestResultSparql(metric_evaluation_result_text, term):

    g = rdflib.Graph()
    result = g.parse(data=metric_evaluation_result_text, format='json-ld')
    rdf_string = g.serialize(format="turtle").decode("utf-8")
    # print(g.serialize(format="json-ld").decode("utf-8"))

    prefix = """
    PREFIX obo:<http://purl.obolibrary.org/obo/>
    PREFIX schema:<http://schema.org/>
    PREFIX ss:<http://semanticscience.org/resource/>
    """
    s = Template(
        """
        $prefix
        SELECT ?s ?p ?o
        WHERE { ?s $term ?o } limit 50
        """)

    query_string = s.substitute(prefix=prefix, term=term)

    query_res = result.query(query_string)
    res_list = []
    for (s, p, o) in query_res:
        res_list.append(o)

    return "\n".join(res_list)

def sumScoresTimes(headers_list, test_score_list, time_list):
    """
    """


    sum_score_dict = {}
    sum_dict = {}
    for i, principle in enumerate(headers_list):
        if i > 0:
            lettre = principle[0]
            score = test_score_list[i]
            time = time_list[i]

            # scores
            if not lettre in sum_dict.keys():
                sum_dict[lettre] = [(score, time)]
            else:
                sum_dict[lettre].append((score, time))

    total_score = 0
    total_time = timedelta()
    for key, value_list in sum_dict.items():
        letter_score = 0
        letter_time = timedelta()

        # accumulate values for each letter
        for value in value_list:
            letter_score += int(value[0])
            letter_time += value[1]

        # accumulate total values
        total_score += letter_score
        total_time += letter_time

        # adding sum by caterogy (FAIR)
        headers_list.append(key)
        test_score_list.append(str(letter_score))
        time_list.append(letter_time)

    # adding total sum
    headers_list.append("total")
    test_score_list.append(str(total_score))
    time_list.append(total_time)

    # convert datetime in time_list to str

def writeTimeFile(headers_list, time_list, output_dir, filename):
    """
    """
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    filename = output_dir + filename
    exists = os.path.isfile(filename)
    if exists:
        file = open(filename, "a")
        file.write("\n" + time_list )
        file.close()
    else:
        file = open(filename, "w")
        file.write(headers_list)
        file.write("\n" + time_list)
        file.close()

def writeCommentFile(headers_list, test_comment_list, descriptions_list, output_dir, filename):
    """

    @param descriptions_list List Contains the description of eache principle added to the top of the file
    """
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    filename = output_dir + filename

    exists = os.path.isfile(filename)
    if exists:
        file = open(filename, "a")
        file.write("\n" + test_comment_list )
        file.close()
    else:
        file = open(filename, "w")
        file.write(descriptions_list)
        file.write("\n" + headers_list)
        file.write("\n" + test_comment_list)
        file.close()

def writeScoreFile(headers_list, test_score_list, output_dir, filename):
    """
    Write a line of scores associated to a GUID to a res file, create the file and headers if it doesn't exist yet.

    @param test_score_list List Score results for each test (0 or 1)
    @param headers_list List Principle of each metric that will be used as headers
    @param filename String The name of the output file
    """
    logname = "result_metrics_test.log"

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    filename = output_dir + filename

    exists = os.path.isfile(filename)
    if exists:
        file = open(filename, "a")
        file.write("\n" + test_score_list )
        file.close()
    else:
        file = open(filename, "w")
        file.write(headers_list)
        file.write("\n" + test_score_list)
        file.close()

def getCurrentTime():
    """
    Function returning the current time formated

    @return datetime object
    """
    return datetime.strptime(time.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')

def getMetricInfo(metric_url):
    """
    Send a request to retrieve additional info about one metric.

    @param metric_url String The url where the metric informations are

    @return json Result returned by the request that is JSON-LD formated
    """
    while True:
        try:
            response = requests.request(method='GET', url=metric_url + '.json', allow_redirects=True, timeout=TIMEOUT)
            result = response.json()
            break
        except requests.exceptions.Timeout:
            time.sleep(5)
        except requests.exceptions.ReadTimeout:
            time.sleep(20)
        except SSLError:
            time.sleep(10)
    return result

def printTestMetricResult(result, test_time):
    """
    A function that send the comments of a metric test against a GUID to the stdout.

    @param key
    """

    if args.comment:
        print("Comment:")
        # print(result[0][key][0]['@value'], end='\n\n')
        comment = requestResultSparql(result, "schema:comment")

        comment = cleanComment(comment)
        comment_args = args.comment
        comment = filterComment(comment, comment_args)

        # mettre boucle dans colorComment
        for line in comment.split("\n"):
            # if line.startswith('SUCCESS') or line.startswith('FAILURE'):
            l = colorComment(line)
            print(l, end='\n')
        print("")

    if args.score:
        print("Score:")
        print(requestResultSparql(result, "ss:SIO_000300"), end='\n\n')

    if args.time:
        print("Metric test time:")
        print(test_time, end='\n\n')

def filterComment(comment, comment_args):
    """
    Select the type of comment to display based on the command line arguments.

    @param comment String The comment from the metric test

    @return String The filtered comment
    """
    association_dict = {
                        's': 'SUCCESS',
                        'f': 'FAILURE',
                        'w': 'WARN',
                        'i': 'INFO',
                        'c': 'CRITICAL',
                        }
    filtered_comment = []

    additional_info = False
    for line in comment.split("\n"):
        # check if line is not additional info (starts with any associantion_dict value)
        for value in association_dict.values():
            if line.startswith(value):
                additional_info = False
                break

        for arg in comment_args:
            # if line statswith the param value or is additional info, add it to filtered_comment
            if line.startswith(association_dict[arg]) or additional_info:
                filtered_comment.append(line)
                additional_info = True
                break
            # if additional_info:
            #     filtered_comment.append(line)
            #     break


    return "\n".join(filtered_comment)

def cleanComment(comment):
    """
    Remove empty lines from the comment.

    @param comment String The comment about the metric test

    @return String The cleaned comment about the metric test
    """
    comment = comment.split('\n')
    if '' in comment:
        comment = [l for l in comment if l != '']
    comment = '\n'.join(comment)
    return comment

def colorComment(line):
    """
    Color some specific terms in the comments in the stdout.

    @param line String The comment line to be colored
    """

    # dict containing words as key and the associated color as value
    association_dict = {
                        'SUCCESS': 'green',
                        'FAILURE': 'red',
                        'WARN': 'yellow',
                        'INFO': 'cyan',
                        'CRITICAL': 'magenta',
                        }
    l = ''
    # add the color to the terms if they exists
    for key_term, value_color in association_dict.items():
        if line.startswith(key_term):
            l = line.replace(key_term, termcolor.colored(key_term, value_color))
            return l

    return line


def printMetricInfo(metric_info):
    if args.name or args.principle or args.description or args.comment or args.score or args.time:
        print('#' * 70, end='\n\n')

    if args.name:
        print(metric_info["name"], end='\n\n')
    if args.principle:
        print("Principle: " + metric_info["principle"].rsplit('/', 1)[-1], end='\n\n')
    if args.description:
        print("Description:")
        print(metric_info["description"], end='\n\n')

def getMetrics():
    """
    Retrieve general informations of each metrics.

    @return json Result returned by the request that is JSON-LD formated
    """

    metrics_url = 'https://fair-evaluator.semanticscience.org/FAIR_Evaluator/metrics.json'

    while(True):
        try:
            response = requests.get(url=metrics_url, timeout=TIMEOUT)
            break
        except SSLError:
            time.sleep(5)
        except requests.exceptions.Timeout:
            print("Timeout, retrying")
            time.sleep(5)
        except requests.exceptions.ConnectionError as e:
            print(e)
            print("ConnectionError, retrying...")
            time.sleep(10)

    json_res = response.json()

    return json_res



def readDOIsFile(filename):
    """
    Read the DOIs from a file input.

    @param filename String The inputs DOIs to be tested
    """
    with open(filename, 'r') as file:
        data = file.read()
    return data

def webTestMetrics(GUID_test):
    global args
    args = parser.parse_args()
    PRINT_DETAILS = True
    args.description = True
    args.thread_num = multiprocessing.cpu_count()
    args.directory = "web_test_dir"

    return testMetrics(GUID_test)

if __name__ == "__main__":
    args = parser.parse_args()
    PRINT_DETAILS = True

    # if len(sys.argv) < 2:
    #     print("You haven't specified any arguments. Use -h to get more details on how to use this command.")
    #     sys.exit(1)


    # RSAT paper
    # GUID_test = "10.1093/nar/gky317"

    # Dataset +++
    GUID_test = "https://doi.pangaea.de/10.1594/PANGAEA.902591"

    # Dataset
    #GUID_test = "https://doi.org/10.5061/dryad.615"
    #GUID_test = "10.5061/dryad.615"
    # GUID_test = "https://www.france-bioinformatique.fr/en"
    # GUID_test = "https://fairsharing.org/"
    # GUID_test = "https://biit.cs.ut.ee/gprofiler/gost"
    # GUID_test = "https://bio.tools/rsat_peak-motifs"
    if args.input: GUID_test = args.input
    # !!!! preblematic url !!!!
    # GUID_test = "10.1155/2019/2561828"
    # GUID_test = "10.1155/2017/3783714"



    # GUID_test = "https://identifiers.org/biotools:the_flux_capacitor"

    # GUID_test = "10.1002/cpbi.72"
    # GUID_test = "10.1093/neuros/nyw135"
    # GUID_test = 'https://orcid.org/0000-0002-3597-8557'


    # for i in range(0, 10):
    results = testMetrics(GUID_test)

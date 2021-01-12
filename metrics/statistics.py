from pymongo import MongoClient
from datetime import datetime, date, timedelta

def evaluations_this_week():
        client = MongoClient()
        db = client.fair_checker
        evaluations = db.evaluations

        a_day_ago = datetime.now() - timedelta(1)
        a_week_ago = datetime.now() - timedelta(7)
        a_month_ago = datetime.now() - timedelta(30)

        #nb_eval = evaluations.find({"started_at": {"$gt": a_day_ago}}).count_documents()
        nb_eval = evaluations.count_documents({"started_at": {"$gt": a_week_ago}})
        return nb_eval

def success_this_week():
    client = MongoClient()
    db = client.fair_checker
    evaluations = db.evaluations

    a_day_ago = datetime.now() - timedelta(1)
    a_week_ago = datetime.now() - timedelta(7)
    a_month_ago = datetime.now() - timedelta(30)

    nb_eval = evaluations.count_documents({"started_at": {"$gt": a_week_ago}, "success": "1"})
    return nb_eval

def this_week_for_named_metrics(prefix='F', success=0):
    client = MongoClient()
    db = client.fair_checker
    evaluations = db.evaluations

    a_day_ago = datetime.now() - timedelta(1)
    a_week_ago = datetime.now() - timedelta(7)
    a_month_ago = datetime.now() - timedelta(30)

    evals = evaluations.find({"started_at": {"$gt": a_week_ago},"success": str(success)})
    count = 0
    for e in evals:
        if e.get('metrics') :
            if e['metrics'].startswith(prefix):
                count += 1
    return count

def failures_this_week():
    client = MongoClient()
    db = client.fair_checker
    evaluations = db.evaluations

    a_day_ago = datetime.now() - timedelta(1)
    a_week_ago = datetime.now() - timedelta(7)
    a_month_ago = datetime.now() - timedelta(30)

    nb_eval = evaluations.count_documents({"started_at": {"$gt": a_week_ago}, "success": "0"})
    return nb_eval

def success_weekly_one_year():
    client = MongoClient()
    db = client.fair_checker
    evaluations = db.evaluations

    a_week_ago = datetime.now() - timedelta(356)

    pipeline = [
        {
            "$match": {
                "started_at": {"$gt": a_week_ago},
                "success": "1",
            }
        },
        {
            "$group": {

                "_id": {
                    "week": { "$isoWeek": "$started_at"},
                    "year": { "$year": "$started_at"},
                },
                "documentCount": {"$sum": 1}
            }
        }
    ];
    # print(list(db.evaluations.aggregate(pipeline)))
    week_count_eval = {}
    results = list(db.evaluations.aggregate(pipeline))
    for result in results:
        year_week = str(result["_id"]["year"]) + "-" + str(result["_id"]["week"])
        week_count_eval[year_week] = result["documentCount"]

    return week_count_eval

def failures_weekly_one_year():
    client = MongoClient()
    db = client.fair_checker
    evaluations = db.evaluations

    a_week_ago = datetime.now() - timedelta(356)

    pipeline = [
        {
            "$match": {
                "started_at": {"$gt": a_week_ago},
                "success": "0",
            }
        },
        {
            "$group": {

                "_id": {
                    "week": { "$isoWeek": "$started_at"},
                    "year": { "$year": "$started_at"},
                },
                "documentCount": {"$sum": 1}
            }
        }
    ];
    # print(list(db.evaluations.aggregate(pipeline)))
    week_count_eval = {}
    results = list(db.evaluations.aggregate(pipeline))
    for result in results:
        year_week = str(result["_id"]["year"]) + "-" + str(result["_id"]["week"])
        week_count_eval[year_week] = result["documentCount"]

    return week_count_eval

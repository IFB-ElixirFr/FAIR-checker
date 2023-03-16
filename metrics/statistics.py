from pymongo import MongoClient
from datetime import datetime, date, timedelta


def evaluations_this_week():
    client = MongoClient()
    db = client.fair_checker
    evaluations = db.evaluations

    a_day_ago = datetime.now() - timedelta(1)
    a_week_ago = datetime.now() - timedelta(7)
    a_month_ago = datetime.now() - timedelta(30)

    # nb_eval = evaluations.find({"started_at": {"$gt": a_day_ago}}).count_documents()
    nb_eval = evaluations.count_documents({"started_at": {"$gt": a_week_ago}})
    return nb_eval


def evaluations_this_month():
    client = MongoClient()
    db = client.fair_checker
    evaluations = db.evaluations

    a_month_ago = datetime.now() - timedelta(30)

    # nb_eval = evaluations.find({"started_at": {"$gt": a_day_ago}}).count_documents()
    nb_eval = evaluations.count_documents({"started_at": {"$gt": a_month_ago}})
    return nb_eval


def success_this_week():
    client = MongoClient()
    db = client.fair_checker
    evaluations = db.evaluations

    a_day_ago = datetime.now() - timedelta(1)
    a_week_ago = datetime.now() - timedelta(7)
    a_month_ago = datetime.now() - timedelta(30)

    nb_eval = evaluations.count_documents(
        {"started_at": {"$gt": a_week_ago}, "success": "1"}
    )
    nb_eval_2 = evaluations.count_documents(
        {"started_at": {"$gt": a_week_ago}, "success": "2"}
    )
    return nb_eval + nb_eval_2


def this_week_for_named_metrics(prefix="F", success="0"):
    client = MongoClient()
    db = client.fair_checker
    evaluations = db.evaluations

    a_day_ago = datetime.now() - timedelta(1)
    a_week_ago = datetime.now() - timedelta(7)
    a_month_ago = datetime.now() - timedelta(30)

    if success == 1:
        evals = evaluations.find(
            {
                "$or": [
                    {"started_at": {"$gt": a_week_ago}, "success": "1"},
                    {"started_at": {"$gt": a_week_ago}, "success": "2"},
                ]
            }
        )
    else:
        evals = evaluations.find({"started_at": {"$gt": a_week_ago}, "success": "0"})
    print(evals)
    count = 0
    for e in evals:
        print(e)
        if e.get("metrics"):
            if e["metrics"].startswith(prefix):

                count += 1
    return count


def failures_this_week():
    client = MongoClient()
    db = client.fair_checker
    evaluations = db.evaluations

    a_day_ago = datetime.now() - timedelta(1)
    a_week_ago = datetime.now() - timedelta(7)
    a_month_ago = datetime.now() - timedelta(30)

    nb_eval = evaluations.count_documents(
        {"started_at": {"$gt": a_week_ago}, "success": "0"}
    )
    return nb_eval


def success_weekly_one_year():
    client = MongoClient()
    db = client.fair_checker
    evaluations = db.evaluations

    a_year_ago = datetime.now() - timedelta(356)

    success = ["1", "2"]

    pipeline = [
        {
            "$match": {
                "started_at": {"$gt": a_year_ago},
                "success": {"$in": success},
            }
        },
        {
            "$group": {
                "_id": {
                    "week": {"$isoWeek": "$started_at"},
                    "year": {"$year": "$started_at"},
                },
                "documentCount": {"$sum": 1},
            }
        },
    ]

    week_count_eval = {}
    week_count_eval_list = []
    results = list(db.evaluations.aggregate(pipeline))

    for result in results:
        week = str(result["_id"]["week"])
        # add 0 before single digit num for sorting purpose
        if len(week) == 1:
            week = "0" + week
        year_week = str(result["_id"]["year"]) + "-" + week
        # year_week = str(result["_id"]["week"]) + "-" + str(result["_id"]["year"])
        week_count_eval[year_week] = result["documentCount"]

    for key in sorted(week_count_eval.keys()):
        print(key + ": " + str(week_count_eval[key]))
        week_count_eval_list.append({"x": key, "y": week_count_eval[key]})
    return week_count_eval_list


def failures_weekly_one_year():
    client = MongoClient()
    db = client.fair_checker
    evaluations = db.evaluations

    a_year_ago = datetime.now() - timedelta(356)

    pipeline = [
        {
            "$match": {
                "started_at": {"$gt": a_year_ago},
                "success": "0",
            }
        },
        {
            "$group": {
                "_id": {
                    "week": {"$isoWeek": "$started_at"},
                    "year": {"$year": "$started_at"},
                },
                "documentCount": {"$sum": 1},
            }
        },
    ]

    week_count_eval = {}
    week_count_eval_list = []
    results = list(db.evaluations.aggregate(pipeline))

    for result in results:
        week = str(result["_id"]["week"])
        # add 0 before single digit num for sorting purpose
        if len(week) == 1:
            week = "0" + week
        year_week = str(result["_id"]["year"]) + "-" + week
        # year_week = str(result["_id"]["week"]) + "-" + str(result["_id"]["year"])
        week_count_eval[year_week] = result["documentCount"]

    for key in sorted(week_count_eval.keys()):
        print(key + ": " + str(week_count_eval[key]))
        week_count_eval_list.append({"x": key, "y": week_count_eval[key]})

    return week_count_eval_list


def weekly_named_metrics(prefix="F", success=0):
    client = MongoClient()
    db = client.fair_checker
    evaluations = db.evaluations

    a_year_ago = datetime.now() - timedelta(356)

    if success == 1:
        success = ["1", "2"]
    else:
        success = ["0"]

    pipeline = [
        {
            "$match": {
                "started_at": {"$gt": a_year_ago},
                "success": {"$in": success},
                "metrics": {"$regex": "^" + prefix},
            }
        },
        {
            "$group": {
                "_id": {
                    "week": {"$isoWeek": "$started_at"},
                    "year": {"$year": "$started_at"},
                },
                "documentCount": {"$sum": 1},
            }
        },
    ]

    week_count_eval = {}
    week_count_eval_list = []
    results = list(db.evaluations.aggregate(pipeline))

    for result in results:
        week = str(result["_id"]["week"])
        # add 0 before single digit num for sorting purpose
        if len(week) == 1:
            week = "0" + week
        year_week = str(result["_id"]["year"]) + "-" + week
        week_count_eval[year_week] = result["documentCount"]

    for key in sorted(week_count_eval.keys()):
        print(key + ": " + str(week_count_eval[key]))
        week_count_eval_list.append({"x": key, "y": week_count_eval[key]})

    return week_count_eval_list

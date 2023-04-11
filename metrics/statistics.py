from pymongo import MongoClient
from datetime import datetime, timedelta


def evaluations_this_week():
    client = MongoClient()
    db = client.fair_checker
    evaluations = db.evaluations
    a_week_ago = datetime.now() - timedelta(7)

    nb_eval = evaluations.count_documents({"started_at": {"$gt": a_week_ago}})
    return nb_eval


def evaluations_this_month():
    client = MongoClient()
    db = client.fair_checker
    evaluations = db.evaluations
    a_month_ago = datetime.now() - timedelta(30)
    nb_eval = evaluations.count_documents({"started_at": {"$gt": a_month_ago}})
    return nb_eval


def success_this_month():
    client = MongoClient()
    db = client.fair_checker
    evaluations = db.evaluations
    a_month_ago = datetime.now() - timedelta(30)
    nb_eval_1 = evaluations.count_documents(
        {"started_at": {"$gt": a_month_ago}, "success": "1"}
    )
    nb_eval_2 = evaluations.count_documents(
        {"started_at": {"$gt": a_month_ago}, "success": "2"}
    )
    return nb_eval_1 + nb_eval_2


def failures_this_month():
    client = MongoClient()
    db = client.fair_checker
    evaluations = db.evaluations
    a_month_ago = datetime.now() - timedelta(30)
    nb_eval = evaluations.count_documents(
        {"started_at": {"$gt": a_month_ago}, "success": "0"}
    )
    return nb_eval


def this_month_for_named_metrics(prefix="F", success="0"):
    client = MongoClient()
    db = client.fair_checker
    evaluations = db.evaluations
    a_month_ago = datetime.now() - timedelta(30)

    if success == 1:
        evals = evaluations.find(
            {
                "$or": [
                    {"started_at": {"$gt": a_month_ago}, "success": "1"},
                    {"started_at": {"$gt": a_month_ago}, "success": "2"},
                ]
            }
        )
    else:
        evals = evaluations.find({"started_at": {"$gt": a_month_ago}, "success": "0"})
    count = 0
    for e in evals:
        if e.get("metrics"):
            if e["metrics"].startswith(prefix):
                count += 1
    return count


def success_this_week():
    client = MongoClient()
    db = client.fair_checker
    evaluations = db.evaluations
    a_week_ago = datetime.now() - timedelta(7)

    nb_eval = evaluations.count_documents(
        {"started_at": {"$gt": a_week_ago}, "success": "1"}
    )
    nb_eval_2 = evaluations.count_documents(
        {"started_at": {"$gt": a_week_ago}, "success": "2"}
    )
    return nb_eval + nb_eval_2


def failures_this_week():
    client = MongoClient()
    db = client.fair_checker
    evaluations = db.evaluations
    a_week_ago = datetime.now() - timedelta(7)

    nb_eval = evaluations.count_documents(
        {"started_at": {"$gt": a_week_ago}, "success": "0"}
    )
    return nb_eval


def success_monthly_one_year():
    client = MongoClient()
    db = client.fair_checker

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
                    "month": {"$month": "$started_at"},
                    "year": {"$year": "$started_at"},
                },
                "documentCount": {"$sum": 1},
            }
        },
    ]

    month_count_eval = {}
    month_count_eval_list = []
    results = list(db.evaluations.aggregate(pipeline))

    for result in results:
        month = str(result["_id"]["month"])
        # add 0 before single digit num for sorting purpose
        if len(month) == 1:
            month = "0" + month
        year_month = str(result["_id"]["year"]) + "-" + month
        month_count_eval[year_month] = result["documentCount"]

    for key in sorted(month_count_eval.keys()):
        month_count_eval_list.append({"x": key, "y": month_count_eval[key]})
    return month_count_eval_list


def failures_monthly_one_year():
    client = MongoClient()
    db = client.fair_checker
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
                    "month": {"$month": "$started_at"},
                    "year": {"$year": "$started_at"},
                },
                "documentCount": {"$sum": 1},
            }
        },
    ]

    month_count_eval = {}
    month_count_eval_list = []
    results = list(db.evaluations.aggregate(pipeline))

    for result in results:
        month = str(result["_id"]["month"])
        # add 0 before single digit num for sorting purpose
        if len(month) == 1:
            month = "0" + month
        year_month = str(result["_id"]["year"]) + "-" + month
        month_count_eval[year_month] = result["documentCount"]

    for key in sorted(month_count_eval.keys()):
        month_count_eval_list.append({"x": key, "y": month_count_eval[key]})
    return month_count_eval_list


def monthly_named_metrics(prefix="F", success=0):
    client = MongoClient()
    db = client.fair_checker
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
                    "month": {"$month": "$started_at"},
                    "year": {"$year": "$started_at"},
                },
                "documentCount": {"$sum": 1},
            }
        },
    ]

    month_count_eval = {}
    month_count_eval_list = []
    results = list(db.evaluations.aggregate(pipeline))

    for result in results:
        month = str(result["_id"]["month"])
        # add 0 before single digit num for sorting purpose
        if len(month) == 1:
            month = "0" + month
        year_month = str(result["_id"]["year"]) + "-" + month
        month_count_eval[year_month] = result["documentCount"]

    for key in sorted(month_count_eval.keys()):
        month_count_eval_list.append({"x": key, "y": month_count_eval[key]})
    return month_count_eval_list


def total_monthly():
    client = MongoClient()
    db = client.fair_checker

    a_year_ago = datetime.now() - timedelta(356)
    two_year_ago = datetime.now() - timedelta(356 * 2)
    # success = ["1", "2"]

    pipeline = [
        {
            "$match": {
                "started_at": {"$gt": two_year_ago},
            }
        },
        {
            "$group": {
                "_id": {
                    "month": {"$month": "$started_at"},
                    "year": {"$year": "$started_at"},
                },
                "documentCount": {"$sum": 1},
            }
        },
    ]

    month_count_eval = {}
    month_count_eval_list = []
    results = list(db.evaluations.aggregate(pipeline))

    for result in results:
        month = str(result["_id"]["month"])
        # add 0 before single digit num for sorting purpose
        if len(month) == 1:
            month = "0" + month
        year_month = str(result["_id"]["year"]) + "-" + month
        month_count_eval[year_month] = result["documentCount"]

    for key in sorted(month_count_eval.keys()):
        month_count_eval_list.append({"x": key, "y": month_count_eval[key]})
    print(month_count_eval_list)
    return month_count_eval_list

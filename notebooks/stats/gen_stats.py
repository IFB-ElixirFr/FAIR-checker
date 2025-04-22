import sys

sys.path.append("../")

import pandas as pd
from pymongo import MongoClient
from datetime import datetime, timedelta
import seaborn as sns
import matplotlib.pyplot as plt
import json

import metrics.statistics as stats


stats_dict = {
    "evals_30": stats.evaluations_this_month(),
    "success_30": stats.success_this_month(),
    "failures_30": stats.failures_this_month(),
    "f_success_30": stats.this_month_for_named_metrics(prefix="F", success=1),
    "f_failures_30": stats.this_month_for_named_metrics(prefix="F", success=0),
    "a_success_30": stats.this_month_for_named_metrics(prefix="A", success=1),
    "a_failures_30": stats.this_month_for_named_metrics(prefix="A", success=0),
    "i_success_30": stats.this_month_for_named_metrics(prefix="I", success=1),
    "i_failures_30": stats.this_month_for_named_metrics(prefix="I", success=0),
    "r_success_30": stats.this_month_for_named_metrics(prefix="R", success=1),
    "r_failures_30": stats.this_month_for_named_metrics(prefix="R", success=0),
    "total_monthly": stats.total_monthly(),
}
with open("usage_stats.json", "w") as outfile:
    json.dump(stats_dict, outfile)


client = MongoClient()
db = client.fair_checker
evaluations = db.evaluations

# print(f"{len(list(evaluations.find({})))} evaluations")
# print(f"{len(evaluations.distinct('target_uri'))} unique evaluated URLs")

six_month_ago = datetime.now() - timedelta(days=180)
# print(six_month_ago.isoformat())
# print(datetime.now().isoformat())

sixm_eval = evaluations.count_documents({"started_at": {"$gt": six_month_ago}})
print(f"{sixm_eval} evaluations the last 6 months. ")
sixm_eval_unique = evaluations.find({"started_at": {"$gt": six_month_ago}}).distinct(
    "target_uri"
)
print(f"{len(sixm_eval_unique)} unique resources evaluated the last 6 months. ")


client = MongoClient()
db = client.fair_checker
evaluations = db.evaluations

data = {}

for i in range(2018, 2024):
    # print(i)
    start = datetime.fromisoformat(f"{i}-01-01")
    end = datetime.fromisoformat(f"{i+1}-01-01")
    count = evaluations.count_documents({"started_at": {"$gte": start, "$lt": end}})
    # print(f"FAIR-checker evaluations in {i}: {count}")
    data[str(i)] = [count]

df = pd.DataFrame(data)
df.to_csv("year.csv")
plot = sns.barplot(data=df)
plt.savefig("stats.png")


data_m = {}

for y in range(2019, 2024):
    for m in ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]:
        start = datetime.fromisoformat(f"{y}-{m}-01")
        end = start + timedelta(days=30)
        count = evaluations.count_documents({"started_at": {"$gte": start, "$lt": end}})
        # print(f"FAIR-checker evaluations in {i}: {count}")
        data_m[f"{y}-{m}"] = [count]

df_m = pd.DataFrame(data_m)
df_m.to_csv("months.csv")


import matplotlib.pyplot as plt

plt.rcParams["figure.figsize"] = (18, 6)
plt.rcParams["figure.dpi"] = 100
plt.rcParams["savefig.dpi"] = 300
plt.xticks(rotation="vertical")
plot = sns.barplot(data=df_m)
plt.savefig("stats_m.png")


from urllib.parse import urlparse

client = MongoClient()
db = client.fair_checker
evaluations = db.evaluations

domains = {}

for e in evaluations.find({}):
    url = urlparse(e["target_uri"])
    d = url.netloc
    if d not in domains.keys():
        domains[d] = 1
    domains[d] += 1

json_data = []
print(domains)
for d in domains.keys():
    json_data.append({"domain": d, "FAIReval": domains[d]})

df_domains = pd.DataFrame(json_data)

df_sorted = df_domains.sort_values(by="FAIReval", ascending=False)
df_sorted.to_csv("domains.csv")

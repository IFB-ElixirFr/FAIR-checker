import pandas as pd
from pymongo import MongoClient
from datetime import datetime, timedelta
import seaborn as sns
import matplotlib.pyplot as plt
from tqdm import tqdm

client = MongoClient()
db = client.fair_checker
evaluations = db.evaluations

data_m = {}

count = 0
for y in tqdm(range(2018, 2024)):
    for m in ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]:
        start = datetime.fromisoformat(f"{y}-{m}-01")
        end = start + timedelta(days=30)
        count += evaluations.count_documents(
            {"started_at": {"$gte": start, "$lt": end}}
        )
        data_m[f"{y}-{m}"] = [count]

df_m = pd.DataFrame(data_m)
df_m.to_csv("cumulated_months.csv")

plt.figure(figsize=(12, 6))
sns.lineplot(data=df_m.iloc[0], marker="o", label="Cumulative Count Over Time")
plt.xlabel("Year-Month")
plt.ylabel("Cumulative Count")
plt.title("Cumulative Count Over Time")
plt.xticks(rotation=90)
plt.savefig("cumulative_count.png", dpi=300)
plt.show()

plt.figure(figsize=(12, 6))
sns.lineplot(data=df_m.iloc[0], marker="o", label="Cumulative Count Over Time")
plt.xlabel("Year-Month")
plt.ylabel("Cumulative Count")
plt.title("Cumulative Count Over Time")
plt.xticks(rotation=90)
plt.yscale("log")
plt.savefig("cumulative_count_log.png", dpi=300)
plt.show()

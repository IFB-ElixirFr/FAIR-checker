import requests
import pandas as pd
from json import JSONDecodeError

FC_all_metrics_url = (
    "https://fair-checker.france-bioinformatique.fr/api/check/metrics_all"
)
remote_rdf_file = "https://raw.githubusercontent.com/frmichel/taxref-ld/master/dataset/Taxrefld_static_dataset_description.ttl"
rows = []

try:
    res = requests.get(url=FC_all_metrics_url, params={"url": remote_rdf_file})
    evaluations = res.json()
    row = {"URL": remote_rdf_file}
    for e in evaluations:
        row[e["metric"]] = int(e["score"])

    rows.append(row)
except JSONDecodeError as e:
    print(e)
    pass

df = pd.DataFrame.from_records(rows)
print(df)

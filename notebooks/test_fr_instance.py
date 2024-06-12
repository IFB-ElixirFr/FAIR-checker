import requests
import time
import json

FC_f2a_url = "https://fair-checker.france-bioinformatique.fr/api/check/metric_F2A"
test_url = "http://bio.tools/bwa"

start = time.time()
res = requests.get(url=FC_f2a_url, params={"url": test_url})
eval_in_sec = time.time() - start
eval = res.json()

#print(json.dumps(eval, indent=4))

assert "score" in eval.keys()
assert "recommendation" in eval.keys()



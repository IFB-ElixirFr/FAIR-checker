#!/bin/bash
curl --silent --insecure https://134.158.247.157/sparql | grep "Virtuoso SPARQL Query Editor"

ret_val=$?

if [ $ret_val -eq 1 ]; then
         echo "OFFLINE Bio.tools SPARQL endpoint (https://134.158.247.157/sparql)"
         exit 1
else
         echo "ONLINE Bio.tools SPARQL endpoint (https://134.158.247.157/sparql)"
         exit 0
fi
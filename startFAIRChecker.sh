#!/bin/bash

# launch mongodb server
screen -dmS mongodb bash --init-file ~/.bashrc -c 'sudo mongod --dbpath /var/lib/mongodb'

# launch fair-checker server
screen -dmS fairchecker bash --init-file ~/.bashrc -c 'conda activate fair-checker; export FLASK_ENV=production; exec gunicorn -b 0.0.0.0:5000 --reload --access-logfile - --e
rror-logfile - app:app --worker-class eventlet -w 1'


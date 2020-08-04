#!/bin/sh
echo "test"
#exec source activate fair-checker-webapp
exec gunicorn -b 0.0.0.0:5000 --access-logfile - --error-logfile - app:app --worker-class eventlet -w 1


#exec source activate fair-checker-webapp && python3 app.py

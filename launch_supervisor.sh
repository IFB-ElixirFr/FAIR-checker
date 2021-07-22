#!/bin/sh
echo "ENV is set to: "
export FLASK_ENV=production
printenv FLASK_ENV
#exec source activate fair-checker-webapp
# exec gunicorn -b 0.0.0.0:5000 --reload --access-logfile - --error-logfile - app:app --worker-class eventlet -w 1
supervisord -c supervisord.conf
#exec source activate fair-checker-webapp && python3 app.py

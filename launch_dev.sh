#!/bin/sh
echo "ENV is set to: "
export FLASK_ENV=development
printenv FLASK_ENV

if [ "$1" = 'bs_update' ]
then
    update=True
else
    update=False
fi

echo $1
echo $update

# exec gunicorn 'app:app(update="$update")'
#exec source activate fair-checker-webapp
exec gunicorn -b 0.0.0.0:5000 \
--reload \
--access-logfile \
- --error-logfile - app:app \
--worker-class eventlet \
-w 1 \
--timeout 120
# supervisord -c supervisord.conf
#exec source activate fair-checker-webapp && python3 app.py

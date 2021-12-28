#!/bin/sh
echo "Hello, dear employer!"
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn yatube.wsgi:application --bind 0.0.0.0:8000

#!/bin/bash

python3 manage.py collectstatic --no-input
python3 manage.py migrate --no-input
python3 manage.py createsuperuser --noinput
uwsgi --ini /etc/uwsgi.ini

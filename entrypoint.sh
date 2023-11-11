#!/bin/sh
cd /home/app/webapp
python3 manage.py makemigrations --noinput
python3 manage.py migrate --noinput
python3 manage.py collectstatic --noinput
DJANGO_SUPERUSER_PASSWORD=testpass python3 manage.py createsuperuser --username testuser --email admin@email.com --noinput
mkdir -p media/inbox
mkdir -p media/data

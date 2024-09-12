#!/usr/bin/env bash
# exit on error
set -o errexit

python -m pip install --upgrade pip

pip install -r requirements.txt

RUN mkdir -p /app/mediafiles
RUN mkdir -p /app/db

# Collect static files
RUN python manage.py collectstatic --noinput

RUN python manage.py makemigrations

# running migrations
RUN python manage.py migrate

#
RUN python manage.py createsuperadmin
# compile SCSS
yarn
yarn build
yarn min-css

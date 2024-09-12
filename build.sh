#!/usr/bin/env bash
# exit on error
set -o errexit

python -m pip install --upgrade pip

pip install -r requirements.txt

mkdir -p /app/mediafiles
mkdir -p /app/db

# Collect static files
python manage.py collectstatic --noinput

python manage.py makemigrations

# running migrations
python manage.py migrate

python manage.py createsuperadmin
# compile SCSS
yarn
yarn build
yarn min-css

FROM python:3.10

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .
# install python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/mediafiles
RUN mkdir -p /app/db

# Collect static files
RUN python manage.py collectstatic --noinput

RUN python manage.py makemigrations

# running migrations
RUN python manage.py migrate

#
RUN python manage.py createsuperadmin

# gunicorn
CMD ["gunicorn", "--config", "gunicorn-cfg.py", "core.wsgi"]

#!/bin/bash

if [ "$DATABASE" = "postgres" ]; then
    echo "Waiting for postgres..."

    while ! nc -z $DB_HOST $DB_PORT; do
        sleep 0.1
    done

    echo "PostgreSQL started"
fi

poetry run python app/manage.py flush --no-input
poetry run python app/manage.py migrate

exec "$@"

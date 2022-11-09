#!/bin/bash

#echo "Waiting for Postgres..."
#
#while ! nc -z "$DATABASE_HOST" "$DATABASE_PORT"; do
#  sleep 0.1
#done
#
#echo "Postgres started..."
#
#exec "$@"

# run migrations
alembic upgrade head

# populate database with test data
# scripts/database_populate.sql  # TODO: find out how to do this!

# launch webserver
uvicorn main:app --host 0.0.0.0 --port 8000 --reload --reload-include *

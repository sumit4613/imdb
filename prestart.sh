#! /usr/bin/env bash
set -e

cd src

# Check if the database is up
python check_db.py

# Run migrations
alembic upgrade head

# Let the DB start and Create initial data in DB
python init.py
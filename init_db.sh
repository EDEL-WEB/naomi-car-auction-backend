#!/bin/bash
# Initialize the database and migrations

echo "Creating database..."
createdb naomi_auction_dev || true

echo "Installing dependencies..."
pipenv install

echo "Initializing Flask-Migrate..."
pipenv run flask db init migrations || true

echo "Creating initial migration..."
pipenv run flask db migrate -m "Initial migration"

echo "Applying migrations..."
pipenv run flask db upgrade

echo "Database setup complete!"

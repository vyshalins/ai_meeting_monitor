#!/bin/bash

# This script initializes the database for the AI Meeting Monitor project.

# Create the database if it doesn't exist
if [ ! -f "backend/db/database.db" ]; then
    echo "Creating database..."
    touch backend/db/database.db
else
    echo "Database already exists."
fi

# Run migrations (if using Alembic or similar)
# Uncomment the following line if you have migrations set up
# alembic upgrade head

echo "Database initialization complete."
#!/bin/bash
# Database initialization script for Behflow
# This script runs all SQL migration files in order

set -e

echo "=========================================="
echo "Behflow Database Initialization"
echo "=========================================="

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "PostgreSQL is ready!"

# Run migration files in order
MIGRATION_DIR="/docker-entrypoint-initdb.d/migrations"

if [ -d "$MIGRATION_DIR" ]; then
    echo ""
    echo "Running migrations from $MIGRATION_DIR..."
    echo ""
    
    for migration_file in "$MIGRATION_DIR"/*.sql; do
        if [ -f "$migration_file" ]; then
            echo "----------------------------------------"
            echo "Running: $(basename "$migration_file")"
            echo "----------------------------------------"
            
            psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f "$migration_file"
            
            if [ $? -eq 0 ]; then
                echo "✓ Success: $(basename "$migration_file")"
            else
                echo "✗ Failed: $(basename "$migration_file")"
                exit 1
            fi
            echo ""
        fi
    done
    
    echo "=========================================="
    echo "All migrations completed successfully!"
    echo "=========================================="
else
    echo "Warning: Migration directory not found: $MIGRATION_DIR"
fi


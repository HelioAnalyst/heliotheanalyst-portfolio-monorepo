#!/bin/bash
# HelioTheAnalyst Portfolio Monorepo - PostgreSQL Database Initialization
# 
# This script creates multiple databases for the portfolio projects.
# It is idempotent - safe to run multiple times.
#
# Usage:
#   chmod +x scripts/init-multiple-databases.sh
#   ./scripts/init-multiple-databases.sh
#
# Or automatically via docker-compose:
#   docker-compose up -d postgres

set -e

# List of databases to create
DATABASES=(
    "shopify_integration"
    "order_processing"
    "api_testing"
)

echo "=========================================="
echo "PostgreSQL Database Initialization"
echo "=========================================="

# Check if running inside Docker (via docker-entrypoint-initdb.d)
# or manually by a user
if [ -n "$POSTGRES_USER" ] && [ -n "$POSTGRES_PASSWORD" ]; then
    # Running inside Docker container
    echo "Running inside Docker container..."
    PSQL="psql -U $POSTGRES_USER"
else
    # Running manually - use default postgres user
    echo "Running manually..."
    PSQL="psql -U postgres"
fi

# Function to check if database exists
database_exists() {
    local db_name=$1
    $PSQL -tAc "SELECT 1 FROM pg_database WHERE datname='$db_name'" | grep -q 1
}

# Function to create database if it doesn't exist
create_database() {
    local db_name=$1
    
    if database_exists "$db_name"; then
        echo "  ✓ Database '$db_name' already exists - skipping"
    else
        echo "  → Creating database '$db_name'..."
        $PSQL -c "CREATE DATABASE \"$db_name\";"
        echo "  ✓ Database '$db_name' created successfully"
    fi
}

# Create each database
echo ""
echo "Creating databases..."
for db in "${DATABASES[@]}"; do
    create_database "$db"
done

echo ""
echo "=========================================="
echo "Database initialization complete!"
echo "=========================================="
echo ""
echo "Created databases:"
for db in "${DATABASES[@]}"; do
    echo "  - $db"
done
echo ""

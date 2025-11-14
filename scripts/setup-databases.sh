#!/bin/bash

# Database setup script
echo "🔧 Setting up databases..."

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
until pg_isready -h shared-postgres -U postgres; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "✅ PostgreSQL is ready"

# List of databases to create
DATABASES=(
  "user_service_db"
  "template_service_db"
  "push_service_db"
  "email_service_db"
  "api_gateway_db"
)

# Create each database
for db in "${DATABASES[@]}"; do
  echo "🔧 Creating database: $db"
  
  # Check if database exists
  DB_EXISTS=$(PGPASSWORD=password psql -h shared-postgres -U postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$db'")
  
  if [ "$DB_EXISTS" = "1" ]; then
    echo "✅ Database '$db' already exists"
  else
    # Create database
    PGPASSWORD=password psql -h shared-postgres -U postgres -c "CREATE DATABASE $db;"
    if [ $? -eq 0 ]; then
      echo "✅ Created database '$db'"
    else
      echo "❌ Failed to create database '$db'"
    fi
  fi
done

echo "✅ Database setup complete"
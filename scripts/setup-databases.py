#!/usr/bin/env python3
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
import time

# Database configuration
DB_HOST = "localhost"
DB_USER = "postgres"
DB_PASSWORD = "password"
DB_PORT = 5432

# Databases to create
DATABASES = [
    "user_service_db",
    "template_service_db", 
    "push_service_db",
    "email_service_db",
    "api_gateway_db"
]

def wait_for_postgres():
    """Wait for PostgreSQL to be ready"""
    max_retries = 30
    for i in range(max_retries):
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                port=DB_PORT,
                database="postgres"
            )
            conn.close()
            print("✅ PostgreSQL is ready")
            return True
        except psycopg2.OperationalError:
            print(f"⏳ Waiting for PostgreSQL... ({i+1}/{max_retries})")
            time.sleep(2)
    
    print("❌ PostgreSQL is not ready after 60 seconds")
    return False

def database_exists(cursor, db_name):
    """Check if database exists"""
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
    return cursor.fetchone() is not None

def create_database(cursor, db_name):
    """Create database if it doesn't exist"""
    if database_exists(cursor, db_name):
        print(f"✅ Database '{db_name}' already exists")
        return True
    
    try:
        cursor.execute(f'CREATE DATABASE "{db_name}"')
        print(f"✅ Created database '{db_name}'")
        return True
    except Exception as e:
        print(f"❌ Failed to create database '{db_name}': {e}")
        return False

def main():
    if not wait_for_postgres():
        sys.exit(1)
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("🔧 Setting up databases...")
        
        # Create each database
        success_count = 0
        for db_name in DATABASES:
            if create_database(cursor, db_name):
                success_count += 1
        
        cursor.close()
        conn.close()
        
        print(f"✅ Database setup complete: {success_count}/{len(DATABASES)} databases ready")
        
        if success_count == len(DATABASES):
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
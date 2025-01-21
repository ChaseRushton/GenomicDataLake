#!/usr/bin/env python3
import argparse
import subprocess
import sys
import os
import json
import time
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def run_command(command):
    """Run a shell command and return the output"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            text=True,
            capture_output=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def check_postgres_installation():
    """Check if PostgreSQL is installed"""
    success, _ = run_command("pg_config --version")
    return success

def get_postgres_version():
    """Get PostgreSQL version"""
    success, output = run_command("pg_config --version")
    if success:
        return output.strip()
    return None

def is_postgres_running():
    """Check if PostgreSQL service is running"""
    if sys.platform == 'win32':
        success, _ = run_command('sc query "postgresql"')
        return success
    else:
        success, _ = run_command('pg_isready')
        return success

def start_postgres_service():
    """Start PostgreSQL service"""
    print("Starting PostgreSQL service...")
    if sys.platform == 'win32':
        success, output = run_command('net start postgresql')
    else:
        if sys.platform == 'darwin':  # macOS
            success, output = run_command('brew services start postgresql')
        else:  # Linux
            success, output = run_command('sudo service postgresql start')
    
    if not success:
        print("Failed to start PostgreSQL service:", output)
        return False
    return True

def create_user(args):
    """Create database user"""
    try:
        # Connect as superuser
        conn = psycopg2.connect(
            host=args.host,
            port=args.port,
            user=args.superuser,
            password=args.superuser_password,
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Check if user exists
        cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (args.user,))
        if not cur.fetchone():
            # Create user
            cur.execute(f"CREATE USER {args.user} WITH PASSWORD %s", (args.password,))
            print(f"Created user: {args.user}")
        
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print("Error creating user:", str(e))
        return False

def create_database(args):
    """Create database and schema"""
    try:
        # Connect as superuser
        conn = psycopg2.connect(
            host=args.host,
            port=args.port,
            user=args.superuser,
            password=args.superuser_password,
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Check if database exists
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (args.dbname,))
        if not cur.fetchone():
            # Create database
            cur.execute(f"CREATE DATABASE {args.dbname} OWNER {args.user}")
            print(f"Created database: {args.dbname}")
        
        cur.close()
        conn.close()
        
        # Connect to new database and create schema
        conn = psycopg2.connect(
            host=args.host,
            port=args.port,
            user=args.superuser,
            password=args.superuser_password,
            database=args.dbname
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Read and execute schema file
        with open('init-scripts/01-init-schema.sql', 'r') as f:
            schema_sql = f.read()
            cur.execute(schema_sql)
        
        print("Created database schema")
        
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print("Error creating database:", str(e))
        return False

def create_db_config(args):
    """Create db_config.json file"""
    config = {
        "host": args.host,
        "port": args.port,
        "database": args.dbname,
        "user": args.user,
        "password": args.password
    }
    
    with open("db_config.json", "w") as f:
        json.dump(config, f, indent=4)
    print("Created db_config.json")

def test_connection(args):
    """Test database connection"""
    try:
        conn = psycopg2.connect(
            host=args.host,
            port=args.port,
            user=args.user,
            password=args.password,
            database=args.dbname
        )
        conn.close()
        return True
    except Exception as e:
        print("Error testing connection:", str(e))
        return False

def setup_database(args):
    """Set up the database"""
    # Check PostgreSQL installation
    if not check_postgres_installation():
        print("Error: PostgreSQL is not installed")
        print("Please install PostgreSQL and make sure it's in your PATH")
        return False
    
    # Print PostgreSQL version
    version = get_postgres_version()
    if version:
        print(f"Found PostgreSQL: {version}")
    
    # Check if PostgreSQL is running
    if not is_postgres_running():
        print("PostgreSQL is not running")
        if not start_postgres_service():
            print("Failed to start PostgreSQL service")
            return False
    
    print("PostgreSQL is running")
    
    # Create user
    if not create_user(args):
        return False
    
    # Create database and schema
    if not create_database(args):
        return False
    
    # Create configuration file
    create_db_config(args)
    
    # Test connection
    if test_connection(args):
        print("\nDatabase setup completed successfully!")
        print(f"\nConnection details:")
        print(f"  Host: {args.host}")
        print(f"  Port: {args.port}")
        print(f"  Database: {args.dbname}")
        print(f"  User: {args.user}")
        print("\nYou can now run the genomic data upload script:")
        print("python genomic_data_upload.py /path/to/data")
        return True
    
    return False

def main():
    parser = argparse.ArgumentParser(description="Set up local PostgreSQL database")
    parser.add_argument("--host", default="localhost", help="Database host")
    parser.add_argument("--port", type=int, default=5432, help="Database port")
    parser.add_argument("--user", default="genomic_user", help="Database user to create")
    parser.add_argument("--password", default="genomic_password", help="Database user password")
    parser.add_argument("--dbname", default="genomic_data", help="Database name")
    parser.add_argument("--superuser", default="postgres", help="PostgreSQL superuser name")
    parser.add_argument("--superuser-password", help="PostgreSQL superuser password")
    
    args = parser.parse_args()
    
    if not args.superuser_password:
        print("Error: --superuser-password is required")
        parser.print_help()
        return
    
    setup_database(args)

if __name__ == "__main__":
    main()

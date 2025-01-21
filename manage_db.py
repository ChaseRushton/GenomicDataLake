#!/usr/bin/env python3
import argparse
import os
import subprocess
import time
import json
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def run_command(command, cwd=None):
    """Run a shell command and return the output"""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            check=True,
            text=True,
            capture_output=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def check_docker():
    """Check if Docker is installed and running"""
    success, output = run_command("docker info")
    if not success:
        print("Error: Docker is not running or not installed")
        print("Please install Docker and Docker Compose, then start the Docker service")
        return False
    return True

def wait_for_postgres(host, port, user, password, dbname, max_retries=30):
    """Wait for PostgreSQL to be ready"""
    retry = 0
    while retry < max_retries:
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                dbname=dbname
            )
            conn.close()
            return True
        except psycopg2.OperationalError:
            retry += 1
            print(f"Waiting for PostgreSQL to be ready... ({retry}/{max_retries})")
            time.sleep(1)
    return False

def create_db_config(host, port, user, password, dbname):
    """Create db_config.json file"""
    config = {
        "host": host,
        "port": port,
        "database": dbname,
        "user": user,
        "password": password
    }
    
    with open("db_config.json", "w") as f:
        json.dump(config, f, indent=4)
    print("Created db_config.json")

def start_db(args):
    """Start the database using Docker Compose"""
    if not check_docker():
        return False

    # Set environment variable for database password
    os.environ["DB_PASSWORD"] = args.password

    print("Starting PostgreSQL container...")
    success, output = run_command("docker-compose up -d")
    if not success:
        print("Error starting containers:", output)
        return False

    print("Waiting for PostgreSQL to be ready...")
    if not wait_for_postgres(
        args.host,
        args.port,
        args.user,
        args.password,
        args.dbname
    ):
        print("Error: PostgreSQL did not become ready in time")
        return False

    # Create db_config.json
    create_db_config(
        args.host,
        args.port,
        args.user,
        args.password,
        args.dbname
    )

    print("\nDatabase is ready!")
    print(f"Connection details:")
    print(f"  Host: {args.host}")
    print(f"  Port: {args.port}")
    print(f"  Database: {args.dbname}")
    print(f"  User: {args.user}")
    print("\nConfiguration file db_config.json has been created.")
    return True

def stop_db(args):
    """Stop the database containers"""
    print("Stopping PostgreSQL container...")
    success, output = run_command("docker-compose down")
    if not success:
        print("Error stopping containers:", output)
        return False
    print("Database stopped successfully")
    return True

def main():
    parser = argparse.ArgumentParser(description="Manage the genomic database")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Start command
    start_parser = subparsers.add_parser("start", help="Start the database")
    start_parser.add_argument("--host", default="localhost", help="Database host")
    start_parser.add_argument("--port", type=int, default=5432, help="Database port")
    start_parser.add_argument("--user", default="genomic_user", help="Database user")
    start_parser.add_argument("--password", default="genomic_password", help="Database password")
    start_parser.add_argument("--dbname", default="genomic_data", help="Database name")

    # Stop command
    stop_parser = subparsers.add_parser("stop", help="Stop the database")

    args = parser.parse_args()

    if args.command == "start":
        if start_db(args):
            print("\nYou can now run the genomic data upload script:")
            print("python genomic_data_upload.py /path/to/data")
    elif args.command == "stop":
        stop_db(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

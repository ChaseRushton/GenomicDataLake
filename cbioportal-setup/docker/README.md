# Local cBioPortal Instance

This directory contains the configuration for running a local instance of cBioPortal connected to your SQL Server database.

## Prerequisites

1. Docker Desktop installed and running
2. SQL Server running with the following configuration:
   - Host: localhost (will be accessed as host.docker.internal from Docker)
   - Port: 1433
   - Database: cbioportal (will be created by the migration)
   - Authentication: SQL Server authentication enabled

## Setup Instructions

1. Update the database credentials in both files:
   - `docker-compose.yml`
   - `config/portal.properties`
   Replace the following placeholders with your actual SQL Server credentials:
   - `DB_USER=sa` (replace 'sa' with your username)
   - `DB_PASSWORD=YourPassword` (replace 'YourPassword' with your actual password)

2. Create the cBioPortal database in SQL Server:
   ```sql
   CREATE DATABASE cbioportal;
   ```

3. Start the cBioPortal services:
   ```bash
   docker-compose up -d
   ```

4. Access cBioPortal at: http://localhost:8080

## Loading Studies

Place your study files in the `study` directory. The files should follow the [cBioPortal study format](https://docs.cbioportal.org/file-formats/).

## Troubleshooting

1. If you encounter database connection issues:
   - Verify SQL Server is running and accessible
   - Check that the credentials in configuration files are correct
   - Ensure SQL Server is configured to accept TCP/IP connections

2. For other issues, check the logs:
   ```bash
   docker-compose logs -f
   ```

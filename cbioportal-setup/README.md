# cBioPortal Setup

This repository contains configuration and setup files for running cBioPortal in different environments. It provides three different setup options:

## Setup Options

1. [Docker Setup](docker/README.md)
   - Containerized setup using Docker and Docker Compose
   - Easiest to get started with
   - Ideal for development and testing

2. [Windows Setup](windows/README.md)
   - Native Windows installation
   - Direct installation on Windows without containers
   - Good for Windows-based production environments

3. [Linux Setup](linux/README.md)
   - Native Linux installation
   - Includes automated installation scripts
   - Recommended for production deployments

## Common Features

All setups include:
- SQL Server database integration
- Complete configuration files
- Logging setup
- Study data management

## Prerequisites

- SQL Server instance
- Java 11 or later (for non-Docker setups)
- Docker Desktop (for Docker setup)
- Git

## Getting Started

1. Choose your preferred setup option from the directories above
2. Follow the README instructions in the respective directory
3. Configure your database connection settings
4. Start cBioPortal using the provided scripts

## Database Configuration

All setups require a SQL Server database. Update the following settings in your chosen setup's `portal.properties`:

```properties
db.user=your_username
db.password=your_password
db.host=your_database_host
db.portal_db_name=cbioportal
```

## Contributing

Feel free to submit issues and enhancement requests!

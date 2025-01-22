# Local cBioPortal Installation (Non-Docker)

This guide details how to run cBioPortal directly on Windows without Docker.

## Prerequisites

1. Java 11 or later
2. Maven 3.6.1 or later
3. Git
4. SQL Server (already configured)
5. Python 3.9 or later

## Installation Steps

1. Install required dependencies:
```powershell
winget install OpenJDK.JDK.11
winget install Apache.Maven
winget install Python.Python.3.9
```

2. Clone cBioPortal:
```powershell
git clone https://github.com/cBioPortal/cbioportal.git
cd cbioportal
git checkout v5.4.6
```

3. Configure database:
- Create database named 'cbioportal' in SQL Server
- Run the database migration script

4. Build cBioPortal:
```powershell
mvn clean install -DskipTests
```

5. Configure the application:
- Update portal.properties with database credentials
- Configure log4j settings if needed

6. Run the application:
```powershell
mvn tomcat7:run -Dmaven.tomcat.port=8080
```

Access the portal at: http://localhost:8080

## Directory Structure
```
cbioportal-local/
├── config/
│   ├── portal.properties    # Main configuration file
│   └── log4j.properties    # Logging configuration
├── studies/                # Directory for study files
└── logs/                  # Application logs
```

## Troubleshooting

1. Java/Maven Issues:
   - Verify JAVA_HOME is set correctly
   - Ensure Maven is in system PATH

2. Database Issues:
   - Check SQL Server connection settings
   - Verify database permissions

3. Build Issues:
   - Clear Maven cache: `mvn clean`
   - Delete target directory and rebuild

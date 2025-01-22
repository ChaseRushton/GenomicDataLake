# Linux cBioPortal Installation

This guide provides instructions for installing cBioPortal directly on a Linux system.

## Prerequisites

- Ubuntu/Debian-based Linux distribution (for other distributions, modify the package installation commands accordingly)
- Root access or sudo privileges
- SQL Server instance accessible from the Linux machine

## Directory Structure

```
/opt/cbioportal/
├── cbioportal/        # Source code
├── config/            # Configuration files
│   ├── portal.properties
│   └── log4j.properties
├── studies/           # Study files
└── logs/             # Application logs
```

## Installation

1. Clone this repository and navigate to it:
```bash
git clone <repository-url>
cd cbioportal-linux
```

2. Make the scripts executable:
```bash
chmod +x install.sh start.sh
```

3. Run the installation script:
```bash
sudo ./install.sh
```

4. Update the database configuration:
Edit `/opt/cbioportal/config/portal.properties` and update these fields:
```properties
db.user=your_username
db.password=your_password
db.host=your_sql_server_host
```

5. Start cBioPortal:
```bash
./start.sh
```

The portal will be available at: http://localhost:8080

## Configuration Files

### portal.properties
- Main configuration file
- Located at `/opt/cbioportal/config/portal.properties`
- Contains database connection settings and portal customization options

### log4j.properties
- Logging configuration
- Located at `/opt/cbioportal/config/log4j.properties`
- Logs are written to `/opt/cbioportal/logs/portal.log`

## Managing Studies

1. Place study files in `/opt/cbioportal/studies/`
2. Follow the [cBioPortal study format](https://docs.cbioportal.org/file-formats/)
3. Import studies using the provided web interface or command-line tools

## Troubleshooting

1. Database Connection Issues:
   - Verify SQL Server is running and accessible
   - Check credentials in portal.properties
   - Ensure SQL Server allows remote connections
   - Verify firewall settings

2. Java/Maven Issues:
   - Check Java version: `java -version`
   - Verify Maven installation: `mvn -version`
   - Clear Maven cache: `mvn clean`

3. Permission Issues:
   - Ensure proper ownership: `sudo chown -R $USER:$USER /opt/cbioportal`
   - Check log file permissions

4. Memory Issues:
   - Adjust Java heap size in `start.sh`
   - Monitor memory usage with `top` or `htop`

## Maintenance

1. Updating cBioPortal:
```bash
cd /opt/cbioportal/cbioportal
git fetch
git checkout <new-version-tag>
mvn clean install -DskipTests
```

2. Log Rotation:
- Logs are automatically rotated based on size
- Old logs are kept in `/opt/cbioportal/logs/`

3. Backup:
- Regularly backup the database
- Backup the `/opt/cbioportal/studies/` directory
- Consider backing up configuration files

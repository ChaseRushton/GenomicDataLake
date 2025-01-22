#!/bin/bash

# Exit on any error
set -e

# Check if running as the correct user
if [ "$EUID" -eq 0 ]; then 
    echo "Please do not run as root"
    exit 1
fi

# Set environment variables
export PORTAL_HOME=/opt/cbioportal
export JAVA_OPTS="-Xms2g -Xmx4g -Djava.awt.headless=true"

# Check if database exists and is accessible
echo "Checking database connection..."
python3 /opt/cbioportal/cbioportal/core/src/main/scripts/migrate_db.py --properties-file /opt/cbioportal/config/portal.properties

# Start cBioPortal
echo "Starting cBioPortal..."
cd /opt/cbioportal/cbioportal
mvn tomcat7:run -Dmaven.tomcat.port=8080

# Note: The process will stay in the foreground. Use Ctrl+C to stop.

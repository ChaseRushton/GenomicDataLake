#!/bin/bash

# Exit on any error
set -e

echo "Installing cBioPortal dependencies..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root or with sudo"
    exit 1
fi

# Update package list
apt-get update

# Install Java 11
echo "Installing Java 11..."
apt-get install -y openjdk-11-jdk

# Install Maven
echo "Installing Maven..."
apt-get install -y maven

# Install Python 3
echo "Installing Python 3..."
apt-get install -y python3 python3-pip

# Install git
echo "Installing git..."
apt-get install -y git

# Create directory structure
echo "Creating directory structure..."
mkdir -p /opt/cbioportal/{config,studies,logs}

# Clone cBioPortal
echo "Cloning cBioPortal..."
cd /opt/cbioportal
if [ ! -d "cbioportal" ]; then
    git clone https://github.com/cBioPortal/cbioportal.git
    cd cbioportal
    git checkout v5.4.6
else
    echo "cBioPortal directory already exists, skipping clone..."
fi

# Copy configuration files
echo "Setting up configuration..."
cp config/portal.properties /opt/cbioportal/config/
cp config/log4j.properties /opt/cbioportal/config/

# Set permissions
echo "Setting permissions..."
chown -R $SUDO_USER:$SUDO_USER /opt/cbioportal

# Build cBioPortal
echo "Building cBioPortal..."
cd /opt/cbioportal/cbioportal
su - $SUDO_USER -c "cd /opt/cbioportal/cbioportal && mvn clean install -DskipTests"

echo "Installation complete!"
echo "Please update the database configuration in /opt/cbioportal/config/portal.properties"
echo "To start cBioPortal, run: ./start.sh"

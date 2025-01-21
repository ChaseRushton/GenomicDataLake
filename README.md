# Genomic Data Lake

A robust Python script for uploading and managing genomic data files to a database with advanced features including parallel processing, quality control reporting, and email notifications.

## Features

- **File Processing**
  - Automatic file type detection and handling
  - Parallel processing for large files
  - Configurable chunk size for optimal performance
  - Dry run mode for validation without uploads

- **Data Validation**
  - Schema validation for different file types
  - Data type checking and standardization
  - Duplicate detection using record hashing
  - Comprehensive QC reports

- **Database Management**
  - Automatic table creation and schema validation
  - Table backups before modifications
  - Transaction support for data integrity

- **Reporting**
  - Detailed HTML email reports
  - Processing statistics and summaries
  - Color-coded success/failure indicators
  - QC report attachments

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ChaseRushton/GenomicDataLake.git
   cd GenomicDataLake
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your database and email settings:
   - Copy `email_config.yaml.example` to `email_config.yaml`
   - Copy `db_config.json.example` to `db_config.json`
   - Update both files with your settings

## Database Setup

You can set up the database using either Docker (recommended for development) or a local PostgreSQL installation.

### Option 1: Docker Setup (Recommended for Development)

The project includes a Docker-based PostgreSQL database setup for easy deployment. Make sure you have Docker and Docker Compose installed on your system.

#### Prerequisites

- Docker
- Docker Compose
- Python 3.7+
- pip

#### Starting the Database

1. Start the database using the management script:
   ```bash
   python manage_db.py start
   ```

   This will:
   - Start a PostgreSQL container
   - Create necessary database schemas and tables
   - Generate a `db_config.json` file with connection details

   Optional arguments:
   ```bash
   python manage_db.py start \
       --host localhost \
       --port 5432 \
       --user genomic_user \
       --password genomic_password \
       --dbname genomic_data
   ```

2. To stop the database:
   ```bash
   python manage_db.py stop
   ```

### Option 2: Local PostgreSQL Setup

If you prefer to use a local PostgreSQL installation, follow these steps:

1. Install PostgreSQL:
   - Windows: Download and install from [PostgreSQL Downloads](https://www.postgresql.org/download/windows/)
   - macOS: `brew install postgresql`
   - Linux: `sudo apt-get install postgresql`

2. Make sure PostgreSQL service is running:
   - Windows: Check Services app
   - macOS: `brew services start postgresql`
   - Linux: `sudo service postgresql start`

3. Run the local setup script:
   ```bash
   python setup_local_db.py --superuser-password your_superuser_password
   ```

   Optional arguments:
   ```bash
   python setup_local_db.py \
       --host localhost \
       --port 5432 \
       --user genomic_user \
       --password genomic_password \
       --dbname genomic_data \
       --superuser postgres \
       --superuser-password your_superuser_password
   ```

   This will:
   - Create a new database user
   - Create the database
   - Set up the schema and tables
   - Generate a `db_config.json` file

### Database Schema

The database includes the following tables in the `genomic` schema:

1. `tmb_data`:
   - Sample-level TMB (Tumor Mutational Burden) data
   - Includes confidence intervals and metadata

2. `cns_data`:
   - Copy number segment data
   - Includes chromosomal positions and gene annotations

Each table includes:
- Automatic timestamps
- Record hashing for deduplication
- Appropriate indexes for efficient querying
- Trigger-based timestamp updates

## Usage

Basic usage:
```bash
python genomic_data_upload.py /path/to/data
```

With all options:
```bash
python genomic_data_upload.py /path/to/data \
    --files file1.txt file2.txt \
    --db-config db_config.json \
    --log-file upload.log \
    --parallel \
    --chunk-size 5000 \
    --backup-dir ./backups \
    --qc-dir ./qc_reports \
    --email-config email_config.yaml
```

### Command Line Arguments

- `directory`: Directory containing the files to process
- `--files`: Specific files to process (optional)
- `--db-config`: Path to database configuration file
- `--log-file`: Path to log file
- `--parallel`: Enable parallel processing
- `--chunk-size`: Chunk size for parallel processing
- `--backup-dir`: Directory for table backups
- `--qc-dir`: Directory for QC reports
- `--dry-run`: Validate files without uploading
- `--email-config`: Path to email configuration file

## Configuration Files

### Database Configuration (db_config.json)
```json
{
    "host": "localhost",
    "port": 5432,
    "database": "genomic_data",
    "user": "username",
    "password": "password"
}
```

### Email Configuration (email_config.yaml)
```yaml
smtp:
  server: smtp.example.com
  port: 587
  sender: sender@example.com
  username: username
  password: password
  use_tls: true

recipients:
  - recipient1@example.com
  - recipient2@example.com
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

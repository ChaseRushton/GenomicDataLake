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

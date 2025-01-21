# Genomic Data Lake

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.7%2B-blue)
![PostgreSQL](https://img.shields.io/badge/postgresql-15%2B-blue)

A robust Python-based solution for managing and analyzing genomic data. This project provides a comprehensive system for uploading, validating, and storing genomic data files with features like parallel processing, quality control reporting, and automated notifications.

## 🚀 Key Features

- **Robust Data Processing**
  - Automatic file type detection and validation
  - Parallel processing for large files
  - Duplicate detection and handling
  - Data standardization and cleaning

- **Quality Control**
  - Comprehensive QC reports
  - Data validation against predefined schemas
  - Automated error detection and logging
  - File-level and record-level validation

- **Database Management**
  - Automated schema management
  - Optimized table indexing
  - Automatic backups
  - Transaction support

- **Monitoring & Reporting**
  - HTML email reports with processing statistics
  - Detailed logging
  - Processing time tracking
  - Error notifications

## 📋 Requirements

### Core Dependencies
- Python 3.7+
- PostgreSQL 15+
- pip (Python package manager)

### Python Packages
```
pandas>=1.5.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
PyYAML>=6.0.1
tqdm>=4.65.0
```

### Optional Dependencies
- Docker & Docker Compose (for containerized setup)
- SMTP server (for email notifications)

## 🛠️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ChaseRushton/GenomicDataLake.git
   cd GenomicDataLake
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure settings:
   ```bash
   # Copy example configuration files
   cp email_config.yaml.example email_config.yaml
   cp db_config.json.example db_config.json
   
   # Edit the files with your settings
   nano email_config.yaml
   nano db_config.json
   ```

## 💾 Database Setup

Choose between two setup methods based on your needs:

### 🐳 Option 1: Docker Setup (Recommended for Development)

Quick setup with Docker:
```bash
# Start the database
python manage_db.py start

# Optional: Configure custom settings
python manage_db.py start \
    --host localhost \
    --port 5432 \
    --user genomic_user \
    --password custom_password
```

### 🔧 Option 2: Local PostgreSQL Setup

For production or when Docker isn't available:

1. **Install PostgreSQL**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install postgresql postgresql-contrib

   # macOS with Homebrew
   brew install postgresql

   # Windows
   # Download installer from https://www.postgresql.org/download/windows/
   ```

2. **Run Setup Script**:
   ```bash
   python setup_local_db.py --superuser-password your_password
   ```

## 📊 Data Processing

### Supported File Types

1. **TMB Data Files**
   - Format: Tab-delimited text
   - Required columns: SampleName, TMB
   - Optional columns: BinomialLow, BinomialHigh

2. **CNS Data Files**
   - Format: Tab-delimited text
   - Required columns: SampleName, CHROM, START, STOP
   - Optional columns: GENE, log2

### Running the Upload

Basic usage:
```bash
python genomic_data_upload.py /path/to/data
```

Advanced options:
```bash
python genomic_data_upload.py /path/to/data \
    --parallel \
    --chunk-size 5000 \
    --backup-dir ./backups \
    --qc-dir ./qc_reports \
    --email-config email_config.yaml
```

## 📊 Data Visualization

The project provides multiple visualization options through an interactive web interface and advanced genomic visualization tools.

### 🌐 Interactive Dashboard

Start the visualization dashboard:
```bash
streamlit run visualize_data.py
```

#### Basic Visualizations
- **TMB Analysis**
  - Distribution histogram
  - Confidence interval plots
  - Summary statistics
  - Interactive data table

- **Copy Number Analysis**
  - Chromosome coverage plots
  - CNV heatmap for top genes
  - Sample statistics
  - Filtered data browser

### 🧬 Advanced Genomic Visualizations

#### Circos Plots
Circular genome visualization showing CNV patterns across all chromosomes:
```python
from genomic_visualizations import GenomicVisualizer

visualizer = GenomicVisualizer()
visualizer.create_circos_plot(cnv_data, title="Genome-wide CNV Profile")
```

Features:
- Chromosome ideograms
- Color-coded CNV segments
- Automatic scaling
- Publication-quality output

#### IGV Integration
Export data for visualization in the Integrative Genomics Viewer (IGV):

1. **IGV Format**
   ```python
   visualizer.export_for_igv(cnv_data, track_name="My CNV Data")
   ```
   - Wiggle track format
   - Automatic track configuration
   - Custom track names and colors

2. **BED Format**
   ```python
   visualizer.export_bed_file(cnv_data)
   ```
   - Standard BED format
   - Color-coded segments
   - Gene annotations
   - Position information

#### Chromosome-Specific Plots
Detailed visualization of individual chromosomes:
```python
visualizer.create_chromosome_plot(cnv_data, "1")  # For chromosome 1
```

Features:
- Detailed CNV segments
- Gene annotations
- Position markers
- Interactive zooming

### 🎨 Customization Options

#### Plot Styling
```python
# Custom colors for CNV segments
def get_rgb(log2):
    if log2 > 0.5:
        return "255,0,0"  # Strong amplification
    elif log2 > 0:
        return "255,165,0"  # Weak amplification
    elif log2 < -0.5:
        return "0,0,255"  # Strong deletion
    else:
        return "0,165,255"  # Weak deletion
```

#### Output Formats
- PNG (default)
- SVG for vector graphics
- PDF for publications
- Interactive HTML for web

#### Data Filtering
```python
# Filter by chromosome
chromosome_data = cnv_data[cnv_data['chrom'] == '1']

# Filter by gene
gene_data = cnv_data[cnv_data['gene'].isin(['BRCA1', 'BRCA2'])]
```

### 📊 Example Workflows

#### 1. Basic Analysis
```bash
# Start the dashboard
streamlit run visualize_data.py

# Select "TMB Analysis" or "Copy Number Analysis"
# Interact with plots and tables
```

#### 2. IGV Visualization
```bash
# 1. Export data
python genomic_visualizations.py --input cnv_data.csv --output-dir viz

# 2. Open IGV
# 3. Load exported files
# 4. Configure tracks
```

#### 3. Publication Plots
```python
# Create high-resolution Circos plot
visualizer = GenomicVisualizer(output_dir="publication_figures")
visualizer.create_circos_plot(
    cnv_data,
    output_file="figure1.png",
    title="Figure 1: Genome-wide CNV Profile"
)
```

### 🔧 Troubleshooting

Common issues and solutions:

1. **Memory Issues**
   ```python
   # Reduce data size
   filtered_data = cnv_data.sample(n=1000)
   ```

2. **Plot Quality**
   ```python
   # Increase DPI for better resolution
   visualizer.create_circos_plot(cnv_data, dpi=300)
   ```

3. **IGV Format**
   - Ensure chromosome names match genome build
   - Check file permissions
   - Verify track format

### 🎯 Best Practices

1. **Data Preparation**
   - Clean data before visualization
   - Remove outliers if necessary
   - Verify chromosome naming

2. **Plot Organization**
   - Use consistent colors
   - Add clear titles and labels
   - Include scale bars

3. **File Management**
   - Use descriptive filenames
   - Organize by analysis type
   - Back up visualization configs

## 📧 Email Notifications

Configure email settings in `email_config.yaml`:
```yaml
smtp:
  server: smtp.example.com
  port: 587
  sender: sender@example.com
  username: your-username
  password: your-password
  use_tls: true

recipients:
  - analyst1@example.com
  - analyst2@example.com
```

Email reports include:
- Processing summary
- Success/failure statistics
- QC report summaries
- Attached detailed reports

## 🔍 Quality Control

QC reports include:
- Record counts
- Missing value analysis
- Data type validation
- Value distribution statistics
- Duplicate detection results

Access QC reports:
```bash
# Generate QC report only
python genomic_data_upload.py /path/to/data --dry-run

# Specify custom QC directory
python genomic_data_upload.py /path/to/data --qc-dir ./custom_qc
```

## 🔄 Database Schema

### TMB Data Table
```sql
CREATE TABLE genomic.tmb_data (
    id SERIAL PRIMARY KEY,
    sample_name VARCHAR(255) NOT NULL,
    tmb FLOAT NOT NULL,
    binomial_low FLOAT,
    binomial_high FLOAT,
    upload_timestamp TIMESTAMP,
    record_hash VARCHAR(32) UNIQUE
);
```

### CNS Data Table
```sql
CREATE TABLE genomic.cns_data (
    id SERIAL PRIMARY KEY,
    sample_name VARCHAR(255) NOT NULL,
    chrom VARCHAR(50) NOT NULL,
    start_pos INTEGER NOT NULL,
    stop_pos INTEGER NOT NULL,
    gene VARCHAR(255),
    log2 FLOAT,
    upload_timestamp TIMESTAMP,
    record_hash VARCHAR(32) UNIQUE
);
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. Commit your changes:
   ```bash
   git commit -m 'Add amazing feature'
   ```
4. Push to the branch:
   ```bash
   git push origin feature/amazing-feature
   ```
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Add unit tests for new features
- Update documentation
- Maintain backward compatibility

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- PostgreSQL team for the robust database system
- Python community for excellent libraries
- Contributors and users of this project

## 📞 Support

- Create an issue for bug reports or feature requests
- Contact maintainers for security concerns
- Check documentation for common issues

## 🔮 Future Plans

- [ ] Support for additional genomic file formats
- [ ] Advanced data visualization
- [ ] REST API for data access
- [ ] Integration with analysis pipelines
- [ ] Cloud storage support

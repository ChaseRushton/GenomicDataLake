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

1. **TMB (Tumor Mutational Burden) Data**
   **Format**: Tab-delimited text (`.txt`, `.tsv`)
   ```
   SampleName	TMB	BinomialLow	BinomialHigh	ExtraInfo
   SAMPLE1	12.5	10.2	14.8	PASSED
   SAMPLE2	8.3	6.1	10.5	PASSED
   ```

   **Required Columns**:
   - `SampleName`: Unique sample identifier
   - `TMB`: Tumor mutational burden value (float)

   **Optional Columns**:
   - `BinomialLow`: Lower confidence interval
   - `BinomialHigh`: Upper confidence interval
   - `ExtraInfo`: Additional sample information

2. **CNV (Copy Number Variation) Data**
   **Format**: Tab-delimited text (`.txt`, `.tsv`)
   ```
   SampleName	CHROM	START	STOP	GENE	log2	CN	Type
   SAMPLE1	1	1000	2000	BRCA1	0.58	3	AMP
   SAMPLE1	2	3000	4000	TP53	-1.0	1	DEL
   ```

   **Required Columns**:
   - `SampleName`: Sample identifier
   - `CHROM`: Chromosome number/name
   - `START`: Start position
   - `STOP`: End position

   **Optional Columns**:
   - `GENE`: Gene symbol
   - `log2`: Log2 ratio
   - `CN`: Copy number
   - `Type`: Variation type (AMP/DEL)

3. **VCF (Variant Call Format)**
   **Format**: Standard VCF (`.vcf`, `.vcf.gz`)
   ```
   ##fileformat=VCFv4.2
   #CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO
   1	1000	rs123	A	G	100	PASS	AF=0.5
   ```

   **Required Fields**:
   - Standard VCF headers
   - Core fields (CHROM, POS, ID, REF, ALT)

   **Supported INFO Fields**:
   - `AF`: Allele frequency
   - `DP`: Read depth
   - `SOMATIC`: Somatic status
   - `IMPACT`: Variant impact

4. **MAF (Mutation Annotation Format)**
   **Format**: Tab-delimited text (`.maf`)
   ```
   Hugo_Symbol	Chromosome	Start_Position	Variant_Classification
   BRCA1	17	41234451	Missense_Mutation
   TP53	17	7577121	Nonsense_Mutation
   ```

   **Required Columns**:
   - `Hugo_Symbol`: Gene symbol
   - `Chromosome`: Chromosome number
   - `Start_Position`: Mutation position
   - `Variant_Classification`: Mutation type

   **Optional Columns**:
   - `Variant_Type`: SNP/INS/DEL
   - `Reference_Allele`: Reference base(s)
   - `Tumor_Seq_Allele2`: Tumor allele
   - `t_alt_count`: Alt allele count

5. **Expression Data**
   **Format**: Tab-delimited text (`.txt`, `.tsv`)
   ```
   GeneID	SAMPLE1	SAMPLE2	SAMPLE3
   BRCA1	10.5	12.3	9.8
   TP53	8.7	7.9	11.2
   ```

   **Required Columns**:
   - `GeneID`: Gene identifier
   - Sample columns: Expression values

   **Optional Metadata**:
   - Gene descriptions
   - Chromosome locations
   - Strand information

6. **Fusion Data**
   **Format**: Tab-delimited text (`.txt`, `.tsv`)
   ```
   Sample	Gene1	Gene2	Breakpoint1	Breakpoint2	Type
   SAMPLE1	BCR	ABL1	22:23632600	9:133729450	FUSION
   ```

   **Required Columns**:
   - `Sample`: Sample identifier
   - `Gene1`: 5' gene
   - `Gene2`: 3' gene
   - `Breakpoint1`: 5' breakpoint
   - `Breakpoint2`: 3' breakpoint

   **Optional Columns**:
   - `Type`: Fusion type
   - `ReadCount`: Supporting reads
   - `Confidence`: Detection confidence

7. **Clinical Data**
   **Format**: Tab-delimited text (`.txt`, `.tsv`)
   ```
   SampleID	Age	Gender	Stage	Response
   SAMPLE1	65	M	III	CR
   SAMPLE2	45	F	II	PR
   ```

   **Required Columns**:
   - `SampleID`: Sample identifier
   - At least one clinical variable

   **Optional Columns**:
   - Demographic information
   - Clinical outcomes
   - Treatment information

8. **BED Format**
   **Format**: BED file (`.bed`)
   ```
   chr1	1000	2000	Feature1	0	+	1000	2000	255,0,0
   ```

   **Required Fields**:
   - Chromosome
   - Start position
   - End position

   **Optional Fields**:
   - Name
   - Score
   - Strand
   - ThickStart/ThickEnd
   - RGB color

### File Processing Rules

1. **Validation**:
   ```python
   def validate_file(file_path):
       """Validate file format and content"""
       extension = file_path.suffix.lower()
       if extension in ['.txt', '.tsv']:
           validate_tabular_file(file_path)
       elif extension in ['.vcf', '.vcf.gz']:
           validate_vcf_file(file_path)
       elif extension == '.maf':
           validate_maf_file(file_path)
   ```

2. **Data Type Conversion**:
   ```python
   def convert_data_types(df, file_type):
       """Convert columns to appropriate data types"""
       if file_type == 'TMB':
           df['TMB'] = pd.to_numeric(df['TMB'])
           if 'BinomialLow' in df.columns:
               df['BinomialLow'] = pd.to_numeric(df['BinomialLow'])
       elif file_type == 'CNV':
           df['START'] = pd.to_numeric(df['START'])
           df['STOP'] = pd.to_numeric(df['STOP'])
   ```

3. **Quality Control**:
   ```python
   def check_data_quality(df, file_type):
       """Check data quality"""
       # Check for missing values
       missing = df.isnull().sum()
       
       # Check for duplicates
       duplicates = df.duplicated().sum()
       
       # Validate value ranges
       if file_type == 'TMB':
           assert df['TMB'].min() >= 0, "TMB values must be non-negative"
   ```

### Example Usage

```python
# Load and process multiple file types
def process_genomic_data(sample_id):
    # Load TMB data
    tmb_data = pd.read_csv(f"{sample_id}_tmb.txt", sep='\t')
    validate_file(tmb_data, 'TMB')
    
    # Load CNV data
    cnv_data = pd.read_csv(f"{sample_id}_cnv.txt", sep='\t')
    validate_file(cnv_data, 'CNV')
    
    # Load VCF data
    vcf_data = read_vcf(f"{sample_id}.vcf")
    validate_file(vcf_data, 'VCF')
    
    # Create integrated report
    create_report(sample_id, tmb_data, cnv_data, vcf_data)
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

### 📚 Example Use Cases

#### 1. Clinical Report Generation
Generate a comprehensive clinical report with TMB and CNV data:

```python
from genomic_visualizations import GenomicVisualizer
import pandas as pd

# Initialize visualizer
visualizer = GenomicVisualizer(output_dir="clinical_reports")

# Load data
tmb_data = pd.read_csv("patient_tmb.csv")
cnv_data = pd.read_csv("patient_cnv.csv")

# Create patient report directory
patient_id = "PATIENT001"
report_dir = f"reports/{patient_id}"
os.makedirs(report_dir, exist_ok=True)

# 1. TMB Plot with confidence intervals
tmb_plot = visualizer.create_tmb_plot(
    tmb_data,
    highlight_sample=patient_id,
    output_file=f"{report_dir}/tmb_profile.png"
)

# 2. Chromosome-specific CNV plots
affected_chromosomes = cnv_data[cnv_data['log2'].abs() > 0.5]['chrom'].unique()
for chrom in affected_chromosomes:
    visualizer.create_chromosome_plot(
        cnv_data,
        chrom,
        output_file=f"{report_dir}/chr{chrom}_profile.png",
        highlight_genes=['BRCA1', 'BRCA2', 'TP53']  # Highlight important genes
    )

# 3. Genome-wide Circos plot
visualizer.create_circos_plot(
    cnv_data,
    output_file=f"{report_dir}/genome_overview.png",
    title=f"Patient {patient_id} Genomic Profile"
)
```

#### 2. Cohort Analysis
Compare multiple samples in a cohort:

```python
# Load cohort data
cohort_data = pd.read_csv("cohort_cnv.csv")

# 1. Create cohort-wide heatmap
visualizer.create_cohort_heatmap(
    cohort_data,
    sample_groups={'Responder': ['P1', 'P2'], 'Non-responder': ['P3', 'P4']},
    output_file="cohort_heatmap.png"
)

# 2. Compare TMB distributions
visualizer.create_tmb_distribution(
    cohort_data,
    group_column='response_status',
    output_file="tmb_by_response.png"
)

# 3. Export for detailed IGV analysis
for sample in cohort_data['sample_id'].unique():
    sample_data = cohort_data[cohort_data['sample_id'] == sample]
    visualizer.export_for_igv(
        sample_data,
        output_file=f"igv_tracks/{sample}.igv",
        track_name=f"Sample_{sample}"
    )
```

#### 3. Publication-Quality Figures
Create publication-ready visualizations:

```python
# Configure publication settings
publication_settings = {
    'dpi': 300,
    'width': 8,
    'height': 6,
    'font_family': 'Arial',
    'font_size': 12,
    'line_width': 1.5
}

# 1. Multi-panel figure
def create_figure_1(data, settings):
    """Create a multi-panel figure for publication"""
    import matplotlib.pyplot as plt
    from matplotlib.gridspec import GridSpec
    
    fig = plt.figure(figsize=(settings['width']*2, settings['height']*2))
    gs = GridSpec(2, 2, figure=fig)
    
    # A. TMB Distribution
    ax1 = fig.add_subplot(gs[0, 0])
    visualizer.plot_tmb_distribution(
        data,
        ax=ax1,
        title='A) TMB Distribution'
    )
    
    # B. Circos Plot
    ax2 = fig.add_subplot(gs[0, 1])
    visualizer.plot_circos(
        data,
        ax=ax2,
        title='B) Genome-wide CNV'
    )
    
    # C. Gene-level Analysis
    ax3 = fig.add_subplot(gs[1, :])
    visualizer.plot_gene_heatmap(
        data,
        ax=ax3,
        title='C) Gene-level CNV Profile'
    )
    
    plt.tight_layout()
    return fig

# Create and save the figure
fig1 = create_figure_1(data, publication_settings)
fig1.savefig('figure1.pdf', dpi=publication_settings['dpi'])
```

#### 4. Custom Analysis Pipeline
Create a custom analysis pipeline combining multiple visualizations:

```python
class GenomicAnalysisPipeline:
    def __init__(self, output_dir):
        self.visualizer = GenomicVisualizer(output_dir)
        self.output_dir = output_dir
    
    def analyze_sample(self, sample_id, cnv_data, tmb_data):
        """Run complete analysis for a sample"""
        # Create sample directory
        sample_dir = os.path.join(self.output_dir, sample_id)
        os.makedirs(sample_dir, exist_ok=True)
        
        # 1. Basic QC plots
        self._create_qc_plots(sample_dir, cnv_data)
        
        # 2. Detailed analysis
        self._create_detailed_analysis(sample_dir, cnv_data, tmb_data)
        
        # 3. Export for IGV
        self._export_igv_files(sample_dir, cnv_data)
    
    def _create_qc_plots(self, output_dir, data):
        """Create quality control plots"""
        # Coverage plot
        self.visualizer.create_coverage_plot(
            data,
            output_file=os.path.join(output_dir, "coverage.png")
        )
        
        # Segment size distribution
        self.visualizer.create_segment_size_plot(
            data,
            output_file=os.path.join(output_dir, "segment_sizes.png")
        )
    
    def _create_detailed_analysis(self, output_dir, cnv_data, tmb_data):
        """Create detailed analysis plots"""
        # CNV profile
        self.visualizer.create_circos_plot(
            cnv_data,
            output_file=os.path.join(output_dir, "cnv_profile.png")
        )
        
        # TMB analysis
        self.visualizer.create_tmb_plot(
            tmb_data,
            output_file=os.path.join(output_dir, "tmb_profile.png")
        )
        
        # Gene-level analysis
        self.visualizer.create_gene_heatmap(
            cnv_data,
            output_file=os.path.join(output_dir, "gene_profile.png")
        )
    
    def _export_igv_files(self, output_dir, data):
        """Export files for IGV visualization"""
        # Export IGV format
        self.visualizer.export_for_igv(
            data,
            output_file=os.path.join(output_dir, "cnv.igv")
        )
        
        # Export BED format
        self.visualizer.export_bed_file(
            data,
            output_file=os.path.join(output_dir, "cnv.bed")
        )

# Usage example
pipeline = GenomicAnalysisPipeline("analysis_results")
pipeline.analyze_sample("PATIENT001", cnv_data, tmb_data)
```

#### 5. Interactive Analysis Session
Example of an interactive analysis session:

```python
import streamlit as st
from genomic_visualizations import GenomicVisualizer

def interactive_analysis():
    st.title("Interactive Genomic Analysis")
    
    # File upload
    cnv_file = st.file_uploader("Upload CNV Data", type="csv")
    if cnv_file is not None:
        data = pd.read_csv(cnv_file)
        
        # Analysis options
        analysis_type = st.selectbox(
            "Select Analysis",
            ["Basic QC", "Detailed Analysis", "Gene Focus"]
        )
        
        if analysis_type == "Basic QC":
            # Show QC plots
            st.subheader("Coverage Analysis")
            coverage_plot = visualizer.create_coverage_plot(data)
            st.pyplot(coverage_plot)
            
            st.subheader("Data Quality")
            quality_metrics = calculate_quality_metrics(data)
            st.table(quality_metrics)
            
        elif analysis_type == "Detailed Analysis":
            # Show detailed analysis
            st.subheader("Genome-wide Analysis")
            circos_plot = visualizer.create_circos_plot(data)
            st.pyplot(circos_plot)
            
            # Chromosome selection
            selected_chrom = st.selectbox("Select Chromosome", data['chrom'].unique())
            chrom_plot = visualizer.create_chromosome_plot(data, selected_chrom)
            st.pyplot(chrom_plot)
            
        else:  # Gene Focus
            # Gene-specific analysis
            genes = st.multiselect("Select Genes", data['gene'].unique())
            if genes:
                gene_plot = visualizer.create_gene_focused_plot(data, genes)
                st.pyplot(gene_plot)

if __name__ == "__main__":
    interactive_analysis()
```

These examples demonstrate various ways to use the visualization tools for different purposes, from clinical reporting to research analysis. Each example can be customized based on specific needs.

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

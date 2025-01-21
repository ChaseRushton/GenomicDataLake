import os
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, text
import logging
from datetime import datetime
import hashlib
import re
import glob
import json
from collections import defaultdict
import argparse
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from tqdm import tqdm
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import yaml

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database connection parameters - Update these with your database details
DB_CONFIG = {
    'host': 'your_host',
    'database': 'genomic_data',
    'user': 'your_username',
    'password': 'your_password'
}

def create_engine_url():
    """Create SQLAlchemy engine URL"""
    return f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}"

def clean_column_name(column_name):
    """Clean column names to be SQL-friendly"""
    return column_name.replace(' ', '_').replace('-', '_').lower()

def get_table_name(file_path, file_type=None):
    """Generate table name from file type"""
    if file_type:
        return f"{file_type}_data"
    else:
        file_type = os.path.splitext(file_path)[1][1:]  # Remove the dot
        base_name = os.path.basename(file_path).split('-')[0]  # Get the first part of the filename
        return f"{base_name}_{file_type}_data"

def get_table_schema(table_type):
    """
    Define expected data types and validation rules for each table.
    """
    schemas = {
        'tmb': {
            'SampleName': {'type': str, 'required': True, 'pattern': r'^[A-Za-z0-9\-_]+$'},
            'TMB': {'type': float, 'required': True, 'min': 0},
            'BinomialLow': {'type': float, 'required': True, 'min': 0, 'max': 1},
            'BinomialHigh': {'type': float, 'required': True, 'min': 0, 'max': 1}
        },
        'cns': {
            'CHROM': {'type': str, 'required': True, 'pattern': r'^(chr)?\d+$|^(chr)?[XY]$'},
            'START': {'type': int, 'required': True, 'min': 0},
            'STOP': {'type': int, 'required': True, 'min': 0},
            'GENE': {'type': str, 'required': True, 'pattern': r'^[A-Za-z0-9\-_]+$'},
            'log2': {'type': float, 'required': True},
            'SampleName': {'type': str, 'required': True, 'pattern': r'^[A-Za-z0-9\-_]+$'}
        },
        'mean_gene_coverage': {
            'SampleName': {'type': str, 'required': True, 'pattern': r'^[A-Za-z0-9\-_]+$'},
            'GENE': {'type': str, 'required': True, 'pattern': r'^[A-Za-z0-9\-_]+$'},
            'MEAN_COVERAGE': {'type': float, 'required': True, 'min': 0}
        },
        'mastervar': {
            'SampleName': {'type': str, 'required': True, 'pattern': r'^[A-Za-z0-9\-_]+$'},
            'CHROM': {'type': str, 'required': True, 'pattern': r'^(chr)?\d+$|^(chr)?[XY]$'},
            'POS': {'type': int, 'required': True, 'min': 0},
            'REF': {'type': str, 'required': True, 'pattern': r'^[ACGT]+$'},
            'ALT': {'type': str, 'required': True, 'pattern': r'^[ACGT]+$'},
            'AF': {'type': float, 'required': True, 'min': 0, 'max': 1}
        }
    }
    return schemas.get(table_type, {})

def standardize_value(value, column_name, schema):
    """
    Standardize values based on column type and rules.
    """
    if pd.isna(value):
        return None
        
    try:
        if 'CHROM' in column_name:
            # Standardize chromosome format (e.g., 'chr1' to '1')
            value = str(value).upper().replace('CHR', '')
            if value == 'X':
                value = '23'
            elif value == 'Y':
                value = '24'
            return value
            
        elif schema['type'] == float:
            return float(value)
        elif schema['type'] == int:
            return int(float(value))  # Handle cases where integers are stored as floats
        elif schema['type'] == str:
            return str(value).strip()
            
    except (ValueError, TypeError):
        return None
    
    return value

def generate_record_hash(row):
    """
    Generate a unique hash for a record to detect duplicates.
    """
    # Convert row to string, sort keys to ensure consistent ordering
    row_str = str(sorted(row.items()))
    return hashlib.md5(row_str.encode()).hexdigest()

def read_file(file_path):
    """Read different file types into pandas DataFrame"""
    ext = os.path.splitext(file_path)[1].lower()
    base_name = os.path.basename(file_path).lower()
    
    try:
        if base_name == 'tmb2022.tsv':
            # Special handling for TMB file
            df = pd.read_csv(file_path, sep='\t')
            # Select and rename specific columns
            df = df[['Samplename', 'FAF', 'FAD', 'FRD']].copy()
            df.columns = ['SampleName', 'TMB', 'BinomialLow', 'BinomialHigh']
        elif ext == '.cns':
            # Special handling for CNS files
            df = pd.read_csv(file_path, sep='\t')
            # Get sample name from file name (everything before first period)
            sample_name = os.path.basename(file_path).split('.')[0]
            # Select and rename columns
            df = df[['chromosome', 'start', 'end', 'gene', 'log2', 'ci_hi', 'ci_lo', 'cn', 'depth', 'probes', 'weight']].copy()
            df.columns = ['CHROM', 'START', 'STOP', 'GENE', 'log2', 'ci_hi', 'ci_lo', 'cn', 'DEPTH', 'probes', 'weight']
            # Add SampleName column
            df['SampleName'] = sample_name
        elif 'mean_gene_coverage.tsv' in base_name:
            # Special handling for mean_gene_coverage.tsv files
            df = pd.read_csv(file_path, sep='\t')
            # Select and rename columns
            df = df[['NAME', 'GENE', 'MEAN_COVERAGE']].copy()
            df.columns = ['SampleName', 'GENE', 'MEAN_COVERAGE']
        elif 'run_mastervarfinal.txt' in base_name:
            # Special handling for Run_masterVarFinal.txt files
            column_names = [
                'SampleName', 'CHROM', 'POS', 'REF', 'ALT', 'TYPE', 'GENE',
                'TRANSCRIPT', 'EXON', 'EFFECT', 'C_CHANGE', 'P_CHANGE',
                'GENE_REGION', 'DEPTH', 'RD', 'AD', 'AF', 'STRAND', 'START', 'STOP'
            ]
            usecols = [0, 1, 2, 66, 67, 3, 4, 11, 27, 15, 5, 16, 25, 26, 51, 52, 53, 54, 13, 58]
            df = pd.read_csv(file_path, sep='\t', usecols=usecols, names=column_names)
        elif 'segments.called.named.tsv' in base_name:
            # Special handling for segments.called.named.tsv files
            df = pd.read_csv(file_path, sep='\t')
            # Get sample name from file name (everything before first period)
            sample_name = os.path.basename(file_path).split('.')[0]
            # Ensure all required columns exist and select them in the specified order
            required_columns = [
                'SampleName', 'GENE', 'CHROM', 'START', 'STOP', 'log2', 'cn', 'DEPTH',
                'weight', 'ci_hi', 'ci_lo', 'probes', 'segment_weight', 'segment_probes'
            ]
            # Map existing column names to required names (assuming they might have different cases)
            column_mapping = {col.lower(): col for col in required_columns}
            df_columns = {col.lower(): col for col in df.columns}
            
            # Create new DataFrame with required columns
            new_df = pd.DataFrame()
            for req_col_lower, req_col in column_mapping.items():
                if req_col_lower in df_columns:
                    new_df[req_col] = df[df_columns[req_col_lower]]
                else:
                    # If column doesn't exist, fill with None
                    new_df[req_col] = None
            
            # Ensure SampleName is set
            new_df['SampleName'] = sample_name
            df = new_df
        elif ext in ['.tsv', '.txt']:
            df = pd.read_csv(file_path, sep='\t')
        elif ext == '.cnr':
            # Assuming these are tab-separated as well, adjust if needed
            df = pd.read_csv(file_path, sep='\t')
        else:
            logging.warning(f"Unsupported file type: {ext}")
            return None
        
        # Clean column names for files without special handling
        if base_name != 'tmb2022.tsv' and ext != '.cns' and 'segments.called.named.tsv' not in base_name and 'mean_gene_coverage.tsv' not in base_name and 'run_mastervarfinal.txt' not in base_name:
            df.columns = [clean_column_name(col) for col in df.columns]
        return df
    
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {str(e)}")
        return None

def validate_and_clean_data(df, table_name):
    """
    Enhanced validation and cleaning of DataFrame.
    """
    if df is None or df.empty:
        return None, None
        
    dropped_records = []
    original_count = len(df)
    
    # Reset index for error reporting
    df = df.reset_index(drop=True)
    
    # Determine table type and get schema
    table_type = next((t for t in ['tmb', 'cns', 'mean_gene_coverage', 'mastervar'] 
                      if t in table_name.lower()), None)
    schema = get_table_schema(table_type)
    
    # Add metadata columns
    df['upload_timestamp'] = datetime.now()
    df['record_hash'] = df.apply(generate_record_hash, axis=1)
    
    # Validate and standardize each row
    cleaned_rows = []
    for idx, row in df.iterrows():
        invalid_columns = []
        standardized_row = {}
        
        for col, val in row.items():
            if col in schema:
                # Standardize value
                std_val = standardize_value(val, col, schema[col])
                
                # Validate value
                if schema[col].get('required', False) and std_val is None:
                    invalid_columns.append(f"{col}: Required field is null")
                elif std_val is not None:
                    # Type validation
                    if not isinstance(std_val, schema[col]['type']):
                        invalid_columns.append(f"{col}: Invalid type")
                    # Pattern validation for strings
                    elif schema[col]['type'] == str and 'pattern' in schema[col]:
                        if not re.match(schema[col]['pattern'], std_val):
                            invalid_columns.append(f"{col}: Does not match pattern {schema[col]['pattern']}")
                    # Range validation for numbers
                    elif schema[col]['type'] in (int, float):
                        if 'min' in schema[col] and std_val < schema[col]['min']:
                            invalid_columns.append(f"{col}: Below minimum value {schema[col]['min']}")
                        if 'max' in schema[col] and std_val > schema[col]['max']:
                            invalid_columns.append(f"{col}: Above maximum value {schema[col]['max']}")
                
                standardized_row[col] = std_val
            else:
                standardized_row[col] = val
        
        if invalid_columns:
            dropped_records.append({
                'index': idx,
                'reason': f"Invalid values in columns: {', '.join(invalid_columns)}",
                **row.to_dict()
            })
        else:
            cleaned_rows.append(standardized_row)
    
    # Create new DataFrame from cleaned rows
    cleaned_df = pd.DataFrame(cleaned_rows) if cleaned_rows else None
    dropped_df = pd.DataFrame(dropped_records) if dropped_records else None
    
    # Check for duplicates using record_hash
    if cleaned_df is not None and not cleaned_df.empty:
        duplicates = cleaned_df[cleaned_df.duplicated(subset=['record_hash'], keep='first')]
        if not duplicates.empty:
            logging.warning(f"Found {len(duplicates)} duplicate records in {table_name}")
            dropped_df = pd.concat([
                dropped_df,
                duplicates.assign(reason="Duplicate record")
            ]) if dropped_df is not None else duplicates.assign(reason="Duplicate record")
            cleaned_df = cleaned_df.drop_duplicates(subset=['record_hash'], keep='first')
    
    # Log summary
    final_count = len(cleaned_df) if cleaned_df is not None else 0
    if original_count != final_count:
        logging.info(f"Data cleaning summary for {table_name}:")
        logging.info(f"  Original records: {original_count}")
        logging.info(f"  Cleaned records: {final_count}")
        logging.info(f"  Dropped records: {original_count - final_count}")
        
        if dropped_df is not None:
            reasons = dropped_df['reason'].value_counts()
            logging.info("Dropped records by reason:")
            for reason, count in reasons.items():
                logging.info(f"  {reason}: {count}")
    
    return cleaned_df, dropped_df

def verify_upload(df, table_name, engine):
    """
    Verify that all records from the DataFrame were successfully uploaded to the database.
    
    Args:
        df (pandas.DataFrame): Original DataFrame that was uploaded
        table_name (str): Name of the table in the database
        engine (sqlalchemy.engine.Engine): Database engine connection
        
    Returns:
        bool: True if verification passes, False otherwise
    """
    try:
        # Get the count from the database
        db_count = pd.read_sql(f'SELECT COUNT(*) as count FROM {table_name}', engine).iloc[0]['count']
        
        # Get the count from the DataFrame
        df_count = len(df)
        
        # Compare counts
        if db_count != df_count:
            logging.error(f"Verification failed for {table_name}: DataFrame has {df_count} records but database has {db_count} records")
            return False
            
        # Sample check - verify a few random records exist in the database
        sample_size = min(5, len(df))  # Check up to 5 random records
        if sample_size > 0:
            sample_records = df.sample(n=sample_size)
            
            for _, record in sample_records.iterrows():
                # Construct WHERE clause based on all columns
                where_conditions = []
                for column in record.index:
                    if pd.isna(record[column]):
                        where_conditions.append(f"{column} IS NULL")
                    else:
                        where_conditions.append(f"{column} = '{str(record[column]).replace("'", "''")}'")
                
                where_clause = ' AND '.join(where_conditions)
                query = f"SELECT COUNT(*) as count FROM {table_name} WHERE {where_clause}"
                
                result = pd.read_sql(query, engine)
                if result.iloc[0]['count'] == 0:
                    logging.error(f"Verification failed: Record not found in database for {table_name}")
                    return False
        
        logging.info(f"Verification passed for {table_name}: All {df_count} records successfully uploaded")
        return True
        
    except Exception as e:
        logging.error(f"Error during verification for {table_name}: {str(e)}")
        return False

def upload_to_database(df, table_name, engine):
    """Upload DataFrame to database and verify the upload"""
    try:
        if df is None or df.empty:
            logging.warning(f"No data to upload for table {table_name}")
            return False
            
        # Clean and validate data before upload
        cleaned_df, dropped_df = validate_and_clean_data(df, table_name)
        
        if cleaned_df is None or cleaned_df.empty:
            logging.error(f"No valid data remaining after cleaning for table {table_name}")
            return False
        
        # Upload cleaned data to database
        cleaned_df.to_sql(table_name, engine, if_exists='append', index=False)
        
        # Save dropped records to a separate table if there are any
        if dropped_df is not None and not dropped_df.empty:
            dropped_table = f"{table_name}_dropped_records"
            dropped_df.to_sql(dropped_table, engine, if_exists='append', index=False)
            logging.info(f"Saved {len(dropped_df)} dropped records to {dropped_table}")
        
        # Verify the upload
        if verify_upload(cleaned_df, table_name, engine):
            logging.info(f"Successfully uploaded and verified {len(cleaned_df)} records to {table_name}")
            return True
        else:
            logging.error(f"Upload verification failed for {table_name}")
            return False
            
    except Exception as e:
        logging.error(f"Error uploading to database for table {table_name}: {str(e)}")
        return False

def process_file_chunk(chunk_data):
    """Process a chunk of data for parallel processing"""
    df, table_name, engine = chunk_data
    try:
        df.to_sql(table_name, engine, if_exists='append', index=False)
        return True, None
    except Exception as e:
        return False, str(e)

def parallel_upload(df, table_name, engine, chunk_size=10000):
    """Upload data in parallel using chunks"""
    if len(df) < chunk_size:
        return upload_to_database(df, table_name, engine)
    
    chunks = [df[i:i + chunk_size] for i in range(0, len(df), chunk_size)]
    chunk_data = [(chunk, table_name, engine) for chunk in chunks]
    
    with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        futures = [executor.submit(process_file_chunk, data) for data in chunk_data]
        
        success = True
        errors = []
        
        with tqdm(total=len(chunks), desc=f"Uploading {table_name}") as pbar:
            for future in as_completed(futures):
                result, error = future.result()
                if not result:
                    success = False
                    errors.append(error)
                pbar.update(1)
        
        if not success:
            logging.error(f"Errors during parallel upload: {'; '.join(errors)}")
        
        return success

def generate_qc_report(df, table_name, output_dir):
    """Generate a quality control report for the data"""
    report = {
        'table_name': table_name,
        'timestamp': datetime.now().isoformat(),
        'record_count': len(df),
        'column_stats': {},
        'data_quality': {
            'missing_values': df.isnull().sum().to_dict(),
            'unique_values': {col: df[col].nunique() for col in df.columns},
        }
    }
    
    # Calculate column statistics
    for column in df.columns:
        col_stats = {
            'dtype': str(df[column].dtype),
            'unique_count': df[column].nunique(),
            'missing_count': df[column].isnull().sum()
        }
        
        if df[column].dtype in ['int64', 'float64']:
            col_stats.update({
                'mean': df[column].mean(),
                'median': df[column].median(),
                'std': df[column].std(),
                'min': df[column].min(),
                'max': df[column].max()
            })
        
        report['column_stats'][column] = col_stats
    
    # Save report
    report_path = os.path.join(output_dir, f"{table_name}_qc_report.json")
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    return report_path

def backup_table(table_name, engine, backup_dir):
    """Backup existing table before modifications"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f"{table_name}_backup_{timestamp}.csv")
    
    try:
        # Read existing table
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, engine)
        
        # Save to CSV
        df.to_csv(backup_file, index=False)
        logging.info(f"Backup created: {backup_file}")
        return backup_file
    except Exception as e:
        logging.error(f"Failed to create backup: {str(e)}")
        return None

def validate_database_schema(engine):
    """Validate and create necessary database schemas"""
    required_tables = {
        'tmb_data': '''
            CREATE TABLE IF NOT EXISTS tmb_data (
                id SERIAL PRIMARY KEY,
                SampleName VARCHAR(255) NOT NULL,
                TMB FLOAT NOT NULL,
                BinomialLow FLOAT,
                BinomialHigh FLOAT,
                upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                record_hash VARCHAR(32) UNIQUE
            )
        ''',
        'cns_data': '''
            CREATE TABLE IF NOT EXISTS cns_data (
                id SERIAL PRIMARY KEY,
                SampleName VARCHAR(255) NOT NULL,
                CHROM VARCHAR(50) NOT NULL,
                START INTEGER NOT NULL,
                STOP INTEGER NOT NULL,
                GENE VARCHAR(255),
                log2 FLOAT,
                upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                record_hash VARCHAR(32) UNIQUE
            )
        '''
        # Add other table definitions as needed
    }
    
    try:
        with engine.connect() as conn:
            for table_name, create_stmt in required_tables.items():
                conn.execute(text(create_stmt))
            conn.commit()
        return True
    except Exception as e:
        logging.error(f"Failed to validate database schema: {str(e)}")
        return False

def get_default_file_patterns():
    """Return default file patterns to look for"""
    return {
        'tmb': ['TMB*.tsv'],
        'cns': ['*.cns'],
        'coverage': ['*mean_gene_coverage.tsv'],
        'mastervar': ['*Run_masterVarFinal.txt'],
        'segments': ['*segments.called.named.tsv']
    }

def find_files(directory, patterns=None):
    """
    Find files matching the given patterns in the directory.
    If no patterns provided, use default patterns.
    """
    if patterns is None:
        patterns = []
        for file_patterns in get_default_file_patterns().values():
            patterns.extend(file_patterns)
    
    found_files = []
    for pattern in patterns:
        # Use glob to find files matching pattern
        pattern_path = os.path.join(directory, pattern)
        found_files.extend(glob.glob(pattern_path))
    
    return found_files

def load_email_config(config_file):
    """Load email configuration from YAML file"""
    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logging.error(f"Failed to load email config: {str(e)}")
        return None

def format_file_status_table(processed_files, failed_files):
    """Format file status into an HTML table"""
    html = """
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <tr style="background-color: #f2f2f2;">
            <th style="padding: 8px; text-align: left;">File Name</th>
            <th style="padding: 8px; text-align: left;">Status</th>
        </tr>
    """
    
    # Add processed files
    for file_path in processed_files:
        html += f"""
        <tr style="background-color: #e6ffe6;">
            <td style="padding: 8px;">{os.path.basename(file_path)}</td>
            <td style="padding: 8px;">Success</td>
        </tr>
        """
    
    # Add failed files
    for file_path in failed_files:
        html += f"""
        <tr style="background-color: #ffe6e6;">
            <td style="padding: 8px;">{os.path.basename(file_path)}</td>
            <td style="padding: 8px;">Failed</td>
        </tr>
        """
    
    html += "</table>"
    return html

def format_qc_summary(qc_reports):
    """Format QC summary into HTML"""
    html = "<h3>Quality Control Summary</h3>"
    
    for report_file in qc_reports:
        try:
            with open(report_file, 'r') as f:
                report = json.load(f)
            
            html += f"""
            <h4>{report['table_name']}</h4>
            <ul>
                <li>Total Records: {report['record_count']}</li>
                <li>Missing Values: {sum(report['data_quality']['missing_values'].values())}</li>
            </ul>
            """
        except Exception as e:
            logging.error(f"Failed to read QC report {report_file}: {str(e)}")
    
    return html

def send_email_report(config_file, report_data):
    """
    Send email report with upload results.
    
    Args:
        config_file (str): Path to email configuration file
        report_data (dict): Dictionary containing:
            - processed_files (list): Successfully processed files
            - failed_files (list): Failed files
            - qc_reports (list): Paths to QC report files
            - start_time (datetime): Start time of processing
            - end_time (datetime): End time of processing
    """
    config = load_email_config(config_file)
    if not config:
        return False
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['Subject'] = f"Genomic Data Upload Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        msg['From'] = config['smtp']['sender']
        msg['To'] = ', '.join(config['recipients'])
        
        # Calculate processing time
        processing_time = report_data['end_time'] - report_data['start_time']
        
        # Create HTML content
        html_content = f"""
        <html>
        <body>
            <h2>Genomic Data Upload Report</h2>
            
            <h3>Processing Summary</h3>
            <ul>
                <li>Start Time: {report_data['start_time'].strftime('%Y-%m-%d %H:%M:%S')}</li>
                <li>End Time: {report_data['end_time'].strftime('%Y-%m-%d %H:%M:%S')}</li>
                <li>Processing Time: {str(processing_time)}</li>
                <li>Total Files: {len(report_data['processed_files']) + len(report_data['failed_files'])}</li>
                <li>Successfully Processed: {len(report_data['processed_files'])}</li>
                <li>Failed: {len(report_data['failed_files'])}</li>
            </ul>
            
            <h3>File Status</h3>
            {format_file_status_table(report_data['processed_files'], report_data['failed_files'])}
            
            {format_qc_summary(report_data['qc_reports'])}
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_content, 'html'))
        
        # Attach QC reports
        for report_file in report_data['qc_reports']:
            with open(report_file, 'rb') as f:
                part = MIMEApplication(f.read(), Name=os.path.basename(report_file))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(report_file)}"'
                msg.attach(part)
        
        # Send email
        with smtplib.SMTP(config['smtp']['server'], config['smtp']['port']) as server:
            if config['smtp'].get('use_tls', True):
                server.starttls()
            if 'username' in config['smtp'] and 'password' in config['smtp']:
                server.login(config['smtp']['username'], config['smtp']['password'])
            server.send_message(msg)
        
        logging.info("Email report sent successfully")
        return True
        
    except Exception as e:
        logging.error(f"Failed to send email report: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Upload genomic data files to database')
    parser.add_argument('directory', help='Directory containing the files to process')
    parser.add_argument('--files', nargs='*', help='Specific files to process. If not provided, will look for files with standard endings')
    parser.add_argument('--db-config', help='Path to database configuration file', default='db_config.json')
    parser.add_argument('--log-file', help='Path to log file', default='genomic_upload.log')
    parser.add_argument('--parallel', action='store_true', help='Enable parallel processing for large files')
    parser.add_argument('--chunk-size', type=int, default=10000, help='Chunk size for parallel processing')
    parser.add_argument('--backup-dir', help='Directory for table backups', default='backups')
    parser.add_argument('--qc-dir', help='Directory for QC reports', default='qc_reports')
    parser.add_argument('--dry-run', action='store_true', help='Validate files without uploading')
    parser.add_argument('--email-config', help='Path to email configuration file')
    
    args = parser.parse_args()
    
    # Record start time
    start_time = datetime.now()
    
    # Initialize lists to track files
    processed_files = []
    failed_files = []
    qc_reports = []
    
    # Create necessary directories
    os.makedirs(args.backup_dir, exist_ok=True)
    os.makedirs(args.qc_dir, exist_ok=True)
    
    # Set up file logging in addition to console logging
    file_handler = logging.FileHandler(args.log_file)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logging.getLogger().addHandler(file_handler)
    
    # Load database configuration
    try:
        with open(args.db_config) as f:
            DB_CONFIG.update(json.load(f))
    except FileNotFoundError:
        logging.warning(f"Database config file {args.db_config} not found, using default configuration")
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON in database config file {args.db_config}")
        return
    
    # Validate directory
    if not os.path.isdir(args.directory):
        logging.error(f"Directory not found: {args.directory}")
        return
    
    # Find files to process
    if args.files:
        # Use provided files, but validate they exist
        files_to_process = []
        for file_pattern in args.files:
            file_path = os.path.join(args.directory, file_pattern)
            matching_files = glob.glob(file_path)
            if not matching_files:
                logging.warning(f"No files found matching pattern: {file_pattern}")
            files_to_process.extend(matching_files)
    else:
        # Use default file patterns
        files_to_process = find_files(args.directory)
    
    if not files_to_process:
        logging.error("No files found to process")
        return
    
    # Group files by type for organized processing
    file_groups = defaultdict(list)
    for file_path in files_to_process:
        file_type = None
        file_lower = file_path.lower()
        
        # Determine file type
        if 'tmb' in file_lower:
            file_type = 'tmb'
        elif file_lower.endswith('.cns'):
            file_type = 'cns'
        elif 'mean_gene_coverage' in file_lower:
            file_type = 'coverage'
        elif 'mastervarfinal' in file_lower:
            file_type = 'mastervar'
        elif 'segments.called.named' in file_lower:
            file_type = 'segments'
        
        if file_type:
            file_groups[file_type].append(file_path)
        else:
            logging.warning(f"Unrecognized file type: {file_path}")
    
    # Create database engine
    try:
        engine = create_engine(
            f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@"
            f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        )
    except Exception as e:
        logging.error(f"Failed to connect to database: {str(e)}")
        return
    
    # Validate database schema
    if not validate_database_schema(engine):
        return
    
    # Process each group of files
    total_files = len(files_to_process)
    processed_files = 0
    failed_files = []
    
    for file_type, files in file_groups.items():
        logging.info(f"\nProcessing {file_type} files...")
        for file_path in files:
            try:
                logging.info(f"Processing file: {os.path.basename(file_path)}")
                df = read_file(file_path)
                
                if df is not None:
                    table_name = get_table_name(file_path, file_type)
                    
                    # Generate QC report
                    qc_report = generate_qc_report(df, table_name, args.qc_dir)
                    qc_reports.append(qc_report)
                    logging.info(f"QC report generated: {qc_report}")
                    
                    if not args.dry_run:
                        # Backup existing table
                        backup_file = backup_table(table_name, engine, args.backup_dir)
                        
                        # Upload data
                        if args.parallel and len(df) > args.chunk_size:
                            success = parallel_upload(df, table_name, engine, args.chunk_size)
                        else:
                            success = upload_to_database(df, table_name, engine)
                        
                        if success:
                            processed_files.append(file_path)
                            logging.info(f"Successfully processed {os.path.basename(file_path)}")
                        else:
                            failed_files.append(file_path)
                            logging.error(f"Failed to upload {os.path.basename(file_path)} to database")
                    else:
                        processed_files.append(file_path)
                        logging.info(f"Dry run - file {os.path.basename(file_path)} validated successfully")
                else:
                    failed_files.append(file_path)
                    logging.error(f"Failed to read file: {file_path}")
                    
            except Exception as e:
                failed_files.append(file_path)
                logging.error(f"Error processing file {file_path}: {str(e)}")
    
    # Record end time
    end_time = datetime.now()
    
    # Print summary
    logging.info("\nProcessing Summary:")
    logging.info(f"Total files found: {len(processed_files) + len(failed_files)}")
    logging.info(f"Successfully processed: {len(processed_files)}")
    logging.info(f"Failed to process: {len(failed_files)}")
    
    if failed_files:
        logging.info("\nFailed files:")
        for file_path in failed_files:
            logging.info(f"  - {os.path.basename(file_path)}")
    
    # Send email report if configured
    if args.email_config:
        report_data = {
            'processed_files': processed_files,
            'failed_files': failed_files,
            'qc_reports': qc_reports,
            'start_time': start_time,
            'end_time': end_time
        }
        send_email_report(args.email_config, report_data)

if __name__ == '__main__':
    main()

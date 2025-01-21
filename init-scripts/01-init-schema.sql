-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS genomic;

-- Set search path
SET search_path TO genomic, public;

-- Create tables
CREATE TABLE IF NOT EXISTS genomic.tmb_data (
    id SERIAL PRIMARY KEY,
    sample_name VARCHAR(255) NOT NULL,
    tmb FLOAT NOT NULL,
    binomial_low FLOAT,
    binomial_high FLOAT,
    upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    record_hash VARCHAR(32) UNIQUE
);

CREATE TABLE IF NOT EXISTS genomic.cns_data (
    id SERIAL PRIMARY KEY,
    sample_name VARCHAR(255) NOT NULL,
    chrom VARCHAR(50) NOT NULL,
    start_pos INTEGER NOT NULL,
    stop_pos INTEGER NOT NULL,
    gene VARCHAR(255),
    log2 FLOAT,
    upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    record_hash VARCHAR(32) UNIQUE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_tmb_sample_name ON genomic.tmb_data(sample_name);
CREATE INDEX IF NOT EXISTS idx_tmb_upload_timestamp ON genomic.tmb_data(upload_timestamp);
CREATE INDEX IF NOT EXISTS idx_tmb_record_hash ON genomic.tmb_data(record_hash);

CREATE INDEX IF NOT EXISTS idx_cns_sample_name ON genomic.cns_data(sample_name);
CREATE INDEX IF NOT EXISTS idx_cns_gene ON genomic.cns_data(gene);
CREATE INDEX IF NOT EXISTS idx_cns_chrom ON genomic.cns_data(chrom);
CREATE INDEX IF NOT EXISTS idx_cns_upload_timestamp ON genomic.cns_data(upload_timestamp);
CREATE INDEX IF NOT EXISTS idx_cns_record_hash ON genomic.cns_data(record_hash);

-- Create a function to update upload_timestamp
CREATE OR REPLACE FUNCTION update_upload_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.upload_timestamp = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers
CREATE TRIGGER update_tmb_timestamp
    BEFORE UPDATE ON genomic.tmb_data
    FOR EACH ROW
    EXECUTE FUNCTION update_upload_timestamp();

CREATE TRIGGER update_cns_timestamp
    BEFORE UPDATE ON genomic.cns_data
    FOR EACH ROW
    EXECUTE FUNCTION update_upload_timestamp();

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA genomic TO genomic_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA genomic TO genomic_user;

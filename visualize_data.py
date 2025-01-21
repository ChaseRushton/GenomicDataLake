import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import json
import os

def load_db_config():
    """Load database configuration"""
    with open('db_config.json', 'r') as f:
        return json.load(f)

def create_db_connection():
    """Create database connection"""
    config = load_db_config()
    connection_string = f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
    return create_engine(connection_string)

def load_tmb_data(engine):
    """Load TMB data from database"""
    query = """
    SELECT sample_name, tmb, binomial_low, binomial_high, upload_timestamp
    FROM genomic.tmb_data
    ORDER BY upload_timestamp DESC
    """
    return pd.read_sql(query, engine)

def load_cns_data(engine):
    """Load CNS data from database"""
    query = """
    SELECT sample_name, chrom, start_pos, stop_pos, gene, log2, upload_timestamp
    FROM genomic.cns_data
    ORDER BY upload_timestamp DESC
    """
    return pd.read_sql(query, engine)

def plot_tmb_distribution(df):
    """Plot TMB distribution"""
    fig = px.histogram(
        df,
        x='tmb',
        title='TMB Distribution Across Samples',
        labels={'tmb': 'Tumor Mutational Burden', 'count': 'Number of Samples'},
        nbins=30
    )
    fig.update_layout(showlegend=False)
    return fig

def plot_tmb_confidence_intervals(df):
    """Plot TMB with confidence intervals"""
    fig = go.Figure()
    
    # Sort by TMB value for better visualization
    df_sorted = df.sort_values('tmb')
    
    # Add confidence intervals
    fig.add_trace(go.Scatter(
        x=df_sorted.index,
        y=df_sorted['binomial_high'],
        mode='lines',
        line=dict(width=0),
        showlegend=False,
        name='Upper CI'
    ))
    
    fig.add_trace(go.Scatter(
        x=df_sorted.index,
        y=df_sorted['binomial_low'],
        mode='lines',
        fill='tonexty',
        line=dict(width=0),
        fillcolor='rgba(68, 68, 68, 0.3)',
        name='95% Confidence Interval'
    ))
    
    # Add TMB values
    fig.add_trace(go.Scatter(
        x=df_sorted.index,
        y=df_sorted['tmb'],
        mode='markers',
        name='TMB',
        marker=dict(size=8, color='rgb(31, 119, 180)')
    ))
    
    fig.update_layout(
        title='TMB Values with Confidence Intervals',
        xaxis_title='Sample Index',
        yaxis_title='TMB',
        hovermode='closest'
    )
    return fig

def plot_chromosome_coverage(df):
    """Plot coverage across chromosomes"""
    # Calculate coverage per chromosome
    coverage = df.groupby('chrom').agg({
        'start_pos': 'min',
        'stop_pos': 'max',
        'sample_name': 'count'
    }).reset_index()
    
    coverage['coverage'] = coverage['stop_pos'] - coverage['start_pos']
    
    fig = px.bar(
        coverage,
        x='chrom',
        y='coverage',
        title='Chromosome Coverage',
        labels={
            'chrom': 'Chromosome',
            'coverage': 'Base Pairs Covered'
        }
    )
    return fig

def plot_gene_cnv_heatmap(df):
    """Plot CNV heatmap for top genes"""
    # Get top genes by frequency
    top_genes = df['gene'].value_counts().head(20).index
    
    # Pivot data for heatmap
    pivot_data = df[df['gene'].isin(top_genes)].pivot_table(
        index='gene',
        columns='sample_name',
        values='log2',
        aggfunc='mean'
    )
    
    fig = px.imshow(
        pivot_data,
        title='Copy Number Variation Heatmap',
        labels=dict(x='Sample', y='Gene', color='Log2 Ratio'),
        aspect='auto'
    )
    return fig

def main():
    st.set_page_config(page_title="Genomic Data Viewer", layout="wide")
    
    st.title("Genomic Data Lake Viewer")
    
    try:
        engine = create_db_connection()
    except Exception as e:
        st.error(f"Failed to connect to database: {str(e)}")
        return
    
    # Sidebar for navigation
    page = st.sidebar.selectbox(
        "Select Analysis",
        ["TMB Analysis", "Copy Number Analysis"]
    )
    
    if page == "TMB Analysis":
        st.header("Tumor Mutational Burden Analysis")
        
        try:
            tmb_data = load_tmb_data(engine)
            
            # Display summary statistics
            st.subheader("Summary Statistics")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Samples", len(tmb_data))
            col2.metric("Average TMB", f"{tmb_data['tmb'].mean():.2f}")
            col3.metric("Median TMB", f"{tmb_data['tmb'].median():.2f}")
            
            # TMB Distribution
            st.subheader("TMB Distribution")
            st.plotly_chart(plot_tmb_distribution(tmb_data), use_container_width=True)
            
            # TMB with Confidence Intervals
            st.subheader("TMB Values with Confidence Intervals")
            st.plotly_chart(plot_tmb_confidence_intervals(tmb_data), use_container_width=True)
            
            # Raw data table
            st.subheader("Raw Data")
            st.dataframe(tmb_data)
            
        except Exception as e:
            st.error(f"Error loading TMB data: {str(e)}")
    
    else:  # Copy Number Analysis
        st.header("Copy Number Variation Analysis")
        
        try:
            cns_data = load_cns_data(engine)
            
            # Display summary statistics
            st.subheader("Summary Statistics")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Samples", len(cns_data['sample_name'].unique()))
            col2.metric("Total Genes", len(cns_data['gene'].unique()))
            col3.metric("Total Segments", len(cns_data))
            
            # Chromosome Coverage
            st.subheader("Chromosome Coverage")
            st.plotly_chart(plot_chromosome_coverage(cns_data), use_container_width=True)
            
            # CNV Heatmap
            st.subheader("Copy Number Variation Heatmap (Top 20 Genes)")
            st.plotly_chart(plot_gene_cnv_heatmap(cns_data), use_container_width=True)
            
            # Raw data table with filters
            st.subheader("Raw Data")
            
            # Filters
            col1, col2 = st.columns(2)
            selected_chrom = col1.multiselect(
                "Filter by Chromosome",
                options=sorted(cns_data['chrom'].unique())
            )
            selected_genes = col2.multiselect(
                "Filter by Gene",
                options=sorted(cns_data['gene'].unique())
            )
            
            # Apply filters
            filtered_data = cns_data
            if selected_chrom:
                filtered_data = filtered_data[filtered_data['chrom'].isin(selected_chrom)]
            if selected_genes:
                filtered_data = filtered_data[filtered_data['gene'].isin(selected_genes)]
            
            st.dataframe(filtered_data)
            
        except Exception as e:
            st.error(f"Error loading CNS data: {str(e)}")

if __name__ == "__main__":
    main()

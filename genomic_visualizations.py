import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pycircos import Circos
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
import logging

class GenomicVisualizer:
    def __init__(self, output_dir="visualizations"):
        """Initialize the visualizer with output directory"""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize chromosome sizes (hg38)
        self.chrom_sizes = {
            '1': 248956422, '2': 242193529, '3': 198295559,
            '4': 190214555, '5': 181538259, '6': 170805979,
            '7': 159345973, '8': 145138636, '9': 138394717,
            '10': 133797422, '11': 135086622, '12': 133275309,
            '13': 114364328, '14': 107043718, '15': 101991189,
            '16': 90338345, '17': 83257441, '18': 80373285,
            '19': 58617616, '20': 64444167, '21': 46709983,
            '22': 50818468, 'X': 156040895, 'Y': 57227415
        }
    
    def export_for_igv(self, df, output_file=None, track_name="CNV"):
        """
        Export copy number data in IGV-compatible format
        
        Args:
            df: DataFrame with columns: chrom, start_pos, stop_pos, log2
            output_file: Path to save the IGV file
            track_name: Name of the track in IGV
        """
        if output_file is None:
            output_file = os.path.join(self.output_dir, "cnv_data.igv")
        
        # Create IGV header
        header = f'track type=wiggle_0 name="{track_name}" description="Copy Number Data" visibility=full color=255,0,0\n'
        
        try:
            # Prepare data in IGV format
            igv_data = df.copy()
            igv_data['chrom'] = 'chr' + igv_data['chrom'].astype(str)
            
            # Sort by chromosome and position
            igv_data = igv_data.sort_values(['chrom', 'start_pos'])
            
            # Write header and data
            with open(output_file, 'w') as f:
                f.write(header)
                for _, row in igv_data.iterrows():
                    f.write(f'fixedStep chrom={row["chrom"]} start={row["start_pos"]} step={row["stop_pos"]-row["start_pos"]}\n')
                    f.write(f'{row["log2"]}\n')
            
            self.logger.info(f"IGV file created: {output_file}")
            return output_file
            
        except Exception as e:
            self.logger.error(f"Error creating IGV file: {str(e)}")
            return None
    
    def export_bed_file(self, df, output_file=None):
        """Export data in BED format for IGV"""
        if output_file is None:
            output_file = os.path.join(self.output_dir, "cnv_data.bed")
        
        try:
            # Prepare data in BED format
            bed_data = df.copy()
            bed_data['chrom'] = 'chr' + bed_data['chrom'].astype(str)
            bed_data['name'] = bed_data.apply(
                lambda x: f"CNV_{x['chrom']}:{x['start_pos']}-{x['stop_pos']}", 
                axis=1
            )
            
            # Add RGB colors based on log2 values
            def get_rgb(log2):
                if log2 > 0:
                    return "255,0,0"  # Red for amplifications
                else:
                    return "0,0,255"  # Blue for deletions
            
            bed_data['rgb'] = bed_data['log2'].apply(get_rgb)
            
            # Select and order columns for BED format
            bed_columns = [
                'chrom', 'start_pos', 'stop_pos', 'name', 
                'log2', 'strand', 'start_pos', 'stop_pos', 'rgb'
            ]
            bed_data['strand'] = '.'
            
            # Write BED file
            bed_data[bed_columns].to_csv(
                output_file, 
                sep='\t', 
                header=False, 
                index=False
            )
            
            self.logger.info(f"BED file created: {output_file}")
            return output_file
            
        except Exception as e:
            self.logger.error(f"Error creating BED file: {str(e)}")
            return None
    
    def create_circos_plot(self, df, output_file=None, title="Genome-wide CNV Profile"):
        """
        Create a Circos plot for copy number data
        
        Args:
            df: DataFrame with columns: chrom, start_pos, stop_pos, log2
            output_file: Path to save the plot
            title: Plot title
        """
        if output_file is None:
            output_file = os.path.join(self.output_dir, "circos_plot.png")
        
        try:
            # Initialize Circos plot
            circos = Circos(
                sectors={
                    f'chr{chrom}': size for chrom, size in self.chrom_sizes.items()
                },
                sector_width=0.5,
                space=2
            )
            
            # Add base ideogram
            circos.add_sectors()
            
            # Process CNV data
            for chrom in self.chrom_sizes.keys():
                chrom_data = df[df['chrom'] == str(chrom)]
                if len(chrom_data) > 0:
                    # Add CNV track
                    positions = list(zip(
                        chrom_data['start_pos'],
                        chrom_data['stop_pos']
                    ))
                    values = chrom_data['log2'].values
                    
                    # Color coding
                    colors = ['red' if v > 0 else 'blue' for v in values]
                    
                    circos.add_track(
                        f'chr{chrom}',
                        positions,
                        values,
                        track_name=f'CNV_chr{chrom}',
                        fill_colors=colors,
                        track_height=0.2
                    )
            
            # Create the plot
            fig, ax = plt.subplots(figsize=(15, 15))
            circos.plot(ax)
            plt.title(title)
            
            # Save plot
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"Circos plot created: {output_file}")
            return output_file
            
        except Exception as e:
            self.logger.error(f"Error creating Circos plot: {str(e)}")
            return None
    
    def create_chromosome_plot(self, df, chrom, output_file=None):
        """Create a detailed plot for a specific chromosome"""
        if output_file is None:
            output_file = os.path.join(self.output_dir, f"chromosome_{chrom}_plot.png")
        
        try:
            # Filter data for chromosome
            chrom_data = df[df['chrom'] == str(chrom)].sort_values('start_pos')
            
            # Create plot
            plt.figure(figsize=(15, 5))
            
            # Plot CNV segments
            plt.plot(
                [chrom_data['start_pos'], chrom_data['stop_pos']],
                [chrom_data['log2'], chrom_data['log2']],
                'b-', linewidth=2
            )
            
            # Add genes if available
            if 'gene' in chrom_data.columns:
                for _, row in chrom_data.iterrows():
                    if pd.notna(row['gene']):
                        plt.text(
                            row['start_pos'],
                            row['log2'],
                            row['gene'],
                            rotation=45,
                            fontsize=8
                        )
            
            # Customize plot
            plt.title(f'Chromosome {chrom} Copy Number Profile')
            plt.xlabel('Genomic Position')
            plt.ylabel('Log2 Ratio')
            plt.grid(True, alpha=0.3)
            
            # Save plot
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"Chromosome plot created: {output_file}")
            return output_file
            
        except Exception as e:
            self.logger.error(f"Error creating chromosome plot: {str(e)}")
            return None

def main():
    """Example usage of the GenomicVisualizer class"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Create genomic visualizations")
    parser.add_argument('--input', required=True, help="Input CNV data file")
    parser.add_argument('--output-dir', default="visualizations", help="Output directory")
    parser.add_argument('--chromosome', help="Specific chromosome to plot")
    
    args = parser.parse_args()
    
    # Initialize visualizer
    visualizer = GenomicVisualizer(args.output_dir)
    
    # Read data
    df = pd.read_csv(args.input)
    
    # Create visualizations
    visualizer.export_for_igv(df)
    visualizer.export_bed_file(df)
    visualizer.create_circos_plot(df)
    
    if args.chromosome:
        visualizer.create_chromosome_plot(df, args.chromosome)

if __name__ == "__main__":
    main()

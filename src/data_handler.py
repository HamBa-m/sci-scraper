# data_handler.py
import pandas as pd
import json
import os
from pathlib import Path

try:
    from .config import RESULTS_DIR
except (ImportError, ValueError):
    from config import RESULTS_DIR

class DataHandler:
    def __init__(self, results_dir=None):
        self.results_dir = Path(results_dir) if results_dir else RESULTS_DIR
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def save_to_excel(self, data, filename):
        """Save results to an Excel file with specified filename."""
        df = pd.DataFrame(data)
        file_path = self.results_dir / filename
        df.to_excel(str(file_path), index=False)
        return file_path
    
    def load_from_excel(self, filename):
        """Load data from an Excel file into a DataFrame."""
        file_path = self.results_dir / filename
        return pd.read_excel(str(file_path))

    def save_to_json(self, data, filename):
        """Save results to a JSON file with specified filename."""
        file_path = self.results_dir / filename
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file)
        return file_path

    def load_from_json(self, filename):
        """Load data from a JSON file."""
        file_path = self.results_dir / filename
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    # data_handler.py
    def calculate_statistics(self, data):
        """Calculate and return summary statistics as a string for display."""
        df = pd.DataFrame(data)
        output = []
        
        total_papers = len(df)
        papers_with_abstracts = df['abstract'].notna().sum()
        abstract_success_rate = (papers_with_abstracts / total_papers * 100) if total_papers > 0 else 0
        output.append(f"\nOverall Summary:")
        output.append(f"Total papers found: {total_papers}")
        output.append(f"Total papers with abstracts: {papers_with_abstracts}")
        output.append(f"Overall abstract success rate: {abstract_success_rate:.1f}%\n")
        
        source_stats = df.groupby('source').agg({
            'abstract': lambda x: x.notna().sum(),
            'title': 'count'
        }).reset_index()
        source_stats.columns = ['Source', 'Papers with Abstract', 'Total Papers']
        source_stats['Success Rate (%)'] = (source_stats['Papers with Abstract'] / source_stats['Total Papers'] * 100).round(1)
        source_stats = source_stats.sort_values('Total Papers', ascending=False)
        output.append("\nBreakdown by Source:")
        output.append(source_stats.to_string(index=False))

        other_sources = df[df['source'].str.contains('Other', na=False)]['source'].unique()
        output.append("\nUnique Sources in 'Other' Category:")
        for source in sorted(other_sources):
            count = len(df[df['source'] == source])
            output.append(f"- {source}: {count} papers")
        
        return "\n".join(output)

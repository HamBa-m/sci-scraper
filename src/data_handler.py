# data_handler.py
import pandas as pd
import json
import os

class DataHandler:
    def save_to_excel(self, data, filename):
        """Save results to an Excel file with specified filename."""
        df = pd.DataFrame(data)
        # check if results folder exists
        if not os.path.exists('./results'):
            os.makedirs('./results')
        df.to_excel('./results/{}'.format(filename), index=False)
    
    def load_from_excel(self, filename):
        """Load data from an Excel file into a DataFrame."""
        # check if results folder exists
        if not os.path.exists('./results'):
            os.makedirs('./results')
        return pd.read_excel('./results/{}'.format(filename))

    def save_to_json(self, data, filename):
        """Save results to a JSON file with specified filename."""
        # check if results folder exists
        if not os.path.exists('./results'):
            os.makedirs('./results')
        with open('./results/{}'.format(filename), 'w') as file:
            json.dump(data, file)

    def load_from_json(self, filename):
        """Load data from a JSON file."""
        # check if results folder exists
        if not os.path.exists('./results'):
            os.makedirs('./results')
        with open('./results/{}'.format(filename), 'r') as file:
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

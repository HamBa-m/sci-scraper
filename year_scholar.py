# read the excel of papers and extract the year from the citation column and save it to a new column in the excel file
import pandas as pd
import re
import os
import time

def extract_year(citation):
    # Extract year from citation
    year = re.search(r"\b(19|20)\d{2}\b", citation)
    if year:
        return year.group()
    return None

def extract_year_from_excel(file_path):
    # Read Excel file
    df = pd.read_excel(file_path, engine="openpyxl")
    
    # Extract year from citation
    df["year"] = df["citation"].apply(extract_year)
    
    # Save to new Excel file
    new_file_path = "{}_with_year.xlsx".format(os.path.splitext(file_path)[0])
    df.to_excel(new_file_path, index=False)
    
    print("\nYear extracted and saved to {}.".format(new_file_path))
    
    return new_file_path

def extract_year_from_csv(file_path):
    # Read CSV file
    df = pd.read_csv(file_path)
    
    # Extract year from citation
    df["year"] = df["citation"].apply(extract_year)
    
    # Save to new CSV file
    new_file_path = "{}_with_year.csv".format(os.path.splitext(file_path)[0])
    df.to_csv(new_file_path, index=False)
    
    print("\nYear extracted and saved to {}.".format(new_file_path))
    
    return new_file_path

def main(file_path):
    # Extract year from citation in Excel file
    # new_file_path = extract_year_from_excel(file_path)
    new_file_path = extract_year_from_csv(file_path)
    
    return new_file_path

if __name__ == "__main__":
    # test_file_path = "20241222-224257_results.csv"
    test_file_path = "results/20241222-224257_results.csv"
    main(test_file_path)
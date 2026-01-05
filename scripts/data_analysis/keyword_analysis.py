import pandas as pd
import matplotlib.pyplot as plt
import os

def load_data(file_path):
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None

# Count Keyword Occurrences
def count_keyword_occurrences(df_condensed, keyword, occupation_code):
    counts = {}
    row = df_condensed[df_condensed['occupation_code'] == occupation_code]
    if row.empty:
        return counts

    for column in df_condensed.columns:
        if column == 'occupation_code':
            continue
        if row[column].dtype == object:
            counts[column] = row[column].str.lower().str.count(keyword.lower()).sum()
        else:
            counts[column] = 0

    return counts

# Keyword Analysis
def analyze_keywords(keyword_df, condensed_df):
    keyword_counts = {}
    
    for keyword in keyword_df['Keyword'].unique():
        keyword_counts[keyword] = {col: 0 for col in condensed_df.columns if col != 'occupation_code'}
        
        keyword_occupations = keyword_df[keyword_df['Keyword'] == keyword]
        for occupation_code in keyword_occupations['Job Code']:
            counts = count_keyword_occurrences(condensed_df, keyword, occupation_code)
            for col, count in counts.items():
                keyword_counts[keyword][col] += count

    return keyword_counts

# Keyword Counts Visualization
def plot_keyword_counts(keyword_counts, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for keyword, counts in keyword_counts.items():
        plt.figure(figsize=(10, 6))
        plt.bar(counts.keys(), counts.values())
        plt.title(f"Keyword '{keyword}' Occurrences in Each Column")
        plt.xlabel('Columns')
        plt.ylabel('Count')
        plt.xticks(rotation=90)
        plt.tight_layout()
        output_path = os.path.join(output_dir, f"{keyword}_keyword_counts.png")
        plt.savefig(output_path)
        plt.close()

def main():
    keyword_csv_path = 'data/raw/keyword_search_results.csv'
    condensed_csv_path = 'data/processed/condensed_job_details.csv'
    output_csv_path = 'data/results/keyword_analysis_results.csv'
    output_dir = 'data/results/'

    keyword_df = load_data(keyword_csv_path)
    condensed_df = load_data(condensed_csv_path)

    if keyword_df is None or condensed_df is None:
        return

    keyword_counts = analyze_keywords(keyword_df, condensed_df)
    
    # Save the analysis results to a CSV file
    analysis_df = pd.DataFrame(keyword_counts).transpose()
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    analysis_df.to_csv(output_csv_path, index=True)
    print(f"Keyword analysis results saved to {output_csv_path}")

    plot_keyword_counts(keyword_counts, output_dir)

if __name__ == "__main__":
    main()

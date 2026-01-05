import os
import pandas as pd
from onet_data_collector.keyword_search import keyword_search

def save_results_to_csv(df, output_csv_path):
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)

    df.to_csv(output_csv_path, index=False)
    print(f"Keyword search results saved to {output_csv_path}")

def perform_keyword_searches(username, password, keywords):
    combined_df = pd.DataFrame()
    for keyword in keywords:
        df = keyword_search(username, password, keyword)
        combined_df = pd.concat([combined_df, df], ignore_index=True)
    return combined_df

def main():
    username = input("Enter O*NET Web Services username: ")
    password = input("Enter O*NET Web Services password: ")
    keywords = ["engineering", "healthcare", "finance", "technology", "education", "marketing", "construction", "management", "science", "design"]
    output_csv_path = 'data/raw/keyword_search_results.csv'

    combined_df = perform_keyword_searches(username, password, keywords)
    
    save_results_to_csv(combined_df, output_csv_path)

if __name__ == "__main__":
    main()
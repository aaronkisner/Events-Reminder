import pandas as pd
import os

def load_csv(file_name='dates.csv'):
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    print(f"Reading CSV file from {file_path}...")
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
        print("CSV file loaded successfully:")
        print(df.head())
        return df
    except Exception as e:
        print(f"Failed to read CSV file: {e}")
        raise

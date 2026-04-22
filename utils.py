import pandas as pd
import os

def load_inventory():
    if os.path.exists("processed_inventory.pkl"):
        return pd.read_pickle("processed_inventory.pkl")
    return None

def get_paginated_data(df, page_size, page_number):
    """Chunks the dataframe for the 4x3 grid display."""
    start_idx = page_number * page_size
    end_idx = start_idx + page_size
    return df.iloc[start_idx:end_idx]
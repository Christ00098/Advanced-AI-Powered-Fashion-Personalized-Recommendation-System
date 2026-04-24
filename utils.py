import pandas as pd
import os


def load_inventory():
    """Load the pkl — all columns including enhanced ones are already inside."""
    if not os.path.exists("processed_inventory.pkl"):
        return None
    df = pd.read_pickle("processed_inventory.pkl")
    return df


def get_paginated_data(df, page_size, page_number):
    """Chunks the dataframe for the 4-column grid display."""
    start = page_number * page_size
    return df.iloc[start: start + page_size]


def get_all_sizes(df):
    """Returns a logically ordered list of all unique sizes in the dataset."""
    all_sizes = set()
    for sizes in df["available_sizes"].dropna():
        if isinstance(sizes, list):
            all_sizes.update(sizes)

    priority = ["XS", "S", "M", "L", "XL", "XXL", "XXXL"]
    ordered  = [s for s in priority if s in all_sizes]
    numeric  = sorted(
        [s for s in all_sizes if s not in priority and str(s).replace(".", "").isdigit()],
        key=lambda x: float(x)
    )
    others   = sorted([s for s in all_sizes if s not in priority and not str(s).replace(".", "").isdigit()])
    return ordered + numeric + others

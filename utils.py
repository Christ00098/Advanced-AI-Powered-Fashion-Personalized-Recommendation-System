import pandas as pd
import os


def load_inventory():
    """Load the pkl — all columns including enhanced ones are already inside."""
    if not os.path.exists("processed_inventory.pkl"):
        return None
    df = pd.read_pickle("processed_inventory.pkl")

    # Convert available_sizes string → sorted list if not already a list
    if "available_sizes" in df.columns:
        df["available_sizes"] = df["available_sizes"].apply(
            lambda x: sorted(set(s.strip() for s in str(x).split(",")
                             if s.strip() and s.strip() != "nan"))
            if not isinstance(x, list) and pd.notna(x) and str(x) != "nan"
            else (x if isinstance(x, list) else [])
        )

    return df


def get_paginated_data(df, page_size, page_number):
    """Chunks the dataframe for the 4-column grid display."""
    start = page_number * page_size
    return df.iloc[start: start + page_size]


def get_all_sizes(df):
    """Returns a logically ordered list of all unique sizes in the dataset."""
    if "available_sizes" not in df.columns:
        return []

    all_sizes = set()
    for sizes in df["available_sizes"].dropna():
        if isinstance(sizes, list):
            all_sizes.update(sizes)
        elif isinstance(sizes, str) and sizes != "nan":
            all_sizes.update(s.strip() for s in sizes.split(",") if s.strip())

    priority = ["XS", "S", "M", "L", "XL", "XXL", "XXXL"]
    ordered  = [s for s in priority if s in all_sizes]
    numeric  = sorted(
        [s for s in all_sizes if s not in priority and str(s).replace(".", "").isdigit()],
        key=lambda x: float(x)
    )
    others   = sorted([
        s for s in all_sizes
        if s not in priority and not str(s).replace(".", "").isdigit()
    ])
    return ordered + numeric + others

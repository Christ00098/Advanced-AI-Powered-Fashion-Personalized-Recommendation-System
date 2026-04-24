import torch
import open_clip
import numpy as np
import pandas as pd


def load_ai_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, _, _ = open_clip.create_model_and_transforms("hf-hub:Marqo/marqo-fashionSigLIP")
    model       = model.to(device).eval()
    tokenizer   = open_clip.get_tokenizer("hf-hub:Marqo/marqo-fashionSigLIP")
    return model, tokenizer, device


def search_items(
    query_text,
    df,
    index,
    model,
    tokenizer,
    device,
    gender       = "All",
    master_cat   = "All",
    article_type = "All",
    age_group    = "All",
    size         = "All",
    price_range  = None,
    top_n        = 8,
):
    """
    Unified search with all filters + semantic ranking.
    All filter args default to "All" which means no filter applied for that field.
    """
    mask = pd.Series([True] * len(df), index=df.index)

    # Gender
    if gender and gender != "All":
        mask &= df["gender"].str.lower() == gender.lower()

    # Master Category
    if master_cat and master_cat != "All":
        mask &= df["masterCategory"].str.lower() == master_cat.lower()

    # Article Type
    if article_type and article_type != "All":
        mask &= df["articleType"].str.lower() == article_type.lower()

    # Age Group
    if age_group and age_group != "All":
        mask &= df["age_group"].astype(str).str.lower() == age_group.lower()

    # Size — checks if selected size is present in the available_sizes list
    if size and size != "All":
        mask &= df["available_sizes"].apply(
            lambda x: size in x if isinstance(x, list) else False
        )

    # Price Range
    if price_range:
        low, high = price_range
        mask &= (
            df["price"].between(low, high, inclusive="both") | df["price"].isna()
        )

    filtered = df[mask].copy()
    if filtered.empty:
        return pd.DataFrame()

    # Semantic ranking
    with torch.no_grad():
        tokens = tokenizer([query_text]).to(device)
        q_vec  = model.encode_text(tokens)
        q_vec /= q_vec.norm(dim=-1, keepdim=True)
        q_vec  = q_vec.cpu().numpy().flatten()

    filtered["score"] = [
        np.dot(q_vec, index.get_item_vector(i)) for i in filtered.index
    ]
    return filtered.sort_values("score", ascending=False).head(top_n)


# ── Kept for backward compatibility if anything still calls the old signature ──
def search_with_filters(query_text, gender, size, price_range, article, df, index, model, tokenizer, device):
    return search_items(
        query_text=query_text,
        df=df, index=index, model=model, tokenizer=tokenizer, device=device,
        gender=gender,
        article_type=article,
        size=size,
        price_range=price_range,
    )

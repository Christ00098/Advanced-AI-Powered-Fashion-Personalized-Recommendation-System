import torch
import open_clip
import numpy as np
import pandas as pd


def load_ai_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, _, preprocess = open_clip.create_model_and_transforms('hf-hub:Marqo/marqo-fashionSigLIP')
    model = model.to(device).eval()
    tokenizer = open_clip.get_tokenizer('hf-hub:Marqo/marqo-fashionSigLIP')
    return model, tokenizer, device


def search_with_filters(
    query_text, gender, size, price_range, article,
    df, index, model, tokenizer, device,
    colour="All"
):
    """Core Search: Gender + Size + Article + Colour + Price + Semantic Ranking."""

    # 1. Gender filter
    mask = df['gender'].str.lower() == gender.lower()

    # 2. Article type filter
    mask = mask & (df['articleType'].str.lower() == article.lower())

    # 3. Size filter — checks if selected size exists in the available_sizes list
    if size and size != "All":
        mask = mask & df['available_sizes'].apply(
            lambda x: size in x if isinstance(x, list) else False
        )

    # 4. Colour filter from baseColour column
    if colour and colour != "All":
        mask = mask & (df['baseColour'].str.lower() == colour.lower())

    # 5. Price filter — uses numeric price column
    if price_range:
        low, high = price_range
        mask = mask & (
            df['price'].between(low, high, inclusive="both") | df['price'].isna()
        )

    filtered_df = df[mask].copy()
    if filtered_df.empty:
        return pd.DataFrame()

    # 6. Semantic Ranking
    with torch.no_grad():
        tokens = tokenizer([query_text]).to(device)
        q_vec = model.encode_text(tokens)
        q_vec /= q_vec.norm(dim=-1, keepdim=True)
        q_vec = q_vec.cpu().numpy().flatten()

    max_idx = index.get_n_items() - 1
    scores = [
        np.dot(q_vec, index.get_item_vector(idx)) if idx <= max_idx else -1.0
        for idx in filtered_df.index
    ]
    filtered_df['score'] = scores
    return filtered_df.sort_values(by='score', ascending=False)

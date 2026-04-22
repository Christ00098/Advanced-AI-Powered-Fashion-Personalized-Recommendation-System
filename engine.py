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

def search_with_filters(query_text, gender, size, price_range, article, df, index, model, tokenizer, device):
    """Core Search: Logic for 5 filters + Semantic Search."""
    # 1. Hard Filtering (Gender, Size, Article)
    mask = (df['gender'].str.lower() == gender.lower()) & \
           (df['standard_size'].astype(str) == str(size)) & \
           (df['articleType'].str.lower() == article.lower())
    
    # Extract numeric price for range filtering
    df['temp_price'] = df['price_tag'].str.replace('£', '').astype(float)
    mask = mask & (df['temp_price'] >= price_range[0]) & (df['temp_price'] <= price_range[1])
    
    filtered_df = df[mask].copy()
    if filtered_df.empty: return pd.DataFrame()

    # 2. Semantic Ranking
    with torch.no_grad():
        tokens = tokenizer([query_text]).to(device)
        q_vec = model.encode_text(tokens)
        q_vec /= q_vec.norm(dim=-1, keepdim=True)
        q_vec = q_vec.cpu().numpy().flatten()

    scores = [np.dot(q_vec, index.get_item_vector(idx)) for idx in filtered_df.index]
    filtered_df['score'] = scores
    return filtered_df.sort_values(by='score', ascending=False)
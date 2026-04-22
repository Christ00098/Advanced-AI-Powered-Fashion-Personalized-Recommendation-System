import streamlit as st
from PIL import Image
from annoy import AnnoyIndex
import engine
import utils
import os

st.set_page_config(page_title="AuraStyle AI", layout="wide")

@st.cache_resource
def startup_resources():
    # This ensures the model is loaded ONCE and kept in RAM
    model, tokenizer, device = engine.load_ai_model()
    df = utils.load_inventory()
    
    # Load Annoy Index
    index = AnnoyIndex(768, 'angular')
    index.load("fashion_vector_index.ann")
    
    return model, tokenizer, device, df, index

# Call the cached function
model, tokenizer, device, df, index = startup_resources()

raw_df = utils.load_inventory()
# --- Custom Component: Product Card ---
def product_card(row):
    if os.path.exists(row['image_path']):
        st.image(Image.open(row['image_path']), width='stretch')
    st.markdown(f"**{row['price_tag']}**")
    st.caption(f"{row['productDisplayName'][:20]}... \n\n Size: {row['standard_size']}")

# --- APP LAYOUT ---
st.title("✨ AuraStyle AI: The Premier Fashion Suite")

# Sidebar for Search Parameters
#"""st.sidebar.header("🔍 Search Filters")
#s_gender = st.sidebar.selectbox("Gender", options=df['gender'].unique())
#s_size = st.sidebar.selectbox("Your UK Size", options=sorted(df['standard_size'].astype(str).unique()))
#s_price = st.sidebar.slider("Price Range (£)", 0, 300, (20, 150))"""

menu = ["🏠 Home Gallery", "🔎 Advanced Search", "👔 Attire Architect"]
choice = st.sidebar.selectbox("Navigate", menu)

# --- 1. HOME GALLERY (4x3 Grid) ---
if choice == "🏠 Home Gallery":
    st.subheader("Shop the Collection")
    if "page" not in st.session_state: st.session_state.page = 0
    
    # 4x3 logic
    page_size = 12
    display_df = utils.get_paginated_data(df, page_size, st.session_state.page)
    
    cols = st.columns(4)
    for i, (idx, row) in enumerate(display_df.iterrows()):
        with cols[i % 4]:
            product_card(row)
            
    # Pagination
    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        if st.button("Previous") and st.session_state.page > 0:
            st.session_state.page -= 1
            st.rerun()
    with c3:
        if st.button("Next") and (st.session_state.page + 1) * page_size < len(df):
            st.session_state.page += 1
            st.rerun()

# --- 2. ADVANCED SEARCH ---
elif choice == "🔎 Advanced Search":
    st.subheader("Find Your Perfect Piece")

    col1, col2 = st.columns(2)
    with col1:
        s_gender = st.selectbox("Gender", options=df['gender'].unique())
        s_size = st.selectbox("Your UK Size", options=sorted(df['standard_size'].astype(str).unique()))
    with col2:
        s_type = st.selectbox("Article Type", options=sorted(df['articleType'].unique()))
        s_price = st.slider("Price Range (£)", 0, 300, (20, 150))
        
    s_color = st.text_input("Preferred Color/Pattern (e.g. Navy Floral)")
    
    if st.button("Discover"):
        # The engine logic remains the same, just using these local variables
        query = f"{s_gender} {s_color} {s_type}"
        results = engine.search_with_filters(query, s_gender, s_size, s_price, s_type, df, index, model, tokenizer, device)

        if not results.empty:
            st.write(f"Showing best matches for Size {s_size}:")
            cols = st.columns(4)
            for i, (idx, row) in enumerate(results.head(8).iterrows()):
                with cols[i % 4]: product_card(row)
        else:
            st.warning("No items match your exact filters. Try broadening your price or color.")
    #s_type = st.selectbox("Article Type", options=sorted(df['articleType'].unique()))
    #s_color = st.text_input("Preferred Color/Pattern (e.g. Navy Floral)")
    
    """if st.button("Discover"):
        query = f"{s_gender} {s_color} {s_type}"
        results = engine.search_with_filters(query, s_gender, s_size, s_price, s_type, df, index, model, tokenizer, device)"""
        


# --- 3. ATTIRE ARCHITECT (Outfit Builder) ---
elif choice == "👔 Attire Architect":
    st.subheader("Outfit Matcher: Build Your Full Look")

    c_gender = st.selectbox("Target Gender", options=df['gender'].unique())
    c_size = st.selectbox("User UK Size", options=sorted(df['standard_size'].astype(str).unique()))
    
    st.divider() # Visual separator

    col1, col2 = st.columns(2)
    with col1:
        top_type = st.selectbox("Top", ["Tshirts", "Shirts", "Dresses"])
        bottom_type = st.selectbox("Bottom", ["Trousers", "Jeans", "Shorts"])
        shoes_type = st.selectbox("Footwear", ["Casual Shoes", "Formal Shoes", "Sports Shoes"])
    with col2:
        acc_type = st.selectbox("Accessory", ["Belts", "Watches", "Caps"])
        outfit_color = st.text_input("Overall Color Theme (e.g., Earth Tones)")

    if st.button("Generate Befitting Combo"):
        # We query for each component using the same 'vibe' and size
        st.write("### Your AI-Suggested Ensemble")
        outfit_cols = st.columns(4)
        
        components = [top_type, bottom_type, shoes_type, acc_type]
        for i, comp in enumerate(components):
            with outfit_cols[i]:
                res = engine.search_with_filters(f"{outfit_color} {comp}", c_gender, c_size, (0, 500), comp, df, index, model, tokenizer, device)
                if not res.empty:
                    st.write(f"**{comp}**")
                    product_card(res.iloc[0])
                else:
                    st.caption(f"No {comp} in Size {c_size}")
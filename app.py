import streamlit as st
from annoy import AnnoyIndex
import engine
import utils
import pandas as pd
import os

st.set_page_config(
    page_title="AuraStyle AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── GLOBAL CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0a0a0f !important;
    color: #f0ece4 !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* Keep header/toolbar visible but styled */
footer, [data-testid="stDecoration"] { display: none !important; }
header, [data-testid="stToolbar"] {
    background: #0a0a0f !important;
    border-bottom: 1px solid rgba(197,168,105,0.08) !important;
}
[data-testid="stToolbar"] button svg { fill: rgba(197,168,105,0.5) !important; }

[data-testid="stAppViewContainer"] > .main { background: #0a0a0f !important; }
.block-container { padding: 0 2.5rem 3rem !important; max-width: 1400px !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0f0f18 !important;
    border-right: 1px solid rgba(197,168,105,0.15) !important;
}
[data-testid="stSidebar"] * { color: #f0ece4 !important; font-family: 'DM Sans', sans-serif !important; }

/* Radio nav — hide dots, style labels */
[data-testid="stSidebar"] .stRadio > div { gap: 0 !important; }
[data-testid="stSidebar"] .stRadio input[type="radio"] { display: none !important; }
[data-testid="stSidebar"] .stRadio label {
    display: flex !important; align-items: center !important;
    padding: 0.65rem 1rem !important; border-radius: 6px !important;
    margin-bottom: 0.3rem !important; font-size: 0.85rem !important;
    letter-spacing: 0.06em !important; color: rgba(240,236,228,0.7) !important;
    cursor: pointer !important; transition: all 0.2s ease !important;
    border: 1px solid transparent !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(197,168,105,0.07) !important;
    color: #c5a869 !important;
    border-color: rgba(197,168,105,0.15) !important;
}

/* ── Hide keyboard tooltip ── */
[data-testid="InputInstructions"],
span[class*="instructionsDisplay"],
div[class*="instructionsDisplay"] {
    display: none !important; visibility: hidden !important;
    height: 0 !important; overflow: hidden !important;
}

/* ── Hero ── */
.hero-banner {
    position: relative; width: 100%; padding: 3rem 0 2rem;
    text-align: center; overflow: hidden; margin-bottom: 0.5rem;
}
.hero-banner::before {
    content: ''; position: absolute; inset: 0;
    background: radial-gradient(ellipse 80% 60% at 50% 0%, rgba(197,168,105,0.12) 0%, transparent 70%);
    pointer-events: none;
}
.hero-logo-ring {
    display: inline-flex; align-items: center; justify-content: center;
    width: 72px; height: 72px; border-radius: 50%;
    border: 1.5px solid rgba(197,168,105,0.6);
    background: rgba(197,168,105,0.06); margin-bottom: 1rem; font-size: 2rem;
    box-shadow: 0 0 40px rgba(197,168,105,0.15), inset 0 0 20px rgba(197,168,105,0.05);
}
.hero-title {
    font-family: 'Cormorant Garamond', serif !important;
    font-size: clamp(2.4rem, 5vw, 4rem) !important; font-weight: 300 !important;
    letter-spacing: 0.18em !important; color: #f0ece4 !important;
    line-height: 1 !important; margin-bottom: 0.4rem !important;
}
.hero-title span { color: #c5a869; font-style: italic; }
.hero-subtitle {
    font-size: 0.78rem !important; font-weight: 300 !important;
    letter-spacing: 0.35em !important; color: rgba(197,168,105,0.7) !important;
    text-transform: uppercase !important; margin-bottom: 1.5rem !important;
}
.hero-divider {
    width: 120px; height: 1px;
    background: linear-gradient(90deg, transparent, #c5a869, transparent); margin: 0 auto;
}

/* ── Section header ── */
.section-header {
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 1.6rem !important; font-weight: 300 !important;
    letter-spacing: 0.12em !important; color: #f0ece4 !important;
    margin: 2rem 0 1.2rem !important; padding-bottom: 0.6rem !important;
    border-bottom: 1px solid rgba(197,168,105,0.2) !important;
}
.sub-header {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.05rem; font-weight: 300; letter-spacing: 0.15em;
    color: rgba(197,168,105,0.75); margin: 1.5rem 0 0.8rem;
    text-transform: uppercase;
}

/* ── Product Card ── */
.product-card {
    background: #12121c; border: 1px solid rgba(197,168,105,0.12);
    border-radius: 8px; overflow: hidden;
    transition: all 0.35s cubic-bezier(0.4,0,0.2,1);
    position: relative; height: 100%;
}
.product-card:hover {
    border-color: rgba(197,168,105,0.45); transform: translateY(-4px);
    box-shadow: 0 20px 50px rgba(0,0,0,0.5), 0 0 30px rgba(197,168,105,0.06);
}
.product-card-img {
    width: 100%; height: 320px;
    object-fit: cover; object-position: top center;
    display: block; background: #1a1a27;
}
.product-card-body { padding: 0.85rem 0.9rem 1rem; }
.product-card-name {
    font-size: 0.78rem; font-weight: 400; color: #d4cfc6;
    line-height: 1.4; margin-bottom: 0.5rem;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.product-card-price {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.1rem; font-weight: 600; color: #c5a869; letter-spacing: 0.04em;
}
.product-card-price-disc {
    font-size: 0.75rem; color: rgba(197,168,105,0.4);
    text-decoration: line-through; margin-left: 0.4rem;
}
.product-card-sizes {
    font-size: 0.66rem; font-weight: 300; color: rgba(197,168,105,0.5);
    letter-spacing: 0.08em; text-transform: uppercase; margin-top: 0.35rem;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.product-card-badge {
    position: absolute; top: 0.6rem; left: 0.6rem;
    background: rgba(10,10,15,0.75); backdrop-filter: blur(6px);
    border: 1px solid rgba(197,168,105,0.25); border-radius: 3px;
    padding: 0.15rem 0.45rem; font-size: 0.6rem;
    letter-spacing: 0.12em; text-transform: uppercase; color: #c5a869;
}
.img-placeholder {
    width: 100%; height: 320px;
    background: linear-gradient(135deg, #1a1a27 0%, #12121c 100%);
    display: flex; align-items: center; justify-content: center;
    font-size: 2.5rem; color: rgba(197,168,105,0.2);
}

/* ── Outfit slot label ── */
.outfit-slot-label {
    font-family: 'Cormorant Garamond', serif;
    font-size: 0.88rem; color: rgba(197,168,105,0.75);
    letter-spacing: 0.12em; text-transform: uppercase;
    margin-bottom: 0.6rem; padding-bottom: 0.3rem;
    border-bottom: 1px solid rgba(197,168,105,0.15);
}
.outfit-no-result {
    padding: 2rem 1rem; text-align: center;
    color: rgba(197,168,105,0.35); font-size: 0.75rem;
    letter-spacing: 0.1em; border: 1px dashed rgba(197,168,105,0.15);
    border-radius: 8px; margin-top: 0.5rem;
}

/* ── Buttons ── */
.stButton > button {
    background: transparent !important;
    border: 1px solid rgba(197,168,105,0.4) !important;
    color: #c5a869 !important; font-family: 'DM Sans', sans-serif !important;
    font-size: 0.75rem !important; letter-spacing: 0.2em !important;
    text-transform: uppercase !important; padding: 0.55rem 1.8rem !important;
    border-radius: 3px !important; transition: all 0.25s ease !important;
}
.stButton > button:hover {
    background: rgba(197,168,105,0.1) !important;
    border-color: #c5a869 !important;
    box-shadow: 0 0 20px rgba(197,168,105,0.1) !important;
}

/* ── Inputs & Selects ── */
.stTextInput > div > div > input,
[data-baseweb="select"] > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(197,168,105,0.2) !important;
    border-radius: 4px !important; color: #f0ece4 !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput > div > div > input:focus {
    border-color: rgba(197,168,105,0.5) !important;
    box-shadow: 0 0 0 2px rgba(197,168,105,0.08) !important;
}
.stTextInput label, .stSelectbox label, .stSlider label, .stMultiSelect label {
    color: rgba(197,168,105,0.8) !important; font-size: 0.72rem !important;
    letter-spacing: 0.15em !important; text-transform: uppercase !important;
}
/* Multiselect tags */
[data-baseweb="tag"] {
    background: rgba(197,168,105,0.15) !important;
    border: 1px solid rgba(197,168,105,0.3) !important;
}
[data-baseweb="tag"] span { color: #c5a869 !important; }

/* Slider */
.stSlider [data-baseweb="slider"] div[role="slider"] {
    background: #c5a869 !important; border-color: #c5a869 !important;
}

/* Page indicator */
.page-indicator {
    font-family: 'Cormorant Garamond', serif; font-size: 0.9rem;
    color: rgba(197,168,105,0.6); letter-spacing: 0.1em;
    text-align: center; padding-top: 0.5rem;
}

/* Alerts */
.stAlert {
    background: rgba(197,168,105,0.06) !important;
    border: 1px solid rgba(197,168,105,0.2) !important;
    border-radius: 4px !important; color: #f0ece4 !important;
}

hr { border-color: rgba(197,168,105,0.15) !important; }
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: rgba(197,168,105,0.3); border-radius: 2px; }
</style>
""", unsafe_allow_html=True)


# ── LOAD RESOURCES ─────────────────────────────────────────────────────────────
@st.cache_resource
def startup_resources():
    model, tokenizer, device = engine.load_ai_model()
    df = utils.load_inventory()
    index = AnnoyIndex(768, 'angular')
    index.load("fashion_vector_index.ann")
    return model, tokenizer, device, df, index

model, tokenizer, device, df, index = startup_resources()

# ── DERIVED FILTER OPTIONS ─────────────────────────────────────────────────────
all_sizes       = utils.get_all_sizes(df)
all_genders     = ["All"] + sorted(df["gender"].dropna().unique().tolist())
all_master_cats = ["All"] + sorted(df["masterCategory"].dropna().unique().tolist())
all_age_groups  = ["All"] + sorted(df["age_group"].dropna().unique().tolist())
all_sub_cats    = sorted(df["subCategory"].dropna().unique().tolist())
all_articles    = sorted(df["articleType"].dropna().unique().tolist())

min_price = int(df["price"].min()) if "price" in df.columns and df["price"].notna().any() else 0
max_price = int(df["price"].max()) if "price" in df.columns and df["price"].notna().any() else 10000


# ── HERO BANNER ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <div class="hero-logo-ring">✦</div>
    <h1 class="hero-title">AURA<span>STYLE</span> AI</h1>
    <p class="hero-subtitle">The Premier AI Fashion Experience</p>
    <div class="hero-divider"></div>
</div>
""", unsafe_allow_html=True)


# ── SIDEBAR ────────────────────────────────────────────────────────────────────
st.sidebar.markdown("""
<div style="padding:1.2rem 0 0.8rem; text-align:center;">
    <div style="font-family:'Cormorant Garamond',serif; font-size:1.05rem;
                letter-spacing:0.22em; color:#c5a869; text-transform:uppercase;">
        ✦ Navigate
    </div>
    <div style="height:1px; background:linear-gradient(90deg,transparent,rgba(197,168,105,0.3),transparent);
                margin:0.8rem 0 1rem;"></div>
</div>
""", unsafe_allow_html=True)

menu   = ["🏠  Home Gallery", "🔎  Advanced Search", "👔  Attire Architect"]
choice = st.sidebar.radio("Navigation", menu, label_visibility="collapsed")


# ── PRODUCT CARD ───────────────────────────────────────────────────────────────
def product_card(row):
    image_path = row.get("image_path", None)
    name       = str(row.get("productDisplayName", ""))[:40]
    article    = str(row.get("articleType", ""))

    # Price display
    price = row.get("price", None)
    disc  = row.get("discounted_price", None)
    if pd.notna(price) and price:
        p_str = f"₹{int(price):,}"
        if pd.notna(disc) and disc and int(disc) < int(price):
            price_html = (f'<span class="product-card-price">{p_str}</span>'
                          f'<span class="product-card-price-disc">₹{int(disc):,}</span>')
        else:
            price_html = f'<span class="product-card-price">{p_str}</span>'
    elif pd.notna(row.get("price_tag", None)):
        price_html = f'<span class="product-card-price">{row["price_tag"]}</span>'
    else:
        price_html = '<span class="product-card-price">—</span>'

    # Sizes display
    sizes = row.get("available_sizes", [])
    if isinstance(sizes, list) and sizes:
        shown = "  ·  ".join(sizes[:6])
        if len(sizes) > 6:
            shown += f"  +{len(sizes)-6}"
        sizes_html = f'<div class="product-card-sizes">Sizes: {shown}</div>'
    else:
        sizes_html = ""

    # Image
    if image_path and isinstance(image_path, str) and image_path.startswith("http"):
        img_html = f'<img class="product-card-img" src="{image_path}" alt="{name}" loading="lazy">'
    elif image_path and isinstance(image_path, str) and os.path.exists(image_path):
        import base64
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        img_html = f'<img class="product-card-img" src="data:image/jpeg;base64,{b64}" alt="{name}">'
    else:
        img_html = '<div class="img-placeholder">◈</div>'

    st.markdown(f"""
    <div class="product-card">
        <div class="product-card-badge">{article}</div>
        {img_html}
        <div class="product-card-body">
            <div class="product-card-name">{name}</div>
            {price_html}
            {sizes_html}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — HOME GALLERY
# ══════════════════════════════════════════════════════════════════════════════
if "🏠" in choice:
    st.markdown('<p class="section-header">The Collection</p>', unsafe_allow_html=True)

    if "page" not in st.session_state:
        st.session_state.page = 0

    page_size   = 12
    display_df  = utils.get_paginated_data(df, page_size, st.session_state.page)
    total_pages = (len(df) - 1) // page_size + 1

    cols = st.columns(4, gap="medium")
    for i, (_, row) in enumerate(display_df.iterrows()):
        with cols[i % 4]:
            product_card(row)

    st.markdown("<div style='margin-top:2rem;'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.button("← Prev", use_container_width=True):
            if st.session_state.page > 0:
                st.session_state.page -= 1
                st.rerun()
    with c2:
        st.markdown(
            f"<div class='page-indicator'>Page {st.session_state.page+1} of {total_pages}</div>",
            unsafe_allow_html=True
        )
    with c3:
        if st.button("Next →", use_container_width=True):
            if (st.session_state.page + 1) * page_size < len(df):
                st.session_state.page += 1
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — ADVANCED SEARCH
# ══════════════════════════════════════════════════════════════════════════════
elif "🔎" in choice:
    st.markdown('<p class="section-header">Find Your Perfect Piece</p>', unsafe_allow_html=True)

    # ── Filters ──
    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        s_gender     = st.selectbox("Gender",          options=all_genders)
        s_master_cat = st.selectbox("Master Category", options=all_master_cats)

    with col2:
        # Dynamically filter article types based on master category selection
        if s_master_cat != "All":
            filtered_articles = ["All"] + sorted(
                df[df["masterCategory"] == s_master_cat]["articleType"].dropna().unique().tolist()
            )
        else:
            filtered_articles = ["All"] + all_articles

        s_article   = st.selectbox("Article Type", options=filtered_articles)
        s_age_group = st.selectbox("Age Group",    options=all_age_groups)

    with col3:
        s_size  = st.selectbox("Size", options=["All"] + all_sizes)
        s_price = st.slider("Price Range (₹)", min_price, max_price, (min_price, max_price))

    s_query = st.text_input("Style / Color Vibe  (e.g. Navy Floral, Casual Earth Tones)")

    st.markdown("<div style='margin-top:0.5rem;'></div>", unsafe_allow_html=True)

    if st.button("DISCOVER →"):
        # Build semantic query from selections + text
        parts = [p for p in [s_gender, s_master_cat, s_article, s_query] if p and p != "All"]
        query = " ".join(parts) if parts else "fashion"

        with st.spinner("Curating your selection..."):
            results = engine.search_items(
                query_text   = query,
                df           = df,
                index        = index,
                model        = model,
                tokenizer    = tokenizer,
                device       = device,
                gender       = s_gender,
                master_cat   = s_master_cat,
                article_type = s_article,
                age_group    = s_age_group,
                size         = s_size,
                price_range  = (s_price[0], s_price[1]),
                top_n        = 8,
            )

        if not results.empty:
            st.markdown(
                f"<p style='font-size:0.75rem; letter-spacing:0.15em; color:rgba(197,168,105,0.6);"
                f"text-transform:uppercase; margin:1.5rem 0 1rem;'>"
                f"Showing {len(results)} results</p>",
                unsafe_allow_html=True
            )
            cols = st.columns(4, gap="medium")
            for i, (_, row) in enumerate(results.iterrows()):
                with cols[i % 4]:
                    product_card(row)
        else:
            st.warning("No items match your filters. Try broadening your selections.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — ATTIRE ARCHITECT
# ══════════════════════════════════════════════════════════════════════════════
elif "👔" in choice:
    st.markdown('<p class="section-header">Attire Architect — Build Your Complete Look</p>',
                unsafe_allow_html=True)

    # ── Global Preferences ────────────────────────────────────────────────────
    st.markdown('<p class="sub-header">Your Preferences</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3, gap="large")
    with col1:
        c_gender    = st.selectbox("Gender",    options=all_genders)
        c_age_group = st.selectbox("Age Group", options=all_age_groups)
    with col2:
        c_size  = st.selectbox("Size", options=["All"] + all_sizes)
        c_price = st.slider("Price Range (₹)", min_price, max_price, (min_price, max_price))
    with col3:
        c_style = st.text_input(
            "Style / Color Theme",
            placeholder="e.g. Earth Tones, Smart Casual, Navy Blue"
        )

    st.markdown("<div style='margin-top:0.5rem;'></div>", unsafe_allow_html=True)
    st.divider()

    # ── Outfit Builder ────────────────────────────────────────────────────────
    st.markdown('<p class="sub-header">Select Outfit Items</p>', unsafe_allow_html=True)
    st.caption("Choose one or more article types you want in your outfit.")

    selected_items = st.multiselect(
        "Outfit Items",
        options=all_articles,
        default=["Tshirts", "Jeans", "Casual Shoes"],
        label_visibility="collapsed"
    )

    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)

    if st.button("GENERATE MY OUTFIT →"):
        if not selected_items:
            st.warning("Please select at least one outfit item.")
        else:
            st.markdown(
                "<p style='font-size:0.75rem; letter-spacing:0.18em; color:rgba(197,168,105,0.6);"
                "text-transform:uppercase; margin:1.5rem 0 1.2rem;'>"
                "Your AI-Curated Complete Look</p>",
                unsafe_allow_html=True
            )

            # Render in rows of 4 columns
            items_per_row = 4
            for row_start in range(0, len(selected_items), items_per_row):
                batch = selected_items[row_start: row_start + items_per_row]
                cols  = st.columns(items_per_row, gap="medium")

                for col_idx, item in enumerate(batch):
                    with cols[col_idx]:
                        # Slot label
                        st.markdown(
                            f'<div class="outfit-slot-label">{item}</div>',
                            unsafe_allow_html=True
                        )

                        # Build query: style theme + article type
                        query = f"{c_style} {item}".strip() if c_style else item

                        with st.spinner(""):
                            res = engine.search_items(
                                query_text   = query,
                                df           = df,
                                index        = index,
                                model        = model,
                                tokenizer    = tokenizer,
                                device       = device,
                                gender       = c_gender,
                                age_group    = c_age_group,
                                size         = c_size,
                                price_range  = (c_price[0], c_price[1]),
                                article_type = item,
                                top_n        = 1,
                            )

                        if not res.empty:
                            product_card(res.iloc[0])
                        else:
                            st.markdown(
                                f'<div class="outfit-no-result">No {item} found<br>'
                                f'for your filters</div>',
                                unsafe_allow_html=True
                            )

                # Fill empty slots in last row to keep layout clean
                for empty in range(len(batch), items_per_row):
                    with cols[empty]:
                        st.empty()

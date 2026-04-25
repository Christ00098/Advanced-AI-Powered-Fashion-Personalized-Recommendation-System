import streamlit as st
from PIL import Image
from annoy import AnnoyIndex
import engine
import utils
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
/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0a0a0f !important;
    color: #f0ece4 !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Hide Streamlit chrome ── */
footer, [data-testid="stDecoration"] { display: none !important; }

/* Style the header to match dark theme instead of hiding it */
header, [data-testid="stToolbar"] {
    background: #0a0a0f !important;
}
[data-testid="stToolbar"] button, [data-testid="stToolbar"] svg {
    color: rgba(197,168,105,0.6) !important;
    fill: rgba(197,168,105,0.6) !important;
}

/* ── Main container ── */
[data-testid="stAppViewContainer"] > .main {
    background: #0a0a0f !important;
}
.block-container {
    padding: 0 2.5rem 3rem !important;
    max-width: 1400px !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0f0f18 !important;
    border-right: 1px solid rgba(197,168,105,0.15) !important;
}
[data-testid="stSidebar"] * {
    color: #f0ece4 !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] h1, h2, h3 {
    color: #c5a869 !important;
    font-family: 'Cormorant Garamond', serif !important;
    letter-spacing: 0.08em !important;
}

/* Sidebar selectbox */
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: rgba(197,168,105,0.07) !important;
    border: 1px solid rgba(197,168,105,0.25) !important;
    border-radius: 4px !important;
    color: #f0ece4 !important;
}

/* ── Hero Banner ── */
.hero-banner {
    position: relative;
    width: 100%;
    padding: 3rem 0 2rem;
    text-align: center;
    overflow: hidden;
    margin-bottom: 0.5rem;
}
.hero-banner::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse 80% 60% at 50% 0%, rgba(197,168,105,0.12) 0%, transparent 70%);
    pointer-events: none;
}
.hero-logo-ring {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 72px;
    height: 72px;
    border-radius: 50%;
    border: 1.5px solid rgba(197,168,105,0.6);
    background: rgba(197,168,105,0.06);
    margin-bottom: 1rem;
    font-size: 2rem;
    box-shadow: 0 0 40px rgba(197,168,105,0.15), inset 0 0 20px rgba(197,168,105,0.05);
}
.hero-title {
    font-family: 'Cormorant Garamond', serif !important;
    font-size: clamp(2.4rem, 5vw, 4rem) !important;
    font-weight: 300 !important;
    letter-spacing: 0.18em !important;
    color: #f0ece4 !important;
    line-height: 1 !important;
    margin-bottom: 0.4rem !important;
}
.hero-title span {
    color: #c5a869;
    font-style: italic;
}
.hero-subtitle {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 300 !important;
    letter-spacing: 0.35em !important;
    color: rgba(197,168,105,0.7) !important;
    text-transform: uppercase !important;
    margin-bottom: 1.5rem !important;
}
.hero-divider {
    width: 120px;
    height: 1px;
    background: linear-gradient(90deg, transparent, #c5a869, transparent);
    margin: 0 auto;
}

/* ── Section Header ── */
.section-header {
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 1.6rem !important;
    font-weight: 300 !important;
    letter-spacing: 0.12em !important;
    color: #f0ece4 !important;
    margin: 2rem 0 1.2rem !important;
    padding-bottom: 0.6rem !important;
    border-bottom: 1px solid rgba(197,168,105,0.2) !important;
}

/* ── Product Card ── */
.product-card {
    background: #12121c;
    border: 1px solid rgba(197,168,105,0.12);
    border-radius: 8px;
    overflow: hidden;
    transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    height: 100%;
}
.product-card:hover {
    border-color: rgba(197,168,105,0.45);
    transform: translateY(-4px);
    box-shadow: 0 20px 50px rgba(0,0,0,0.5), 0 0 30px rgba(197,168,105,0.06);
}
.product-card-img {
    width: 100%;
    height: 320px;
    object-fit: cover;
    object-position: top center;
    display: block;
    background: #1a1a27;
}
.product-card-body {
    padding: 0.85rem 0.9rem 1rem;
}
.product-card-name {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.78rem;
    font-weight: 400;
    color: #d4cfc6;
    line-height: 1.4;
    margin-bottom: 0.5rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.product-card-price {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.15rem;
    font-weight: 600;
    color: #c5a869;
    letter-spacing: 0.04em;
}
.product-card-size {
    font-size: 0.68rem;
    font-weight: 300;
    color: rgba(197,168,105,0.55);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-top: 0.2rem;
}
.product-card-badge {
    position: absolute;
    top: 0.6rem;
    left: 0.6rem;
    background: rgba(10,10,15,0.75);
    backdrop-filter: blur(6px);
    border: 1px solid rgba(197,168,105,0.25);
    border-radius: 3px;
    padding: 0.15rem 0.45rem;
    font-size: 0.6rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #c5a869;
}

/* ── Placeholder image ── */
.img-placeholder {
    width: 100%;
    height: 320px;
    background: linear-gradient(135deg, #1a1a27 0%, #12121c 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2.5rem;
    color: rgba(197,168,105,0.2);
}

            /* Hide sidebar collapse button tooltip text */
[data-testid="collapsedControl"] span,
button[kind="header"] span,
[data-testid="stSidebarCollapseButton"] span {
    display: none !important;
}
            
/* ── Hide Streamlit keyboard navigation text ── */
[data-testid="InputInstructions"],
span[class*="instructionsDisplay"],
div[class*="instructionsDisplay"] {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    overflow: hidden !important;
}

/* ── Buttons ── */
.stButton > button {
    background: transparent !important;
    border: 1px solid rgba(197,168,105,0.4) !important;
    color: #c5a869 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    padding: 0.55rem 1.8rem !important;
    border-radius: 3px !important;
    transition: all 0.25s ease !important;
}
.stButton > button:hover {
    background: rgba(197,168,105,0.1) !important;
    border-color: #c5a869 !important;
    box-shadow: 0 0 20px rgba(197,168,105,0.1) !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stSelectbox > div > div,
[data-baseweb="select"] > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(197,168,105,0.2) !important;
    border-radius: 4px !important;
    color: #f0ece4 !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput > div > div > input:focus {
    border-color: rgba(197,168,105,0.5) !important;
    box-shadow: 0 0 0 2px rgba(197,168,105,0.08) !important;
}

/* Labels */
.stTextInput label, .stSelectbox label, .stSlider label {
    color: rgba(197,168,105,0.8) !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    font-weight: 400 !important;
}

/* ── Slider ── */
[data-testid="stSlider"] [data-baseweb="slider"] [data-testid="stThumbValue"] {
    color: #c5a869 !important;
}
.stSlider [data-baseweb="slider"] div[role="slider"] {
    background: #c5a869 !important;
    border-color: #c5a869 !important;
}

/* ── Pagination row ── */
.pagination-row {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1.5rem;
    margin-top: 2.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid rgba(197,168,105,0.1);
}
.page-indicator {
    font-family: 'Cormorant Garamond', serif;
    font-size: 0.9rem;
    color: rgba(197,168,105,0.6);
    letter-spacing: 0.1em;
}

/* ── Warning / Info ── */
.stAlert {
    background: rgba(197,168,105,0.06) !important;
    border: 1px solid rgba(197,168,105,0.2) !important;
    border-radius: 4px !important;
    color: #f0ece4 !important;
}

/* ── Divider ── */
hr { border-color: rgba(197,168,105,0.15) !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: rgba(197,168,105,0.3); border-radius: 2px; }
</style>
""", unsafe_allow_html=True)


# ── CACHED RESOURCES ────────────────────────────────────────────────────────────
@st.cache_resource
def startup_resources():
    model, tokenizer, device = engine.load_ai_model()
    df = utils.load_inventory()
    index = AnnoyIndex(768, 'angular')
    index.load("fashion_vector_index.ann")
    return model, tokenizer, device, df, index

model, tokenizer, device, df, index = startup_resources()
raw_df = utils.load_inventory()


# ── HERO BANNER ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <div class="hero-logo-ring">✦</div>
    <h1 class="hero-title">AURA<span>STYLE</span> AI</h1>
    <p class="hero-subtitle">The Premier AI Fashion Experience</p>
    <div class="hero-divider"></div>
</div>
""", unsafe_allow_html=True)


# ── SIDEBAR ──────────────────────────────────────────────────────────────────────
st.sidebar.markdown("""
<div style="padding: 1.2rem 0 0.5rem; text-align:center;">
    <div style="font-family:'Cormorant Garamond',serif; font-size:1.1rem;
                letter-spacing:0.2em; color:#c5a869; text-transform:uppercase;">
        ✦ Navigate
    </div>
    <div style="height:1px; background:linear-gradient(90deg,transparent,rgba(197,168,105,0.3),transparent);
                margin:0.8rem 0 1.2rem;"></div>
</div>
""", unsafe_allow_html=True)

menu = ["🏠  Home Gallery", "🔎  Advanced Search", "👔  Attire Architect"]
choice = st.sidebar.selectbox("Menu", menu, label_visibility="collapsed")


# ── PRODUCT CARD ─────────────────────────────────────────────────────────────────
def product_card(row):
    image_path = row.get('image_path', None)
    name = str(row.get('productDisplayName', ''))[:38]
    price = str(row.get('price_tag', ''))
    size = str(row.get('standard_size', ''))
    article = str(row.get('articleType', ''))

    # Build image HTML
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
            <div class="product-card-price">{price}</div>
            <div class="product-card-size">Size — {size}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── PAGE 1: HOME GALLERY ─────────────────────────────────────────────────────────
if "🏠" in choice:
    st.markdown('<p class="section-header">The Collection</p>', unsafe_allow_html=True)

    if "page" not in st.session_state:
        st.session_state.page = 0

    page_size = 12
    display_df = utils.get_paginated_data(df, page_size, st.session_state.page)
    total_pages = (len(df) - 1) // page_size + 1

    cols = st.columns(4, gap="medium")
    for i, (idx, row) in enumerate(display_df.iterrows()):
        with cols[i % 4]:
            product_card(row)

    # Pagination
    st.markdown("<div style='margin-top:2rem;'></div>", unsafe_allow_html=True)
    col_prev, col_mid, col_next = st.columns([1, 2, 1])
    with col_prev:
        if st.button("← Prev", use_container_width=True):
            if st.session_state.page > 0:
                st.session_state.page -= 1
                st.rerun()
    with col_mid:
        st.markdown(
            f"<div class='page-indicator' style='text-align:center; padding-top:0.5rem;'>"
            f"Page {st.session_state.page + 1} of {total_pages}</div>",
            unsafe_allow_html=True
        )
    with col_next:
        if st.button("Next →", use_container_width=True):
            if (st.session_state.page + 1) * page_size < len(df):
                st.session_state.page += 1
                st.rerun()


# ── PAGE 2: ADVANCED SEARCH ───────────────────────────────────────────────────────
elif "🔎" in choice:
    st.markdown('<p class="section-header">Find Your Perfect Piece</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")
    with col1:
        s_gender = st.selectbox("Gender", options=df['gender'].unique())
        s_size = st.selectbox("UK Size", options=sorted(df['standard_size'].astype(str).unique()))
    with col2:
        s_type = st.selectbox("Article Type", options=sorted(df['articleType'].unique()))
        s_price = st.slider("Price Range (£)", 0, 300, (20, 150))

    s_color = st.text_input("Color / Style Vibe  (e.g. Navy Floral, Earthy Casual)")

    st.markdown("<div style='margin-top:0.5rem;'></div>", unsafe_allow_html=True)
    if st.button("DISCOVER →"):
        with st.spinner("Curating your selection..."):
            query = f"{s_gender} {s_color} {s_type}"
            results = engine.search_with_filters(
                query, s_gender, s_size, s_price, s_type,
                df, index, model, tokenizer, device
            )

        if not results.empty:
            st.markdown(
                f"<p style='font-size:0.75rem; letter-spacing:0.15em; color:rgba(197,168,105,0.6);"
                f"text-transform:uppercase; margin: 1.5rem 0 1rem;'>"
                f"Showing {min(8, len(results))} results for Size {s_size}</p>",
                unsafe_allow_html=True
            )
            cols = st.columns(4, gap="medium")
            for i, (idx, row) in enumerate(results.head(8).iterrows()):
                with cols[i % 4]:
                    product_card(row)
        else:
            st.warning("No items match your exact filters. Try broadening your price range or color.")


# ── PAGE 3: ATTIRE ARCHITECT ──────────────────────────────────────────────────────
elif "👔" in choice:
    st.markdown('<p class="section-header">Attire Architect — Build Your Full Look</p>',
                unsafe_allow_html=True)

    col_a, col_b = st.columns(2, gap="large")
    with col_a:
        c_gender = st.selectbox("Gender", options=df['gender'].unique())
        c_size = st.selectbox("UK Size", options=sorted(df['standard_size'].astype(str).unique()))
        outfit_color = st.text_input("Color Theme  (e.g. Earth Tones, Monochrome)")
    with col_b:
        top_type = st.selectbox("Top", ["Tshirts", "Shirts", "Dresses"])
        bottom_type = st.selectbox("Bottom", ["Trousers", "Jeans", "Shorts"])
        shoes_type = st.selectbox("Footwear", ["Casual Shoes", "Formal Shoes", "Sports Shoes"])
        acc_type = st.selectbox("Accessory", ["Belts", "Watches", "Caps"])

    st.markdown("<div style='margin-top:0.5rem;'></div>", unsafe_allow_html=True)
    if st.button("GENERATE ENSEMBLE →"):
        with st.spinner("Composing your look..."):
            components = [
                ("Top", top_type),
                ("Bottom", bottom_type),
                ("Footwear", shoes_type),
                ("Accessory", acc_type)
            ]

        st.markdown(
            "<p style='font-size:0.75rem; letter-spacing:0.18em; color:rgba(197,168,105,0.6);"
            "text-transform:uppercase; margin: 1.8rem 0 1rem;'>Your AI-Curated Ensemble</p>",
            unsafe_allow_html=True
        )

        outfit_cols = st.columns(4, gap="medium")
        for i, (label, comp) in enumerate(components):
            with outfit_cols[i]:
                st.markdown(
                    f"<div style='font-family:\"Cormorant Garamond\",serif; font-size:0.9rem;"
                    f"color:rgba(197,168,105,0.7); letter-spacing:0.1em; margin-bottom:0.6rem;"
                    f"text-transform:uppercase;'>{label}</div>",
                    unsafe_allow_html=True
                )
                res = engine.search_with_filters(
                    f"{outfit_color} {comp}", c_gender, c_size,
                    (0, 500), comp, df, index, model, tokenizer, device
                )
                if not res.empty:
                    product_card(res.iloc[0])
                else:
                    st.markdown(
                        f"<div style='padding:1rem; text-align:center; color:rgba(197,168,105,0.4);"
                        f"font-size:0.75rem; letter-spacing:0.1em;'>No {comp}<br>in Size {c_size}</div>",
                        unsafe_allow_html=True
                    )

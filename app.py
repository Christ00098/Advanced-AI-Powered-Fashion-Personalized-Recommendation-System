import streamlit as st
from annoy import AnnoyIndex
import engine
import utils
import pandas as pd
import os

st.set_page_config(
    page_title="Advanced AI-Powered Fashion Personalized Recommendation System",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── GLOBAL CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

st.html("""
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0a0a0f !important;
    color: #f0ece4 !important;
    font-family: 'DM Sans', sans-serif !important;
}

footer, [data-testid="stDecoration"] { display: none !important; }
header, [data-testid="stToolbar"] { background: #0a0a0f !important; }
[data-testid="stToolbar"] button svg { fill: rgba(197,168,105,0.6) !important; }
[data-testid="stSidebar"] { display: none !important; }

[data-testid="stAppViewContainer"] > .main { background: #0a0a0f !important; }
.block-container { padding: 0 2.5rem 3rem !important; max-width: 1400px !important; }

/* ── Hide keyboard tooltip ── */
[data-testid="InputInstructions"],
span[class*="instructionsDisplay"],
div[class*="instructionsDisplay"] {
    display: none !important; visibility: hidden !important;
    height: 0 !important; overflow: hidden !important;
}

/* ── Top Navigation Bar ── */
.top-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.4rem 0 1.2rem;
    border-bottom: 1px solid rgba(197,168,105,0.15);
    margin-bottom: 0;
}
.top-nav-logo {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.2rem; font-weight: 300;
    letter-spacing: 0.22em; color: #f0ece4;
    text-transform: uppercase;
}
.top-nav-logo span { color: #c5a869; font-style: italic; }
.top-nav-btns {
    display: flex; gap: 0.7rem; align-items: center;
}
.nav-btn {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.7rem; letter-spacing: 0.18em; text-transform: uppercase;
    padding: 0.55rem 1.4rem; border-radius: 4px;
    text-decoration: none; transition: all 0.25s; cursor: pointer;
    border: 1px solid rgba(197,168,105,0.3); color: rgba(197,168,105,0.7);
    background: transparent;
}
.nav-btn:hover { border-color: #c5a869; color: #c5a869; background: rgba(197,168,105,0.07); }
.nav-btn.active {
    background: rgba(197,168,105,0.12);
    border-color: #c5a869; color: #c5a869;
}
.nav-btn-home {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.7rem; letter-spacing: 0.18em; text-transform: uppercase;
    padding: 0.55rem 1.4rem; border-radius: 4px;
    text-decoration: none; transition: all 0.25s;
    border: 1px solid rgba(197,168,105,0.15); color: rgba(240,236,228,0.5);
    background: transparent; display: inline-block;
}
.nav-btn-home:hover { border-color: rgba(197,168,105,0.4); color: rgba(240,236,228,0.8); }

/* ── Hero Banner ── */
.hero-banner {
    position: relative; width: 100%; padding: 2.5rem 0 2rem;
    text-align: center; overflow: hidden; margin-bottom: 0.5rem;
}
.hero-banner::before {
    content: ''; position: absolute; inset: 0;
    background: radial-gradient(ellipse 80% 60% at 50% 0%, rgba(197,168,105,0.1) 0%, transparent 70%);
    pointer-events: none;
}
.hero-logo-ring {
    display: inline-flex; align-items: center; justify-content: center;
    width: 60px; height: 60px; border-radius: 50%;
    border: 1.5px solid rgba(197,168,105,0.6);
    background: rgba(197,168,105,0.06); margin-bottom: 0.8rem; font-size: 1.6rem;
    box-shadow: 0 0 40px rgba(197,168,105,0.15);
}
.hero-title {
    font-family: 'Cormorant Garamond', serif !important;
    font-size: clamp(1.8rem, 4vw, 3rem) !important; font-weight: 300 !important;
    letter-spacing: 0.18em !important; color: #f0ece4 !important;
    line-height: 1 !important; margin-bottom: 0.4rem !important;
}
.hero-title span { color: #c5a869; font-style: italic; }
.hero-subtitle {
    font-size: 0.68rem !important; font-weight: 300 !important;
    letter-spacing: 0.3em !important; color: rgba(197,168,105,0.6) !important;
    text-transform: uppercase !important; margin-bottom: 0 !important;
}
.hero-divider {
    width: 80px; height: 1px;
    background: linear-gradient(90deg, transparent, #c5a869, transparent);
    margin: 1rem auto 0;
}

/* ── Section Header ── */
.section-header {
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 1.5rem !important; font-weight: 300 !important;
    letter-spacing: 0.12em !important; color: #f0ece4 !important;
    margin: 2rem 0 1.2rem !important; padding-bottom: 0.6rem !important;
    border-bottom: 1px solid rgba(197,168,105,0.2) !important;
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
    width: 100%; height: 320px; object-fit: cover;
    object-position: top center; display: block; background: #1a1a27;
}
.product-card-body { padding: 0.85rem 0.9rem 1rem; }
.product-card-name {
    font-size: 0.78rem; font-weight: 400; color: #d4cfc6;
    line-height: 1.4; margin-bottom: 0.5rem;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.product-card-price {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.15rem; font-weight: 600; color: #c5a869; letter-spacing: 0.04em;
}
.product-card-size {
    font-size: 0.68rem; font-weight: 300; color: rgba(197,168,105,0.55);
    letter-spacing: 0.08em; text-transform: uppercase; margin-top: 0.2rem;
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

/* ── Streamlit Buttons ── */
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

/* ── Inputs ── */
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
.stTextInput label, .stSelectbox label, .stSlider label {
    color: rgba(197,168,105,0.8) !important; font-size: 0.72rem !important;
    letter-spacing: 0.15em !important; text-transform: uppercase !important;
    font-weight: 400 !important;
}

/* ── Slider ── */
.stSlider [data-baseweb="slider"] div[role="slider"] {
    background: #c5a869 !important; border-color: #c5a869 !important;
}

/* ── Page indicator ── */
.page-indicator {
    font-family: 'Cormorant Garamond', serif;
    font-size: 0.9rem; color: rgba(197,168,105,0.6);
    letter-spacing: 0.1em; text-align: center; padding-top: 0.5rem;
}

/* ── Alerts ── */
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
""")


# ── LOAD RESOURCES ─────────────────────────────────────────────────────────────
@st.cache_resource
def startup_resources():
    model, tokenizer, device = engine.load_ai_model()
    df = utils.load_inventory()
    index = AnnoyIndex(768, 'angular')
    index.load("fashion_vector_index.ann")
    return model, tokenizer, device, df, index

model, tokenizer, device, df, index = startup_resources()

all_sizes   = utils.get_all_sizes(df)
all_colours = ["All"] + sorted(df['baseColour'].dropna().unique().tolist())
min_price   = int(df['price'].min()) if 'price' in df.columns and df['price'].notna().any() else 0
max_price   = int(df['price'].max()) if 'price' in df.columns and df['price'].notna().any() else 10000

# ── PAGE STATE ─────────────────────────────────────────────────────────────────
if "active_page" not in st.session_state:
    st.session_state.active_page = "search"


# ── TOP NAVIGATION ─────────────────────────────────────────────────────────────
HOME_URL = "https://hor-layinka.github.io/Advance-AI-Integration-App/"

search_active   = "active" if st.session_state.active_page == "search"   else ""
architect_active = "active" if st.session_state.active_page == "architect" else ""

st.markdown(f"""
<div class="top-nav">
    <div class="top-nav-logo">Aura<span>Style</span> AI</div>
    <div class="top-nav-btns">
        <a href="{HOME_URL}" class="nav-btn-home" target="_self">← Home</a>
        <span class="nav-btn {search_active}"
              onclick="window.location.href='?page=search'"
              id="btn-search">🔎 &nbsp;Advanced Search</span>
        <span class="nav-btn {architect_active}"
              onclick="window.location.href='?page=architect'"
              id="btn-architect">👔 &nbsp;Attire Architect</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── HERO ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <div class="hero-logo-ring">✦</div>
    <h1 class="hero-title">Advanced AI-Powered Fashion Personalized Recommendation System</h1>
    <p class="hero-subtitle">The Premier Destination for AI-Driven Fashion Recommendations</p>
    <div class="hero-divider"></div>
</div>
""", unsafe_allow_html=True)

# ── HANDLE QUERY PARAM PAGE SWITCHING ─────────────────────────────────────────
params = st.query_params
if "page" in params:
    if params["page"] in ["search", "architect"]:
        st.session_state.active_page = params["page"]

page = st.session_state.active_page


# ── STREAMLIT NAV BUTTONS (hidden but functional for state switching) ──────────
col_s, col_a, _ = st.columns([1, 1, 4])
with col_s:
    if st.button("🔎  Advanced Search", use_container_width=True):
        st.session_state.active_page = "search"
        st.rerun()
with col_a:
    if st.button("👔  Attire Architect", use_container_width=True):
        st.session_state.active_page = "architect"
        st.rerun()

st.markdown("<hr style='margin: 0.5rem 0 1.5rem;'>", unsafe_allow_html=True)


# ── PRODUCT CARD ───────────────────────────────────────────────────────────────
def product_card(row):
    image_path = row.get('image_path', None)
    name       = str(row.get('productDisplayName', ''))[:38]
    article    = str(row.get('articleType', ''))

    price = row.get('price', None)
    if pd.notna(price) and price:
        price_str = f"₹{int(price):,}"
    elif pd.notna(row.get('price_tag', None)):
        price_str = str(row['price_tag'])
    else:
        price_str = "—"

    sizes = row.get('available_sizes', [])
    if isinstance(sizes, list) and sizes:
        sizes_str = "  ·  ".join(sizes[:5])
        if len(sizes) > 5:
            sizes_str += f"  +{len(sizes)-5}"
    else:
        sizes_str = ""

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
            <div class="product-card-price">{price_str}</div>
            <div class="product-card-size">{sizes_str}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ADVANCED SEARCH
# ══════════════════════════════════════════════════════════════════════════════
if page == "search":
    st.markdown('<p class="section-header">Find Your Perfect Piece</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3, gap="large")
    with col1:
        s_gender = st.selectbox("Gender",      options=df['gender'].unique())
        s_size   = st.selectbox("Size",         options=["All"] + all_sizes)
    with col2:
        s_type   = st.selectbox("Article Type", options=sorted(df['articleType'].unique()))
        s_colour = st.selectbox("Base Colour",  options=all_colours)
    with col3:
        s_price  = st.slider("Price Range (₹)", min_price, max_price, (min_price, max_price))

    st.markdown("<div style='margin-top:0.5rem;'></div>", unsafe_allow_html=True)

    if st.button("DISCOVER →"):
        with st.spinner("Curating your selection..."):
            query   = f"{s_gender} {s_colour} {s_type}"
            results = engine.search_with_filters(
                query, s_gender, s_size, s_price, s_type,
                df, index, model, tokenizer, device,
                colour=s_colour
            )
        if not results.empty:
            st.markdown(
                f"<p style='font-size:0.75rem; letter-spacing:0.15em; color:rgba(197,168,105,0.6);"
                f"text-transform:uppercase; margin:1.5rem 0 1rem;'>"
                f"Showing {min(8, len(results))} results</p>",
                unsafe_allow_html=True
            )
            cols = st.columns(4, gap="medium")
            for i, (_, row) in enumerate(results.head(8).iterrows()):
                with cols[i % 4]:
                    product_card(row)
        else:
            st.warning("No items match your filters. Try broadening your selections.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ATTIRE ARCHITECT
# ══════════════════════════════════════════════════════════════════════════════
elif page == "architect":
    st.markdown('<p class="section-header">Attire Architect — Build Your Full Look</p>',
                unsafe_allow_html=True)

    col_a, col_b = st.columns(2, gap="large")
    with col_a:
        c_gender    = st.selectbox("Gender",       options=df['gender'].unique())
        c_size      = st.selectbox("Size",          options=["All"] + all_sizes)
        c_colour    = st.selectbox("Colour Theme",  options=all_colours)
        outfit_vibe = st.text_input("Style Vibe  (e.g. Earth Tones, Monochrome)")
    with col_b:
        top_type    = st.selectbox("Top",       ["Tshirts", "Shirts", "Dresses"])
        bottom_type = st.selectbox("Bottom",    ["Trousers", "Jeans", "Shorts"])
        shoes_type  = st.selectbox("Footwear",  ["Casual Shoes", "Formal Shoes", "Sports Shoes"])
        acc_type    = st.selectbox("Accessory", ["Belts", "Watches", "Caps"])

    st.markdown("<div style='margin-top:0.5rem;'></div>", unsafe_allow_html=True)

    if st.button("GENERATE ENSEMBLE →"):
        components = [
            ("Top",       top_type),
            ("Bottom",    bottom_type),
            ("Footwear",  shoes_type),
            ("Accessory", acc_type),
        ]
        st.markdown(
            "<p style='font-size:0.75rem; letter-spacing:0.18em; color:rgba(197,168,105,0.6);"
            "text-transform:uppercase; margin:1.8rem 0 1rem;'>Your AI-Curated Ensemble</p>",
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
                query = f"{outfit_vibe} {c_colour} {comp}".strip()
                with st.spinner(""):
                    res = engine.search_with_filters(
                        query, c_gender, c_size, (0, max_price), comp,
                        df, index, model, tokenizer, device,
                        colour=c_colour
                    )
                if not res.empty:
                    product_card(res.iloc[0])
                else:
                    st.markdown(
                        f"<div style='padding:1rem; text-align:center; color:rgba(197,168,105,0.4);"
                        f"font-size:0.75rem; letter-spacing:0.1em;'>No {comp}<br>in Size {c_size}</div>",
                        unsafe_allow_html=True
                    )

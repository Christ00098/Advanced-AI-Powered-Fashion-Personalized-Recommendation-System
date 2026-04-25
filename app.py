import streamlit as st
import streamlit.components.v1 as components
from annoy import AnnoyIndex
import engine
import utils
import pandas as pd
import os

st.set_page_config(
    page_title="AuraStyle AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"  # collapsed on landing page
)

# ── QUERY PARAM: jump straight to gallery if coming from landing CTA ───────────
params = st.query_params
if "page" in params and "nav" not in st.session_state:
    mapping = {
        "gallery":  "🏠  Home Gallery",
        "search":   "🔎  Advanced Search",
        "architect":"👔  Attire Architect",
    }
    st.session_state["nav"] = mapping.get(params["page"], "🌐  Welcome")

# Default nav
if "nav" not in st.session_state:
    st.session_state["nav"] = "🌐  Welcome"

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
[data-testid="stToolbar"] button, [data-testid="stToolbar"] svg {
    color: rgba(197,168,105,0.6) !important;
    fill: rgba(197,168,105,0.6) !important;
}

[data-testid="stAppViewContainer"] > .main { background: #0a0a0f !important; }
.block-container { padding: 0 2.5rem 3rem !important; max-width: 1400px !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0f0f18 !important;
    border-right: 1px solid rgba(197,168,105,0.15) !important;
}
[data-testid="stSidebar"] * { color: #f0ece4 !important; font-family: 'DM Sans', sans-serif !important; }

/* Hide keyboard tooltip */
[data-testid="InputInstructions"],
span[class*="instructionsDisplay"],
div[class*="instructionsDisplay"],
[data-testid="collapsedControl"] span,
[data-testid="stSidebarCollapseButton"] span {
    display: none !important; visibility: hidden !important;
    height: 0 !important; overflow: hidden !important;
}

/* ── Hero Banner (app pages) ── */
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

/* ── Section Header ── */
.section-header {
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 1.6rem !important; font-weight: 300 !important;
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
    letter-spacing: 0.1em; text-transform: uppercase; margin-top: 0.2rem;
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

/* ── Inputs ── */
.stTextInput > div > div > input,
.stSelectbox > div > div,
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

/* Hide iframe border on landing page */
iframe {
    border: none !important;
    display: block !important;
}

[data-testid="stAppViewContainer"] {
    overflow: hidden !important;
}
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

menu = ["🌐  Welcome", "🏠  Home Gallery", "🔎  Advanced Search", "👔  Attire Architect"]

# Use session_state to control which page is active
nav_index = menu.index(st.session_state["nav"]) if st.session_state["nav"] in menu else 0
choice = st.sidebar.radio("Navigation", menu, index=nav_index, label_visibility="collapsed")

# Keep session_state in sync with sidebar selection
st.session_state["nav"] = choice


# ── PRODUCT CARD ───────────────────────────────────────────────────────────────
def product_card(row):
    image_path = row.get('image_path', None)
    name       = str(row.get('productDisplayName', ''))[:38]
    price      = row.get('price', None)
    sizes      = row.get('available_sizes', [])
    article    = str(row.get('articleType', ''))

    # Price display
    if pd.notna(price) and price:
        price_str = f"₹{int(price):,}"
    elif pd.notna(row.get('price_tag', None)):
        price_str = str(row['price_tag'])
    else:
        price_str = "—"

    # Sizes display
    if isinstance(sizes, list) and sizes:
        sizes_str = "  ·  ".join(sizes[:5])
        if len(sizes) > 5:
            sizes_str += f"  +{len(sizes)-5}"
    else:
        sizes_str = ""

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
            <div class="product-card-price">{price_str}</div>
            <div class="product-card-size">{sizes_str}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 0 — LANDING PAGE
# ══════════════════════════════════════════════════════════════════════════════
if "🌐" in choice:
    components.html("""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400;1,600&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500&display=swap" rel="stylesheet">
<style>
:root {
  --gold: #c5a869; --gold-dim: rgba(197,168,105,0.12);
  --gold-border: rgba(197,168,105,0.25);
  --dark: #0a0a0f; --dark2: #0f0f18; --dark3: #12121c;
  --cream: #f0ece4; --cream-dim: rgba(240,236,228,0.6);
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body { background: var(--dark); color: var(--cream); font-family: 'DM Sans', sans-serif; font-weight: 300; overflow-x: hidden; }

/* NAV */
nav {
  position: sticky; top: 0; z-index: 100;
  display: flex; align-items: center; justify-content: space-between;
  padding: 1.2rem 3rem;
  background: rgba(10,10,15,0.92); backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--gold-border);
}
.nav-logo { font-family: 'Cormorant Garamond', serif; font-size: 1.2rem; font-weight: 300; letter-spacing: 0.22em; color: var(--cream); text-transform: uppercase; }
.nav-logo span { color: var(--gold); font-style: italic; }
.nav-links { display: flex; gap: 2rem; list-style: none; }
.nav-links a { font-size: 0.7rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--cream-dim); text-decoration: none; transition: color 0.2s; }
.nav-links a:hover { color: var(--gold); }
.nav-cta {
  font-size: 0.7rem; letter-spacing: 0.2em; text-transform: uppercase;
  color: var(--dark); background: var(--gold);
  padding: 0.5rem 1.4rem; border-radius: 3px; cursor: pointer;
  border: none; font-family: 'DM Sans', sans-serif; font-weight: 500;
  transition: all 0.2s;
}
.nav-cta:hover { background: #d4b97a; }

/* HERO */
.hero {
  min-height: 92vh; display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  text-align: center; padding: 5rem 2rem 3rem; position: relative; overflow: hidden;
}
.hero::before {
  content: ''; position: absolute; inset: 0;
  background: radial-gradient(ellipse 70% 50% at 50% 0%, rgba(197,168,105,0.1) 0%, transparent 60%),
              radial-gradient(ellipse 40% 30% at 80% 80%, rgba(197,168,105,0.05) 0%, transparent 50%);
}
.hero-eyebrow { font-size: 0.65rem; letter-spacing: 0.45em; text-transform: uppercase; color: var(--gold); margin-bottom: 2rem; opacity: 0; animation: fadeUp 0.9s 0.2s forwards; }
.hero-ring {
  width: 76px; height: 76px; border-radius: 50%;
  border: 1px solid var(--gold-border); background: var(--gold-dim);
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 1.5rem; font-size: 1.8rem; color: var(--gold);
  box-shadow: 0 0 60px rgba(197,168,105,0.12);
  opacity: 0; animation: fadeUp 0.9s 0.4s forwards;
}
.hero h1 {
  font-family: 'Cormorant Garamond', serif;
  font-size: clamp(3.5rem, 9vw, 6.5rem); font-weight: 300; line-height: 0.95;
  letter-spacing: 0.12em; text-transform: uppercase; color: var(--cream);
  margin-bottom: 0.5rem; opacity: 0; animation: fadeUp 0.9s 0.6s forwards;
}
.hero h1 em { color: var(--gold); font-style: italic; }
.hero-sub {
  font-family: 'Cormorant Garamond', serif; font-size: clamp(1rem, 2.5vw, 1.4rem);
  font-weight: 300; font-style: italic; color: var(--cream-dim);
  margin-bottom: 2.5rem; opacity: 0; animation: fadeUp 0.9s 0.8s forwards;
}
.hero-line { width: 60px; height: 1px; background: linear-gradient(90deg, transparent, var(--gold), transparent); margin: 0 auto 2.5rem; opacity: 0; animation: fadeUp 0.9s 1s forwards; }
.hero-desc { max-width: 500px; font-size: 0.88rem; line-height: 1.85; color: var(--cream-dim); margin: 0 auto 3rem; opacity: 0; animation: fadeUp 0.9s 1.1s forwards; }
.hero-btns { display: flex; gap: 1rem; align-items: center; justify-content: center; flex-wrap: wrap; opacity: 0; animation: fadeUp 0.9s 1.3s forwards; }
.btn-primary { font-size: 0.7rem; letter-spacing: 0.25em; text-transform: uppercase; color: var(--dark); background: var(--gold); padding: 0.85rem 2.2rem; border-radius: 3px; cursor: pointer; border: none; font-family: 'DM Sans', sans-serif; font-weight: 500; transition: all 0.2s; }
.btn-primary:hover { background: #d4b97a; transform: translateY(-1px); }
.btn-ghost { font-size: 0.7rem; letter-spacing: 0.25em; text-transform: uppercase; color: var(--gold); border: 1px solid var(--gold-border); padding: 0.85rem 2.2rem; border-radius: 3px; cursor: pointer; background: transparent; font-family: 'DM Sans', sans-serif; transition: all 0.2s; text-decoration: none; display: inline-block; }
.btn-ghost:hover { background: var(--gold-dim); border-color: var(--gold); }
.scroll-hint { margin-top: 3rem; display: flex; flex-direction: column; align-items: center; gap: 0.4rem; opacity: 0; animation: fadeUp 0.9s 1.6s forwards; }
.scroll-hint span { font-size: 0.58rem; letter-spacing: 0.3em; text-transform: uppercase; color: rgba(197,168,105,0.35); }
.scroll-line { width: 1px; height: 36px; background: linear-gradient(to bottom, var(--gold), transparent); animation: pulse 2s ease-in-out infinite; }

/* STATS */
.stats { display: grid; grid-template-columns: repeat(4, 1fr); border-top: 1px solid var(--gold-border); border-bottom: 1px solid var(--gold-border); background: var(--dark2); }
.stat { padding: 2rem 1rem; text-align: center; border-right: 1px solid var(--gold-border); }
.stat:last-child { border-right: none; }
.stat-n { font-family: 'Cormorant Garamond', serif; font-size: 2.2rem; font-weight: 300; color: var(--gold); display: block; margin-bottom: 0.3rem; }
.stat-l { font-size: 0.62rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--cream-dim); }

/* FEATURES */
.features { padding: 5rem 3rem; }
.feature-row { display: grid; grid-template-columns: 1fr 1fr; gap: 5rem; align-items: center; max-width: 1100px; margin: 0 auto 6rem; }
.feature-row:last-child { margin-bottom: 0; }
.feature-row.flip { direction: rtl; }
.feature-row.flip > * { direction: ltr; }
.feat-tag { font-size: 0.62rem; letter-spacing: 0.4em; text-transform: uppercase; color: var(--gold); margin-bottom: 1rem; display: block; }
.feat-num { font-family: 'Cormorant Garamond', serif; font-size: 4rem; font-weight: 300; color: rgba(197,168,105,0.07); line-height: 1; margin-bottom: -1.2rem; display: block; }
.feat-title { font-family: 'Cormorant Garamond', serif; font-size: clamp(1.8rem, 3vw, 2.6rem); font-weight: 300; color: var(--cream); line-height: 1.1; margin-bottom: 1.2rem; }
.feat-title em { color: var(--gold); font-style: italic; }
.feat-body { font-size: 0.85rem; line-height: 1.9; color: var(--cream-dim); margin-bottom: 1.5rem; }
.feat-points { display: flex; flex-direction: column; gap: 0.7rem; }
.feat-point { display: flex; align-items: flex-start; gap: 0.7rem; font-size: 0.82rem; color: var(--cream-dim); line-height: 1.6; }
.feat-point::before { content: '✦'; color: var(--gold); font-size: 0.5rem; margin-top: 0.35rem; flex-shrink: 0; }

/* VISUAL PANELS */
.panel { background: var(--dark3); border: 1px solid var(--gold-border); border-radius: 12px; overflow: hidden; min-height: 400px; display: flex; align-items: center; justify-content: center; position: relative; }
.panel::before { content: ''; position: absolute; inset: 0; background: radial-gradient(ellipse at 50% 50%, rgba(197,168,105,0.04) 0%, transparent 70%); }

/* Panel: Gallery grid */
.p-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 0.5rem; padding: 1rem; width: 100%; }
.p-card { background: var(--dark2); border: 1px solid rgba(197,168,105,0.1); border-radius: 6px; overflow: hidden; aspect-ratio: 2/3; }
.p-card-img { height: 72%; display: flex; align-items: center; justify-content: center; font-size: 1.8rem; background: linear-gradient(135deg,#1a1a2e,#16213e); }
.p-card-body { padding: 0.4rem 0.5rem; }
.p-line { height: 5px; border-radius: 3px; background: rgba(197,168,105,0.12); margin-bottom: 3px; }
.p-line.s { width: 55%; }
.p-line.p { background: rgba(197,168,105,0.35); width: 40%; }

/* Panel: Search */
.p-search { padding: 1.5rem; width: 100%; }
.p-bar { background: rgba(255,255,255,0.04); border: 1px solid var(--gold-border); border-radius: 6px; padding: 0.7rem 1rem; display: flex; align-items: center; gap: 0.7rem; margin-bottom: 1rem; }
.p-bar-ic { color: var(--gold); font-size: 0.8rem; }
.p-bar-tx { font-size: 0.72rem; color: var(--cream-dim); }
.p-chips { display: flex; gap: 0.4rem; flex-wrap: wrap; margin-bottom: 1.2rem; }
.p-chip { background: rgba(197,168,105,0.1); border: 1px solid var(--gold-border); border-radius: 20px; padding: 0.25rem 0.8rem; font-size: 0.6rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--gold); }
.p-results { display: grid; grid-template-columns: repeat(2,1fr); gap: 0.5rem; }
.p-item { background: var(--dark2); border: 1px solid rgba(197,168,105,0.1); border-radius: 6px; padding: 0.7rem; display: flex; align-items: center; gap: 0.6rem; }
.p-item-img { width: 36px; height: 48px; border-radius: 4px; background: linear-gradient(135deg,#1a1a2e,#0f3460); display: flex; align-items: center; justify-content: center; font-size: 1rem; flex-shrink: 0; }
.p-item-l1 { height: 6px; background: rgba(240,236,228,0.15); border-radius: 3px; margin-bottom: 4px; }
.p-item-l2 { height: 6px; width: 50%; background: rgba(197,168,105,0.35); border-radius: 3px; }

/* Panel: Outfit */
.p-outfit { padding: 1.2rem; width: 100%; }
.p-outfit-hdr { font-family: 'Cormorant Garamond', serif; font-size: 0.72rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--gold); margin-bottom: 1rem; text-align: center; }
.p-out-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 0.4rem; }
.p-out-card { background: var(--dark2); border: 1px solid rgba(197,168,105,0.12); border-radius: 6px; overflow: hidden; text-align: center; }
.p-out-lbl { padding: 0.28rem; font-size: 0.52rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--gold); border-bottom: 1px solid rgba(197,168,105,0.1); }
.p-out-img { aspect-ratio: 2/3; display: flex; align-items: center; justify-content: center; font-size: 1.6rem; }
.p-out-prc { padding: 0.28rem; font-size: 0.62rem; color: var(--gold); font-family: 'Cormorant Garamond', serif; }
.s1 { background: linear-gradient(160deg,#1a1040,#2d1b69); }
.s2 { background: linear-gradient(160deg,#0a1628,#1a3a5c); }
.s3 { background: linear-gradient(160deg,#1a0a0a,#4a1515); }
.s4 { background: linear-gradient(160deg,#0a1a0a,#1a4a1a); }

/* HOW IT WORKS */
.how { background: var(--dark2); padding: 5rem 3rem; border-top: 1px solid var(--gold-border); border-bottom: 1px solid var(--gold-border); }
.how-inner { max-width: 1000px; margin: 0 auto; }
.how-ttl { font-family: 'Cormorant Garamond', serif; font-size: 2.2rem; font-weight: 300; text-align: center; color: var(--cream); margin-bottom: 3.5rem; }
.how-ttl em { color: var(--gold); font-style: italic; }
.steps { display: grid; grid-template-columns: repeat(3,1fr); gap: 2.5rem; }
.step { text-align: center; }
.step-n { width: 52px; height: 52px; border-radius: 50%; border: 1px solid var(--gold-border); background: var(--gold-dim); display: flex; align-items: center; justify-content: center; margin: 0 auto 1.2rem; font-family: 'Cormorant Garamond', serif; font-size: 1.3rem; color: var(--gold); }
.step h3 { font-family: 'Cormorant Garamond', serif; font-size: 1.15rem; font-weight: 400; color: var(--cream); margin-bottom: 0.7rem; }
.step p { font-size: 0.78rem; line-height: 1.8; color: var(--cream-dim); }

/* CATEGORIES */
.cats { padding: 5rem 3rem; }
.cats-inner { max-width: 1100px; margin: 0 auto; text-align: center; }
.sec-tag { font-size: 0.62rem; letter-spacing: 0.4em; text-transform: uppercase; color: var(--gold); display: block; margin-bottom: 1rem; }
.sec-ttl { font-family: 'Cormorant Garamond', serif; font-size: 2.2rem; font-weight: 300; color: var(--cream); margin-bottom: 2.5rem; }
.sec-ttl em { color: var(--gold); font-style: italic; }
.cats-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 0.9rem; }
.cat-card { background: var(--dark3); border: 1px solid rgba(197,168,105,0.1); border-radius: 10px; padding: 1.8rem 1rem; text-align: center; cursor: pointer; transition: all 0.3s; }
.cat-card:hover { border-color: rgba(197,168,105,0.35); transform: translateY(-3px); }
.cat-ic { font-size: 1.8rem; display: block; margin-bottom: 0.8rem; }
.cat-nm { font-family: 'Cormorant Garamond', serif; font-size: 1.05rem; color: var(--cream); margin-bottom: 0.3rem; }
.cat-ct { font-size: 0.62rem; letter-spacing: 0.15em; color: var(--cream-dim); text-transform: uppercase; }

/* QUOTE */
.quote-sec { padding: 5rem 3rem; background: var(--dark2); border-top: 1px solid var(--gold-border); text-align: center; }
blockquote { font-family: 'Cormorant Garamond', serif; font-size: clamp(1.3rem, 3vw, 1.9rem); font-weight: 300; font-style: italic; color: var(--cream); line-height: 1.5; max-width: 700px; margin: 0 auto 1.5rem; }
blockquote::before { content: '\201C'; color: var(--gold); }
blockquote::after  { content: '\201D'; color: var(--gold); }
.q-author { font-size: 0.68rem; letter-spacing: 0.25em; text-transform: uppercase; color: var(--gold); }

/* CTA */
.cta-sec { padding: 6rem 3rem; text-align: center; }
.cta-inner { max-width: 620px; margin: 0 auto; }
.cta-inner h2 { font-family: 'Cormorant Garamond', serif; font-size: clamp(2.2rem, 5vw, 3.5rem); font-weight: 300; color: var(--cream); margin-bottom: 1.2rem; line-height: 1.1; }
.cta-inner h2 em { color: var(--gold); font-style: italic; }
.cta-inner p { font-size: 0.85rem; color: var(--cream-dim); margin-bottom: 2.5rem; line-height: 1.85; }
.cta-line { width: 60px; height: 1px; background: linear-gradient(90deg,transparent,var(--gold),transparent); margin: 1.5rem auto; }

/* FOOTER */
footer { border-top: 1px solid var(--gold-border); padding: 2.5rem 3rem; display: flex; align-items: center; justify-content: space-between; background: var(--dark2); }
.f-logo { font-family: 'Cormorant Garamond', serif; font-size: 1rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--cream); }
.f-logo span { color: var(--gold); font-style: italic; }
.f-copy { font-size: 0.62rem; letter-spacing: 0.15em; color: var(--cream-dim); text-transform: uppercase; }

/* ANIMATIONS */
@keyframes fadeUp { from { opacity:0; transform:translateY(22px); } to { opacity:1; transform:translateY(0); } }
@keyframes pulse { 0%,100% { opacity:0.3; } 50% { opacity:1; } }
.reveal { opacity:0; transform:translateY(28px); transition: opacity 0.7s ease, transform 0.7s ease; }
.reveal.on { opacity:1; transform:translateY(0); }
</style>
</head>
<body>

<nav>
  <div class="nav-logo">Aura<span>Style</span> AI</div>
  <ul class="nav-links">
    <li><a href="#features">Features</a></li>
    <li><a href="#how">How It Works</a></li>
    <li><a href="#categories">Collections</a></li>
  </ul>
  <button class="nav-cta" onclick="launchApp()">Launch App →</button>
</nav>

<!-- HERO -->
<section class="hero">
  <p class="hero-eyebrow">Introducing the Future of Fashion Discovery</p>
  <div class="hero-ring">✦</div>
  <h1>Aura<em>Style</em> AI</h1>
  <p class="hero-sub">The Premier AI Fashion Experience</p>
  <div class="hero-line"></div>
  <p class="hero-desc">Discover fashion that truly fits — your style, your size, your budget. Our AI curates a wardrobe that feels effortlessly you.</p>
  <div class="hero-btns">
    <button class="btn-primary" onclick="launchApp()">Explore Collection</button>
    <a href="#features" class="btn-ghost">See How It Works</a>
  </div>
  <div class="scroll-hint">
    <span>Scroll</span>
    <div class="scroll-line"></div>
  </div>
</section>

<!-- STATS -->
<div class="stats">
  <div class="stat"><span class="stat-n">44K+</span><span class="stat-l">Curated Products</span></div>
  <div class="stat"><span class="stat-n">98%</span><span class="stat-l">Match Accuracy</span></div>
  <div class="stat"><span class="stat-n">12+</span><span class="stat-l">Fashion Categories</span></div>
  <div class="stat"><span class="stat-n">AI</span><span class="stat-l">Powered Styling</span></div>
</div>

<!-- FEATURES -->
<section class="features" id="features">

  <!-- 01 Gallery -->
  <div class="feature-row reveal">
    <div>
      <span class="feat-tag">01. Browse</span>
      <span class="feat-num">01</span>
      <h2 class="feat-title">Your Personal<br><em>Fashion Gallery</em></h2>
      <p class="feat-body">Explore thousands of curated fashion pieces in a beautifully designed gallery. Every product is AI-matched for the highest quality selection.</p>
      <div class="feat-points">
        <div class="feat-point">Browse 44,000+ fashion products across all categories</div>
        <div class="feat-point">Filter by gender, category, colour and price instantly</div>
        <div class="feat-point">Real-time prices with discounts clearly displayed</div>
        <div class="feat-point">Available sizes shown on every product card</div>
      </div>
    </div>
    <div class="panel">
      <div class="p-grid">
        <div class="p-card"><div class="p-card-img">👔</div><div class="p-card-body"><div class="p-line"></div><div class="p-line s"></div><div class="p-line p"></div></div></div>
        <div class="p-card"><div class="p-card-img">👗</div><div class="p-card-body"><div class="p-line"></div><div class="p-line s"></div><div class="p-line p"></div></div></div>
        <div class="p-card"><div class="p-card-img">👟</div><div class="p-card-body"><div class="p-line"></div><div class="p-line s"></div><div class="p-line p"></div></div></div>
        <div class="p-card"><div class="p-card-img">🧥</div><div class="p-card-body"><div class="p-line"></div><div class="p-line s"></div><div class="p-line p"></div></div></div>
        <div class="p-card"><div class="p-card-img">👜</div><div class="p-card-body"><div class="p-line"></div><div class="p-line s"></div><div class="p-line p"></div></div></div>
        <div class="p-card"><div class="p-card-img">⌚</div><div class="p-card-body"><div class="p-line"></div><div class="p-line s"></div><div class="p-line p"></div></div></div>
      </div>
    </div>
  </div>

  <!-- 02 Search -->
  <div class="feature-row flip reveal" style="background:transparent; padding: 4rem 0;">
    <div>
      <span class="feat-tag">02. Discover</span>
      <span class="feat-num">02</span>
      <h2 class="feat-title">AI-Powered<br><em>Precision Search</em></h2>
      <p class="feat-body">Go beyond basic filtering. Our semantic AI understands your style language — describe what you want and it finds exactly that.</p>
      <div class="feat-points">
        <div class="feat-point">Natural language search — describe your style vibe</div>
        <div class="feat-point">Filter by master category, article type and age group</div>
        <div class="feat-point">Size-aware — only shows items in your size</div>
        <div class="feat-point">Dynamic price range based on real inventory</div>
      </div>
    </div>
    <div class="panel">
      <div class="p-search">
        <div class="p-bar"><span class="p-bar-ic">✦</span><span class="p-bar-tx">Navy casual summer shirt for men...</span></div>
        <div class="p-chips"><span class="p-chip">Men</span><span class="p-chip">Apparel</span><span class="p-chip">Size L</span><span class="p-chip">₹500–₹2,000</span><span class="p-chip">Adults</span></div>
        <div class="p-results">
          <div class="p-item"><div class="p-item-img">👔</div><div><div class="p-item-l1"></div><div class="p-item-l2"></div></div></div>
          <div class="p-item"><div class="p-item-img">🧢</div><div><div class="p-item-l1"></div><div class="p-item-l2"></div></div></div>
          <div class="p-item"><div class="p-item-img">👕</div><div><div class="p-item-l1"></div><div class="p-item-l2"></div></div></div>
          <div class="p-item"><div class="p-item-img">🧣</div><div><div class="p-item-l1"></div><div class="p-item-l2"></div></div></div>
        </div>
      </div>
    </div>
  </div>

  <!-- 03 Outfit -->
  <div class="feature-row reveal">
    <div>
      <span class="feat-tag">03. Create</span>
      <span class="feat-num">03</span>
      <h2 class="feat-title">The Attire<br><em>Architect</em></h2>
      <p class="feat-body">Build your complete look in one place. Select any combination of clothing pieces and our AI curates the best match for each slot.</p>
      <div class="feat-points">
        <div class="feat-point">Pick any mix of article types for your outfit</div>
        <div class="feat-point">AI finds the closest semantic match per piece</div>
        <div class="feat-point">Consistent size, budget and style across all items</div>
        <div class="feat-point">No limit on outfit size — expand as needed</div>
      </div>
    </div>
    <div class="panel">
      <div class="p-outfit">
        <div class="p-outfit-hdr">Your AI Ensemble — Earth Tones · Size M</div>
        <div class="p-out-grid">
          <div class="p-out-card"><div class="p-out-lbl">Top</div><div class="p-out-img s1">👔</div><div class="p-out-prc">₹1,299</div></div>
          <div class="p-out-card"><div class="p-out-lbl">Bottom</div><div class="p-out-img s2">👖</div><div class="p-out-prc">₹1,799</div></div>
          <div class="p-out-card"><div class="p-out-lbl">Footwear</div><div class="p-out-img s3">👟</div><div class="p-out-prc">₹2,499</div></div>
          <div class="p-out-card"><div class="p-out-lbl">Watch</div><div class="p-out-img s4">⌚</div><div class="p-out-prc">₹4,999</div></div>
        </div>
      </div>
    </div>
  </div>

</section>

<!-- HOW IT WORKS -->
<section class="how" id="how">
  <div class="how-inner reveal">
    <h2 class="how-ttl">How <em>AuraStyle</em> Works</h2>
    <div class="steps">
      <div class="step"><div class="step-n">01</div><h3>Tell Us Your Style</h3><p>Set your gender, age group, preferred sizes and budget. Describe your color or style vibe in plain language.</p></div>
      <div class="step"><div class="step-n">02</div><h3>AI Understands You</h3><p>Our marqo-fashionSigLIP model encodes your preferences into semantic vectors and finds the closest fashion matches in milliseconds.</p></div>
      <div class="step"><div class="step-n">03</div><h3>Discover Your Look</h3><p>Browse AI-ranked results or build a complete outfit in the Attire Architect — perfectly matched across every piece.</p></div>
    </div>
  </div>
</section>

<!-- CATEGORIES -->
<section class="cats" id="categories">
  <div class="cats-inner reveal">
    <span class="sec-tag">Shop by Category</span>
    <h2 class="sec-ttl">Explore the <em>Collection</em></h2>
    <div class="cats-grid">
      <div class="cat-card" onclick="launchApp()"><span class="cat-ic">👔</span><div class="cat-nm">Apparel</div><div class="cat-ct">28,000+ items</div></div>
      <div class="cat-card" onclick="launchApp()"><span class="cat-ic">👟</span><div class="cat-nm">Footwear</div><div class="cat-ct">8,500+ items</div></div>
      <div class="cat-card" onclick="launchApp()"><span class="cat-ic">⌚</span><div class="cat-nm">Accessories</div><div class="cat-ct">6,200+ items</div></div>
      <div class="cat-card" onclick="launchApp()"><span class="cat-ic">💄</span><div class="cat-nm">Personal Care</div><div class="cat-ct">1,700+ items</div></div>
    </div>
  </div>
</section>

<!-- QUOTE -->
<section class="quote-sec">
  <div style="width:40px;height:1px;background:var(--gold);margin:0 auto 2rem;"></div>
  <blockquote>Finally, a fashion app that understands what I mean when I say I want something effortlessly chic yet casual.</blockquote>
  <div class="q-author">— Early Access User</div>
</section>

<!-- CTA -->
<section class="cta-sec">
  <div class="cta-inner reveal">
    <div class="hero-ring" style="opacity:1;">✦</div>
    <div class="cta-line"></div>
    <h2>Ready to Discover<br>Your <em>True Style?</em></h2>
    <p>Join thousands already discovering fashion that truly fits — the right size, the right price, the right look. Powered by AI built for fashion.</p>
    <div class="hero-btns">
      <button class="btn-primary" onclick="launchApp()">Start Exploring</button>
      <a href="#features" class="btn-ghost">Learn More</a>
    </div>
  </div>
</section>

<!-- FOOTER -->
<footer>
  <div class="f-logo">Aura<span>Style</span> AI</div>
  <div class="f-copy">© 2026 AuraStyle AI · All rights reserved</div>
</footer>

<script>
function launchApp() {
  window.parent.postMessage({ type: 'streamlit:setComponentValue', data: 'gallery' }, '*');
}

const obs = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('on'); });
}, { threshold: 0.1 });
document.querySelectorAll('.reveal').forEach(el => obs.observe(el));
</script>
</body>
</html>
""", height=6200, scrolling=True)

    # Listen for the "Launch App" message from the iframe
    # Use a button below the landing page as reliable fallback
    st.markdown("<div style='text-align:center; margin-top:1rem;'>", unsafe_allow_html=True)
    if st.button("✦  Enter the Collection  →", use_container_width=False):
        st.session_state["nav"] = "🏠  Home Gallery"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — HOME GALLERY
# ══════════════════════════════════════════════════════════════════════════════
elif "🏠" in choice:
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-logo-ring">✦</div>
        <h1 class="hero-title">AURA<span>STYLE</span> AI</h1>
        <p class="hero-subtitle">The Premier AI Fashion Experience</p>
        <div class="hero-divider"></div>
    </div>
    """, unsafe_allow_html=True)

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
            f"<div class='page-indicator' style='text-align:center; padding-top:0.5rem;'>"
            f"Page {st.session_state.page + 1} of {total_pages}</div>",
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
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-logo-ring">✦</div>
        <h1 class="hero-title">AURA<span>STYLE</span> AI</h1>
        <p class="hero-subtitle">The Premier AI Fashion Experience</p>
        <div class="hero-divider"></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="section-header">Find Your Perfect Piece</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")
    with col1:
        s_gender = st.selectbox("Gender", options=df['gender'].unique())
        s_size   = st.selectbox("Size", options=["All"] + utils.get_all_sizes(df))
    with col2:
        s_type  = st.selectbox("Article Type", options=sorted(df['articleType'].unique()))
        s_price = st.slider("Price Range (₹)", 0, 10000, (500, 5000))

    s_color = st.text_input("Color / Style Vibe  (e.g. Navy Floral, Earthy Casual)")

    st.markdown("<div style='margin-top:0.5rem;'></div>", unsafe_allow_html=True)
    if st.button("DISCOVER →"):
        with st.spinner("Curating your selection..."):
            query   = f"{s_gender} {s_color} {s_type}"
            results = engine.search_with_filters(
                query, s_gender, s_size, s_price, s_type,
                df, index, model, tokenizer, device
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
            st.warning("No items match your exact filters. Try broadening your price range or color.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — ATTIRE ARCHITECT
# ══════════════════════════════════════════════════════════════════════════════
elif "👔" in choice:
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-logo-ring">✦</div>
        <h1 class="hero-title">AURA<span>STYLE</span> AI</h1>
        <p class="hero-subtitle">The Premier AI Fashion Experience</p>
        <div class="hero-divider"></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="section-header">Attire Architect — Build Your Full Look</p>',
                unsafe_allow_html=True)

    col_a, col_b = st.columns(2, gap="large")
    with col_a:
        c_gender     = st.selectbox("Gender", options=df['gender'].unique())
        c_size       = st.selectbox("Size", options=["All"] + utils.get_all_sizes(df))
        outfit_color = st.text_input("Color Theme  (e.g. Earth Tones, Monochrome)")
    with col_b:
        top_type    = st.selectbox("Top",       ["Tshirts", "Shirts", "Dresses"])
        bottom_type = st.selectbox("Bottom",    ["Trousers", "Jeans", "Shorts"])
        shoes_type  = st.selectbox("Footwear",  ["Casual Shoes", "Formal Shoes", "Sports Shoes"])
        acc_type    = st.selectbox("Accessory", ["Belts", "Watches", "Caps"])

    st.markdown("<div style='margin-top:0.5rem;'></div>", unsafe_allow_html=True)
    if st.button("GENERATE ENSEMBLE →"):
        components_list = [
            ("Top", top_type), ("Bottom", bottom_type),
            ("Footwear", shoes_type), ("Accessory", acc_type)
        ]
        st.markdown(
            "<p style='font-size:0.75rem; letter-spacing:0.18em; color:rgba(197,168,105,0.6);"
            "text-transform:uppercase; margin:1.8rem 0 1rem;'>Your AI-Curated Ensemble</p>",
            unsafe_allow_html=True
        )
        outfit_cols = st.columns(4, gap="medium")
        for i, (label, comp) in enumerate(components_list):
            with outfit_cols[i]:
                st.markdown(
                    f"<div style='font-family:\"Cormorant Garamond\",serif; font-size:0.9rem;"
                    f"color:rgba(197,168,105,0.7); letter-spacing:0.1em; margin-bottom:0.6rem;"
                    f"text-transform:uppercase;'>{label}</div>",
                    unsafe_allow_html=True
                )
                res = engine.search_with_filters(
                    f"{outfit_color} {comp}", c_gender, c_size,
                    (0, 10000), comp, df, index, model, tokenizer, device
                )
                if not res.empty:
                    product_card(res.iloc[0])
                else:
                    st.markdown(
                        f"<div style='padding:1rem; text-align:center; color:rgba(197,168,105,0.4);"
                        f"font-size:0.75rem; letter-spacing:0.1em;'>No {comp}<br>in Size {c_size}</div>",
                        unsafe_allow_html=True
                    )

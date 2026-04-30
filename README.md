# Advance-AI-Integration-App
ML/AI apps that solves business problem


# Advanced AI-Powered Fashion Personalized Recommendation System

## Overview
Advaced AI is an end-to-end AI-powered fashion recommendation system that combines 
semantic search with deep learning to deliver highly personalized fashion discovery. 
Built on a dataset of 44,000+ curated fashion products, the system understands natural 
language style descriptions and matches users to the most relevant items across gender, 
size, colour, price and category filters.

---

## Features

### 🔎 Advanced Search
Semantic search powered by **marqo-fashionSigLIP** — a SigLIP-based vision-language 
model fine-tuned specifically on fashion data. Users describe what they want in plain 
language and the system returns the closest matches ranked by semantic similarity.

- Filter by gender, article type, base colour, size and price range
- Natural language style vibe input (e.g. "Navy casual summer shirt")
- Size-aware filtering using real available sizes per product
- Dynamic price range based on actual inventory data

### 👔 Attire Architect
An AI outfit builder that curates a complete look from a single query. Users select 
the pieces they need (top, bottom, footwear, accessories) and the system returns the 
best-matched product for each slot — consistent in colour, size and style.

- Select any combination of article types
- Colour theme and style vibe inputs
- Budget-aware filtering with real price data
- Graceful fallbacks for unavailable combinations

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend (Landing Page) | HTML, CSS, JavaScript — GitHub Pages |
| Backend / App | Python, Streamlit |
| AI Model | marqo-fashionSigLIP (via open_clip) |
| Vector Search | Annoy (Approximate Nearest Neighbours) |
| Data Storage | Pandas, Pickle |
| Image Hosting | Hugging Face Datasets |
| Version Control | Git, GitHub, Git LFS |

---

## Dataset
- **44,424** fashion products across apparel, footwear, accessories and personal care
- Enhanced with price, discounted price, available sizes, age group and product descriptions
- Product images hosted on Hugging Face (657 MB)
- Feature vectors stored in an Annoy index (`fashion_vector_index.ann`, 168 MB via Git LFS)

---

## Project Structure
├── app.py                      # Streamlit application
├── engine.py                   # Search and filtering logic
├── utils.py                    # Data loading and helper functions
├── processed_inventory.pkl     # Enhanced product dataframe
├── fashion_vector_index.ann    # Annoy vector index (Git LFS)
├── index.html                  # GitHub Pages landing page
├── outfits.json                # Pre-generated outfit combinations
├── requirements.txt            # Python dependencies
└── runtime.txt                 # Python version specification

---

## Setup & Deployment

### Local Development
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Streamlit Cloud
The app is deployed on Streamlit Cloud connected to this repository.
The `.ann` file is managed via **Git LFS** and loaded at runtime.

### GitHub Pages
The landing page (`index.html`) is served via GitHub Pages from the root of the 
repository and links directly to the Streamlit app.

---

## Live Links
- **Landing Page:** https://christ00098.github.io/Advanced-AI-Powered-Fashion-Personalized-Recommendation-System/
- **Streamlit App:** https://advanced-ai-powered-fashion-personalized-recommendation-system.streamlit.app/

---

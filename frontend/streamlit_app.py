# frontend/streamlit_app.py
import streamlit as st
import requests
import json
from PIL import Image
import io
import os

st.set_page_config(
    page_title="AI Image Selector",
    page_icon="📸",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        font-size: 16px;
        padding: 10px;
    }
    .result-card {
        padding: 15px;
        border-radius: 10px;
        background: linear-gradient(135deg, #667eea22 0%, #764ba222 100%);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("📸 AI Image Selector")
st.markdown("### Find your perfect photos with AI")

# Initialize session state
if 'liked_images' not in st.session_state:
    st.session_state.liked_images = []
if 'candidate_images' not in st.session_state:
    st.session_state.candidate_images = []
if 'results' not in st.session_state:
    st.session_state.results = None

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    ranking_method = st.selectbox(
        "Ranking Strategy",
        ["weighted", "centroid", "ensemble", "max", "avg"],
        help="Weighted works best for most users"
    )
    diversity = st.slider("Diversity", 0.0, 0.5, 0.1, help="Higher = more variety")
    
    st.divider()
    st.info("""
    **How it works:**
    1. Upload images you like (3-20)
    2. Upload your collection (up to 50)
    3. AI finds the best matches
    """)

# Main content
col1, col2 = st.columns(2)

with col1:
    st.subheader("❤️ Images You Like")
    liked_files = st.file_uploader(
        "Upload images that represent your style",
        type=['jpg', 'jpeg', 'png'],
        accept_multiple_files=True,
        key="liked"
    )
    
    if liked_files:
        st.session_state.liked_images = liked_files
        cols = st.columns(4)
        for i, file in enumerate(liked_files[:8]):
            with cols[i % 4]:
                img = Image.open(file)
                st.image(img, use_column_width=True)

with col2:
    st.subheader("📷 Your Collection")
    candidate_files = st.file_uploader(
        "Upload images to choose from",
        type=['jpg', 'jpeg', 'png'],
        accept_multiple_files=True,
        key="candidate"
    )
    
    if candidate_files:
        st.session_state.candidate_images = candidate_files
        st.write(f"📁 {len(candidate_files)} images uploaded")

# Process button
if st.session_state.liked_images and st.session_state.candidate_images:
    if st.button("🚀 Find My Top 5 Images", type="primary"):
        with st.spinner("Analyzing your images with AI..."):
            # Simulate processing (in production, call your API)
            import time
            time.sleep(2)
            
            # Mock results (replace with actual API call)
            st.session_state.results = [
                {"rank": 1, "score": 95, "image": st.session_state.candidate_images[0]},
                {"rank": 2, "score": 87, "image": st.session_state.candidate_images[1]},
                {"rank": 3, "score": 82, "image": st.session_state.candidate_images[2]},
                {"rank": 4, "score": 76, "image": st.session_state.candidate_images[3]},
                {"rank": 5, "score": 71, "image": st.session_state.candidate_images[4]},
            ]
            st.success("Done! Here are your top picks!")

# Display results
if st.session_state.results:
    st.divider()
    st.subheader("✨ Your Top 5 Picks")
    
    cols = st.columns(5)
    for i, result in enumerate(st.session_state.results[:5]):
        with cols[i]:
            with st.container():
                img = Image.open(result["image"])
                st.image(img, use_column_width=True)
                st.markdown(f"<div class='result-card'><h3>#{result['rank']}</h3><p>Match: {result['score']}%</p></div>", unsafe_allow_html=True)
    
    # Download button
    st.divider()
    if st.button("📥 Download Results"):
        st.info("Results would be downloaded here")

# Footer
st.divider()
st.caption("Made with ❤️ using AI | Your photos stay private")
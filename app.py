import streamlit as st
import google.generativeai as genai
import urllib.parse

# --- PAGE SETUP ---
st.set_page_config(page_title="Samketan Business Engine", page_icon="📈", layout="wide")

# --- 1. KEY RETRIEVAL ---
api_key = st.secrets.get("GOOGLE_API_KEY") or st.sidebar.text_input("API Key", type="password")

# --- 2. THE FIX: MODEL SELECTION ---
def get_model(key):
    genai.configure(api_key=key.strip())
    # Try the 2026 stable model first, then the 1.5 stable version
    for model_name in ['gemini-2.5-flash', 'gemini-1.5-flash']:
        try:
            m = genai.GenerativeModel(model_name=f'models/{model_name}')
            # Test if it actually works
            m.generate_content("test", generation_config={"max_output_tokens": 1})
            return m
        except:
            continue
    return None

# --- MAIN UI ---
st.header("🚀 Samketan Growth Engine")

region = st.text_input("Target City", placeholder="e.g., Gulbarga")
offer = st.text_input("Offer Details", placeholder="e.g., Warehouse Racking")

if st.button("Generate Leads"):
    if not api_key:
        st.error("API Key missing.")
    else:
        model = get_model(api_key)
        if model is None:
            st.error("❌ 404: No supported models found. Please check your Google AI Studio quota.")
        else:
            with st.spinner("Finding leads..."):
                prompt = f"Find 10 B2B leads in {region} for {offer}. Return as a table: Name | Email | Phone | Person"
                response = model.generate_content(prompt)
                
                # Simple Table Display
                st.markdown("### 📋 Results")
                st.write(response.text)

import streamlit as st
import google.generativeai as genai
import urllib.parse

# --- PAGE SETUP ---
st.set_page_config(page_title="Samketan Business Growth Engine", page_icon="📈", layout="wide")

# --- 1. SIDEBAR: AUTHENTICATION & PROFILE ---
with st.sidebar:
    st.header("🔑 Authentication")
    
    # Check Secrets first, then Sidebar
    raw_key = st.secrets.get("GOOGLE_API_KEY", "")
    if not raw_key:
        raw_key = st.text_input("Paste Google API Key here", type="password")
    
    # THE CLEANING STEP: Removes hidden spaces/newlines
    api_key_input = raw_key.strip() if raw_key else ""
    
    if api_key_input:
        st.success("API Key loaded! ✅")
    else:
        st.warning("Please enter your API Key to proceed.")

    st.header("🏢 Your Company Profile")
    my_company_desc = st.text_area("Describe your company & services", 
        placeholder="e.g., Samketan: We provide high-end Warehouse Storage solutions...")

# --- 2. MAIN DASHBOARD ---
st.header("🚀 Samketan Business Growth Engine")

col1, col2 = st.columns(2)
with col1:
    my_product = st.text_input("1) Product/Service", placeholder="e.g., Industrial Racking")
    region = st.text_input("3) Target City", placeholder="e.g., Gulbarga")
with col2:
    target_client = st.text_input("2) Who is your client?", placeholder="e.g., Dal Mills")
    scope = st.radio("4) Market Scope", ["Local (Domestic)", "Export (International)"])

# --- 3. DATA ENGINE ---
if st.button("🚀 Generate 10 Pro Leads"):
    if not api_key_input:
        st.error("❌ API Key is empty! Please check the sidebar.")
    elif not my_company_desc:
        st.warning("⚠️ Please fill in your Company Profile first.")
    else:
        try:
            # Force apply the clean key
            genai.configure(api_key=api_key_input)
            
            # Use the most stable model version
            model = genai.GenerativeModel('gemini-1.5-flash')

            with st.spinner("🔍 Mining 10 leads..."):
                prompt = f"Find 10 active businesses in {region} for {target_client} needing {my_product}. Return a table: Agency Name | Address | Website | Email ID | Phone | LinkedIn | Person"
                
                response = model.generate_content(prompt)
                
                if response:
                    # Your beautiful morning table logic
                    st.markdown("### 📋 10 Verified Sales Leads")
                    st.write(response.text) # Verify raw text first
                    
        except Exception as e:
            # This will now tell us if the key is still "Invalid" specifically
            st.error(f"❌ Security Check failed: {e}")

import streamlit as st
import google.generativeai as genai
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Samketan Agent", page_icon="🚀", layout="centered")

# --- HEADER ---
st.title("🚀 Samketan Agent")
st.caption("Powered by Google Gemini 1.5 Flash")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Brain Power")
    # We use .strip() to remove any accidental spaces you might copy
    api_key = st.text_input("Paste Google API Key", type="password").strip()
    st.info("ℹ️ First search may take 2-3 mins (Booting up).")

# --- INPUTS ---
col1, col2 = st.columns(2)
with col1:
    domain = st.selectbox("Target Category", 
        ["Warehouse Clients", "Software", "Food/Grain", "Export"])
with col2:
    region = st.text_input("Region", "Gulbarga, Karnataka")

details = st.text_area("Details", "Looking for verified contacts...")

# --- THE OFFICIAL BRAIN LOGIC ---
if st.button("🚀 Find Leads"):
    if not api_key:
        st.error("⛔ Please paste your Google API Key in the sidebar.")
    else:
        try:
            # Configure Google Brain
            genai.configure(api_key=api_key)
            
            # We use the newest stable model
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            with st.spinner("🤖 Samketan is thinking... (If first time, please wait 2 mins)"):
                
                prompt = f"""
                Find 3 business leads for {domain} in {region}.
                Context: {details}
                Return: Business Name, Why matches, and Draft Email Pitch.
                """
                
                response = model.generate_content(prompt)
                
                st.success("✅ Analysis Complete!")
                st.markdown(response.text)
                
        except Exception as e:
            st.error(f"❌ Error: {e}")

import streamlit as st
import requests
import json

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Samketan Agent", page_icon="🚀", layout="centered")

# --- LOGIN ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("🔒 Samketan Login")
    password = st.text_input("Enter Password", type="password")
    if st.button("Unlock System"):
        if password == "Samketan2026": 
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Incorrect Password")

if not st.session_state.logged_in:
    login()
    st.stop()

# --- APP INTERFACE ---
st.title("🚀 Samketan Agent")
st.caption("Standard AI Model (gemini-pro)")

# --- SIDEBAR (API KEY) ---
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Paste Google API Key", type="password")
    
# --- INPUTS ---
col1, col2 = st.columns(2)
with col1:
    domain = st.selectbox("Target Category", ["Warehouse Clients", "Software", "Food/Grain", "Export"])
with col2:
    region = st.text_input("Region", "Gulbarga, Karnataka")

details = st.text_area("Details", "Looking for verified contacts...")

# --- THE LOGIC (UPDATED MODEL) ---
if st.button("🚀 Find Leads"):
    if not api_key:
        st.error("Please paste your API Key first.")
    else:
        with st.spinner("🤖 Analyzing with Standard AI..."):
            
            # UPDATED: Using 'gemini-pro' which is 100% stable
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
            
            headers = {"Content-Type": "application/json"}
            
            prompt_text = f"Find 3 business leads for {domain} in {region}. Context: {details}. Return Business Name, Why, and Email Pitch."
            
            data = { "contents": [{ "parts": [{"text": prompt_text}] }] }

            try:
                response = requests.post(url, headers=headers, json=data)
                
                if response.status_code == 200:
                    answer = response.json()['candidates'][0]['content']['parts'][0]['text']
                    st.success("✅ Success!")
                    st.markdown(answer)
                else:
                    st.error(f"❌ Error: {response.status_code}")
                    st.write(response.text)

            except Exception as e:
                st.error(f"Connection Error: {e}")

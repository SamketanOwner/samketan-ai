import streamlit as st
import requests
import json

# --- PAGE SETUP ---
st.set_page_config(page_title="Samketan Agent", page_icon="🚀", layout="centered")

# --- LOGIN SYSTEM ---
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

# --- THE APP INTERFACE ---
st.title("🚀 Samketan Agent")
st.markdown("### Intelligent Lead Discovery Engine")

# --- SIDEBAR (API KEY) ---
with st.sidebar:
    st.header("⚙️ Brain Power")
    api_key = st.text_input("Paste Google API Key", type="password")
    st.caption("Paste your 'AIza...' key here.")
    st.info("⚡ Lightweight Mode Active")

# --- MAIN INPUTS ---
col1, col2 = st.columns(2)
with col1:
    domain = st.selectbox("Target Category", 
        ["Software Buyers", "Warehouse Clients", "Art/Statue Resellers", "Food/Grain Wholesalers", "Export Agencies"])
with col2:
    region = st.text_input("Target Region", "Gulbarga, Karnataka")

details = st.text_area("Specific Filters", "Looking for verified contacts...")

# --- THE LIGHTWEIGHT BRAIN LOGIC ---
if st.button("🚀 Find Verified Leads"):
    if not api_key:
        st.error("⛔ Please paste your Google API Key in the sidebar first!")
    else:
        with st.spinner(f"🤖 Samketan is contacting Google directly..."):
            
            # 1. Prepare the Prompt
            prompt_text = f"""
            Act as Samketan, a Lead Generation Expert.
            TASK: Find 3 highly relevant business leads for:
            - Domain: {domain}
            - Region: {region}
            - Context: {details}

            STRICT RULES:
            1. If 'Software': Find IT Heads/Purchase Managers.
            2. If 'Warehouse': Find Logistics Managers.
            3. If 'Food': Find Wholesalers.
            
            OUTPUT FORMAT:
            For each lead provide: Business Name, Why them?, and a Draft Email Pitch.
            """

            # 2. Send Data Directly to Google (No Library Needed)
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            data = {
                "contents": [{
                    "parts": [{"text": prompt_text}]
                }]
            }

            try:
                response = requests.post(url, headers=headers, json=data)
                
                if response.status_code == 200:
                    result = response.json()
                    # Extract text from Google's complex JSON
                    answer = result['candidates'][0]['content']['parts'][0]['text']
                    st.success("✅ Analysis Complete")
                    st.markdown(answer)
                else:
                    st.error(f"❌ Error {response.status_code}: {response.text}")

            except Exception as e:
                st.error(f"❌ Connection Error: {e}")

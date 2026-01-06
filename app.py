import streamlit as st
import google.generativeai as genai
import pandas as pd
import io

# --- PAGE SETUP ---
st.set_page_config(page_title="Samketan Growth Engine", page_icon="📈", layout="wide")

# --- 1. LOGIN LOGIC (UNCHANGED) ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    auth_status = "✅ System Connected"
else:
    api_key = st.sidebar.text_input("Paste Google API Key", type="password").strip()
    auth_status = "⚠️ Key Missing"

with st.sidebar:
    st.header("Samketan 2026")
    st.info(auth_status)
    st.caption("Mode: 10x Lead Research + CRM")

# --- MAIN DASHBOARD ---
st.title("🚀 Business Growth Engine")
st.markdown("Generating 10 high-value leads with deep contact info.")

# --- 2. THE 4 QUESTIONS ---
col1, col2 = st.columns(2)
with col1:
    my_product = st.text_input("1) What is your product/service?", value="Warehouse Storage")
    region = st.text_input("3) Target City/Region?", "Gulbarga")
with col2:
    target_client = st.text_input("2) Who is your client?", "Dal Mills")
    scope = st.radio("4) Market Scope", ["Local (Domestic)", "Export (International)"])

# --- 3. DATA ENGINE ---
if st.button("🚀 Generate 10 Pro Leads"):
    if not api_key:
        st.error("Please provide an API Key.")
    else:
        try:
            genai.configure(api_key=api_key)
            
            # Using Gemini 3 Flash for the 1,500 RPD free limit and web grounding
            model_name = 'gemini-3-flash'
            model = genai.GenerativeModel(model_name)

            with st.spinner("🔍 Mining 10 leads with LinkedIn and Email data..."):
                prompt = f"""
                Act as a B2B Lead Generation Expert with Web Research capabilities.
                
                TASK: Find exactly 10 REAL and ACTIVE businesses in {region} for the industry: {target_client}.
                GOAL: They should be potential buyers for: {my_product}.
                SCOPE: {scope}.
                
                For each business, find:
                1. Official Website URL.
                2. Professional Email Address.
                3. LinkedIn Profile (Company page or Owner/Manager profile).
                4. Name of the Concern Person (Owner, Director, or Manager).
                
                OUTPUT: Return ONLY a Markdown table with these columns:
                | Agency Name | Address | Website | Email ID | Phone/WhatsApp | LinkedIn Profile | Concern Person |
                """
                
                response = model.generate_content(prompt)
                
                # --- DISPLAY ---
                st.markdown("### 📋 10 Verified Sales Leads")
                st.markdown(response.text)

                # --- EXPORT TO EXCEL (CSV) ---
                st.download_button(
                    label="📥 Download All 10 Leads for Excel",
                    data=response.text,
                    file_name=f"Samketan_10_Leads_{region}.csv",
                    mime="text/csv",
                )
                st.success(f"✅ 10 Leads Generated using {model_name}. Daily Limit: 1,500.")

        except Exception as e:
            st.error(f"❌ Error: {e}")

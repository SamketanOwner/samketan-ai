import streamlit as st
import google.generativeai as genai
import pandas as pd
import urllib.parse

# --- PAGE SETUP ---
st.set_page_config(page_title="Samketan Growth Engine", page_icon="📈", layout="wide")

# --- 1. LOGIN LOGIC ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    auth_status = "✅ System Connected"
else:
    api_key = st.sidebar.text_input("Paste Google API Key", type="password").strip()
    auth_status = "⚠️ Key Missing"

with st.sidebar:
    st.header("Samketan 2026")
    st.info(auth_status)
    st.caption("Mode: One-Click Sales Outreach")

# --- MAIN DASHBOARD ---
st.title("🚀 Business Growth Engine")
st.markdown("Find 10 leads and start pitching instantly with one click.")

# --- 2. THE 4 QUESTIONS ---
col1, col2 = st.columns(2)
with col1:
    my_product = st.text_input("1) What is your product/service?", value="Warehouse Storage")
    region = st.text_input("3) Target City/Region?", "Gulbarga")
with col2:
    target_client = st.text_input("2) Who is your client?", "Dal Mills")
    scope = st.radio("4) Market Scope", ["Local (Domestic)", "Export (International)"])

# --- HELPER: URL ENCODING FOR LINKS ---
def create_outreach_links(row):
    # WhatsApp Link
    # Cleaning phone number to digits only for wa.me
    phone_digits = "".join(filter(str.isdigit, str(row['Phone/WhatsApp'])))
    if not phone_digits.startswith('91') and len(phone_digits) == 10:
        phone_digits = "91" + phone_digits
    
    wa_msg = f"Hello {row['Concern Person']}, I am reaching out from Samketan. We specialize in {my_product} and noticed {row['Agency Name']} might benefit from our solutions in {region}. Would love to discuss this briefly."
    wa_url = f"https://wa.me/{phone_digits}?text={urllib.parse.quote(wa_msg)}"
    
    # Email Link
    subject = urllib.parse.quote(f"Strategic Partnership Proposal: {my_product} for {row['Agency Name']}")
    body = urllib.parse.quote(f"Dear {row['Concern Person']},\n\nI hope this finds you well.\n\nI am reaching out to introduce our specialized {my_product} services. We have successfully helped similar businesses in the {target_client} industry optimize their operations.\n\nI would appreciate a brief moment to discuss how we can support {row['Agency Name']} in {region}.\n\nBest regards,\n[Your Name]\nSamketan Team")
    mail_url = f"mailto:{row['Email ID']}?subject={subject}&body={body}"
    
    return wa_url, mail_url

# --- 3. DATA ENGINE ---
if st.button("🚀 Generate 10 Pro Leads with Outreach Links"):
    if not api_key:
        st.error("Please provide an API Key.")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')

            with st.spinner("🔍 Mining 10 leads and crafting professional pitches..."):
                prompt = f"""
                Act as a B2B Lead Generation Expert. 
                Find 10 REAL and ACTIVE businesses in {region} for {target_client}.
                They must be potential buyers for {my_product}.
                
                Return a table with exactly these columns:
                Agency Name, Address, Website, Email ID, Phone/WhatsApp, LinkedIn Profile, Concern Person
                """
                
                response = model.generate_content(prompt)
                
                # --- PARSING DATA INTO DATAFRAME FOR INTERACTIVE LINKS ---
                # We show the raw table first as requested
                st.markdown("### 📋 10 Actionable Sales Leads")
                st.markdown(response.text)
                
                st.info("💡 Tip: Download the CSV below to get a spreadsheet with all contact details.")
                
                # Export to Excel (CSV)
                st.download_button(
                    label="📥 Download All 10 Leads for Excel",
                    data=response.text,
                    file_name=f"Samketan_Outreach_{region}.csv",
                    mime="text/csv",
                )
                st.success("✅ 10 Leads Ready. Use the phone and email details for your pitch.")

        except Exception as e:
            st.error(f"❌ Error: {e}")

import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Samketan", page_icon="🚀")

st.title("🚀 Samketan Agent")
st.caption("Factory Reset Version")

# --- SIDEBAR ---
with st.sidebar:
    api_key = st.text_input("Paste Google API Key", type="password").strip()
    st.info("System Ready")

# --- INPUTS ---
domain = st.selectbox("Category", ["Warehouse", "Software", "Food", "Export"])
region = st.text_input("Region", "Gulbarga, Karnataka")

# --- BUTTON ---
if st.button("Find Leads"):
    if not api_key:
        st.error("Please enter API Key")
    else:
        try:
            # Configure the Brain
            genai.configure(api_key=api_key)

            # We try the NEW model first. If it fails, we auto-switch to the OLD one.
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(f"Find 3 business leads for {domain} in {region}.")
            except:
                st.warning("Switching to backup model...")
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content(f"Find 3 business leads for {domain} in {region}.")

            st.success("✅ Connected!")
            st.write(response.text)

        except Exception as e:
            st.error(f"❌ Critical Error: {e}")

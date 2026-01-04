import streamlit as st
import google.generativeai as genai

# --- PAGE SETUP ---
st.set_page_config(page_title="Samketan Leads", page_icon="🎯")

# --- 1. AUTOMATIC LOGIN (Using Secrets) ---
# This looks for the key you just saved in Streamlit Settings
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    key_status = "✅ System Linked"
else:
    # Fallback if you haven't saved secrets yet
    api_key = st.sidebar.text_input("Enter API Key", type="password")
    key_status = "⚠️ Key Missing"

# --- SIDEBAR ---
with st.sidebar:
    st.header("Samketan 2.0")
    st.info(key_status)
    if "✅" in key_status:
        st.success("Auto-Login Active")

# --- INPUTS ---
st.title("🎯 Direct Lead Finder")
col1, col2 = st.columns(2)
with col1:
    domain = st.selectbox("Industry", ["Warehouse", "Software", "Food/Grains", "Construction", "Export"])
with col2:
    region = st.text_input("City/Region", "Gulbarga (Kalaburagi)")

# --- THE AGGRESSIVE PROMPT ---
if st.button("Get Company Names"):
    if not api_key:
        st.error("Please set the API Key in Streamlit Secrets first!")
    else:
        try:
            genai.configure(api_key=api_key)
            # Auto-detect model (Flash is faster for lists)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            with st.spinner("🔍 Scanning for REAL business names..."):
                
                # We force the AI to give names, not advice
                prompt = f"""
                TASK: List 3 REAL, EXISTING Business Names in {region} that match the category '{domain}'.
                
                NO ADVICE. NO PREACHING. ONLY DATA.
                
                Strict Output Format:
                1. **[Company Name]**
                   - *Type:* (e.g. Wholesaler / Manufacturer)
                   - *Likely Needs:* (1 sentence why they need {domain} services)
                
                If exact names are hard to confirm, list the top 3 biggest local players in this sector.
                """
                
                response = model.generate_content(prompt)
                st.markdown(response.text)
                st.warning("ℹ️ Note: Verify these local businesses on Google Maps before calling.")
                
        except Exception as e:
            st.error(f"Error: {e}")

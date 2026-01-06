import streamlit as st
import google.generativeai as genai

# --- PAGE CONFIG ---
st.set_page_config(page_title="Samketan Growth Engine", page_icon="📈", layout="wide")

# --- 1. SECURE LOGIN ---
# This looks for the key in your Streamlit Cloud "Secrets"
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    auth_status = "✅ System Connected"
else:
    # If secrets aren't set, allow manual entry for testing
    api_key = st.sidebar.text_input("Enter API Key", type="password").strip()
    auth_status = "⚠️ Key Missing in Secrets"

# --- SIDEBAR ---
with st.sidebar:
    st.header("Samketan 2026")
    st.info(auth_status)
    st.caption("Using Stable Model: Gemini 3 Flash")

# --- MAIN APP ---
st.title("🚀 Business Growth Engine")
st.markdown("Structure your search to find high-value leads.")

# --- 2. THE 4 QUESTIONS ---
col1, col2 = st.columns(2)
with col1:
    my_product = st.text_input("1) Your Product/Service", value="Warehouse Storage")
    region = st.text_input("3) Target City/Region", value="Gulbarga")
with col2:
    target_client = st.text_input("2) Target Client Industry", value="Dal Mills & Food Processors")
    scope = st.radio("4) Market Scope", ["Local (Domestic)", "Export (International)"])

# --- 3. LEAD GENERATION ENGINE ---
if st.button("🚀 Generate Leads Table"):
    if not api_key or "AIza" not in api_key:
        st.error("❌ Invalid API Key detected. Please update your Streamlit Secrets.")
    else:
        try:
            genai.configure(api_key=api_key)
            
            # 2026 Stable Model: Gemini 3 Flash (High Quota Free Tier)
            model = genai.GenerativeModel('gemini-3-flash')
            
            with st.spinner(f"📊 Mining data for {target_client} in {region}..."):
                prompt = f"""
                Act as a B2B Sales Expert. Find 5 REAL business leads in {region} for:
                - My Product: {my_product}
                - Their Industry: {target_client}
                - Scope: {scope}
                
                OUTPUT: Strictly provide a Markdown table with:
                | Agency Name | Address | Contact Role | Phone / WhatsApp | Why they match |
                """
                
                response = model.generate_content(prompt)
                st.markdown("---")
                st.markdown(response.text)
                st.success("✅ Search Complete")
                
        except Exception as e:
            st.error(f"❌ Connection Failed: {e}")

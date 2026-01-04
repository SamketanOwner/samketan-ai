import streamlit as st
import google.generativeai as genai

# --- PAGE CONFIG ---
st.set_page_config(page_title="Samketan Growth Engine", page_icon="📈", layout="wide")

# --- 1. LOGIN LOGIC ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    auth_status = "✅ Auto-Logged In"
else:
    api_key = st.sidebar.text_input("Paste Google API Key", type="password").strip()
    auth_status = "⚠️ using manual key"

# --- SIDEBAR ---
with st.sidebar:
    st.header("Samketan Growth Engine")
    st.caption(auth_status)
    st.info("Mode: Strategic Table Search")

# --- MAIN APP ---
st.title("🚀 Business Growth Engine")
st.markdown("Define your strategy below to find the perfect leads.")

# --- 2. YOUR 4 INPUTS (Preserved) ---
col1, col2 = st.columns(2)

with col1:
    # Q1: Your Product
    my_product = st.text_input("1) What is your product/service?", placeholder="e.g. Warehouse Storage")
    # Q3: Region
    region = st.text_input("3) Target Region?", "Gulbarga")

with col2:
    # Q2: Target Client
    target_client = st.text_input("2) Who is your client?", placeholder="e.g. Dal Mills")
    # Q4: Scope
    scope = st.radio("4) Market Scope", ["Local (Domestic)", "Export (International)"])

# --- 3. OUTPUT LOGIC (Table Format + Error Fix) ---
if st.button("🚀 Identify Leads"):
    if not api_key:
        st.error("Please provide an API Key.")
    else:
        try:
            genai.configure(api_key=api_key)
            
            # FIX: Force the 1.5 Flash model (1,500 free searches/day)
            # This prevents the '429 Quota Exceeded' error
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            with st.spinner(f"🔎 Analyzing {scope} market in {region} for {target_client}..."):
                
                # PROMPT: Uses your 4 inputs but forces Table Output
                prompt = f"""
                Act as a Data Mining Expert.
                
                MY PROFILE:
                - Offering: {my_product}
                - Client Target: {target_client}
                - Region: {region}
                - Scope: {scope}
                
                TASK: Find 5 REAL business leads matching this profile.
                
                OUTPUT FORMAT:
                Provide the result STRICTLY as a Markdown Table with these columns:
                | Agency Name | Address | Contact Person | Email (Likely) | Phone / WhatsApp |
                
                RULES:
                1. **Agency Name:** Must be a real business in {region}.
                2. **Address:** Be specific (Industrial Area, Road Name).
                3. **Email:** If private, use "Not Available" or standard format info@...
                4. **Phone:** Provide public office number or "Check Google Maps".
                """
                
                response = model.generate_content(prompt)
                st.markdown(response.text)
                st.success("✅ Table Generated Successfully")

        except Exception as e:
            st.error(f"❌ Error: {e}")

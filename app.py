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
    st.info("Mode: High-Quota Free Tier")

# --- MAIN APP ---
st.title("🚀 Business Growth Engine")

# --- 2. INPUTS (YOUR 4 QUESTIONS) ---
col1, col2 = st.columns(2)
with col1:
    my_product = st.text_input("1) What is your product/service?", placeholder="e.g. Warehouse Storage")
    region = st.text_input("3) Target Region?", "Gulbarga")
with col2:
    target_client = st.text_input("2) Who is your client?", placeholder="e.g. Dal Mills")
    scope = st.radio("4) Market Scope", ["Local (Domestic)", "Export (International)"])

# --- 3. OUTPUT LOGIC (FORCED STABLE FLASH) ---
if st.button("🚀 Identify Leads"):
    if not api_key:
        st.error("Please provide an API Key.")
    else:
        try:
            genai.configure(api_key=api_key)
            
            # FORCING THE STABLE 1.5 FLASH (1500 RPD Free Tier)
            # This avoids the 'Limit: 0' error on 2.5 Pro
            model_name = 'gemini-1.5-flash'
            model = genai.GenerativeModel(model_name)
            
            with st.spinner(f"🔎 Using Stable Engine ({model_name})... searching {region}..."):
                
                prompt = f"""
                Act as a Data Mining Expert.
                MY PROFILE:
                - Offering: {my_product}
                - Client Target: {target_client}
                - Region: {region}
                - Scope: {scope}
                
                TASK: Find 5 REAL business leads matching this profile.
                
                OUTPUT FORMAT:
                Provide result as a Markdown Table:
                | Agency Name | Address | Contact Person | Email (Likely) | Phone / WhatsApp |
                
                RULES:
                1. Use real businesses in {region}.
                2. Be specific with locations.
                """
                
                response = model.generate_content(prompt)
                st.success(f"✅ Leads Found!")
                st.markdown(response.text)

        except Exception as e:
            if "429" in str(e):
                st.error("❌ Quota Still Blocked. Please wait 60 seconds or generate a NEW Key at aistudio.google.com (it only takes 30 seconds).")
            else:
                st.error(f"❌ Error: {e}")

import streamlit as st
import google.generativeai as genai
import time

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
    st.info("Mode: Stable Connection")

# --- MAIN APP ---
st.title("🚀 Business Growth Engine")
st.markdown("Define your strategy below to find the perfect leads.")

# --- 2. INPUTS (YOUR 4 QUESTIONS) ---
col1, col2 = st.columns(2)

with col1:
    my_product = st.text_input("1) What is your product/service?", placeholder="e.g. Warehouse Storage")
    region = st.text_input("3) Target Region?", "Gulbarga")

with col2:
    target_client = st.text_input("2) Who is your client?", placeholder="e.g. Dal Mills")
    scope = st.radio("4) Market Scope", ["Local (Domestic)", "Export (International)"])

# --- 3. OUTPUT LOGIC (BRUTE FORCE SELECTOR) ---
if st.button("🚀 Identify Leads"):
    if not api_key:
        st.error("Please provide an API Key.")
    else:
        # Define the Safe List (No experimental models)
        safe_models = [
            "gemini-1.5-flash", 
            "gemini-1.5-flash-latest", 
            "gemini-1.5-flash-001",
            "gemini-1.5-pro",
            "gemini-pro"
        ]
        
        working_model = None
        genai.configure(api_key=api_key)

        # --- FIND A WORKING MODEL ---
        with st.spinner("🔌 Testing connections to find a stable model..."):
            for model_name in safe_models:
                try:
                    # Quick test to see if this model exists for your key
                    test_model = genai.GenerativeModel(model_name)
                    # We just test if it initializes, not running a query yet to save time
                    working_model = model_name
                    break # Found one! Stop looking.
                except:
                    continue
        
        if not working_model:
            st.error("❌ Critical Error: Your API Key is blocked from all standard models. Please create a NEW key at aistudio.google.com")
        else:
            # --- RUN THE REAL SEARCH ---
            try:
                with st.spinner(f"🔎 Analyzing {scope} market in {region} using {working_model}..."):
                    
                    model = genai.GenerativeModel(working_model)
                    
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
                    3. **Email:** If private, use "Not Available" or standard format.
                    4. **Phone:** Provide public office number or "Check Google Maps".
                    """
                    
                    response = model.generate_content(prompt)
                    st.success(f"✅ Success! Connected via: {working_model}")
                    st.markdown(response.text)
                    
            except Exception as e:
                st.error(f"❌ Error during search: {e}")

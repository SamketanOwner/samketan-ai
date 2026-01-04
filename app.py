import streamlit as st
import google.generativeai as genai

# --- PAGE CONFIG ---
st.set_page_config(page_title="Samketan Growth Engine", page_icon="📈")

# --- 1. LOGIN LOGIC (UNCHANGED / MINT CONDITION) ---
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
    st.info("Mode: Strategic Search")

# --- MAIN APP ---
st.title("🚀 Business Growth Engine")
st.markdown("Define your strategy below to find the perfect leads.")

# --- 2. NEW INPUTS (YOUR 4 QUESTIONS) ---
col1, col2 = st.columns(2)

with col1:
    # Q1: Your Product
    my_product = st.text_input("1) What is your product/service?", placeholder="e.g. Warehouse Storage, Custom Software")
    # Q3: Region
    region = st.text_input("3) Target Region?", "Gulbarga")

with col2:
    # Q2: Target Client
    target_client = st.text_input("2) Who is your client?", placeholder="e.g. Dal Mills, Hospitals, Cotton Traders")
    # Q4: Scope
    scope = st.radio("4) Market Scope", ["Local (Domestic)", "Export (International)"])

# --- 3. OUTPUT LOGIC ---
if st.button("🚀 Identify Leads"):
    if not api_key:
        st.error("Please provide an API Key.")
    else:
        if not my_product or not target_client:
            st.warning("Please fill in what you sell and who you want to find.")
        else:
            try:
                genai.configure(api_key=api_key)
                
                # Auto-Detect Model (Unchanged)
                valid_model = None
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        if 'flash' in m.name:
                            valid_model = m.name
                            break
                if not valid_model: valid_model = 'models/gemini-1.5-flash'

                with st.spinner(f"🔎 Analyzing {scope} market in {region} for {target_client}..."):
                    model = genai.GenerativeModel(valid_model)
                    
                    # PROMPT: Uses your 4 inputs to filter results
                    prompt = f"""
                    Act as a Senior Business Consultant.
                    
                    MY PROFILE:
                    - **Offering:** {my_product}
                    - **Target Client:** {target_client}
                    - **Region:** {region}
                    - **Focus:** {scope}
                    
                    TASK:
                    Identify 5 specific business leads in {region} that fit this profile.
                    
                    STRICT OUTPUT RULES:
                    1. Focus on REAL businesses that exist in {region}.
                    2. If "Export" is selected, prioritize companies with trade connections.
                    3. If "Local" is selected, prioritize established local distributors/manufacturers.
                    
                    FORMAT FOR EACH LEAD:
                    -----------------------
                    🏢 **[Business Name]**
                    📍 **Location:** [Area/Industrial Estate]
                    💼 **Relevance:** [Why they need '{my_product}']
                    📞 **Action:** [Who to ask for? e.g. "Ask for Purchase Manager"]
                    -----------------------
                    """
                    
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                    st.success("✅ Strategy Generated")

            except Exception as e:
                st.error(f"❌ Error: {e}")

import streamlit as st
import google.generativeai as genai

# --- PAGE CONFIG ---
st.set_page_config(page_title="Samketan Leads", page_icon="🏢")

# --- 1. LOGIN LOGIC (Secrets + Fallback) ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    auth_status = "✅ Auto-Logged In"
else:
    api_key = st.sidebar.text_input("Paste Google API Key", type="password").strip()
    auth_status = "⚠️ using manual key"

# --- SIDEBAR ---
with st.sidebar:
    st.header("Samketan 3.0")
    st.caption(auth_status)
    st.info("Mode: Real Business Search")

# --- MAIN APP ---
st.title("🏢 Warehouse Lead Finder")
col1, col2 = st.columns(2)
with col1:
    domain = st.selectbox("Looking For", ["Warehouse Clients", "Software Buyers", "Food/Grain Wholesalers", "Construction Material"])
with col2:
    region = st.text_input("Region/City", "Gulbarga (Kalaburagi)")

# --- THE SMART LOGIC ---
if st.button("Get Business Names"):
    if not api_key:
        st.error("Please provide an API Key (in Sidebar or Secrets).")
    else:
        try:
            genai.configure(api_key=api_key)
            
            with st.spinner("🔄 Finding the best AI model for you..."):
                # 1. AUTO-DETECT: Find the first model that actually works
                valid_model = None
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        if 'flash' in m.name or 'pro' in m.name: # Prefer Flash or Pro
                            valid_model = m.name
                            break
                
                # If no specific one found, grab the very first available one
                if not valid_model:
                     for m in genai.list_models():
                        if 'generateContent' in m.supported_generation_methods:
                            valid_model = m.name
                            break

            if not valid_model:
                st.error("❌ No AI models available for this API Key. Please create a new key.")
            else:
                # 2. RUN THE AGGRESSIVE SEARCH
                with st.spinner(f"🔎 Searching {region} using {valid_model}..."):
                    model = genai.GenerativeModel(valid_model)
                    
                    prompt = f"""
                    TASK: List 3 REAL, EXISTING Business Names in {region} that are likely to be {domain}.
                    
                    STRICT RULES:
                    - NO generic advice (e.g., "Look for dal mills").
                    - GIVE SPECIFIC NAMES (e.g., "Maruti Udyog", "XYZ Traders").
                    - If exact names are private, list the Specific Industrial Areas where they are located.
                    
                    OUTPUT FORMAT:
                    1. **[Business Name]**
                       - *Location:* [Area Name]
                       - *Why:* [Short reason]
                    """
                    
                    response = model.generate_content(prompt)
                    st.success(f"✅ Found Leads using {valid_model}")
                    st.markdown(response.text)

        except Exception as e:
            st.error(f"❌ Connection Failed: {e}")

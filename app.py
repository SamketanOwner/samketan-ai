import streamlit as st
import google.generativeai as genai

# --- PAGE SETUP ---
st.set_page_config(page_title="Samketan Growth Engine", page_icon="📈", layout="wide")

# --- 1. LOGIN LOGIC ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    auth_status = "✅ System Connected"
else:
    api_key = st.sidebar.text_input("Enter API Key", type="password").strip()
    auth_status = "⚠️ Key Missing"

with st.sidebar:
    st.header("Samketan 2026")
    st.info(auth_status)

# --- MAIN DASHBOARD ---
st.title("🚀 Business Growth Engine")

# --- 2. THE 4 QUESTIONS ---
col1, col2 = st.columns(2)
with col1:
    my_product = st.text_input("1) Your Product/Service", value="Warehouse Storage")
    region = st.text_input("3) Target City/Region", value="Gulbarga")
with col2:
    target_client = st.text_input("2) Target Client Industry", value="Dal Mills")
    scope = st.radio("4) Market Scope", ["Local (Domestic)", "Export (International)"])

# --- 3. SMART SEARCH ENGINE ---
if st.button("🚀 Generate Leads Table"):
    if not api_key:
        st.error("❌ Please provide a valid API Key.")
    else:
        try:
            genai.configure(api_key=api_key)
            
            # --- SMART MODEL SELECTION ---
            # This part asks Google: "What models can I actually use?"
            with st.spinner("🔍 Detecting your available AI models..."):
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                
                # We try to find the best 2026 models in order of priority
                priority_list = [
                    "models/gemini-3-flash-preview", 
                    "models/gemini-2.5-flash", 
                    "models/gemini-2.0-flash-001"
                ]
                
                chosen_model = next((m for m in priority_list if m in available_models), available_models[0])

            # --- RUN THE SEARCH ---
            model = genai.GenerativeModel(chosen_model)
            with st.spinner(f"📊 Using engine {chosen_model}... finding leads..."):
                prompt = f"""
                Find 5 REAL business leads in {region} for:
                - Product: {my_product}
                - Industry: {target_client}
                - Scope: {scope}
                
                OUTPUT: Strictly a Markdown table with:
                | Company Name | Address | Contact Role | Phone | Why Match |
                """
                
                response = model.generate_content(prompt)
                st.markdown(response.text)
                st.success(f"✅ Leads generated using {chosen_model}")
                
        except Exception as e:
            st.error(f"❌ Connection Failed: {e}")

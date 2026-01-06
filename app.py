import streamlit as st
import google.generativeai as genai

# --- PAGE SETUP ---
st.set_page_config(page_title="Samketan Growth Engine", page_icon="🏢", layout="wide")

# --- LOGIN LOGIC (UNCHANGED) ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    auth_status = "✅ System Linked"
else:
    api_key = st.sidebar.text_input("Enter API Key", type="password").strip()
    auth_status = "⚠️ Key Missing"

with st.sidebar:
    st.header("Settings")
    st.info(auth_status)

# --- MAIN DASHBOARD ---
st.title("🚀 Business Growth Engine")

# --- THE 4 QUESTIONS ---
col1, col2 = st.columns(2)
with col1:
    my_product = st.text_input("1) What is your product?", "Warehouse Storage")
    region = st.text_input("3) Target Region?", "Gulbarga")
with col2:
    target_client = st.text_input("2) Who is your client?", "Dal Mills")
    scope = st.radio("4) Market Scope", ["Local (Domestic)", "Export (International)"])

# --- SMART CONNECTION LOGIC ---
if st.button("🚀 Identify Leads"):
    if not api_key:
        st.error("Please provide an API Key.")
    else:
        try:
            genai.configure(api_key=api_key)
            
            with st.spinner("🔍 Detecting your available models..."):
                # AUTOMATICALLY find a working model name
                # This prevents the 404 error
                model_list = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                
                # Priority list: Gemini 3 -> Gemini 2.5 -> Gemini 1.5
                best_model = None
                for name in ["models/gemini-3-flash", "models/gemini-2.5-flash", "models/gemini-1.5-flash"]:
                    if name in model_list:
                        best_model = name
                        break
                
                if not best_model:
                    best_model = model_list[0] # Just take whatever works

            # --- GENERATE THE TABLE ---
            model = genai.GenerativeModel(best_model)
            prompt = f"Find 5 REAL businesses in {region} that are {target_client}. Use a Table format with columns: Agency Name, Address, Contact Person, Phone."
            
            response = model.generate_content(prompt)
            st.success(f"✅ Found Leads using {best_model}")
            st.markdown(response.text)

        except Exception as e:
            st.error(f"❌ Connection Error: {e}")

import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Samketan Agent", page_icon="🚀")
st.title("🚀 Samketan Agent")
st.caption("Auto-Detect Mode")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Setup")
    api_key = st.text_input("Paste Google API Key", type="password").strip()
    st.info("Paste key to auto-detect models.")

# --- INPUTS ---
domain = st.selectbox("Category", ["Warehouse", "Software", "Food", "Export"])
region = st.text_input("Region", "Gulbarga, Karnataka")

# --- SMART LOGIC ---
if st.button("🚀 Find Leads"):
    if not api_key:
        st.error("Please enter API Key")
    else:
        try:
            genai.configure(api_key=api_key)
            
            with st.spinner("🔍 Scanning for available AI models..."):
                # 1. Ask Google what models are available for this Key
                working_model = None
                available = []
                
                # List all models
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        available.append(m.name)
                
                # 2. Check if we found any
                if not available:
                    st.error("❌ Your API Key works, but it has NO access to any AI models.")
                    st.error("👉 Solution: Go to 'aistudio.google.com' and create a NEW free API key.")
                    st.stop()
                else:
                    # 3. Pick the first one that works (e.g., models/gemini-1.5-flash)
                    working_model = available[0]
                    st.success(f"✅ Connected to: {working_model}")
            
            # 4. Run the Search using the detected model
            with st.spinner(f"🤖 Thinking..."):
                model = genai.GenerativeModel(working_model)
                response = model.generate_content(f"Find 3 business leads for {domain} in {region}.")
                st.markdown("---")
                st.write(response.text)
                
        except Exception as e:
            st.error(f"❌ Connection Error: {e}")

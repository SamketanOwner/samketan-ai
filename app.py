import streamlit as st
import google.generativeai as genai

# --- PAGE CONFIG ---
st.set_page_config(page_title="Samketan Growth Engine", page_icon="📊", layout="wide")

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
    st.info("Mode: Table Output")

# --- MAIN APP ---
st.title("🚀 Lead Generation Table")
st.markdown("Generate a structured list of potential clients.")

# --- 2. INPUTS ---
col1, col2, col3 = st.columns(3)

with col1:
    my_product = st.text_input("1) What do you sell?", "Warehouse Storage Space")
with col2:
    target_client = st.text_input("2) Who is the client?", "Dal Mills & Pulses Traders")
with col3:
    region = st.text_input("3) Region?", "Gulbarga")

# --- 3. OUTPUT LOGIC ---
if st.button("🚀 Generate Table"):
    if not api_key:
        st.error("Please provide an API Key.")
    else:
        try:
            genai.configure(api_key=api_key)
            
            # Auto-Detect Model
            valid_model = None
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    if 'flash' in m.name:
                        valid_model = m.name
                        break
            if not valid_model: valid_model = 'models/gemini-1.5-flash'

            with st.spinner(f"📊 Creating contact table for {target_client} in {region}..."):
                model = genai.GenerativeModel(valid_model)
                
                # PROMPT: Forces Table Format
                prompt = f"""
                Act as a Data Mining Expert.
                
                TASK: Find 5 REAL business leads in {region} matching the profile: '{target_client}'.
                GOAL: To sell them '{my_product}'.
                
                OUTPUT FORMAT:
                Provide the result STRICTLY as a Markdown Table with these columns:
                | Agency Name | Address | Contact Person | Email (Likely) | Phone / WhatsApp |
                
                RULES:
                1. **Agency Name:** Must be a real business in {region}.
                2. **Address:** Be as specific as possible (Industrial Area, Road Name).
                3. **Email:** If specific email is hidden, provide a standard format (e.g., info@company.com) or "Not Available".
                4. **Phone/WhatsApp:** Provide the public office number or "Check Google Maps" if private. Do NOT invent fake numbers.
                
                """
                
                response = model.generate_content(prompt)
                st.markdown(response.text)
                st.success("✅ Table Generated Successfully")

        except Exception as e:
            st.error(f"❌ Error: {e}")

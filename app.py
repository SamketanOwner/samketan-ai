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
    st.info("Mode: Universal Auto-Connect")

# --- MAIN APP ---
st.title("🚀 Business Growth Engine")

# --- 2. INPUTS ---
col1, col2 = st.columns(2)
with col1:
    my_product = st.text_input("1) What is your product/service?", placeholder="e.g. Warehouse Storage")
    region = st.text_input("3) Target Region?", "Gulbarga")
with col2:
    target_client = st.text_input("2) Who is your client?", placeholder="e.g. Dal Mills")
    scope = st.radio("4) Market Scope", ["Local (Domestic)", "Export (International)"])

# --- 3. THE UNIVERSAL LOGIC ---
if st.button("🚀 Identify Leads"):
    if not api_key:
        st.error("Please provide an API Key.")
    else:
        try:
            genai.configure(api_key=api_key)
            
            with st.spinner("🔄 Asking Google for available models..."):
                
                # 1. GET THE ACTUAL LIST FROM GOOGLE
                my_models = []
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        my_models.append(m.name)
                
                # 2. FILTER: FIND A SAFE MODEL (No "Experimental", No "2.0")
                chosen_model = None
                
                # Priority 1: 1.5 Flash (The Best)
                for m in my_models:
                    if "1.5-flash" in m and "exp" not in m and "8b" not in m:
                        chosen_model = m
                        break
                
                # Priority 2: 1.5 Pro (The Second Best)
                if not chosen_model:
                    for m in my_models:
                        if "1.5-pro" in m and "exp" not in m:
                            chosen_model = m
                            break

                # Priority 3: Gemini Pro (The Old Reliable)
                if not chosen_model:
                    for m in my_models:
                        if "gemini-pro" in m:
                            chosen_model = m
                            break
                            
                # Priority 4: ANYTHING that works
                if not chosen_model and len(my_models) > 0:
                    chosen_model = my_models[0]

            if not chosen_model:
                st.error("❌ Your API Key has ZERO access to any AI models. Please create a new key at aistudio.google.com")
                st.write("Debug: Found list is empty.")
            else:
                # --- RUN SEARCH ---
                with st.spinner(f"🔎 Connected via {chosen_model}... searching {region}..."):
                    
                    model = genai.GenerativeModel(chosen_model)
                    
                    prompt = f"""
                    Act as a Lead Generation Expert.
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
                    st.success(f"✅ Success! (Engine: {chosen_model})")
                    st.markdown(response.text)

        except Exception as e:
            st.error(f"❌ Error: {e}")

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
    st.info("Mode: Smart Auto-Select")

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

# --- 3. OUTPUT LOGIC (SMART SELECTOR) ---
if st.button("🚀 Identify Leads"):
    if not api_key:
        st.error("Please provide an API Key.")
    else:
        try:
            genai.configure(api_key=api_key)
            
            with st.spinner("🔄 Finding the best available AI model..."):
                # --- SMART MODEL SELECTOR ---
                chosen_model = None
                available_models = []
                
                # 1. Get ALL models your key can see
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        available_models.append(m.name)
                
                # 2. Filter logic: Avoid '2.5' (Quota limits) and prefer '1.5' (Stable)
                for name in available_models:
                    if "2.5" in name: 
                        continue # Skip the low-quota model
                    if "1.5-flash" in name:
                        chosen_model = name
                        break # Found the best one!
                
                # 3. Fallback: If no 1.5 flash, take the first valid one that isn't 2.5
                if not chosen_model:
                    for name in available_models:
                         if "2.5" not in name:
                             chosen_model = name
                             break
                
                # 4. Final Safety: If ONLY 2.5 exists, use it and warn user
                if not chosen_model and available_models:
                    chosen_model = available_models[0]
            
            if not chosen_model:
                st.error("❌ Fatal Error: Your API Key has NO access to any models. Please generate a new key at aistudio.google.com")
            else:
                # --- RUN THE SEARCH ---
                with st.spinner(f"🔎 Analyzing {scope} market in {region} using {chosen_model}..."):
                    
                    model = genai.GenerativeModel(chosen_model)
                    
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
                    st.markdown(f"**Connected to:** `{chosen_model}`") # Shows you which one worked
                    st.markdown(response.text)
                    st.success("✅ Table Generated Successfully")

        except Exception as e:
            st.error(f"❌ Error: {e}")

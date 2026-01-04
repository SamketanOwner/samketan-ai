import streamlit as st
import google.generativeai as genai

# --- PAGE CONFIG ---
st.set_page_config(page_title="Samketan Leads", page_icon="🏢")

# --- 1. LOGIN LOGIC (KEPT EXACTLY AS REQUESTED) ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    auth_status = "✅ Auto-Logged In"
else:
    api_key = st.sidebar.text_input("Paste Google API Key", type="password").strip()
    auth_status = "⚠️ using manual key"

# --- SIDEBAR ---
with st.sidebar:
    st.header("Samketan 4.0")
    st.caption(auth_status)
    st.info("Mode: Custom Search")

# --- MAIN APP ---
st.title("🎯 Custom Lead Finder")
st.markdown("Type exactly what you are looking for.")

# --- 2. NEW INPUTS (More Freedom) ---
col1, col2 = st.columns(2)
with col1:
    # Changed from Dropdown to Text Input -> Type ANYTHING
    target_business = st.text_input("Who are you looking for?", placeholder="e.g. Cotton Mills, Dal Mills, Hospitals")
with col2:
    region = st.text_input("Region/City", "Gulbarga")

# Optional: Add a specific requirement to filter results
specific_need = st.text_input("Specific Requirement (Optional)", placeholder="e.g. Must have a warehouse, Must be a wholesaler")

# --- 3. NEW OUTPUT LOGIC ---
if st.button("Find Leads"):
    if not api_key:
        st.error("Please provide an API Key.")
    else:
        try:
            genai.configure(api_key=api_key)
            
            # Auto-Detect Model (Kept same as before to ensure connection)
            valid_model = None
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    if 'flash' in m.name:
                        valid_model = m.name
                        break
            if not valid_model: valid_model = 'models/gemini-1.5-flash' # Fallback

            with st.spinner(f"🔎 Scanning {region} for '{target_business}'..."):
                model = genai.GenerativeModel(valid_model)
                
                # REFINED PROMPT: Asking for a list format
                prompt = f"""
                Act as a B2B Lead Generator.
                
                TASK: Find 5 REAL, SPECIFIC business leads in {region} that match: '{target_business}'.
                Context: {specific_need}
                
                OUTPUT RULES:
                - Do NOT give general advice.
                - List specific business names.
                - If exact contact info is private, mention the AREA/LOCALITY where they are located.
                
                FORMAT FOR EACH LEAD:
                -----------------------
                🏢 **[Business Name]**
                📍 **Location:** [Specific Area/Road in {region}]
                💼 **Business Type:** [Wholesaler/Manufacturer/Retailer]
                💡 **Why Pitch Them:** [1 sentence strategy]
                -----------------------
                """
                
                response = model.generate_content(prompt)
                st.markdown(response.text)
                st.success("✅ Search Complete")

        except Exception as e:
            st.error(f"❌ Error: {e}")

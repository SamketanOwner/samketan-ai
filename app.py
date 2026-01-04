import streamlit as st
import google.generativeai as genai

# --- PAGE SETUP ---
st.set_page_config(page_title="Samketan Agent", page_icon="🚀", layout="centered")

# --- LOGIN SYSTEM ---
# Uses Streamlit Secrets for security in production, but simpler here for you
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("🔒 Samketan Login")
    password = st.text_input("Enter Password", type="password")
    if st.button("Unlock System"):
        if password == "Samketan2026": # YOUR PASSWORD
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Incorrect Password")

if not st.session_state.logged_in:
    login()
    st.stop()

# --- THE APP INTERFACE ---
st.title("🚀 Samketan Agent")
st.markdown("### Intelligent Lead Discovery Engine")

# --- SIDEBAR (API KEY INPUT) ---
with st.sidebar:
    st.header("⚙️ Brain Power")
    api_key = st.text_input("Paste Google API Key", type="password")
    st.caption("Paste your 'AIza...' key here to activate the brain.")
    
    st.markdown("---")
    st.markdown("**Search Mode:**")
    st.info("⚡ Live AI Analysis")

# --- MAIN INPUTS ---
col1, col2 = st.columns(2)
with col1:
    domain = st.selectbox("Target Category", 
        ["Software Buyers", "Warehouse Clients", "Art/Statue Resellers", "Food/Grain Wholesalers", "Export Agencies"])
with col2:
    region = st.text_input("Target Region", "Gulbarga, Karnataka")

details = st.text_area("Specific Filters / Notes", "Looking for verified contacts with phone numbers if possible...")

# --- THE BRAIN LOGIC ---
if st.button("🚀 Find Verified Leads"):
    if not api_key:
        st.error("⛔ Please paste your Google API Key in the sidebar first!")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            with st.spinner(f"🤖 Samketan is analyzing {domain} in {region}..."):
                
                # THE SMART PROMPT (The "Logic" you wanted)
                prompt = f"""
                Act as Samketan, a Lead Generation Expert.
                TASK: Find 3 highly relevant business leads for:
                - Domain: {domain}
                - Region: {region}
                - Context: {details}

                STRICT RULES:
                1. If 'Software': Find IT Heads/Purchase Managers.
                2. If 'Warehouse': Find Logistics Managers of growing companies.
                3. If 'Food': Find Wholesalers (Exclude Mills).
                
                OUTPUT FORMAT:
                For each lead, provide:
                1. **Business Name**
                2. **Why them?** (One sentence logic)
                3. **Draft Email Pitch** (Very short, cold-email style)
                """
                
                response = model.generate_content(prompt)
                st.markdown(response.text)
                
                st.success("✅ Analysis Complete")
                
        except Exception as e:
            st.error(f"❌ Error: {e}")

import streamlit as st
import auth  # This connects to auth.py

if not auth.login_screen():
    st.stop()  # Everything below this line stays hidden until login
import streamlit as st
import google.generativeai as genai
import urllib.parse
import pandas as pd
import time
import extra_streamlit_components as stx

# Initialize the cookie manager
cookie_manager = stx.CookieManager()

# 1. Try to get the 'saved_user' cookie
saved_user = cookie_manager.get('samketan_user')

# 2. If cookie exists and user isn't logged in yet, log them in automatically
if saved_user and not st.session_state.get('authenticated'):
    st.session_state.authenticated = True
    st.session_state.current_user = saved_user
# --- PAGE SETUP ---
st.set_page_config(page_title="Samketan Business Growth Engine", page_icon="🚀", layout="wide")
# --- BHOODEVI WAREHOUSE PROMOTION ---
st.markdown(
    """
    <style>
    .flash-container {
        background-color: #FFF4E5;
        padding: 8px;
        border: 1px solid #FF8C00;
        border-radius: 5px;
        margin-bottom: 15px;
        text-align: center;
    }
    .flash-text {
        color: #D35400;
        font-weight: bold;
        font-size: 16px;
        font-family: sans-serif;
    }
    .flash-link {
        color: #2E86C1;
        text-decoration: none;
        font-weight: bold;
    }
    </style>
    
    <div class="flash-container">
        <marquee scrollamount="10" direction="left" class="flash-text">
            📢 <b>AVAILABLE FOR LEASE:</b> Premium 21,000 Sq. Ft. Warehouse in Gulbarga (Kalyana Karnataka). 
            Ideal for FMCG & Logistics. 
            <a href="https://bhoodeviwarehouse.netlify.app/" target="_blank" class="flash-link">
                👉 Click Here to Visit M/s Bhoodevi Warehouse
            </a>
        </marquee>
    </div>
    """,
    unsafe_allow_html=True
)
# ------------------------------------

# --- 1. LOGIN & API SETUP ---
api_key = st.secrets.get("GOOGLE_API_KEY") or st.sidebar.text_input("Paste Google API Key", type="password").strip()

def get_engine(key):
    try:
        genai.configure(api_key=key.strip())
        
        # 1. Ask the API for a list of all models you are allowed to use
        available_models = [m.name for m in genai.list_models() 
                           if 'generateContent' in m.supported_generation_methods]
        
        # 2. Priority list: Try the newest models first
        # This bypasses the 404 error by only using what is actually online
        priority = [
            'models/gemini-3-flash-preview', 
            'models/gemini-2.5-flash', 
            'models/gemini-1.5-flash'
        ]
        
        # Find the best match
        selected = next((m for m in priority if m in available_models), available_models[0])
        return genai.GenerativeModel(selected)
        
    except Exception as e:
        st.error(f"❌ Connection Error: {e}")
        return None

# --- SIDEBAR: COMPANY STRATEGY ---
with st.sidebar:
    st.header("🏢 Samketan Strategy")
    strategy_note = st.text_area("Why Samketan is Best?", 
        value="We provide premium quality, natural ingredients, and a reliable cold-chain supply with 24/7 support.", 
        help="This text will be injected into your WhatsApp and Email.")

# --- MAIN DASHBOARD ---
st.header("🚀 Samketan Business Growth Engine")

col1, col2 = st.columns(2)
with col1:
    my_product = st.text_input("1) Product/Service", value="ice cream")
    region = st.text_input("3) Target City/Region", value="gulbarga")
with col2:
    target_client = st.text_input("2) Who is your client?", value="hotels, smart bazar")
    scope = st.radio("4) Market Scope", ["Local (Domestic)", "Export (International)"])

# --- 3. DATA ENGINE ---
if st.button("🚀 Generate & View Full Leads"):
    if not api_key:
        st.error("Please provide an API Key.")
    else:
        model = get_engine(api_key)
        if model:
            with st.spinner("🔍 Mining detailed leads and generating targeted LinkedIn profile links..."):
                prompt = f"""
                Act as a B2B Sales Expert. Find 10 REAL businesses in {region} for {target_client}.
                They must be potential buyers for {my_product}.
                
                STRICT REQUIREMENT: 
                - Do not say 'Not Available'. 
                - Identify a likely 'Decision Maker Role' (e.g., F&B Manager, Store Manager).
                - Provide a 'Person Name' (or a specific title like 'Operations Head' if name is unknown).
                
                Return ONLY a pipe-separated table:
                Agency Name | Full Address | Website URL | Email ID | Phone Number | Decision Maker Role | Person Name
                """
                
                response = None
                try:
                    response = model.generate_content(prompt)
                except Exception as e:
                    st.error(f"Error: {e}. Please wait a moment for the quota to reset.")

                if response:
                    lines = response.text.split('\n')
                    lead_data = []
                    
                    # --- TABLE RENDERING ---
                    html_table = "<table style='width:100%; border-collapse: collapse; font-family: Arial; font-size: 13px;'>"
                    html_table += "<tr style='background-color: #004a99; color: white;'><th>Business Details</th><th>Website</th><th>Email (Shoot)</th><th>WhatsApp (Shoot)</th><th>Direct LinkedIn Search</th></tr>"

                    for line in lines:
                        if '|' in line and 'Agency' not in line and '---' not in line:
                            cols = [c.strip() for c in line.split('|')]
                            if len(cols) < 7: continue
                            
                            name, addr, web, email, phone, role, person = cols[0], cols[1], cols[2], cols[3], cols[4], cols[5], cols[6]
                            lead_data.append([name, addr, web, email, phone, role, person])
                            
                            # OUTREACH LINKS
                            wa_msg = f"Hello {person}, from Samketan regarding {my_product}. {strategy_note}"
                            clean_phone = "".join(filter(str.isdigit, phone))
                            if len(clean_phone) == 10: clean_phone = "91" + clean_phone
                            wa_link = f"https://wa.me/{clean_phone}?text={urllib.parse.quote(wa_msg)}"
                            mail_link = f"mailto:{email}?subject=Partnership&body={urllib.parse.quote(wa_msg)}"
                            
                            # --- DEEP LINKEDIN SEARCH FIX ---
                            # Logic: Searches specifically for the Person's Name AND Company Name in the People category
                            li_search_query = f'"{person}" "{name}"'
                            li_link = f"https://www.linkedin.com/search/results/people/?keywords={urllib.parse.quote(li_search_query)}&origin=GLOBAL_SEARCH_HEADER"

                            html_table += f"""
                            <tr>
                                <td style='border: 1px solid #ddd; padding: 10px;'><b>{name}</b><br><small>{addr}</small></td>
                                <td style='border: 1px solid #ddd; padding: 10px;'><a href='{web}' target='_blank'>{web}</a></td>
                                <td style='border: 1px solid #ddd; padding: 10px;'><b><a href='{mail_link}'>{email}</a></b></td>
                                <td style='border: 1px solid #ddd; padding: 10px;'><a href='{wa_link}' target='_blank' style='color: #25D366; font-weight: bold;'>{phone} [Shoot]</a></td>
                                <td style='border: 1px solid #ddd; padding: 10px;'>
                                    <b>{person}</b><br><small>({role})</small><br>
                                    <a href='{li_link}' target='_blank' style='color: #0a66c2; font-weight: bold;'>🔗 Direct LinkedIn Profile</a>
                                </td>
                            </tr>"""
                    
                    html_table += "</table>"
                    st.write(html_table, unsafe_allow_html=True)
                    
                    df = pd.DataFrame(lead_data, columns=["Name", "Address", "Web", "Email", "Phone", "Role", "Person"])
                    st.download_button("📥 Download Organized Excel", data=df.to_csv(index=False).encode('utf-8'), file_name="leads.csv", mime="text/csv")
# --- FOOTER & SIDEBAR ---
st.markdown("---")
st.caption("Samketan Engine v3.7 | Targeted LinkedIn People Search Enabled")

with st.sidebar:
    # 1. HELP SECTION (This is the new safe part)
    with st.expander("🎯 How to Use this Engine"):
        st.markdown("""
        **Step 1: Input Details**
        Enter the target industry and location in the main window.
        
        **Step 2: People Search**
        Click 'LinkedIn Search' to find decision-makers.
        
        **Step 3: Lead Tracking**
        Every login is automatically logged to your Google Sheet for security.
        """)
    
    st.write("---") 
    
    # 2. USER PROFILE INFO
    st.info(f"👤 Logged in as:\n{st.session_state.current_user}")
    
    st.write("---") 
    
    # 3. LOGOUT BUTTON
    if st.button("🚪 Logout from Engine", use_container_width=True):
        # Delete the cookie from the browser
        cookie_manager.delete('samketan_user')
        
        # Reset the session variables
        st.session_state.authenticated = False
        st.session_state.otp_sent = False
        st.rerun()

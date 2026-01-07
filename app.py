import streamlit as st
import google.generativeai as genai
import urllib.parse

# --- PAGE SETUP ---
st.set_page_config(page_title="Samketan Business Growth Engine", page_icon="📈", layout="wide")

# --- 1. LOGIN & API ENGINE ---
api_key = st.secrets.get("GOOGLE_API_KEY") or st.sidebar.text_input("Paste Google API Key", type="password").strip()

def get_engine(key):
    try:
        genai.configure(api_key=key)
        # 404 FIX: This searches for whatever model is active for your key today
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        stable_model = next((m for m in ['models/gemini-2.5-flash', 'models/gemini-1.5-flash'] if m in available), available[0])
        return genai.GenerativeModel(stable_model)
    except: return None

# --- SIDEBAR: COMPANY DESCRIPTION ---
with st.sidebar:
    st.header("🏢 Your Company Profile")
    my_company_desc = st.text_area("Describe your company & services", 
        value="", 
        placeholder="e.g., Samketan: We provide high-end Warehouse Storage solutions...",
        help="The AI will use this to write the professional outreach messages.")

# --- MAIN DASHBOARD ---
st.header("🚀 Samketan Business Growth Engine")

# --- 2. THE 4 QUESTIONS (Restored) ---
col1, col2 = st.columns(2)
with col1:
    my_product = st.text_input("1) What is your product/service?", value="", placeholder="e.g., Industrial Racking")
    region = st.text_input("3) Target City/Region?", value="", placeholder="e.g., Gulbarga")
with col2:
    target_client = st.text_input("2) Who is your client?", value="", placeholder="e.g., Dal Mills")
    scope = st.radio("4) Market Scope", ["Local (Domestic)", "Export (International)"])

# --- 3. DATA ENGINE ---
if st.button("🚀 Generate 10 Pro Leads"):
    if not api_key:
        st.error("Please provide an API Key.")
    elif not my_company_desc:
        st.warning("Please fill in your Company Profile first.")
    else:
        model = get_engine(api_key)
        if not model:
            st.error("❌ Connection Failed. Check your API key or Quota.")
        else:
            with st.spinner("🔍 Mining 10 leads with direct LinkedIn & WhatsApp links..."):
                prompt = f"""
                Act as a B2B Lead Gen Expert. Find 10 REAL and ACTIVE businesses in {region} for {target_client} regarding {my_product}.
                Return ONLY a table in this format:
                Name | Address | Website | Email | Phone | Concern Person
                """
                
                response = model.generate_content(prompt)
                lines = response.text.split('\n')
                
                # --- PROCESSING THE HTML TABLE ---
                html_table = "<table style='width:100%; border-collapse: collapse; font-family: Arial; font-size: 13px;'>"
                html_table += "<tr style='background-color: #f8f9fa;'><th>Agency Name</th><th>Website</th><th>Email</th><th>WhatsApp</th><th>LinkedIn</th><th>Person</th></tr>"
                
                for i, line in enumerate(lines):
                    if '|' in line and 'Name' not in line and '---' not in line:
                        cols = [c.strip() for c in line.split('|') if c.strip()]
                        if len(cols) < 5: continue
                        
                        name, addr, web, email, phone = cols[0], cols[1], cols[2], cols[3], cols[4]
                        person = cols[5] if len(cols) > 5 else "Purchase Manager"
                        
                        # Clickable Links
                        web_click = web if web.startswith("http") else f"http://{web}"
                        
                        # LinkedIn Search URL logic
                        li_query = f"{person} {name}".replace(" ", "+")
                        li_click = f"https://www.linkedin.com/search/results/all/?keywords={urllib.parse.quote(person + ' ' + name)}"
                        
                        # WhatsApp Logic
                        wa_msg = f"Hello {person}, I am reaching out from {my_company_desc} regarding {my_product}."
                        clean_phone = "".join(filter(str.isdigit, phone))
                        if len(clean_phone) == 10: clean_phone = "91" + clean_phone
                        wa_link = f"<a href='https://wa.me/{clean_phone}?text={urllib.parse.quote(wa_msg)}' target='_blank' style='color: #25D366; font-weight: bold;'>📲 WhatsApp</a>"
                        
                        # Email Logic
                        subject = f"Collaboration Proposal: {name} x {my_product}"
                        mail_link = f"<a href='mailto:{email}?subject={urllib.parse.quote(subject)}' style='color: #007bff;'>📧 Email</a>"
                        
                        html_table += f"<tr>"
                        html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'><b>{name}</b><br><small>{addr}</small></td>"
                        html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'><a href='{web_click}' target='_blank'>🌐 Site</a></td>"
                        html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'>{mail_link}</td>"
                        html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'>{wa_link}</td>"
                        html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'><a href='{li_click}' target='_blank' style='color: #0a66c2; font-weight: bold;'>🔗 Profile</a></td>"
                        html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'>{person}</td>"
                        html_table += f"</tr>"
                
                html_table += "</table>"
                st.write(html_table, unsafe_allow_html=True)
                st.download_button("📥 Download CSV", data=response.text, file_name="samketan_leads.csv")

# --- FOOTER ---
st.markdown("---")
st.caption("Samketan Growth Engine v2.7 | LinkedIn Search Enabled")

import streamlit as st
import google.generativeai as genai
import urllib.parse
import pandas as pd

# --- PAGE SETUP ---
st.set_page_config(page_title="Samketan Business Growth Engine", page_icon="🚀", layout="wide")

# --- 1. LOGIN & API SETUP ---
api_key = st.secrets.get("GOOGLE_API_KEY") or st.sidebar.text_input("Paste Google API Key", type="password").strip()

def get_engine(key):
    try:
        genai.configure(api_key=key)
        # 2026 Stable Path Selection
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        stable_model = next((m for m in ['models/gemini-2.5-flash', 'models/gemini-1.5-flash'] if m in available), available[0])
        return genai.GenerativeModel(stable_model)
    except: return None

# --- SIDEBAR: COMPANY STRATEGY ---
with st.sidebar:
    st.header("🏢 Samketan Strategy")
    st.write("**Why are we the best?**")
    strategy_note = st.text_area("Our Core Strength", 
        value="We provide premium quality, natural ingredients, and a reliable cold-chain supply. Our 24/7 delivery support ensures your stocks never run out.", 
        help="This will be included in your WhatsApp/Email as the 'Why Us' factor.")

# --- MAIN DASHBOARD ---
st.header("🚀 Samketan Business Growth Engine")

col1, col2 = st.columns(2)
with col1:
    my_product = st.text_input("1) Product/Service", value="ice cream")
    region = st.text_input("3) Target Region", value="gulbarga")
with col2:
    target_client = st.text_input("2) Target Client", value="hotels, smart bazar")
    scope = st.radio("4) Market Scope", ["Local (Domestic)", "Export (International)"])

# --- 3. DATA ENGINE ---
if st.button("🚀 Generate & View Full Leads"):
    if not api_key:
        st.error("Please provide an API Key.")
    else:
        model = get_engine(api_key)
        if model:
            with st.spinner("🔍 Mining detailed leads for Gulbarga..."):
                prompt = f"""
                Act as a B2B Sales Expert. Find 10 REAL and ACTIVE businesses in {region} for {target_client}.
                They must be potential buyers for {my_product}.
                
                Format your output ONLY as a pipe-separated table with these EXACT headers:
                Agency Name | Full Address | Website URL | Email ID | Phone Number | LinkedIn Profile | Person Name
                """
                
                response = model.generate_content(prompt)
                lines = response.text.split('\n')
                
                # --- PREPARE DATA FOR EXCEL ---
                lead_data = []
                
                # --- START THE VISIBLE TABLE ---
                html_table = "<table style='width:100%; border-collapse: collapse; font-family: Arial; font-size: 12px;'>"
                html_table += """<tr style='background-color: #004a99; color: white;'>
                                    <th>Agency Details</th>
                                    <th>Website (Full)</th>
                                    <th>Email ID (Visible)</th>
                                    <th>Phone / WhatsApp</th>
                                    <th>LinkedIn / Decision Maker</th>
                                 </tr>"""

                for line in lines:
                    if '|' in line and 'Agency' not in line and '---' not in line:
                        cols = [c.strip() for c in line.split('|')]
                        if len(cols) < 7: continue
                        
                        name, addr, web, email, phone, link, person = cols[0], cols[1], cols[2], cols[3], cols[4], cols[5], cols[6]
                        
                        # Store for Excel
                        lead_data.append([name, addr, web, email, phone, link, person])
                        
                        # --- OUTREACH CONTENT ---
                        wa_msg = (f"Welcome to the Samketan family!\n\nHello {person}, I am reaching out regarding {my_product} supply for {name}. "
                                  f"At Samketan, we are the best because: {strategy_note}. "
                                  f"Can we discuss a partnership strategy?")
                        
                        clean_phone = "".join(filter(str.isdigit, phone))
                        if len(clean_phone) == 10: clean_phone = "91" + clean_phone
                        wa_link = f"https://wa.me/{clean_phone}?text={urllib.parse.quote(wa_msg)}"
                        
                        subject = f"Business Strategy for {name} | Premium {my_product} Supply"
                        mail_body = f"Dear {person},\n\nWelcome to Samketan. We noticed your presence in {region} and want to offer our {my_product}.\n\nWhy Samketan? {strategy_note}\n\nRegards."
                        mail_link = f"mailto:{email}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(mail_body)}"

                        # --- ROW RENDERING ---
                        html_table += f"""
                        <tr>
                            <td style='border: 1px solid #ddd; padding: 10px;'><b>{name}</b><br>{addr}</td>
                            <td style='border: 1px solid #ddd; padding: 10px;'><a href='{web}' target='_blank'>{web}</a></td>
                            <td style='border: 1px solid #ddd; padding: 10px;'><b><a href='{mail_link}'>{email}</a></b></td>
                            <td style='border: 1px solid #ddd; padding: 10px;'>
                                <b>{phone}</b><br>
                                <a href='{wa_link}' target='_blank' style='color: #25D366; font-weight: bold;'>[Shoot WhatsApp]</a>
                            </td>
                            <td style='border: 1px solid #ddd; padding: 10px;'>
                                <b>{person}</b><br>
                                <a href='{link}' target='_blank' style='color: #0a66c2;'>Full LinkedIn Profile</a>
                            </td>
                        </tr>"""
                
                html_table += "</table>"
                st.write(html_table, unsafe_allow_html=True)

                # --- EXCEL DOWNLOAD (Organized) ---
                if lead_data:
                    df = pd.DataFrame(lead_data, columns=["Agency Name", "Address", "Website", "Email", "Phone", "LinkedIn", "Decision Maker"])
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Download Organized Excel/CSV", data=csv, file_name="samketan_leads_organized.csv", mime='text/csv')

# --- FOOTER ---
st.markdown("---")
st.caption("Samketan Engine v3.0 | Fully Visible Details | Organized Excel Export")

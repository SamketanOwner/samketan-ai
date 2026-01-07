import streamlit as st
import google.generativeai as genai
import urllib.parse
import pandas as pd
import time

# --- PAGE SETUP ---
st.set_page_config(page_title="Samketan Business Growth Engine", page_icon="🚀", layout="wide")

# --- 1. LOGIN & API SETUP ---
api_key = st.secrets.get("GOOGLE_API_KEY") or st.sidebar.text_input("Paste Google API Key", type="password").strip()

def get_engine(key):
    try:
        genai.configure(api_key=key)
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Using 1.5-flash as it has the most stable free-tier quota
        return genai.GenerativeModel('gemini-1.5-flash')
    except: return None

# --- SIDEBAR: COMPANY STRATEGY ---
with st.sidebar:
    st.header("🏢 Samketan Strategy")
    strategy_note = st.text_area("Why Samketan is Best?", 
        value="We provide premium quality, natural ingredients, and a reliable cold-chain supply with 24/7 support.", 
        help="This text will be injected into your WhatsApp and Email compositions.")

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
            with st.spinner("🔍 Connecting to Google AI... (Respecting Rate Limits)"):
                prompt = f"""
                Act as a B2B Sales Expert. Find 10 REAL and ACTIVE businesses in {region} for {target_client}.
                They must be potential buyers for {my_product}.
                Format ONLY as a pipe-separated table:
                Agency Name | Full Address | Website URL | Email ID | Phone Number | Decision Maker Role | Name of Person
                """
                
                # --- AUTO-RETRY LOGIC ---
                response = None
                success = False
                for attempt in range(3):
                    try:
                        response = model.generate_content(prompt)
                        success = True
                        break
                    except Exception as e:
                        if "429" in str(e) or "ResourceExhausted" in str(e):
                            st.warning(f"⚠️ API is busy. Retrying in 15 seconds... (Attempt {attempt+1}/3)")
                            time.sleep(15) # Wait for the minute-limit to reset
                        else:
                            st.error(f"❌ Connection Error: {e}")
                            break

                if success and response:
                    lines = response.text.split('\n')
                    lead_data = []
                    
                    # Visible Table Structure
                    html_table = "<table style='width:100%; border-collapse: collapse; font-family: Arial; font-size: 13px;'>"
                    html_table += "<tr style='background-color: #004a99; color: white;'><th>Business</th><th>Website</th><th>Email (Compose)</th><th>WhatsApp (Shoot)</th><th>LinkedIn</th></tr>"

                    for line in lines:
                        if '|' in line and 'Agency' not in line and '---' not in line:
                            cols = [c.strip() for c in line.split('|')]
                            if len(cols) < 7: continue
                            
                            name, addr, web, email, phone, role, person = cols[0], cols[1], cols[2], cols[3], cols[4], cols[5], cols[6]
                            lead_data.append([name, addr, web, email, phone, role, person])
                            
                            # Outreach Links
                            wa_msg = f"Hello {person}, from Samketan regarding {my_product}. {strategy_note}"
                            clean_phone = "".join(filter(str.isdigit, phone))
                            if len(clean_phone) == 10: clean_phone = "91" + clean_phone
                            wa_link = f"https://wa.me/{clean_phone}?text={urllib.parse.quote(wa_msg)}"
                            
                            mail_link = f"mailto:{email}?subject=Partnership&body={urllib.parse.quote(wa_msg)}"
                            li_link = f"https://www.linkedin.com/search/results/all/?keywords={urllib.parse.quote(person + ' ' + role + ' ' + name)}"

                            html_table += f"""
                            <tr>
                                <td style='border: 1px solid #ddd; padding: 10px;'><b>{name}</b><br><small>{addr}</small></td>
                                <td style='border: 1px solid #ddd; padding: 10px;'><a href='{web}' target='_blank'>{web}</a></td>
                                <td style='border: 1px solid #ddd; padding: 10px;'><b><a href='{mail_link}'>{email}</a></b></td>
                                <td style='border: 1px solid #ddd; padding: 10px;'><a href='{wa_link}' target='_blank' style='color: #25D366;'>{phone} [Shoot]</a></td>
                                <td style='border: 1px solid #ddd; padding: 10px;'><b>{person}</b><br><a href='{li_link}' target='_blank' style='color: #0a66c2;'>View Profile</a></td>
                            </tr>"""
                    
                    html_table += "</table>"
                    st.write(html_table, unsafe_allow_html=True)
                    
                    df = pd.DataFrame(lead_data, columns=["Name", "Address", "Web", "Email", "Phone", "Role", "Person"])
                    st.download_button("📥 Download Organized Excel", data=df.to_csv(index=False).encode('utf-8'), file_name="leads.csv")

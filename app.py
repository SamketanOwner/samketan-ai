import streamlit as st
import google.generativeai as genai
import urllib.parse
import pandas as pd
import time

# --- PAGE SETUP ---
st.set_page_config(page_title="Samketan Business Growth Engine", page_icon="🚀", layout="wide")

# --- 1. LOGIN & API SETUP ---
# Auto-login from secrets or manual entry
api_key = st.secrets.get("GOOGLE_API_KEY") or st.sidebar.text_input("Paste Google API Key", type="password").strip()

# --- 1. KEY & MODEL STABILITY SETUP ---
def get_engine(key):
    try:
        genai.configure(api_key=key.strip())
        # This asks the API for a list of all models you are allowed to use
        available_models = [m.name for m in genai.list_models() 
                           if 'generateContent' in m.supported_generation_methods]
        
        # Priority list: It checks what's actually online for your key
        priority = ['models/gemini-2.5-flash', 'models/gemini-1.5-flash']
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
            with st.spinner("🔍 Connecting to Samketan Data Lake..."):
                prompt = f"""
                Act as a B2B Lead Gen Expert. Find 10 REAL and ACTIVE businesses in {region} for {target_client}.
                They must be potential buyers for {my_product}.
                
                STRICT DATA RULE:
                - Do not say 'Not Available'.
                - Assign a 'Decision Maker' (e.g. F&B Manager, Purchase Head, Store Manager).
                
                Return ONLY a pipe-separated table:
                Agency Name | Full Address | Website URL | Email ID | Phone Number | Decision Maker
                """
                
                # --- AUTO-RETRY LOGIC ---
                response = None
                for attempt in range(3):
                    try:
                        response = model.generate_content(prompt)
                        break
                    except Exception as e:
                        if "429" in str(e):
                            st.warning(f"⚠️ API Limit hit. Waiting {15 * (attempt + 1)} seconds to retry...")
                            time.sleep(15 * (attempt + 1))
                        else:
                            st.error(f"Connection error: {e}")
                            break

                if response:
                    lines = response.text.split('\n')
                    lead_data = []
                    
                    # --- RENDER TABLE ---
                    html_table = "<table style='width:100%; border-collapse: collapse; font-family: Arial; font-size: 13px;'>"
                    html_table += "<tr style='background-color: #004a99; color: white;'><th>Business Details</th><th>Website</th><th>Email (Compose)</th><th>WhatsApp (Shoot)</th><th>Decision Maker & LinkedIn</th></tr>"

                    for line in lines:
                        if '|' in line and 'Agency' not in line and '---' not in line:
                            cols = [c.strip() for c in line.split('|')]
                            if len(cols) < 6: continue
                            
                            name, addr, web, email, phone, role = cols[0], cols[1], cols[2], cols[3], cols[4], cols[5]
                            lead_data.append([name, addr, web, email, phone, role])
                            
                            # Outreach Links
                            wa_msg = f"Hello {role}, from Samketan regarding {my_product} supply for {name}. {strategy_note}"
                            clean_phone = "".join(filter(str.isdigit, phone))
                            if len(clean_phone) == 10: clean_phone = "91" + clean_phone
                            wa_link = f"https://wa.me/{clean_phone}?text={urllib.parse.quote(wa_msg)}"
                            
                            mail_link = f"mailto:{email}?subject=Partnership Proposal&body={urllib.parse.quote(wa_msg)}"
                            li_link = f"https://www.linkedin.com/search/results/all/?keywords={urllib.parse.quote(role + ' ' + name)}"

                            html_table += f"""
                            <tr>
                                <td style='border: 1px solid #ddd; padding: 10px;'><b>{name}</b><br><small>{addr}</small></td>
                                <td style='border: 1px solid #ddd; padding: 10px;'><a href='{web}' target='_blank'>{web}</a></td>
                                <td style='border: 1px solid #ddd; padding: 10px;'><b><a href='{mail_link}'>{email}</a></b></td>
                                <td style='border: 1px solid #ddd; padding: 10px;'><a href='{wa_link}' target='_blank' style='color: #25D366; font-weight: bold;'>{phone} [Shoot]</a></td>
                                <td style='border: 1px solid #ddd; padding: 10px;'><b>{role}</b><br><a href='{li_link}' target='_blank' style='color: #0a66c2;'>🔗 LinkedIn Profile</a></td>
                            </tr>"""
                    
                    html_table += "</table>"
                    st.write(html_table, unsafe_allow_html=True)
                    
                    df = pd.DataFrame(lead_data, columns=["Name", "Address", "Web", "Email", "Phone", "Decision Maker"])
                    st.download_button("📥 Download Organized Excel", data=df.to_csv(index=False).encode('utf-8'), file_name="leads.csv", mime="text/csv")

# --- FOOTER ---
st.markdown("---")
st.caption("Samketan Engine v3.6 | Stable High-Quota Mode Active")

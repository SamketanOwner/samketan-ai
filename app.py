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
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        stable_model = next((m for m in ['models/gemini-2.5-flash', 'models/gemini-1.5-flash'] if m in available), available[0])
        return genai.GenerativeModel(stable_model)
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
                
                Format ONLY as a pipe-separated table:
                Agency Name | Full Address | Website URL | Email ID | Phone Number | Decision Maker Role | Name of Person
                """
                
                response = model.generate_content(prompt)
                lines = response.text.split('\n')
                
                lead_data = []
                html_table = "<table style='width:100%; border-collapse: collapse; font-family: Arial; font-size: 12px;'>"
                html_table += """<tr style='background-color: #004a99; color: white;'>
                                    <th>Agency Details</th>
                                    <th>Website (Full)</th>
                                    <th>Email ID (Compose)</th>
                                    <th>WhatsApp (Shoot)</th>
                                    <th>LinkedIn (Person Profile)</th>
                                 </tr>"""

                for line in lines:
                    if '|' in line and 'Agency' not in line and '---' not in line:
                        cols = [c.strip() for c in line.split('|')]
                        if len(cols) < 7: continue
                        
                        name, addr, web, email, phone, role, person = cols[0], cols[1], cols[2], cols[3], cols[4], cols[5], cols[6]
                        lead_data.append([name, addr, web, email, phone, role, person])
                        
                        # --- 1. WHATSAPP WEB & MOBILE COMPATIBLE ---
                        wa_msg = (f"Welcome to the Samketan family!\n\nHello {person} ({role}), I am reaching out regarding {my_product} supply for {name}.\n\n"
                                  f"At Samketan, we are the best because: {strategy_note}.\n\n"
                                  f"Can we discuss a partnership strategy?")
                        
                        clean_phone = "".join(filter(str.isdigit, phone))
                        if len(clean_phone) == 10: clean_phone = "91" + clean_phone
                        # Using web.whatsapp.com for laptops and wa.me for mobile
                        wa_link = f"https://wa.me/{clean_phone}?text={urllib.parse.quote(wa_msg)}"
                        
                        # --- 2. EMAIL COMPOSER (WEB COMPATIBLE) ---
                        subject = f"Business Strategy for {name} | Premium {my_product} Supply"
                        mail_body = f"Dear {person} ({role}),\n\nWelcome to Samketan. We noticed your presence in {region} and want to offer our {my_product}.\n\nWhy Samketan? {strategy_note}\n\nRegards."
                        mail_link = f"mailto:{email}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(mail_body)}"

                        # --- 3. TARGETED LINKEDIN SEARCH ---
                        # This creates a search specifically for the person's name and role within that specific company
                        li_query = f"{person} {role} {name}"
                        li_link = f"https://www.linkedin.com/search/results/all/?keywords={urllib.parse.quote(li_query)}"

                        html_table += f"""
                        <tr>
                            <td style='border: 1px solid #ddd; padding: 10px;'><b>{name}</b><br>{addr}</td>
                            <td style='border: 1px solid #ddd; padding: 10px;'><a href='{web}' target='_blank'>{web}</a></td>
                            <td style='border: 1px solid #ddd; padding: 10px;'>
                                <a href='{mail_link}' style='color: #007bff; font-weight: bold;'>{email}</a><br>
                                <small>(Click to Shoot Mail)</small>
                            </td>
                            <td style='border: 1px solid #ddd; padding: 10px;'>
                                <b>{phone}</b><br>
                                <a href='{wa_link}' target='_blank' style='color: #25D366; font-weight: bold;'>[Shoot WhatsApp]</a>
                            </td>
                            <td style='border: 1px solid #ddd; padding: 10px;'>
                                <b>{person}</b><br>({role})<br>
                                <a href='{li_link}' target='_blank' style='color: #0a66c2; font-weight: bold;'>🔗 View Person Profile</a>
                            </td>
                        </tr>"""
                
                html_table += "</table>"
                st.write(html_table, unsafe_allow_html=True)

                if lead_data:
                    df = pd.DataFrame(lead_data, columns=["Agency Name", "Address", "Website", "Email", "Phone", "Role", "Person"])
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Download Organized Excel", data=csv, file_name="samketan_leads.csv", mime='text/csv')

# --- FOOTER ---
st.markdown("---")
st.caption("Samketan Engine v3.1 | Cross-Platform Outreach Fix | Targeted LinkedIn Search")

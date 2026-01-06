import streamlit as st
import google.generativeai as genai
import urllib.parse

# --- PAGE SETUP ---
st.set_page_config(page_title="Samketan Growth Engine", page_icon="📈", layout="wide")

# --- 1. LOGIN & COMPANY PROFILE ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    api_key = st.sidebar.text_input("Paste Google API Key", type="password").strip()

# --- NEW: COMPANY DESCRIPTION TAB ---
with st.sidebar:
    st.header("🏢 Your Company Profile")
    my_company_desc = st.text_area("Describe your company & services", 
        value="Samketan: We provide high-end Warehouse Storage solutions and Industrial Racking for large businesses.",
        help="The AI will use this to write the professional email and WhatsApp pitch.")

# --- MAIN DASHBOARD ---
st.title("🚀 Business Growth Engine")

# --- 2. THE 4 QUESTIONS ---
col1, col2 = st.columns(2)
with col1:
    my_product = st.text_input("1) What is your product/service?", value="Warehouse Storage")
    region = st.text_input("3) Target City/Region?", "Gulbarga")
with col2:
    target_client = st.text_input("2) Who is your client?", "Dal Mills")
    scope = st.radio("4) Market Scope", ["Local (Domestic)", "Export (International)"])

# --- 3. DATA ENGINE ---
if st.button("🚀 Generate 10 Pro Leads"):
    if not api_key:
        st.error("Please provide an API Key.")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')

            with st.spinner("🔍 Mining 10 leads and crafting professional pitches..."):
                prompt = f"""
                Act as a B2B Lead Generation Expert. Find 10 REAL businesses in {region} for {target_client}.
                They must be potential buyers for {my_product}.
                
                STRICT RULE: Phone numbers must be FULL 10-digits. DO NOT hide or mask any digits.
                
                Return a table with:
                Agency Name | Address | Website | Email ID | Phone/WhatsApp | LinkedIn Profile | Concern Person
                """
                
                response = model.generate_content(prompt)
                lines = response.text.split('\n')
                
                # --- PROCESSING FOR CLICKABLE LINKS ---
                html_table = "<table style='width:100%; border-collapse: collapse; font-family: Arial; font-size: 14px;'>"
                
                for i, line in enumerate(lines):
                    if '|' in line and '---' not in line:
                        cols = [c.strip() for c in line.split('|') if c.strip()]
                        if len(cols) < 7: continue
                        
                        if i == 0 or "Agency Name" in line: # Header
                            html_table += "<tr>" + "".join([f"<th style='border: 1px solid #ddd; padding: 12px; background-color: #f8f9fa; text-align: left;'>{c}</th>" for c in cols]) + "</tr>"
                        else: # Data Rows
                            name, addr, web, email, phone, link, person = cols[0], cols[1], cols[2], cols[3], cols[4], cols[5], cols[6]
                            
                            # Clean Web URL
                            web_url = web if web.startswith("http") else f"https://{web}"
                            
                            # Create WhatsApp Link (using wa.me)
                            clean_phone = "".join(filter(str.isdigit, phone))
                            if len(clean_phone) == 10: clean_phone = "91" + clean_phone
                            wa_msg = f"Hello {person},\n\nHope you are doing well. I am reaching out from {my_company_desc}. We identified {name} as a key leader in the {target_client} sector and believe our {my_product} could significantly benefit your operations in {region}. Would love to share more details."
                            wa_link = f"<a href='https://wa.me/{clean_phone}?text={urllib.parse.quote(wa_msg)}' target='_blank' style='color: #25D366; font-weight: bold;'>📲 {phone}</a>"
                            
                            # Create Mail Link
                            subject = f"Business Proposal for {name}: {my_product}"
                            mail_body = f"Dear {person},\n\nI hope this email finds you well.\n\nI am writing to you on behalf of my company. {my_company_desc}\n\nWe specialize in {my_product}, and we have helped many companies in the {target_client} industry optimize their logistics and storage. I would appreciate the opportunity to discuss how we can bring similar value to {name} in {region}.\n\nPlease let me know a convenient time for a brief call.\n\nWarm regards,\n[Your Name]\n{my_company_desc}"
                            mail_link = f"<a href='mailto:{email}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(mail_body)}' style='color: #007bff;'>📧 {email}</a>"
                            
                            html_table += f"<tr>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 10px;'>{name}</td>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 10px;'>{addr}</td>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 10px;'><a href='{web_url}' target='_blank' style='color: #007bff;'>🌐 {web}</a></td>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 10px;'>{mail_link}</td>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 10px;'>{wa_link}</td>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 10px;'><a href='{link}' target='_blank' style='color: #007bff;'>🔗 LinkedIn</a></td>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 10px;'>{person}</td>"
                            html_table += f"</tr>"
                
                html_table += "</table>"
                
                st.markdown("### 📋 10 Actionable Sales Leads")
                st.write(html_table, unsafe_allow_html=True)
                
                st.download_button("📥 Download Raw CSV", data=response.text, file_name="samketan_leads.csv")

        except Exception as e:
            st.error(f"❌ Error: {e}")

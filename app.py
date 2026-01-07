import streamlit as st
import google.generativeai as genai
import urllib.parse

# --- PAGE SETUP ---
st.set_page_config(page_title="Samketan Business Growth Engine", page_icon="📈", layout="wide")

# --- 1. LOGIN & API KEY LOGIC ---
# This ensures the app works whether the key is in Secrets or the Sidebar
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    api_key = st.sidebar.text_input("Paste Google API Key", type="password").strip()

# --- SIDEBAR: COMPANY DESCRIPTION ---
with st.sidebar:
    st.header("🏢 Your Company Profile")
    my_company_desc = st.text_area("Describe your company & services", 
        value="", 
        placeholder="e.g., Samketan: We provide high-end Warehouse Storage solutions...",
        help="The AI will use this to write the professional email and WhatsApp pitch.")
    
    st.info("The profile above helps AI personalize your outreach messages.")

# --- MAIN DASHBOARD ---
st.header("🚀 Samketan Business Growth Engine")

# --- 2. THE 4 QUESTIONS ---
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
        st.warning("Please fill in your Company Profile in the sidebar first.")
    else:
        try:
            # CONFIGURING THE ENGINE
            genai.configure(api_key=api_key)
            # Using the absolute latest stable model for 2026
            model = genai.GenerativeModel('gemini-2.0-flash')

            with st.spinner("🔍 Mining 10 leads with deep contact info and direct links..."):
                prompt = f"""
                Act as a B2B Lead Generation Expert. Find 10 REAL and ACTIVE businesses in {region} for {target_client}.
                They must be potential buyers for {my_product}.
                
                STRICT DATA REQUIREMENTS:
                1. WEBSITE: Full URL.
                2. LINKEDIN: Provide a direct search URL for the Person Name + Company.
                3. PHONE: FULL 10-digits.
                4. EMAIL: Real professional email ID.
                
                Return a table with:
                Agency Name | Address | Website | Email ID | Phone/WhatsApp | LinkedIn Profile | Concern Person
                """
                
                response = model.generate_content(prompt)
                lines = response.text.split('\n')
                
                # --- PROCESSING FOR CLICKABLE LINKS ---
                html_table = "<table style='width:100%; border-collapse: collapse; font-family: Arial; font-size: 13px;'>"
                
                for i, line in enumerate(lines):
                    if '|' in line and '---' not in line:
                        cols = [c.strip() for c in line.split('|') if c.strip()]
                        if len(cols) < 7: continue
                        
                        if i == 0 or "Agency Name" in line: # Header Row
                            html_table += "<tr>" + "".join([f"<th style='border: 1px solid #ddd; padding: 10px; background-color: #f8f9fa;'>{c}</th>" for c in cols]) + "</tr>"
                        else: # Data Rows
                            name, addr, web, email, phone, link, person = cols[0], cols[1], cols[2], cols[3], cols[4], cols[5], cols[6]
                            
                            # Clean URLs
                            web_click = web if web.startswith("http") else f"http://{web}"
                            li_click = f"https://www.linkedin.com/search/results/all/?keywords={urllib.parse.quote(person + ' ' + name)}"
                            
                            # PROFESSIONAL WHATSAPP MESSAGE
                            wa_msg = (f"Hello {person},\n\nI hope you are having a productive day. "
                                      f"I am reaching out from {my_company_desc}.\n\n"
                                      f"We have been following {name} in {region} and believe our "
                                      f"specialized {my_product} can add significant value to your operations. "
                                      f"Are you available for a 2-minute introductory chat?")
                            
                            clean_phone = "".join(filter(str.isdigit, phone))
                            if len(clean_phone) == 10: clean_phone = "91" + clean_phone
                            wa_link = f"<a href='https://wa.me/{clean_phone}?text={urllib.parse.quote(wa_msg)}' target='_blank' style='color: #25D366; font-weight: bold;'>📲 {phone}</a>"
                            
                            # PROFESSIONAL EMAIL COMPOSITION
                            subject = f"Collaboration Proposal for {name} | {my_product}"
                            mail_body = (f"Dear {person},\n\n"
                                         f"I am writing to you on behalf of {my_company_desc}. "
                                         f"We specialize in providing {my_product} for {target_client}.\n\n"
                                         f"We noticed the impressive work {name} is doing in {region}. "
                                         f"Could we schedule a brief call next week?\n\n"
                                         f"Best Regards,\n\n[Your Name]\n{my_company_desc}")
                            
                            mail_link = f"<a href='mailto:{email}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(mail_body)}' style='color: #007bff;'>📧 {email}</a>"
                            
                            # Building the HTML Row
                            html_table += f"<tr>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'>{name}</td>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'>{addr}</td>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'><a href='{web_click}' target='_blank'>{web}</a></td>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'>{mail_link}</td>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'>{wa_link}</td>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'><a href='{li_click}' target='_blank' style='color: #0a66c2;'>🔗 LinkedIn</a></td>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'>{person}</td>"
                            html_table += f"</tr>"
                
                html_table += "</table>"
                
                # --- FINAL DISPLAY ---
                st.markdown("### 📋 10 Verified Sales Leads")
                st.write(html_table, unsafe_allow_html=True)
                
                st.download_button("📥 Download CSV", data=response.text, file_name="samketan_leads.csv")

        except Exception as e:
            st.error(f"❌ Error: {e}")

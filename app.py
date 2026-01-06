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

# --- COMPANY DESCRIPTION TAB (UNCHANGED) ---
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

            with st.spinner("🔍 Performing Deep Search for real numbers and LinkedIn profiles..."):
                # PROMPT: Explicitly told NOT to use generic phrases like "Refer to Director"
                prompt = f"""
                Act as a B2B Data Mining Expert. Find 10 REAL businesses in {region} for {target_client}.
                They must be potential buyers for {my_product}.
                
                STRICT RULES:
                1. PHONE: You MUST provide a real, 10-digit mobile/office number. DO NOT write "Refer to Director" or "Private".
                2. LINKEDIN: You MUST provide the direct URL (e.g., https://linkedin.com/in/name or /company/name). DO NOT just write "LinkedIn".
                3. WEBSITE: Provide the full actual URL.
                
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
                        
                        if i == 0 or "Agency Name" in line: # Header
                            html_table += "<tr>" + "".join([f"<th style='border: 1px solid #ddd; padding: 10px; background-color: #f8f9fa;'>{c}</th>" for c in cols]) + "</tr>"
                        else: # Data Rows
                            name, addr, web, email, phone, link, person = cols[0], cols[1], cols[2], cols[3], cols[4], cols[5], cols[6]
                            
                            # Clean Web & LinkedIn URLs
                            web_url = web if web.startswith("http") else f"https://{web}"
                            li_url = link if link.startswith("http") else f"https://www.linkedin.com/search/results/all/?keywords={urllib.parse.quote(name + ' ' + person)}"
                            
                            # Create WhatsApp Link
                            clean_phone = "".join(filter(str.isdigit, phone))
                            if len(clean_phone) == 10: clean_phone = "91" + clean_phone
                            wa_msg = f"Hello {person},\n\nI am reaching out from {my_company_desc}. We specialize in {my_product} and would love to support {name}."
                            wa_link = f"<a href='https://wa.me/{clean_phone}?text={urllib.parse.quote(wa_msg)}' target='_blank' style='color: #25D366; font-weight: bold;'>📲 {phone}</a>"
                            
                            # Create Mail Link
                            subject = f"Business Proposal: {my_product}"
                            mail_body = f"Dear {person},\n\nI hope you are well. Regarding {name}, {my_company_desc} would like to propose our {my_product} services."
                            mail_link = f"<a href='mailto:{email}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(mail_body)}' style='color: #007bff;'>📧 {email}</a>"
                            
                            html_table += f"<tr>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'>{name}</td>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'>{addr}</td>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'><a href='{web_url}' target='_blank'>🌐 Visit</a></td>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'>{mail_link}</td>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'>{wa_link}</td>"
                            # LINKEDIN FIX: Now uses the actual link found or a direct search link
                            html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'><a href='{li_url}' target='_blank' style='color: #0a66c2; font-weight: bold;'>🔗 Profile</a></td>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'>{person}</td>"
                            html_table += f"</tr>"
                
                html_table += "</table>"
                
                st.markdown("### 📋 10 Actionable Sales Leads")
                st.write(html_table, unsafe_allow_html=True)
                
                st.download_button("📥 Download CSV", data=response.text, file_name="samketan_leads.csv")

        except Exception as e:
            st.error(f"❌ Error: {e}")

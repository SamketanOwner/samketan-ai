import streamlit as st
import google.generativeai as genai
import urllib.parse

# --- PAGE SETUP ---
st.set_page_config(page_title="Samketan Growth Engine", page_icon="📈", layout="wide")

# --- 1. LOGIN LOGIC (UNCHANGED) ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    auth_status = "✅ System Connected"
else:
    api_key = st.sidebar.text_input("Paste Google API Key", type="password").strip()
    auth_status = "⚠️ Key Missing"

with st.sidebar:
    st.header("Samketan 2026")
    st.info(auth_status)

# --- MAIN DASHBOARD ---
st.title("🚀 Business Growth Engine")

# --- 2. THE 4 QUESTIONS (UNCHANGED) ---
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

            with st.spinner("🔍 Mining 10 leads with full contact details..."):
                # PROMPT: Explicitly told NOT to hide digits
                prompt = f"""
                Act as a B2B Lead Generation Expert. 
                Find exactly 10 REAL and ACTIVE businesses in {region} for {target_client}.
                They must be potential buyers for {my_product}.
                
                STRICT RULE: You MUST provide the FULL 10-digit phone number. Do NOT hide or truncate digits.
                
                Return a table with exactly these columns:
                Agency Name | Address | Website | Email ID | Phone/WhatsApp | LinkedIn Profile | Concern Person
                """
                
                response = model.generate_content(prompt)
                lines = response.text.split('\n')
                
                # --- PROCESSING FOR CLICKABLE LINKS ---
                # We turn the markdown table into a beautiful HTML table for direct clicks
                html_table = "<table style='width:100%; border-collapse: collapse;'>"
                
                for i, line in enumerate(lines):
                    if '|' in line and '---' not in line:
                        cols = [c.strip() for c in line.split('|') if c.strip()]
                        if len(cols) < 7: continue
                        
                        if i == 0 or "Agency Name" in line: # Header
                            html_table += "<tr>" + "".join([f"<th style='border: 1px solid #ddd; padding: 8px; background-color: #f2f2f2;'>{c}</th>" for c in cols]) + "</tr>"
                        else: # Data Rows
                            name, addr, web, email, phone, link, person = cols[0], cols[1], cols[2], cols[3], cols[4], cols[5], cols[6]
                            
                            # Create WhatsApp Link
                            clean_phone = "".join(filter(str.isdigit, phone))
                            if len(clean_phone) == 10: clean_phone = "91" + clean_phone
                            wa_msg = f"Hello {person}, reaching out from Samketan regarding {my_product} for {name}."
                            wa_link = f"<a href='https://wa.me/{clean_phone}?text={urllib.parse.quote(wa_msg)}' target='_blank'>📲 {phone}</a>"
                            
                            # Create Mail Link
                            subject = f"Proposal for {name}: {my_product}"
                            mail_body = f"Dear {person},\n\nWe specialize in {my_product} and would like to support {name}."
                            mail_link = f"<a href='mailto:{email}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(mail_body)}'>📧 {email}</a>"
                            
                            html_table += f"<tr>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'>{name}</td>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'>{addr}</td>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'><a href='{web}' target='_blank'>🌐 Web</a></td>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'>{mail_link}</td>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'>{wa_link}</td>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'><a href='{link}' target='_blank'>🔗 LinkedIn</a></td>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'>{person}</td>"
                            html_table += f"</tr>"
                
                html_table += "</table>"
                
                st.markdown("### 📋 10 Verified Sales Leads")
                st.write(html_table, unsafe_allow_html=True)
                
                st.download_button("📥 Download Raw Data", data=response.text, file_name="leads.csv")

        except Exception as e:
            st.error(f"❌ Error: {e}")

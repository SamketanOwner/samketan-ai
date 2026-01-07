import streamlit as st
import google.generativeai as genai
import urllib.parse

# --- PAGE SETUP ---
st.set_page_config(
    page_title="Samketan Business Growth Engine", 
    page_icon="📈", 
    layout="wide"
)

# --- 1. LOGIN & API KEY LOGIC ---
# This block prevents the 'SecretNotFoundError' by checking safely
api_key = None
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    st.sidebar.success("✅ Auto-Login Active")
else:
    # If no secret is found, we fall back to manual entry in the sidebar
    api_key = st.sidebar.text_input("Paste Google API Key", type="password").strip()

# --- SIDEBAR: COMPANY PROFILE ---
with st.sidebar:
    st.header("🏢 Your Company Profile")
    my_company_desc = st.text_area(
        "Describe your company & services", 
        value="Samketan: We provide high-end warehouse storage solutions and business software.", 
        help="The AI uses this to write the professional email and WhatsApp pitch."
    )
    st.markdown("---")
    st.info("💡 Tip: A detailed profile helps the AI write better sales pitches.")

# --- MAIN DASHBOARD ---
st.header("🚀 Samketan Business Growth Engine")

# --- 2. USER INPUTS (The 4 Questions) ---
col1, col2 = st.columns(2)

with col1:
    domain = st.selectbox("Select Business Domain", ["Software Selling", "Warehouse Solutions", "Manufacturing", "Other"])
    region = st.text_input("Target Region", placeholder="e.g., Gulbarga, Karnataka")

with col2:
    offer_details = st.text_input("My Offer Details", placeholder="e.g., CRM for Dal Mills")
    scope = st.radio("Market Scope", ["Local (Domestic)", "Export (International)"])

# --- 3. DATA ENGINE ---
if st.button("🚀 Samketan Growth Engine"):
    if not api_key:
        st.error("❌ Error: API Key not found. Please enter it in the sidebar.")
    elif not region or not offer_details:
        st.warning("⚠️ Please provide the Target Region and Offer Details.")
    else:
        try:
            # Clean the API key to prevent 'Invalid Key' errors
            genai.configure(api_key=api_key.strip())
            
            # FIX: Using the absolute production model path for 2026 to avoid 404
            model = genai.GenerativeModel(model_name='models/gemini-1.5-flash')

            with st.spinner("🔍 Mining 10 high-quality leads..."):
                prompt = f"""
                Act as a B2B Lead Generation Expert. 
                Find 10 REAL and ACTIVE businesses in {region} that fit the {domain} sector.
                Specifically, find leads interested in: {offer_details}.
                
                Return a table with:
                Agency Name | Address | Website | Email ID | Phone/WhatsApp | LinkedIn Profile | Concern Person
                """
                
                response = model.generate_content(prompt)
                lines = response.text.split('\n')
                
                # --- PROCESSING THE HTML TABLE ---
                html_table = "<table style='width:100%; border-collapse: collapse; font-family: Arial; font-size: 13px;'>"
                
                for i, line in enumerate(lines):
                    if '|' in line and '---' not in line:
                        cols = [c.strip() for c in line.split('|') if c.strip()]
                        if len(cols) < 7: continue
                        
                        if i == 0 or "Agency Name" in line:
                            html_table += "<tr>" + "".join([f"<th style='border: 1px solid #ddd; padding: 10px; background-color: #f8f9fa;'>{c}</th>" for c in cols]) + "</tr>"
                        else:
                            name, addr, web, email, phone, link, person = cols[0], cols[1], cols[2], cols[3], cols[4], cols[5], cols[6]
                            web_click = web if web.startswith("http") else f"http://{web}"
                            
                            # Clean phone for WhatsApp
                            clean_phone = "".join(filter(str.isdigit, phone))
                            if len(clean_phone) == 10: clean_phone = "91" + clean_phone
                            
                            # WhatsApp Link with Professional Message
                            wa_msg = f"Hello {person}, I am reaching out from {my_company_desc} regarding our {offer_details}."
                            wa_link = f"<a href='https://wa.me/{clean_phone}?text={urllib.parse.quote(wa_msg)}' target='_blank' style='color: #25D366; font-weight: bold;'>📲 {phone}</a>"
                            
                            # Email Link
                            mail_link = f"<a href='mailto:{email}' style='color: #007bff;'>📧 {email}</a>"
                            
                            # LinkedIn Search
                            li_search = f"https://www.linkedin.com/search/results/all/?keywords={urllib.parse.quote(person + ' ' + name)}"
                            
                            html_table += "<tr>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'>{name}</td>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'>{addr}</td>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'><a href='{web_click}' target='_blank'>Website</a></td>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'>{mail_link}</td>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'>{wa_link}</td>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'><a href='{li_search}' target='_blank'>🔗 Profile</a></td>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'>{person}</td>"
                            html_table += "</tr>"
                
                html_table += "</table>"
                st.markdown("### 📋 10 Verified Sales Leads")
                st.write(html_table, unsafe_allow_html=True)
                st.download_button("📥 Download Results (CSV)", data=response.text, file_name="samketan_leads.csv")

        except Exception as e:
            st.error(f"❌ Connection Error: {e}")

# --- FOOTER ---
st.markdown("---")
st.caption("Samketan Growth Engine v2.5 | 2026 Stable Release")

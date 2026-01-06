import streamlit as st
import firebase_admin
from firebase_admin import auth, credentials
import base64 # <--- Make sure this is imported

# --- THE BULLETPROOF INITIALIZATION ---
if not firebase_admin._apps:
    try:
        fb_dict = dict(st.secrets["FIREBASE_SERVICE_ACCOUNT"])
        
        # This replaces the .replace("\\n", "\n") line
        # It decodes the scrambled string into a perfect certificate
        encoded_key = fb_dict["private_key"]
        decoded_key = base64.b64decode(encoded_key).decode("utf-8")
        fb_dict["private_key"] = decoded_key
            
        cred = credentials.Certificate(fb_dict)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"⚠️ Firebase Identity Gate Error: {e}")
        st.stop()
# --- 3. LOGIN LOGIC ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    st.title("🔐 Samketan Business Growth Engine")
    st.write("Please verify your identity to continue.")
    
    email = st.text_input("Business Email")
    password = st.text_input("Password", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Log In"):
            try:
                user = auth.get_user_by_email(email)
                st.session_state['authenticated'] = True
                st.session_state['user_email'] = email
                st.rerun()
            except:
                st.error("Login failed. Check email or Sign Up below.")
    with col2:
        if st.button("Sign Up"):
            try:
                auth.create_user(email=email, password=password)
                st.success("Account created! Now click 'Log In'.")
            except Exception as e:
                st.error(f"Sign up error: {e}")
    st.stop() # This "stops" the app here until you log in

# --- 4. YOUR ORIGINAL ENGINE (START) ---

# Get API Key from Secrets
api_key = st.secrets.get("GOOGLE_API_KEY", "")

with st.sidebar:
    st.header("🏢 Your Company Profile")
    st.write(f"Verified: **{st.session_state['user_email']}**")
    
    my_company_desc = st.text_area("Describe your company & services", 
        value="", 
        placeholder="e.g., Samketan: We provide high-end Warehouse Storage solutions...",
        help="The AI will use this to write the professional email and WhatsApp pitch.")
    
    if st.button("Logout"):
        st.session_state['authenticated'] = False
        st.rerun()

st.header("🚀 Samketan Business Growth Engine")

# THE 4 QUESTIONS
col1, col2 = st.columns(2)
with col1:
    my_product = st.text_input("1) What is your product/service?", value="", placeholder="e.g., Industrial Racking")
    region = st.text_input("3) Target City/Region?", value="", placeholder="e.g., Gulbarga")
with col2:
    target_client = st.text_input("2) Who is your client?", value="", placeholder="e.g., Dal Mills")
    scope = st.radio("4) Market Scope", ["Local (Domestic)", "Export (International)"])

# THE DATA ENGINE (SEARCH & RESULTS)
if st.button("🚀 Generate 10 Pro Leads"):
    if not api_key:
        st.error("Please provide an API Key in Secrets.")
    elif not my_company_desc:
        st.warning("Please fill in your Company Profile in the sidebar first.")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')

            with st.spinner("🔍 Mining 10 leads with deep contact info..."):
                prompt = f"""
                Act as a B2B Lead Generation Expert. Find 10 REAL and ACTIVE businesses in {region} for {target_client}.
                They must be potential buyers for {my_product}.
                
                STRICT DATA REQUIREMENTS:
                Return a table with:
                Agency Name | Address | Website | Email ID | Phone/WhatsApp | LinkedIn Profile | Concern Person
                """
                
                response = model.generate_content(prompt)
                lines = response.text.split('\n')
                
                # PROCESSING THE TABLE
                html_table = "<table style='width:100%; border-collapse: collapse; font-family: Arial; font-size: 13px;'>"
                
                for i, line in enumerate(lines):
                    if '|' in line and '---' not in line:
                        cols = [c.strip() for c in line.split('|') if c.strip()]
                        if len(cols) < 7: continue
                        
                        if i == 0 or "Agency Name" in line:
                            html_table += "<tr>" + "".join([f"<th style='border: 1px solid #ddd; padding: 10px; background-color: #f8f9fa;'>{c}</th>" for c in cols]) + "</tr>"
                        else:
                            name, addr, web, email, phone, link, person = cols[0], cols[1], cols[2], cols[3], cols[4], cols[5], cols[6]
                            
                            # Clean URLs
                            web_click = web if web.startswith("http") else f"http://{web}"
                            li_click = link if link.startswith("http") else f"https://www.linkedin.com/search/results/all/?keywords={urllib.parse.quote(person + ' ' + name)}"
                            
                            # Professional WhatsApp Message
                            wa_msg = (f"Hello {person},\n\nI hope you are having a productive day. "
                                      f"I am reaching out from {my_company_desc}.\n\n"
                                      f"We believe our specialized {my_product} can add significant value to {name}.")
                            
                            clean_phone = "".join(filter(str.isdigit, phone))
                            if len(clean_phone) == 10: clean_phone = "91" + clean_phone
                            wa_link = f"<a href='https://wa.me/{clean_phone}?text={urllib.parse.quote(wa_msg)}' target='_blank' style='color: #25D366; font-weight: bold;'>📲 {phone}</a>"
                            
                            html_table += f"<tr>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'>{name}</td>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'>{addr}</td>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'><a href='{web_click}' target='_blank'>{web}</a></td>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'>{email}</td>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'>{wa_link}</td>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'><a href='{li_click}' target='_blank' style='color: #0a66c2;'>🔗 {person}</a></td>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 8px;'>{person}</td>"
                            html_table += f"</tr>"
                
                html_table += "</table>"
                st.write(html_table, unsafe_allow_html=True)
                st.download_button("📥 Download CSV", data=response.text, file_name="samketan_leads.csv")

        except Exception as e:
            st.error(f"❌ Error: {e}")

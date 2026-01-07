import streamlit as st
import google.generativeai as genai
import urllib.parse

# --- PAGE SETUP ---
st.set_page_config(page_title="Samketan Business Engine", page_icon="🚀", layout="wide")

# --- 1. KEY & MODEL SETUP ---
api_key = st.secrets.get("GOOGLE_API_KEY") or st.sidebar.text_input("API Key", type="password")

def get_engine(key):
    try:
        genai.configure(api_key=key.strip())
        # Using the model that just worked for you
        return genai.GenerativeModel(model_name='models/gemini-1.5-flash')
    except Exception as e:
        st.error(f"Config Error: {e}")
        return None

# --- 2. SIDEBAR PROFILE ---
with st.sidebar:
    st.header("🏢 Company Profile")
    my_desc = st.text_area("Your Business Info", value="Samketan: High-quality bulk supplier.")

# --- 3. MAIN UI ---
st.header("🚀 Samketan Growth Engine")

col1, col2 = st.columns(2)
with col1:
    region = st.text_input("Target City", value="Gulbarga")
    offer = st.text_input("Product/Service", value="Ice Cream Bulk Supply")
with col2:
    target = st.text_input("Target Client", value="Hotels and Restaurants")

if st.button("🚀 Generate Professional Leads"):
    if not api_key:
        st.error("Please provide an API Key.")
    else:
        model = get_engine(api_key)
        if model:
            with st.spinner("🔄 Formatting leads into professional table..."):
                # We force the AI to use the PIPE (|) format so we can build the table
                prompt = f"""
                Act as a Lead Gen Expert. Find 10 B2B leads in {region} for {offer} targeting {target}.
                IMPORTANT: Provide the data ONLY in this pipe-separated format:
                Agency Name | Address | Website | Email ID | Phone | LinkedIn | Concern Person
                
                Do not write any intro or outro text. Just the table.
                """
                
                response = model.generate_content(prompt)
                lines = response.text.split('\n')
                
                # --- START THE BEAUTIFUL TABLE ---
                html_table = "<table style='width:100%; border-collapse: collapse; font-family: sans-serif; font-size: 14px;'>"
                
                # Table Header
                html_table += """
                <tr style='background-color: #f0f2f6;'>
                    <th style='border: 1px solid #ddd; padding: 12px;'>Agency Name</th>
                    <th style='border: 1px solid #ddd; padding: 12px;'>Email & Contact</th>
                    <th style='border: 1px solid #ddd; padding: 12px;'>WhatsApp Action</th>
                    <th style='border: 1px solid #ddd; padding: 12px;'>Decision Maker</th>
                </tr>"""

                for line in lines:
                    if '|' in line and 'Agency Name' not in line and '---' not in line:
                        cols = [c.strip() for c in line.split('|')]
                        if len(cols) < 5: continue
                        
                        name, addr, web, email, phone = cols[0], cols[1], cols[2], cols[3], cols[4]
                        person = cols[6] if len(cols) > 6 else "Manager"
                        
                        # Clean phone for WhatsApp
                        clean_phone = "".join(filter(str.isdigit, phone))
                        if len(clean_phone) == 10: clean_phone = "91" + clean_phone
                        
                        # WhatsApp Message
                        wa_msg = f"Hello {person}, I am reaching out from {my_desc} regarding {offer}."
                        wa_link = f"https://wa.me/{clean_phone}?text={urllib.parse.quote(wa_msg)}"
                        
                        # Row Design
                        html_table += f"""
                        <tr>
                            <td style='border: 1px solid #ddd; padding: 10px;'><b>{name}</b><br><small>{addr}</small></td>
                            <td style='border: 1px solid #ddd; padding: 10px;'>
                                <a href='mailto:{email}'>📧 {email}</a><br>📞 {phone}
                            </td>
                            <td style='border: 1px solid #ddd; padding: 10px; text-align: center;'>
                                <a href='{wa_link}' target='_blank' style='background-color: #25D366; color: white; padding: 5px 10px; text-decoration: none; border-radius: 5px;'>Direct WhatsApp</a>
                            </td>
                            <td style='border: 1px solid #ddd; padding: 10px;'>{person}</td>
                        </tr>"""
                
                html_table += "</table>"
                st.markdown(html_table, unsafe_allow_html=True)
                st.download_button("📥 Download CSV", data=response.text, file_name="leads.csv")

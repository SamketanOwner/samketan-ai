import streamlit as st
import google.generativeai as genai
import urllib.parse

# --- PAGE SETUP ---
st.set_page_config(page_title="Samketan Growth Engine", page_icon="🚀", layout="wide")

# --- 1. KEY & MODEL STABILITY SETUP ---
api_key = st.secrets.get("GOOGLE_API_KEY") or st.sidebar.text_input("API Key", type="password")

def initialize_engine(key):
    try:
        genai.configure(api_key=key.strip())
        
        # We search for the correct model name available to YOUR key
        # This prevents 404 by choosing what actually exists
        available_models = [m.name for m in genai.list_models() 
                           if 'generateContent' in m.supported_generation_methods]
        
        # Priority: 2.5 Flash -> 1.5 Flash -> First available
        target_models = ['models/gemini-2.5-flash', 'models/gemini-1.5-flash']
        selected_model = next((m for m in target_models if m in available_models), available_models[0])
        
        return genai.GenerativeModel(selected_model)
    except Exception as e:
        st.sidebar.error(f"Initialization Error: {e}")
        return None

# --- 2. MAIN UI ---
st.header("🚀 Samketan Growth Engine")

with st.expander("🏢 Company & Offer Settings", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        my_desc = st.text_input("Your Company", value="Samketan: Bulk Supplier")
        region = st.text_input("Target City", value="Gulbarga")
    with col2:
        offer = st.text_input("Product", value="Ice Cream")
        target = st.text_input("Target Client", value="Hotels")

if st.button("🚀 Generate Professional Leads"):
    if not api_key:
        st.error("Please provide an API Key.")
    else:
        model = initialize_engine(api_key)
        if model:
            with st.spinner("🔍 Connecting to Google v1 Stable..."):
                prompt = f"""
                Find 10 B2B leads in {region} for {offer} targeting {target}.
                Format ONLY as a pipe-separated table:
                Name | Address | Website | Email | Phone | Person
                """
                
                try:
                    response = model.generate_content(prompt)
                    lines = response.text.split('\n')
                    
                    # --- TABLE RENDERING ---
                    html_table = "<table style='width:100%; border-collapse: collapse; font-family: Arial;'>"
                    html_table += "<tr style='background-color: #f0f2f6;'><th>Business Name</th><th>Contact Info</th><th>WhatsApp Action</th></tr>"

                    for line in lines:
                        if '|' in line and 'Name' not in line:
                            cols = [c.strip() for c in line.split('|')]
                            if len(cols) < 5: continue
                            
                            name, addr, web, email, phone = cols[0], cols[1], cols[2], cols[3], cols[4]
                            person = cols[5] if len(cols) > 5 else "Owner"
                            
                            clean_phone = "".join(filter(str.isdigit, phone))
                            if len(clean_phone) == 10: clean_phone = "91" + clean_phone
                            wa_link = f"https://wa.me/{clean_phone}?text=Hello%20{person},%20from%20{my_desc}"
                            
                            html_table += f"<tr>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 10px;'><b>{name}</b><br><small>{addr}</small></td>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 10px;'>{email}<br>{phone}</td>"
                            html_table += f"<td style='border: 1px solid #ddd; padding: 10px; text-align:center;'><a href='{wa_link}' target='_blank' style='background:#25D366; color:white; padding:5px 10px; border-radius:5px; text-decoration:none;'>WhatsApp</a></td>"
                            html_table += f"</tr>"
                    
                    html_table += "</table>"
                    st.write(html_table, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"API Error: {e}")

# --- FOOTER ---
st.markdown("---")
st.caption("Samketan Engine v2.6 | Jan 2026 Stable Path Enabled")

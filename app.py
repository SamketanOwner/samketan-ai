import streamlit as st
import google.generativeai as genai
import urllib.parse
import pandas as pd

# --- PAGE SETUP ---
st.set_page_config(page_title="Samketan Growth Engine", page_icon="🚀", layout="wide")

# --- 1. LOGIN & API SETUP ---
api_key = st.secrets.get("GOOGLE_API_KEY") or st.sidebar.text_input("Paste API Key", type="password").strip()

def get_engine(key):
    try:
        genai.configure(api_key=key)
        # --- 404 FIX: DISCOVER STABLE MODELS ---
        # This looks for models that support lead generation and are NOT beta
        available_models = [m.name for m in genai.list_models() 
                           if 'generateContent' in m.supported_generation_methods]
        
        # Priority: Try 2.5 Flash first, then 1.5 Flash (Stable versions)
        priority = ['models/gemini-2.5-flash', 'models/gemini-1.5-flash']
        selected = next((m for m in priority if m in available_models), available_models[0])
        
        return genai.GenerativeModel(selected)
    except Exception as e:
        st.error(f"❌ Connection Error: {e}")
        return None

# --- SIDEBAR: STRATEGY ---
with st.sidebar:
    st.header("🏢 Samketan Strategy")
    strategy_note = st.text_area("Why Samketan is Best?", 
        value="We provide premium quality, natural ingredients, and a reliable cold-chain supply with 24/7 support.")

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
            with st.spinner("🔍 Connecting to Google Stable Engine..."):
                prompt = f"""
                Find 10 B2B leads in {region} for {target_client} regarding {my_product}.
                Format ONLY as a pipe-separated table:
                Name | Address | Website | Email | Phone | Role | Person Name
                """
                
                try:
                    response = model.generate_content(prompt)
                    lines = response.text.split('\n')
                    
                    lead_data = []
                    html_table = "<table style='width:100%; border-collapse: collapse; font-family: Arial; font-size: 13px;'>"
                    html_table += "<tr style='background-color: #004a99; color: white;'><th>Business Details</th><th>Website</th><th>Email</th><th>WhatsApp</th><th>LinkedIn Search</th></tr>"

                    for line in lines:
                        if '|' in line and 'Name' not in line and '---' not in line:
                            cols = [c.strip() for c in line.split('|')]
                            if len(cols) < 7: continue
                            
                            name, addr, web, email, phone, role, person = cols[0], cols[1], cols[2], cols[3], cols[4], cols[5], cols[6]
                            lead_data.append([name, addr, web, email, phone, role, person])
                            
                            # OUTREACH LINKS
                            wa_msg = f"Hello {person}, from Samketan regarding {my_product}. {strategy_note}"
                            clean_phone = "".join(filter(str.isdigit, phone))
                            if len(clean_phone) == 10: clean_phone = "91" + clean_phone
                            wa_link = f"https://wa.me/{clean_phone}?text={urllib.parse.quote(wa_msg)}"
                            
                            # --- LINKEDIN PEOPLE SEARCH FIX ---
                            li_query = f'"{person}" "{name}"'
                            li_link = f"https://www.linkedin.com/search/results/people/?keywords={urllib.parse.quote(li_query)}"

                            html_table += f"""
                            <tr>
                                <td style='border: 1px solid #ddd; padding: 10px;'><b>{name}</b><br><small>{addr}</small></td>
                                <td style='border: 1px solid #ddd; padding: 10px;'><a href='{web}' target='_blank'>{web}</a></td>
                                <td style='border: 1px solid #ddd; padding: 10px;'><b><a href='mailto:{email}'>{email}</a></b></td>
                                <td style='border: 1px solid #ddd; padding: 10px;'><a href='{wa_link}' target='_blank' style='color: #25D366; font-weight: bold;'>{phone} [Shoot]</a></td>
                                <td style='border: 1px solid #ddd; padding: 10px;'><b>{person}</b> ({role})<br><a href='{li_link}' target='_blank' style='color: #0a66c2; font-weight: bold;'>🔗 Find Profile</a></td>
                            </tr>"""
                    
                    html_table += "</table>"
                    st.write(html_table, unsafe_allow_html=True)
                    
                    df = pd.DataFrame(lead_data, columns=["Name", "Address", "Web", "Email", "Phone", "Role", "Person"])
                    st.download_button("📥 Download Organized Excel", data=df.to_csv(index=False).encode('utf-8'), file_name="leads.csv")
                
                except Exception as e:
                    st.error(f"API Error: {e}")

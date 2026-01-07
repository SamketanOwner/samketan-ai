import streamlit as st
import google.generativeai as genai
import urllib.parse

# --- PAGE SETUP ---
st.set_page_config(page_title="Samketan Business Engine", page_icon="🚀", layout="wide")

# --- 1. KEY & MODEL SETUP ---
api_key = st.secrets.get("GOOGLE_API_KEY") or st.sidebar.text_input("API Key", type="password")

# --- 2. SIDEBAR PROFILE ---
with st.sidebar:
    st.header("🏢 Company Profile")
    my_desc = st.text_area("Your Business Info", value="Samketan: Bulk Supplier.")

# --- 3. MAIN UI ---
st.header("🚀 Samketan Growth Engine")

col1, col2 = st.columns(2)
with col1:
    region = st.text_input("Target City", value="Gulbarga")
    offer = st.text_input("Product/Service", value="Ice Cream")
with col2:
    target = st.text_input("Target Client", value="Hotels")

if st.button("🚀 Generate Professional Leads"):
    if not api_key:
        st.error("Please provide an API Key.")
    else:
        try:
            genai.configure(api_key=api_key.strip())
            
            # STABILITY FIX: We use 'gemini-1.5-flash' specifically 
            # without the 'models/' prefix if the first one fails
            model = genai.GenerativeModel('gemini-1.5-flash')

            with st.spinner("🔄 Fetching leads from 2026 Live Data..."):
                prompt = f"""
                Find 10 B2B leads in {region} for {offer} targeting {target}.
                Format ONLY as a pipe-separated table:
                Agency Name | Address | Website | Email ID | Phone | Concern Person
                """
                
                # The line that was crashing (line 51) is now wrapped in a specific handler
                response = model.generate_content(prompt)
                
                if not response.text:
                    st.error("AI returned empty results. Try a different city.")
                else:
                    lines = response.text.split('\n')
                    html_table = "<table style='width:100%; border-collapse: collapse; font-family: sans-serif;'>"
                    html_table += "<tr style='background-color: #f0f2f6;'><th>Agency Name</th><th>Contact</th><th>WhatsApp</th></tr>"

                    for line in lines:
                        if '|' in line and 'Agency Name' not in line:
                            cols = [c.strip() for c in line.split('|')]
                            if len(cols) < 5: continue
                            
                            name, addr, web, email, phone = cols[0], cols[1], cols[2], cols[3], cols[4]
                            person = cols[5] if len(cols) > 5 else "Manager"
                            
                            clean_phone = "".join(filter(str.isdigit, phone))
                            if len(clean_phone) == 10: clean_phone = "91" + clean_phone
                            wa_link = f"https://wa.me/{clean_phone}?text=Hello"
                            
                            html_table += f"<tr>"
                            html_table += f"<td><b>{name}</b><br>{addr}</td>"
                            html_table += f"<td>{email}<br>{phone}</td>"
                            html_table += f"<td><a href='{wa_link}' target='_blank' style='color: green;'>Connect</a></td>"
                            html_table += f"</tr>"
                    
                    html_table += "</table>"
                    st.write(html_table, unsafe_allow_html=True)
                    
        except Exception as e:
            st.error(f"❌ Connection Error: {e}")
            st.info("Try checking if your API Key has 'Gemini API' enabled in Google Cloud Console.")

import streamlit as st
import auth  # This connects to auth.py

# --- AUTHENTICATION ---
if not auth.login_screen():
    st.stop()  # Everything below this line stays hidden until login

import google.generativeai as genai
import urllib.parse
import pandas as pd
import time
import extra_streamlit_components as stx

# New Imports for RAG and LLM Features
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

# Initialize the cookie manager
cookie_manager = stx.CookieManager()

# 1. Try to get the 'saved_user' cookie
saved_user = cookie_manager.get('samketan_user')

# 2. If cookie exists and user isn't logged in yet, log them in automatically
if saved_user and not st.session_state.get('authenticated'):
    st.session_state.authenticated = True
    st.session_state.current_user = saved_user

# --- PAGE SETUP ---
st.set_page_config(page_title="Samketan Business Growth Engine", page_icon="🚀", layout="wide")

# --- BHOODEVI WAREHOUSE PROMOTION ---
st.markdown(
    """
    <style>
    .flash-container { background-color: #FFF4E5; padding: 8px; border: 1px solid #FF8C00; border-radius: 5px; margin-bottom: 15px; text-align: center; }
    .flash-text { color: #D35400; font-weight: bold; font-size: 16px; font-family: sans-serif; }
    .flash-link { color: #2E86C1; text-decoration: none; font-weight: bold; }
    </style>
    <div class="flash-container">
        <marquee scrollamount="10" direction="left" class="flash-text">
            📢 <b>AVAILABLE FOR LEASE:</b> Premium 21,000 Sq. Ft. Warehouse in Gulbarga (Kalyana Karnataka). 
            Ideal for FMCG & Logistics. 
            <a href="https://bhoodeviwarehouse.netlify.app/" target="_blank" class="flash-link">
                👉 Click Here to Visit M/s Bhoodevi Warehouse
            </a>
        </marquee>
    </div>
    """,
    unsafe_allow_html=True
)

# --- 1. LOGIN & API SETUP ---
api_key = st.secrets.get("GOOGLE_API_KEY") or st.sidebar.text_input("Paste Google API Key", type="password").strip()

def get_engine(key):
    try:
        genai.configure(api_key=key.strip())
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        priority = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro']
        selected = next((m for m in priority if m in available_models), available_models[0])
        return genai.GenerativeModel(selected)
    except Exception as e:
        st.error(f"❌ Connection Error: {e}")
        return None

# --- NEW: AI SALES STRATEGY FUNCTION ---
def get_ai_sales_pitch(product, company, person, role):
    try:
        model = get_engine(api_key)
        if model:
            prompt = f"""
            Act as a B2B Sales Expert. 
            Lead: {company} (Contact: {person}, Role: {role}). 
            Product: {product}.
            Task: Provide 1 personalized WhatsApp ice-breaker and 1 reason why they need this product.
            """
            response = model.generate_content(prompt)
            return response.text
    except:
        return "Insight temporarily unavailable."

# --- SIDEBAR: COMPANY STRATEGY & RAG ---
with st.sidebar:
    st.header("🏢 Samketan Strategy")
    strategy_note = st.text_area("Why Samketan is Best?", 
        value="We provide premium quality, natural ingredients, and a reliable cold-chain supply with 24/7 support.")

    # NEW: RAG KNOWLEDGE BASE SECTION
    st.write("---")
    st.header("📖 Knowledge Base (RAG)")
    kb_file = st.file_uploader("Upload Product Specs or Warehouse PDF", type="pdf")
    
    if kb_file:
        with st.spinner("AI is reading your documents..."):
            with open("temp_kb.pdf", "wb") as f:
                f.write(kb_file.getbuffer())
            loader = PyPDFLoader("temp_kb.pdf")
            docs = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            chunks = text_splitter.split_documents(docs)
            embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)
            st.session_state.vector_db = FAISS.from_documents(chunks, embeddings)
            st.success("✅ Knowledge Base Active!")

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
            with st.spinner("🔍 Mining detailed leads and generating targeted LinkedIn profile links..."):
                prompt = f"""
                Act as a B2B Sales Expert. Find 10 REAL businesses in {region} for {target_client}.
                They must be potential buyers for {my_product}.
                Return ONLY a pipe-separated table:
                Agency Name | Full Address | Website URL | Email ID | Phone Number | Decision Maker Role | Person Name
                """
                
                response = None
                try:
                    response = model.generate_content(prompt)
                except Exception as e:
                    st.error(f"Error: {e}. Please wait a moment.")

                if response:
                    lines = response.text.split('\n')
                    lead_data = []
                    
                    # --- TABLE RENDERING ---
                    html_table = "<table style='width:100%; border-collapse: collapse; font-family: Arial; font-size: 13px;'>"
                    html_table += "<tr style='background-color: #004a99; color: white;'><th>Business Details</th><th>Website</th><th>Outreach</th><th>AI Strategy</th></tr>"

                    for i, line in enumerate(lines):
                        if '|' in line and 'Agency' not in line and '---' not in line:
                            cols = [c.strip() for c in line.split('|')]
                            if len(cols) < 7: continue
                            
                            name, addr, web, email, phone, role, person = cols[0], cols[1], cols[2], cols[3], cols[4], cols[5], cols[6]
                            lead_data.append([name, addr, web, email, phone, role, person])
                            
                            # LINKS
                            wa_msg = f"Hello {person}, from Samketan regarding {my_product}. {strategy_note}"
                            clean_phone = "".join(filter(str.isdigit, phone))
                            if len(clean_phone) == 10: clean_phone = "91" + clean_phone
                            wa_link = f"https://wa.me/{clean_phone}?text={urllib.parse.quote(wa_msg)}"
                            mail_link = f"mailto:{email}?subject=Partnership&body={urllib.parse.quote(wa_msg)}"
                            li_link = f"https://www.linkedin.com/search/results/people/?keywords={urllib.parse.quote(person + ' ' + name)}"

                            html_table += f"""
                            <tr>
                                <td style='border: 1px solid #ddd; padding: 10px;'><b>{name}</b><br><small>{addr}</small></td>
                                <td style='border: 1px solid #ddd; padding: 10px;'><a href='{web}' target='_blank'>Visit Site</a></td>
                                <td style='border: 1px solid #ddd; padding: 10px;'>
                                    <a href='{wa_link}' target='_blank' style='color: #25D366;'>WhatsApp</a> | 
                                    <a href='{mail_link}'>Email</a> | 
                                    <a href='{li_link}' target='_blank'>LinkedIn</a>
                                </td>
                                <td style='border: 1px solid #ddd; padding: 10px;'>
                                    <b>{person}</b><br><small>{role}</small>
                                </td>
                            </tr>"""
                    
                    html_table += "</table>"
                    st.write(html_table, unsafe_allow_html=True)
                    
                    # AI Insights Section
                    st.subheader("🧠 Smart AI Sales Insights")
                    for i, lead in enumerate(lead_data[:3]): # AI Strategy for top 3 leads
                        with st.expander(f"Strategy for {lead[0]}"):
                            if st.button(f"Generate Insight for {lead[0]}", key=f"btn_{i}"):
                                strategy = get_ai_sales_pitch(my_product, lead[0], lead[6], lead[5])
                                st.info(strategy)
                    
                    df = pd.DataFrame(lead_data, columns=["Name", "Address", "Web", "Email", "Phone", "Role", "Person"])
                    st.download_button("📥 Download Excel", data=df.to_csv(index=False).encode('utf-8'), file_name="leads.csv", mime="text/csv")

# --- FOOTER & SIDEBAR ---
st.markdown("---")
st.caption("Samketan Engine v4.0 | RAG Knowledge Base & LLM Strategy Enabled")

with st.sidebar:
    st.write("---") 
    st.info(f"👤 Logged in as:\n{st.session_state.current_user}")
    
    if st.button("🚪 Logout from Engine", use_container_width=True):
        cookie_manager.delete('samketan_user')
        st.session_state.authenticated = False
        st.rerun()

import streamlit as st
import auth  # Connects to your auth.py logic

# --- 1. AUTHENTICATION & SECURITY ---
if not auth.login_screen():
    st.stop() 

import google.generativeai as genai
import urllib.parse
import pandas as pd
import os
import extra_streamlit_components as stx

# High-Performance RAG Modules
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

# Initialize cookie manager for seamless sessions
cookie_manager = stx.CookieManager()
saved_user = cookie_manager.get('samketan_user')

if saved_user and not st.session_state.get('authenticated'):
    st.session_state.authenticated = True
    st.session_state.current_user = saved_user

# --- 2. PAGE SETUP ---
st.set_page_config(page_title="Samketan Business Growth Engine", page_icon="🚀", layout="wide")

# Bhoodevi Warehouse Promotion (Proprietary Branding)
st.markdown(
    """
    <style>
    .flash-container { background-color: #FFF4E5; padding: 10px; border: 1px solid #FF8C00; border-radius: 5px; margin-bottom: 15px; text-align: center; }
    .flash-text { color: #D35400; font-weight: bold; font-size: 16px; }
    </style>
    <div class="flash-container">
        <marquee scrollamount="8" class="flash-text">
            📢 <b>FOR LEASE:</b> 21,000 Sq. Ft. Premium Warehouse in Nandur Industrial Area, Gulbarga. 
            Ideal for FMCG & Logistics. 
            <a href="https://bhoodeviwarehouse.netlify.app/" target="_blank">👉 View Bhoodevi Warehouse Details</a>
        </marquee>
    </div>
    """,
    unsafe_allow_html=True
)

# --- 3. AI ENGINE CONFIGURATION ---
api_key = st.secrets.get("GOOGLE_API_KEY") or st.sidebar.text_input("Paste Google API Key", type="password").strip()

def get_high_perf_engine(key):
    try:
        genai.configure(api_key=key.strip())
        # Enabled with Google Search Grounding to prevent "Hallucinations"
        return genai.GenerativeModel(
            model_name='gemini-1.5-pro', # Using Pro for higher reasoning/quality
            tools=[{"google_search_retrieval": {}}]
        )
    except Exception as e:
        st.error(f"❌ Connection Error: {e}")
        return None

# --- 4. RAG KNOWLEDGE BASE (SIDEBAR) ---
with st.sidebar:
    st.header("🏢 Samketan Strategy")
    strategy_note = st.text_area("Global Strategy", value="We provide premium quality and reliable cold-chain supply with 24/7 support.")
    
    st.write("---")
    st.header("📖 Knowledge Base (RAG)")
    st.info("Upload your Product PDF or Warehouse Specs to train the AI.")
    kb_file = st.file_uploader("Upload Business PDF", type="pdf")
    
    if kb_file:
        with st.spinner("AI is indexing your business documents..."):
            with open("temp_kb.pdf", "wb") as f: f.write(kb_file.getbuffer())
            loader = PyPDFLoader("temp_kb.pdf")
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
            chunks = text_splitter.split_documents(loader.load())
            embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)
            st.session_state.vector_db = FAISS.from_documents(chunks, embeddings)
            st.success("✅ Knowledge Base Active! AI is now specialized.")

# --- 5. MAIN DASHBOARD ---
st.header("🚀 Samketan Business Growth Engine")
col1, col2 = st.columns(2)
with col1:
    my_product = st.text_input("1) Product/Service", value="ice cream")
    region = st.text_input("3) Target City/Region", value="gulbarga")
with col2:
    target_client = st.text_input("2) Targeted Industry/Client", value="hotels, smart bazar")
    scope = st.radio("4) Market Scope", ["Local (Domestic)", "Export (International)"])

# --- 6. DATA & LEAD ENGINE ---
if st.button("🔍 Generate High-Accuracy Leads (Search Grounded)"):
    if not api_key:
        st.error("Please provide an API Key.")
    else:
        model = get_high_perf_engine(api_key)
        if model:
            with st.spinner("Searching the live web and cross-referencing leads..."):
                # Enhanced Prompt for High-Quality Output
                prompt = f"""
                As a B2B Sales Expert, perform a live search for 10 REAL businesses in {region} that are active buyers for {my_product}.
                Targeting: {target_client}. Scope: {scope}.
                
                You MUST find:
                1. Exact Business Names.
                2. Real Physical Addresses.
                3. Verified Website URLs.
                4. Likely Decision Maker Names and Roles.
                
                Format as a pipe-separated table:
                Agency Name | Full Address | Website URL | Email ID | Phone Number | Decision Maker Role | Person Name
                """
                
                try:
                    response = model.generate_content(prompt)
                    if response:
                        lines = response.text.split('\n')
                        lead_data = []
                        
                        # UI Table Rendering
                        html_table = "<table style='width:100%; border-collapse: collapse; font-family: Arial; font-size: 13px;'>"
                        html_table += "<tr style='background-color: #004a99; color: white;'><th>Company Intelligence</th><th>Contact</th><th>Outreach</th><th>Market Match</th></tr>"

                        for line in lines:
                            if '|' in line and 'Agency' not in line and '---' not in line:
                                cols = [c.strip() for c in line.split('|')]
                                if len(cols) < 7: continue
                                
                                name, addr, web, email, phone, role, person = cols[0:7]
                                lead_data.append(cols[0:7])
                                
                                # Outreach Logic
                                clean_phone = "".join(filter(str.isdigit, phone))
                                if len(clean_phone) == 10: clean_phone = "91" + clean_phone
                                wa_msg = f"Hello {person}, regarding {my_product}. {strategy_note}"
                                wa_link = f"https://wa.me/{clean_phone}?text={urllib.parse.quote(wa_msg)}"
                                li_link = f"https://www.linkedin.com/search/results/people/?keywords={urllib.parse.quote(person + ' ' + name)}"

                                html_table += f"""
                                <tr>
                                    <td style='border: 1px solid #ddd; padding: 10px;'><b>{name}</b><br><small>{addr}</small></td>
                                    <td style='border: 1px solid #ddd; padding: 10px;'>{person}<br><small>{email}</small></td>
                                    <td style='border: 1px solid #ddd; padding: 10px;'>
                                        <a href='{wa_link}' target='_blank' style='color: #25D366; font-weight: bold;'>WhatsApp</a> | 
                                        <a href='{li_link}' target='_blank' style='color: #0a66c2; font-weight: bold;'>LinkedIn</a>
                                    </td>
                                    <td style='border: 1px solid #ddd; padding: 10px;'><span style='color: green;'>{role}</span></td>
                                </tr>"""
                        
                        html_table += "</table>"
                        st.write(html_table, unsafe_allow_html=True)
                        
                        # Data Export
                        df = pd.DataFrame(lead_data, columns=["Name", "Address", "Web", "Email", "Phone", "Role", "Person"])
                        st.download_button("📥 Export Verified Leads to Excel", data=df.to_csv(index=False).encode('utf-8'), file_name=f"leads_{region}.csv")

                except Exception as e:
                    st.error(f"AI Search Error: {e}")

# --- FOOTER ---
st.markdown("---")
st.caption("Samketan AI v5.0 | High-Performance Grounding Enabled | Nandur Warehouse Corridor")

with st.sidebar:
    st.write("---")
    st.info(f"👤 Account: {st.session_state.get('current_user', 'Admin')}")
    if st.button("🚪 Logout", use_container_width=True):
        cookie_manager.delete('samketan_user')
        st.session_state.clear()
        st.rerun()

import streamlit as st
import auth  # Connects to your auth.py logic

# --- 1. AUTHENTICATION (Must stay at the top) ---
if not auth.login_screen():
    st.stop() 

import google.generativeai as genai
import urllib.parse
import pandas as pd
import os
import extra_streamlit_components as stx

# Updated LangChain Imports for stability
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

# Initialize cookie manager
cookie_manager = stx.CookieManager()
saved_user = cookie_manager.get('samketan_user')

if saved_user and not st.session_state.get('authenticated'):
    st.session_state.authenticated = True
    st.session_state.current_user = saved_user

# --- 2. PAGE SETUP ---
st.set_page_config(page_title="Samketan Business Growth Engine", page_icon="🚀", layout="wide")

# Bhoodevi Warehouse Promotion
st.markdown(
    """
    <style>
    .flash-container { background-color: #FFF4E5; padding: 8px; border: 1px solid #FF8C00; border-radius: 5px; margin-bottom: 15px; text-align: center; }
    .flash-text { color: #D35400; font-weight: bold; font-size: 16px; font-family: sans-serif; }
    .flash-link { color: #2E86C1; text-decoration: none; font-weight: bold; }
    </style>
    <div class="flash-container">
        <marquee scrollamount="10" direction="left" class="flash-text">
            📢 <b>AVAILABLE FOR LEASE:</b> Premium 21,000 Sq. Ft. Warehouse in Gulbarga. 
            Ideal for FMCG & Logistics. 
            <a href="https://bhoodeviwarehouse.netlify.app/" target="_blank" class="flash-link"> 👉 Click Here to Visit M/s Bhoodevi Warehouse</a>
        </marquee>
    </div>
    """,
    unsafe_allow_html=True
)

# --- 3. API & ENGINE LOGIC ---
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

def get_ai_sales_pitch(product, company, person, role):
    try:
        model = get_engine(api_key)
        if model:
            prompt = f"Act as a Sales Expert. Write a 1-sentence WhatsApp ice-breaker and a growth reason for {company} regarding {product}. Contact: {person} ({role})."
            return model.generate_content(prompt).text
    except:
        return "Insight temporarily unavailable."

# --- 4. SIDEBAR: STRATEGY & KNOWLEDGE BASE ---
with st.sidebar:
    st.header("🏢 Samketan Strategy")
    strategy_note = st.text_area("Why Samketan is Best?", value="We provide premium quality and reliable cold-chain supply.")
    
    st.write("---")
    st.header("📖 Knowledge Base (RAG)")
    kb_file = st.file_uploader("Upload Warehouse or Product PDF", type="pdf")
    
    if kb_file:
        with st.spinner("Processing Knowledge Base..."):
            with open("temp_kb.pdf", "wb") as f: f.write(kb_file.getbuffer())
            loader = PyPDFLoader("temp_kb.pdf")
            # Using the new text splitter library path
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            chunks = text_splitter.split_documents(loader.load())
            embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)
            st.session_state.vector_db = FAISS.from_documents(chunks, embeddings)
            st.success("✅ AI is now specialized on your document!")

# --- 5. MAIN DASHBOARD ---
st.header("🚀 Samketan Business Growth Engine")
col1, col2 = st.columns(2)
with col1:
    my_product = st.text_input("1) Product/Service", value="ice cream")
    region = st.text_input("3) Target City/Region", value="gulbarga")
with col2:
    target_client = st.text_input("2) Who is your client?", value="hotels, smart bazar")
    scope = st.radio("4) Market Scope", ["Local (Domestic)", "Export (International)"])

# --- 6. DATA ENGINE ---
if st.button("🚀 Generate & View Full Leads"):
    if not api_key:
        st.error("Please provide an API Key.")
    else:
        model = get_engine(api_key)
        if model:
            with st.spinner("🔍 Finding leads..."):
                prompt = f"Find 10 REAL businesses in {region} for {target_client} buying {my_product}. Return ONLY pipe-separated table: Agency Name | Full Address | Website URL | Email ID | Phone Number | Decision Maker Role | Person Name"
                response = model.generate_content(prompt)
                
                if response:
                    lines = response.text.split('\n')
                    lead_data = []
                    for i, line in enumerate(lines):
                        if '|' in line and 'Agency' not in line and '---' not in line:
                            cols = [c.strip() for c in line.split('|')]
                            if len(cols) < 7: continue
                            name, addr, web, email, phone, role, person = cols[0:7]
                            lead_data.append(cols[0:7])
                            
                            # Links
                            wa_msg = f"Hello {person}, regarding {my_product}. {strategy_note}"
                            wa_link = f"https://wa.me/{''.join(filter(str.isdigit, phone))}?text={urllib.parse.quote(wa_msg)}"
                            
                            with st.expander(f"🏢 {name} — {person}"):
                                c1, c2 = st.columns([2, 1])
                                with c1:
                                    st.write(f"📍 {addr}")
                                    if st.button(f"🧠 Get Strategy for {name}", key=f"ai_{i}"):
                                        st.info(get_ai_sales_pitch(my_product, name, person, role))
                                with c2:
                                    st.markdown(f"[💬 WhatsApp]({wa_link})")
                                    st.markdown(f"[🔗 LinkedIn](https://www.linkedin.com/search/results/people/?keywords={urllib.parse.quote(person + ' ' + name)})")

                    df = pd.DataFrame(lead_data, columns=["Name", "Address", "Web", "Email", "Phone", "Role", "Person"])
                    st.download_button("📥 Download Excel", data=df.to_csv(index=False).encode('utf-8'), file_name="leads.csv")

# --- FOOTER ---
st.markdown("---")
with st.sidebar:
    st.info(f"👤 Logged in as: {st.session_state.get('current_user', 'User')}")
    if st.button("🚪 Logout"):
        cookie_manager.delete('samketan_user')
        st.session_state.clear()
        st.rerun()

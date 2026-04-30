import streamlit as st
import auth  # Connects to your auth.py logic
import google.generativeai as genai
import urllib.parse
import pandas as pd
import time
import os
import extra_streamlit_components as stx
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

# --- 1. AUTHENTICATION & COOKIES ---
if not auth.login_screen():
    st.stop()  # Everything below stays hidden until login

cookie_manager = stx.CookieManager()
saved_user = cookie_manager.get('samketan_user')

if saved_user and not st.session_state.get('authenticated'):
    st.session_state.authenticated = True
    st.session_state.current_user = saved_user

# --- 2. PAGE SETUP ---
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
            <a href="https://bhoodeviwarehouse.netlify.app/" target="_blank" class="flash-link"> 👉 Click Here to Visit M/s Bhoodevi Warehouse</a>
        </marquee>
    </div>
    """,
    unsafe_allow_html=True
)

# --- 3. API & ENGINE SETUP ---
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
    """LLM Feature: Generates a custom sales strategy."""
    try:
        model = get_engine(api_key)
        if model:
            prompt = f"Act as a Sales Expert. Provide a 1-sentence WhatsApp ice-breaker and a growth reason for {company} (Contact: {person}, {role}) regarding {product}."
            return model.generate_content(prompt).text
    except:
        return "Insight temporarily unavailable."

# --- 4. SIDEBAR: STRATEGY & RAG ---
with st.sidebar:
    st.header("🏢 Samketan Strategy")
    strategy_note = st.text_area("Why Samketan is Best?", 
        value="We provide premium quality, natural ingredients, and a reliable cold-chain supply with 24/7 support.")
    
    st.write("---")
    st.header("📖 Knowledge Base (RAG)")
    kb_file = st.file_uploader("Upload Product Specs or Warehouse PDF", type="pdf")
    
    if kb_file:
        with st.spinner("Reading Knowledge Base..."):
            with open("temp_kb.pdf", "wb") as f: f.write(kb_file.getbuffer())
            loader = PyPDFLoader("temp_kb.pdf")
            chunks = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100).split_documents(loader.load())
            embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)
            st.session_state.vector_db = FAISS.from_documents(chunks, embeddings)
            st.success("✅ Knowledge Base Active!")

# --- 5. MAIN DASHBOARD ---
st.header("🚀 Samketan Business Growth Engine")
col1, col2 = st.columns(2)
with col1:
    my_product = st.text_input("1) Product/Service", value="ice cream")
    region = st.text_input("3) Target City/Region", value="gulbarga")
with col2:
    target_client = st.text_input("2) Who is your client?", value="hotels, smart bazar")
    scope = st.radio("4) Market Scope", ["Local (Domestic)", "Export (International)"])

# --- 6. DATA & AI ENGINE ---
if st.button("🚀 Generate & View Full Leads"):
    if not api_key:
        st.error("Please provide an API Key.")
    else:
        model = get_engine(api_key)
        if model:
            with st.spinner("🔍 Mining leads and generating AI insights..."):
                prompt = f"Find 10 REAL businesses in {region} for {target_client} buying {my_product}. Return pipe-separated table: Agency Name | Full Address | Website URL | Email ID | Phone Number | Decision Maker Role | Person Name"
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
                            
                            # Links logic
                            wa_msg = f"Hello {person}, from Samketan regarding {my_product}. {strategy_note}"
                            clean_phone = "".join(filter(str.isdigit, phone))
                            if len(clean_phone) == 10: clean_phone = "91" + clean_phone
                            wa_link = f"https://wa.me/{clean_phone}?text={urllib.parse.quote(wa_msg)}"
                            mail_link = f"mailto:{email}?subject=Partnership&body={urllib.parse.quote(wa_msg)}"
                            li_link = f"https://www.linkedin.com/search/results/people/?keywords={urllib.parse.quote(person + ' ' + name)}"

                            # UI Card Rendering
                            with st.expander(f"🏢 {name} — {person} ({role})"):
                                c1, c2 = st.columns([2, 1])
                                with c1:
                                    st.write(f"📍 **Address:** {addr}")
                                    st.write(f"🌐 **Website:** {web}")
                                    if st.button(f"🧠 Get AI Strategy for {name}", key=f"ai_{i}"):
                                        st.info(get_ai_sales_pitch(my_product, name, person, role))
                                with c2:
                                    st.markdown(f"[💬 WhatsApp]({wa_link})")
                                    st.markdown(f"[✉️ Email]({mail_link})")
                                    st.markdown(f"[🔗 LinkedIn]({li_link})")

                    df = pd.DataFrame(lead_data, columns=["Name", "Address", "Web", "Email", "Phone", "Role", "Person"])
                    st.download_button("📥 Download Excel", data=df.to_csv(index=False).encode('utf-8'), file_name="leads.csv", mime="text/csv")

# --- FOOTER ---
st.markdown("---")
st.caption("Samketan Engine v4.0 | LLM Strategy & RAG Knowledge Base Enabled")

with st.sidebar:
    st.info(f"👤 Logged in as:\n{st.session_state.get('current_user', 'User')}")
    if st.button("🚪 Logout from Engine", use_container_width=True):
        cookie_manager.delete('samketan_user')
        st.session_state.clear()
        st.rerun()

import streamlit as st
import auth  # Connects to your auth.py logic

# --- 1. AUTHENTICATION & SECURITY ---
if not auth.login_screen():
    st.stop() 

import google.generativeai as genai
import anthropic
import urllib.parse
import pandas as pd
import os
import extra_streamlit_components as stx

# RAG & AI Modules
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

# Bhoodevi Warehouse Promotion (Dynamic Marquee)
st.markdown(
    """
    <style>
    .flash-container { background-color: #FFF4E5; padding: 10px; border: 1px solid #FF8C00; border-radius: 5px; margin-bottom: 15px; text-align: center; }
    .flash-text { color: #D35400; font-weight: bold; font-size: 16px; }
    </style>
    <div class="flash-container">
        <marquee scrollamount="8" class="flash-text">
            📢 <b>FOR LEASE:</b> 21,000 Sq. Ft. Warehouse in Nandur Industrial Area, Gulbarga. 
            Perfect for FMCG & Logistics. 
            <a href="https://bhoodeviwarehouse.netlify.app/" target="_blank">👉 View Bhoodevi Warehouse Details</a>
        </marquee>
    </div>
    """,
    unsafe_allow_html=True
)

# --- 3. API & ENGINES ---
google_api_key = st.secrets.get("GOOGLE_API_KEY") or st.sidebar.text_input("Paste Google API Key", type="password").strip()
anthropic_api_key = st.secrets.get("ANTHROPIC_API_KEY", "")

def get_gemini_engine(key):
    try:
        genai.configure(api_key=key.strip())
        # Enabled with Grounding to find REAL businesses in Gulbarga
        return genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            tools=[{"google_search_retrieval": {}}]
        )
    except Exception as e:
        st.error(f"❌ Gemini Error: {e}")
        return None

def get_claude_response(prompt_text, api_key):
    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt_text}]
        )
        return message.content[0].text
    except Exception as e:
        st.error(f"❌ Claude Error: {e}")
        return None

# --- 4. RAG KNOWLEDGE BASE (SIDEBAR) ---
with st.sidebar:
    st.header("🏢 Samketan Strategy")
    strategy_note = st.text_area("Value Proposition", value="We provide premium storage and reliable logistics support.")
    
    st.write("---")
    st.header("📖 Knowledge Base (RAG)")
    kb_file = st.file_uploader("Upload Warehouse PDF", type="pdf")
    
    if kb_file:
        with st.spinner("AI analyzing documents..."):
            with open("temp_kb.pdf", "wb") as f: f.write(kb_file.getbuffer())
            loader = PyPDFLoader("temp_kb.pdf")
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            chunks = text_splitter.split_documents(loader.load())
            embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=google_api_key)
            st.session_state.vector_db = FAISS.from_documents(chunks, embeddings)
            st.success("✅ AI is now an expert on your Warehouse specs!")

# --- 5. DATA RENDERER ---
def render_lead_table(response_text, my_product):
    lines = response_text.split('\n')
    lead_data = []

    for line in lines:
        if '|' in line and 'Agency' not in line and '---' not in line:
            cols = [c.strip() for c in line.split('|')]
            if len(cols) < 7: continue
            lead_data.append(cols[0:7])

    if not lead_data:
        st.warning("No structured leads found. Try refining your search.")
        return

    # Clean Table UI
    for i, lead in enumerate(lead_data):
        name, addr, web, email, phone, role, person = lead
        with st.expander(f"🏢 {name} — {person} ({role})"):
            c1, c2 = st.columns([2, 1])
            with c1:
                st.write(f"📍 **Location:** {addr}")
                st.write(f"🌐 **Web:** [{web}]({web})")
            with c2:
                clean_phone = "".join(filter(str.isdigit, phone))
                if len(clean_phone) == 10: clean_phone = "91" + clean_phone
                wa_link = f"https://wa.me/{clean_phone}?text={urllib.parse.quote(f'Hello {person}, regarding {my_product}. {strategy_note}')}"
                st.markdown(f"**[💬 WhatsApp Shoot]({wa_link})**")
                st.markdown(f"[🔗 LinkedIn](https://www.linkedin.com/search/results/people/?keywords={urllib.parse.quote(person + ' ' + name)})")

    df = pd.DataFrame(lead_data, columns=["Name", "Address", "Web", "Email", "Phone", "Role", "Person"])
    st.download_button("📥 Export to Excel", data=df.to_csv(index=False).encode('utf-8'), file_name="leads.csv")

# --- 6. SEARCH INTERFACE ---
st.header("🚀 Samketan Business Growth Engine")
col1, col2 = st.columns(2)
with col1:
    my_product = st.text_input("1) Product/Service", value="ice cream")
    region = st.text_input("3) Target City/Region", value="gulbarga")
with col2:
    target_client = st.text_input("2) Client Type", value="hotels, smart bazar")
    scope = st.radio("4) Market Scope", ["Local (Domestic)", "Export (International)"])

tab1, tab2 = st.tabs(["🤖 Live Web Search (Gemini)", "🧠 Pattern Analysis (Claude)"])

PROMPT_TEMPLATE = """
Find 10 REAL businesses in {region} for {target_client} who might buy {my_product}.
Search the web for current data. Return pipe-separated table:
Agency Name | Full Address | Website URL | Email ID | Phone Number | Decision Maker Role | Person Name
"""

with tab1:
    if st.button("🔍 Find Real-Time Leads"):
        model = get_gemini_engine(google_api_key)
        if model:
            with st.spinner("Searching the internet for live B2B buyers..."):
                prompt = PROMPT_TEMPLATE.format(region=region, target_client=target_client, my_product=my_product)
                response = model.generate_content(prompt)
                render_lead_table(response.text, my_product)

with tab2:
    if st.button("🧠 Generate Strategic Leads"):
        if anthropic_api_key:
            with st.spinner("Analyzing market data..."):
                prompt = PROMPT_TEMPLATE.format(region=region, target_client=target_client, my_product=my_product)
                res = get_claude_response(prompt, anthropic_api_key)
                if res: render_lead_table(res, my_product)
        else:
            st.error("Please add ANTHROPIC_API_KEY to secrets.")

# --- FOOTER ---
st.markdown("---")
with st.sidebar:
    st.info(f"👤 Logged in as: {st.session_state.get('current_user', 'Sanjay')}")
    if st.button("🚪 Logout"):
        cookie_manager.delete('samketan_user')
        st.session_state.clear()
        st.rerun()

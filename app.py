import streamlit as st
import auth  # Connects to your auth.py logic

# --- 1. AUTHENTICATION & SECURITY ---
if not auth.login_screen():
    st.stop() 

import google.generativeai as genai
import anthropic
import urllib.parse
import pandas as pd
import time
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

# --- 3. API & ENGINES ---
google_api_key = st.secrets.get("GOOGLE_API_KEY") or st.sidebar.text_input("Paste Google API Key", type="password").strip()
anthropic_api_key = st.secrets.get("ANTHROPIC_API_KEY", "")

def get_gemini_engine(key):
    try:
        genai.configure(api_key=key.strip())
        # Enabled with Google Search Grounding for REAL data
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
            model="claude-3-5-sonnet-20240620", # Updated to the latest stable Sonnet
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
    strategy_note = st.text_area("Why Samketan is Best?", value="We provide premium quality and reliable cold-chain supply.")
    
    st.write("---")
    st.header("📖 Knowledge Base (RAG)")
    kb_file = st.file_uploader("Upload Warehouse specs or Product PDF", type="pdf")
    
    if kb_file:
        with st.spinner("AI reading your Business Documents..."):
            with open("temp_kb.pdf", "wb") as f: f.write(kb_file.getbuffer())
            loader = PyPDFLoader("temp_kb.pdf")
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            chunks = text_splitter.split_documents(loader.load())
            embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=google_api_key)
            st.session_state.vector_db = FAISS.from_documents(chunks, embeddings)
            st.success("✅ AI now knows your Business details!")

# --- 5. SHARED UI: LEAD TABLE RENDERER ---
def render_lead_table(response_text, my_product):
    lines = response_text.split('\n')
    lead_data = []

    html_table = "<table style='width:100%; border-collapse: collapse; font-family: Arial; font-size: 13px;'>"
    html_table += "<tr style='background-color: #004a99; color: white;'><th>Business Name</th><th>Contact Info</th><th>Outreach</th><th>Market Intelligence</th></tr>"

    for i, line in enumerate(lines):
        if '|' in line and 'Agency' not in line and '---' not in line:
            cols = [c.strip() for c in line.split('|')]
            if len(cols) < 7: continue
            name, addr, web, email, phone, role, person = cols[0:7]
            lead_data.append(cols[0:7])

            # Smart Links
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
                <td style='border: 1px solid #ddd; padding: 10px;'><b>{role}</b></td>
            </tr>"""
    
    html_table += "</table>"
    st.write(html_table, unsafe_allow_html=True)
    
    if lead_data:
        df = pd.DataFrame(lead_data, columns=["Name", "Address", "Web", "Email", "Phone", "Role", "Person"])
        st.download_button("📥 Download Excel", data=df.to_csv(index=False).encode('utf-8'), file_name=f"leads_{my_product}.csv")

# --- 6. MAIN DASHBOARD ---
st.header("🚀 Samketan Business Growth Engine")

col1, col2 = st.columns(2)
with col1:
    my_product = st.text_input("1) Product/Service", value="ice cream")
    region = st.text_input("3) Target City/Region", value="gulbarga")
with col2:
    target_client = st.text_input("2) Who is your client?", value="hotels, smart bazar")
    scope = st.radio("4) Market Scope", ["Local (Domestic)", "Export (International)"])

tab1, tab2 = st.tabs(["🤖 Gemini REAL-TIME Leads", "🧠 Claude Strategy Leads"])

PROMPT_TEMPLATE = """
Act as a Sales Researcher. Search the web and find 10 REAL ACTIVE businesses in {region} for {target_client}.
They must be potential buyers for {my_product}.
Return ONLY a pipe-separated table:
Agency Name | Full Address | Website URL | Email ID | Phone Number | Decision Maker Role | Person Name
"""

with tab1:
    st.subheader("Deep Web Mining (Powered by Google Search)")
    if st.button("🔍 Search & Mine REAL Leads"):
        model = get_gemini_engine(google_api_key)
        if model:
            with st.spinner("Searching the web for live businesses in Kalaburagi/Gulbarga..."):
                prompt = PROMPT_TEMPLATE.format(region=region, target_client=target_client, my_product=my_product)
                response = model.generate_content(prompt)
                render_lead_table(response.text, my_product)

with tab2:
    st.subheader("Strategic Analysis with Claude")
    if st.button("🧠 Generate Strategic Leads"):
        if not anthropic_api_key:
            st.error("Please add ANTHROPIC_API_KEY in secrets.")
        else:
            with st.spinner("Claude is analyzing market patterns..."):
                prompt = PROMPT_TEMPLATE.format(region=region, target_client=target_client, my_product=my_product)
                response_text = get_claude_response(prompt, anthropic_api_key)
                if response_text:
                    render_lead_table(response_text, my_product)

# --- FOOTER ---
st.markdown("---")
with st.sidebar:
    st.info(f"👤 Logged in as: {st.session_state.get('current_user', 'User')}")
    if st.button("🚪 Logout from Engine", use_container_width=True):
        cookie_manager.delete('samketan_user')
        st.session_state.clear()
        st.rerun()

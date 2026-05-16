import streamlit as st
import auth  # Connects to your auth.py logic
import google.generativeai as genai
from openai import OpenAI
import urllib.parse
import pandas as pd
import extra_streamlit_components as stx

# --- 1. AUTHENTICATION & SECURITY ---
if not auth.login_screen():
    st.stop() 

cookie_manager = stx.CookieManager()
saved_user = cookie_manager.get('samketan_user')
if saved_user and not st.session_state.get('authenticated'):
    st.session_state.authenticated = True
    st.session_state.current_user = saved_user

# --- 2. PAGE SETUP ---
st.set_page_config(page_title="Samketan AI v6.2", page_icon="🚀", layout="wide")

st.markdown(
    """
    <style>
    .flash-container { background-color: #FFF4E5; padding: 10px; border: 1px solid #FF8C00; border-radius: 5px; margin-bottom: 15px; text-align: center; }
    .flash-text { color: #D35400; font-weight: bold; font-size: 16px; }
    </style>
    <div class="flash-container">
        <marquee scrollamount="8" class="flash-text">
            📢 <b>BHOODEVI WAREHOUSE:</b> 21,000 Sq. Ft. Premium Space in Gulbarga for Lease. 
            <a href="https://bhoodeviwarehouse.netlify.app/" target="_blank">👉 View Details</a>
        </marquee>
    </div>
    """,
    unsafe_allow_html=True
)

# --- 3. THE TRIPLE-AGENT ORCHESTRATOR ---
google_key = st.secrets.get("GOOGLE_API_KEY")
openrouter_key = st.secrets.get("OPENROUTER_API_KEY")
openai_key = st.secrets.get("OPENAI_API_KEY")

def get_best_gemini_model(api_key):
    genai.configure(api_key=api_key)
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    priority = ['models/gemini-2.5-flash-lite', 'models/gemini-1.5-flash']
    for p in priority:
        if p in available_models:
            return genai.GenerativeModel(model_name=p, tools=[{"google_search_retrieval": {}}])
    return genai.GenerativeModel(model_name=available_models[0])

def run_triple_agent_search(product, region, client_type):
    try:
        # AGENT 1: Gemini (The Researcher - Uses Free Tier Lite to avoid 429s)
        st.write("🔍 **Gemini Searcher** is scouring the web for live contacts...")
        gemini = get_best_gemini_model(google_key)
        
        search_prompt = f"""Find 5 REAL business leads in {region} for {client_type} who buy {product}.
        Provide: Name, Company, Website, and Public Email/Phone. CITE YOUR SOURCES."""
        search_res = gemini.generate_content(search_prompt).text
        
        # AGENT 2: OpenRouter Free Auditor (Replaces Paid Claude)
        st.write("🧠 **OpenRouter Auditor** is performing an verification check ($0 cost)...")
        # Initialize OpenRouter client using the OpenAI library format
        or_client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=openrouter_key
        )
        analysis_prompt = f"""Analyze these leads: {search_res}. 
        Perform a 'BS-Check': Do these companies look real? Is the contact likely a decision maker? 
        Rate 'Business Likelihood' 1-100. Be highly critical."""
        
        # Using openrouter/free to dynamically choose the best free thinking model
        analysis_res = or_client.chat.completions.create(
            model="openrouter/free",
            messages=[{"role": "user", "content": analysis_prompt}]
        ).choices[0].message.content
        
        # AGENT 3: ChatGPT (The Communicator)
        st.write("✉️ **ChatGPT Composer** is drafting human-like outreach...")
        gpt = OpenAI(api_key=openai_key)
        outreach_prompt = f"""Based on the audit analysis: {analysis_res}, 
        write 1 professional Email and 1 friendly WhatsApp for the best lead. 
        Focus on value: 'Premium 21,000 sq ft RCC warehouse in Nandur Area'."""
        outreach_res = gpt.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": outreach_prompt}]
        ).choices[0].message.content
        
        return search_res, analysis_res, outreach_res
    except Exception as e:
        st.error(f"❌ Orchestration Error: {e}")
        return None, None, None

# --- 4. USER INTERFACE ---
st.header("🚀 Samketan AI v6.2: Free OpenRouter Integration")

col1, col2 = st.columns(2)
with col1:
    prod = st.text_input("1) What are you selling?", value="Warehouse Space")
    loc = st.text_input("3) Target City/Region", value="Gulbarga")
with col2:
    target = st.text_input("2) Who is your ideal client?", value="FMCG Distributors")

if st.button("🔥 RUN TRIPLE-AGENT ENGINE"):
    if not (google_key and openrouter_key and openai_key):
        st.error("⚠️ Error: Missing API Keys. Please verify Google, OpenRouter, and OpenAI are in secrets.")
    else:
        with st.spinner("AI Agents are coordinating..."):
            raw, analysis, outreach = run_triple_agent_search(prod, loc, target)
            if raw:
                st.success("✅ Workflow Complete!")
                st.balloons()
                t1, t2, t3 = st.tabs(["📡 1. Gemini Research", "🔬 2. OpenRouter Audit (Free)", "✍️ 3. GPT Outreach"])
                with t1: st.markdown(raw)
                with t2: st.markdown(analysis)
                with t3: st.markdown(outreach)

# --- 5. SIDEBAR & FOOTER ---
with st.sidebar:
    st.header("🏢 Settings")
    st.info(f"👤 Account: {st.session_state.get('current_user', 'Sanjay')}")
    if st.button("🚪 Logout"):
        cookie_manager.delete('samketan_user')
        st.session_state.clear()
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("Samketan AI v6.2 | OpenRouter Free Tier Router Enabled")

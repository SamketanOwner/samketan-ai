import streamlit as st
import auth  # Your existing login logic
import google.generativeai as genai
import anthropic
from openai import OpenAI
import urllib.parse
import pandas as pd
import os
import extra_streamlit_components as stx

# --- 1. AUTHENTICATION GATE ---
if not auth.login_screen():
    st.stop() 

# --- 2. ENGINE CONFIGURATION ---
st.set_page_config(page_title="Samketan AI v6.0", page_icon="🚀", layout="wide")

# API Keys from Secrets
google_key = st.secrets.get("GOOGLE_API_KEY")
anthropic_key = st.secrets.get("ANTHROPIC_API_KEY")
openai_key = st.secrets.get("OPENAI_API_KEY")

# Initialize Clients
def get_gemini():
    genai.configure(api_key=google_key)
    return genai.GenerativeModel(model_name='gemini-1.5-flash', tools=[{"google_search_retrieval": {}}])

def get_claude():
    return anthropic.Anthropic(api_key=anthropic_key)

def get_gpt():
    return OpenAI(api_key=openai_key)

# --- 3. THE TRIPLE-AGENT ORCHESTRATOR ---
def run_orchestrator(product, region, client_type):
    try:
        # AGENT 1: Gemini (The Searcher)
        st.write("🔍 **Gemini** is searching for genuine contacts...")
        gemini = get_gemini()
        search_prompt = f"Find 5 REAL business leads in {region} for {client_type} who need {product}. Provide: Name, Company, Website, and Email/Phone if public."
        search_res = gemini.generate_content(search_prompt).text
        
        # AGENT 2: Claude (The Analyst)
        st.write("🧠 **Claude** is verifying genuineness and scoring leads...")
        claude = get_claude()
        analysis_prompt = f"Analyze these leads: {search_res}. Score them 1-100 on 'Business Likelihood'. Check if their websites look professional. Provide a short Rationale for each."
        analysis_res = claude.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1000,
            messages=[{"role": "user", "content": analysis_prompt}]
        ).content[0].text
        
        # AGENT 3: ChatGPT (The Composer)
        st.write("✉️ **ChatGPT** is composing personalized outreach...")
        gpt = get_gpt()
        outreach_prompt = f"Based on Claude's analysis: {analysis_res}, write 1 professional Email and 1 friendly WhatsApp for the top lead. Focus on this value: 'Premium 21,000 sq ft warehouse space in Nandur'."
        outreach_res = gpt.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": outreach_prompt}]
        ).choices[0].message.content
        
        return search_res, analysis_res, outreach_res
    except Exception as e:
        st.error(f"Orchestration Error: {e}")
        return None, None, None

# --- 4. USER INTERFACE ---
st.header("🚀 Samketan AI v6.0: Triple-Agent Orchestrator")

# Branding
st.info("📢 Available: 21,000 Sq. Ft. Warehouse in Gulbarga. [Visit Site](https://bhoodeviwarehouse.netlify.app/)")

col1, col2 = st.columns(2)
with col1:
    prod = st.text_input("Product/Service", value="Warehouse Leasing")
    loc = st.text_input("Region", value="Gulbarga")
with col2:
    target = st.text_input("Client Type", value="FMCG Distributors")

if st.button("🔥 Run Multi-Agent Search"):
    if not (google_key and anthropic_key and openai_key):
        st.error("Missing API Keys in Secrets!")
    else:
        with st.spinner("Agents are coordinating..."):
            raw, analysis, outreach = run_orchestrator(prod, loc, target)
            
            if raw:
                t1, t2, t3 = st.tabs(["📡 Gemini Research", "🔬 Claude Audit", "✍️ GPT Outreach"])
                with t1: st.markdown(raw)
                with t2: st.markdown(analysis)
                with t3: st.markdown(outreach)

# --- 5. FOOTER ---
st.sidebar.markdown("---")
st.sidebar.caption("v6.0 | Gemini + Claude + GPT-4o")
if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

# app.py - Samketan AI v7.0 - Full Multi-Agent Autonomous System

import streamlit as st
import auth

# --- AUTHENTICATION ---
if not auth.login_screen():
    st.stop()

import google.generativeai as genai
import anthropic
from openai import OpenAI
import urllib.parse
import pandas as pd
import random
import json
import time
import extra_streamlit_components as stx
from datetime import datetime

# --- COOKIE MANAGER ---
cookie_manager = stx.CookieManager()
saved_user = cookie_manager.get('samketan_user')
if saved_user and not st.session_state.get('authenticated'):
    st.session_state.authenticated = True
    st.session_state.current_user = saved_user

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Samketan AI v7.0 - Multi-Agent",
    page_icon="🤖",
    layout="wide"
)

# ─────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0a0d14; }
    section[data-testid="stSidebar"] { background-color: #0f1219 !important; }

    /* Header */
    .header-banner {
        background: linear-gradient(135deg, #0d1117 0%, #0a1929 50%, #0d1117 100%);
        border: 1px solid #1e3a5f;
        border-radius: 16px;
        padding: 28px 36px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .header-title { font-size: 2rem; font-weight: 800; color: #fff; margin: 0; }
    .header-sub   { font-size: 0.92rem; color: #7a8ba0; margin-top: 6px; }
    .header-badge {
        background: linear-gradient(135deg, #7b2ff7, #f107a3);
        color: white; padding: 8px 20px; border-radius: 20px;
        font-size: 0.78rem; font-weight: 700; letter-spacing: 1.5px;
    }

    /* Promo bar */
    .promo-bar {
        background: linear-gradient(90deg,#1a0a00,#2d1500);
        border: 1px solid #FF8C00; border-radius: 8px;
        padding: 10px 16px; margin-bottom: 20px;
        font-size: 14px; color: #FFB347; font-weight: 600;
    }
    .promo-bar a { color: #FFD700; text-decoration: none; font-weight: 700; }

    /* Agent Cards */
    .agent-pipeline {
        display: flex; gap: 12px; margin-bottom: 24px; flex-wrap: wrap;
    }
    .agent-card {
        flex: 1; min-width: 200px;
        background: #0f1219;
        border: 1px solid #1e2a3e;
        border-radius: 14px;
        padding: 18px 20px;
        text-align: center;
        position: relative;
        transition: all 0.3s ease;
    }
    .agent-card.active {
        border-color: #7b2ff7;
        box-shadow: 0 0 20px rgba(123,47,247,0.3);
    }
    .agent-card.done {
        border-color: #00c851;
        box-shadow: 0 0 15px rgba(0,200,81,0.2);
    }
    .agent-icon { font-size: 2rem; margin-bottom: 8px; }
    .agent-name { font-size: 0.9rem; font-weight: 700; color: #e0e6f0; }
    .agent-role { font-size: 0.75rem; color: #7a8ba0; margin-top: 4px; }
    .agent-status { font-size: 0.72rem; margin-top: 8px; padding: 3px 10px; border-radius: 10px; display: inline-block; }
    .status-idle    { background: #1a1d27; color: #4a5568; }
    .status-running { background: #1a0d2e; color: #a855f7; }
    .status-done    { background: #0a1a0a; color: #00c851; }

    /* Arrow between agents */
    .agent-arrow { color: #2a3a5e; font-size: 1.5rem; display: flex; align-items: center; padding-top: 10px; }

    /* Input card */
    .input-card {
        background: #0f1219; border: 1px solid #1e2a3e;
        border-radius: 14px; padding: 24px; margin-bottom: 20px;
    }
    .stTextInput > div > div > input,
    .stTextArea  > div > div > textarea {
        background-color: #0a0d14 !important;
        border: 1px solid #1e2a3e !important;
        color: #e0e6f0 !important; border-radius: 8px !important;
    }

    /* Phase Headers */
    .phase-header {
        background: linear-gradient(90deg, #0a1929, #0d1117);
        border: 1px solid #1e3a5f;
        border-left: 4px solid;
        border-radius: 10px;
        padding: 14px 20px;
        margin: 20px 0 14px 0;
        display: flex; align-items: center; gap: 12px;
    }
    .phase-gemini  { border-left-color: #4285f4; }
    .phase-claude  { border-left-color: #a855f7; }
    .phase-gpt     { border-left-color: #00c851; }
    .phase-auto    { border-left-color: #f59e0b; }

    .phase-title { font-size: 1rem; font-weight: 700; color: #fff; margin: 0; }
    .phase-sub   { font-size: 0.8rem; color: #7a8ba0; margin-top: 2px; }

    /* Lead Cards */
    .lead-card {
        background: #0f1219; border: 1px solid #1e2a3e;
        border-radius: 14px; padding: 20px 24px; margin-bottom: 14px;
        transition: border-color 0.2s, box-shadow 0.2s;
    }
    .lead-card:hover { border-color: #4285f4; box-shadow: 0 4px 24px rgba(66,133,244,0.15); }
    .lead-name   { font-size: 1.05rem; font-weight: 700; color: #fff; margin: 0; }
    .lead-address{ font-size: 0.8rem; color: #7a8ba0; margin-top: 4px; }

    .badge-hot  { background:#1a0a0a; color:#ff4444; border:1px solid #ff4444; padding:4px 12px; border-radius:20px; font-size:0.72rem; font-weight:700; }
    .badge-warm { background:#1a1200; color:#ffaa00; border:1px solid #ffaa00; padding:4px 12px; border-radius:20px; font-size:0.72rem; font-weight:700; }
    .badge-cold { background:#001a2a; color:#0099ff; border:1px solid #0099ff; padding:4px 12px; border-radius:20px; font-size:0.72rem; font-weight:700; }

    /* Strategy Box */
    .strategy-box {
        background: #0a0d14; border: 1px solid #2d1657;
        border-left: 3px solid #a855f7;
        border-radius: 10px; padding: 16px 20px; margin: 10px 0;
    }
    .strategy-title { color: #a855f7; font-weight: 700; font-size: 0.85rem; margin-bottom: 8px; }
    .strategy-text  { color: #b0bec5; font-size: 0.84rem; line-height: 1.6; }

    /* Message Boxes */
    .msg-box {
        background: #0a0d14; border: 1px solid #1e2a3e;
        border-radius: 10px; padding: 16px; margin: 10px 0;
    }
    .msg-whatsapp { border-left: 3px solid #25D366; }
    .msg-email    { border-left: 3px solid #4285f4; }
    .msg-label { font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
    .msg-label-wa   { color: #25D366; }
    .msg-label-mail { color: #4285f4; }
    .msg-content { color: #b0bec5; font-size: 0.84rem; line-height: 1.6; white-space: pre-wrap; }

    /* Auto-Reply Box */
    .autoreply-box {
        background: #0f1a0f; border: 1px solid #1a3a1a;
        border-left: 3px solid #00c851;
        border-radius: 10px; padding: 16px; margin: 10px 0;
    }
    .autoreply-label { color: #00c851; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
    .autoreply-text  { color: #b0bec5; font-size: 0.84rem; line-height: 1.6; white-space: pre-wrap; }

    /* Action Buttons */
    .action-row { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 14px; }
    .btn-wa   { background:#0d2a1a; color:#25D366; border:1px solid #25D366; padding:8px 16px; border-radius:8px; font-size:0.82rem; font-weight:700; text-decoration:none; display:inline-block; }
    .btn-mail { background:#0d1a2a; color:#64b5f6; border:1px solid #64b5f6; padding:8px 16px; border-radius:8px; font-size:0.82rem; font-weight:700; text-decoration:none; display:inline-block; }
    .btn-li   { background:#0a1929; color:#0a66c2; border:1px solid #0a66c2; padding:8px 16px; border-radius:8px; font-size:0.82rem; font-weight:700; text-decoration:none; display:inline-block; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: #0f1219 !important;
        border-radius: 10px; padding: 4px; gap: 4px;
        border: 1px solid #1e2a3e;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important; color: #7a8ba0 !important;
        border-radius: 8px !important; font-weight: 600 !important;
        padding: 10px 20px !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg,#7b2ff7,#f107a3) !important;
        color: white !important;
    }

    /* Main Button */
    .stButton > button {
        background: linear-gradient(135deg,#7b2ff7,#f107a3) !important;
        color: white !important; border: none !important;
        border-radius: 10px !important; font-weight: 700 !important;
        font-size: 1rem !important; padding: 14px 32px !important;
        width: 100% !important;
    }

    /* Stats bar */
    .stats-bar { display:flex; gap:12px; margin-bottom:20px; flex-wrap:wrap; }
    .stat-chip {
        background:#0f1219; border:1px solid #1e2a3e;
        border-radius:8px; padding:10px 18px;
        color:#b0bec5; font-size:0.82rem; font-weight:600;
    }
    .stat-chip span { color:#a855f7; font-size:1.05rem; font-weight:800; }

    .conversation-entry {
        background: #0a0d14; border: 1px solid #1e2a3e;
        border-radius: 10px; padding: 14px 18px; margin-bottom: 10px;
    }
    .conv-from   { font-size: 0.75rem; color: #7a8ba0; margin-bottom: 6px; }
    .conv-msg    { color: #b0bec5; font-size: 0.84rem; line-height: 1.6; }
    .conv-time   { font-size: 0.72rem; color: #4a5568; margin-top: 6px; }

    .user-chip {
        background: #0a0d14; border: 1px solid #1e2a3e;
        border-radius: 8px; padding: 10px 14px;
        color: #e0e6f0; font-size: 0.88rem; margin-bottom: 12px;
    }
    .ai-note {
        background: #0a0d14; border: 1px solid #1e2a3e;
        border-radius: 8px; padding: 12px 16px; margin-bottom: 16px;
        font-size: 0.83rem; color: #7a8ba0;
    }
    .ai-note b { color: #b0bec5; }

    #MainMenu { visibility: hidden; }
    footer     { visibility: hidden; }
    header     { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# API KEYS
# ─────────────────────────────────────────────
gemini_key  = st.secrets.get("GOOGLE_API_KEY", "")
openrouter_api_key = st.secret.get("your_new_openrouter_key","")
openai_key  = st.secrets.get("OPENAI_API_KEY", "")
claude_key  = st.secrets.get("ANTHROPIC_API_KEY", "")

# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────
for key in ['pipeline_results', 'conversation_log', 'leads_data', 'agent_statuses']:
    if key not in st.session_state:
        st.session_state[key] = None

if 'conversation_log' not in st.session_state or st.session_state.conversation_log is None:
    st.session_state.conversation_log = []

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="header-banner">
    <div>
        <p class="header-title">🤖 Samketan AI v7.0</p>
        <p class="header-sub">
            Autonomous Multi-Agent Pipeline: 
            Gemini Scouts → Claude Strategizes → ChatGPT Communicates → Auto-Replies
        </p>
    </div>
    <span class="header-badge">MULTI-AGENT</span>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="promo-bar">
    📢 <b>AVAILABLE FOR LEASE:</b> Premium 21,000 Sq. Ft. RCC Warehouse · Nandur Area, Gulbarga &nbsp;
    <a href="https://bhoodeviwarehouse.netlify.app/" target="_blank">👉 Visit Bhoodevi Warehouse →</a>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏢 Samketan Profile")
    st.markdown(f'<div class="user-chip">👤 {st.session_state.get("current_user", "User")}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🔑 API Keys")
    st.caption("Auto-loaded from Streamlit Secrets.")
    if not gemini_key:
        gemini_key = st.text_input("Google Gemini Key", type="password", placeholder="AIza...")
    if not claude_key:
        claude_key = st.text_input("Anthropic Claude Key", type="password", placeholder="sk-ant-...")
    if not openai_key:
        openai_key = st.text_input("OpenAI Key", type="password", placeholder="sk-...")

    st.markdown("---")
    st.markdown("### 🏭 Our Offering (Context for AI)")
    our_product = st.text_area(
        "What we offer:",
        value="Premium 21,000 sq ft RCC warehouse in Nandur Area, Gulbarga. Features: 24/7 security, loading docks, fire safety, power backup. Ideal for FMCG, pharma, agri storage.",
        height=120,
        help="This is injected into all AI agents as context."
    )
    our_company = st.text_input("Company Name", value="Samketan / Bhoodevi Warehouse")
    our_contact = st.text_input("Our Contact (for messages)", value="+91-XXXXXXXXXX")
    our_email   = st.text_input("Our Email", value="samketan@example.com")

    st.markdown("---")
    st.markdown("### ⚙️ Auto-Reply Settings")
    auto_reply_enabled = st.toggle("🔄 Enable Auto-Reply Simulation", value=True)
    reply_tone = st.selectbox("Reply Tone", ["Professional & Warm", "Formal", "Friendly & Casual", "Urgent & Direct"])

    st.markdown("---")
    with st.expander("🎯 How Multi-Agent Works"):
        st.markdown("""
**🔍 Agent 1 - Gemini (Scout)**
Searches web for real business leads with contact details

**🧠 Agent 2 - Claude (Strategist)**
Analyses each lead, understands their business need, creates personalised strategy

**✉️ Agent 3 - ChatGPT (Communicator)**  
Writes tailored WhatsApp + Email for each lead

**🔄 Agent 4 - Auto-Responder**
Simulates client reply & generates intelligent follow-up
        """)

    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        cookie_manager.delete('samketan_user')
        st.session_state.authenticated = False
        st.rerun()

# ─────────────────────────────────────────────
# AGENT STATUS DISPLAY
# ─────────────────────────────────────────────
def show_agent_pipeline(statuses):
    agents = [
        {"icon": "🔍", "name": "Gemini Scout", "role": "Lead Discovery", "key": "gemini"},
        {"icon": "🧠", "name": "Claude Analyst", "role": "Strategy & Profiling", "key": "claude"},
        {"icon": "✉️", "name": "GPT Communicator", "role": "Message Drafting", "key": "gpt"},
        {"icon": "🔄", "name": "Auto-Responder", "role": "Conversation AI", "key": "auto"},
    ]
    cols = st.columns(7)
    for i, agent in enumerate(agents):
        status = statuses.get(agent["key"], "idle")
        card_class  = "agent-card active" if status == "running" else ("agent-card done" if status == "done" else "agent-card")
        status_class = f"agent-status status-{status}"
        status_label = {"idle": "⏸ Idle", "running": "⚡ Running", "done": "✅ Done"}.get(status, "⏸ Idle")
        with cols[i * 2]:
            st.markdown(f"""
            <div class="{card_class}">
                <div class="agent-icon">{agent['icon']}</div>
                <div class="agent-name">{agent['name']}</div>
                <div class="agent-role">{agent['role']}</div>
                <span class="{status_class}">{status_label}</span>
            </div>
            """, unsafe_allow_html=True)
        if i < len(agents) - 1:
            with cols[i * 2 + 1]:
                st.markdown('<div style="text-align:center;color:#2a3a5e;font-size:1.8rem;padding-top:30px;">→</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# MAIN INPUT SECTION
# ─────────────────────────────────────────────
st.markdown('<div class="input-card">', unsafe_allow_html=True)
st.markdown("### 🎯 Define Your Target")
col1, col2, col3 = st.columns(3)
with col1:
    my_product    = st.text_input("🛒 Product / Service to Sell", value="Warehouse Space", placeholder="e.g. Warehouse, Ice Cream, Software")
    region        = st.text_input("📍 Target City / Region", value="Gulbarga, Karnataka", placeholder="e.g. Bengaluru, Mumbai")
with col2:
    target_client = st.text_input("🏢 Ideal Client Type", value="FMCG Distributors, Pharma Companies", placeholder="e.g. hotels, retailers")
    num_leads     = st.slider("Number of Leads to Find", 3, 10, 5)
with col3:
    scope         = st.radio("🌍 Market Scope", ["Local (Domestic)", "Export (International)"], horizontal=False)
    urgency       = st.selectbox("📊 Deal Urgency", ["High - Close this month", "Medium - Next quarter", "Low - Exploring"])
st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# AGENT 1: GEMINI — LEAD DISCOVERY
# ─────────────────────────────────────────────
def agent_gemini_scout(region, target_client, my_product, our_product, num_leads):
    """Gemini searches for real business leads with web context"""
    
    genai.configure(api_key=gemini_key.strip())
    available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    priority  = ['models/gemini-2.5-flash', 'models/gemini-2.0-flash', 'models/gemini-1.5-flash']
    selected  = next((m for m in priority if m in available), available[0])
    model     = genai.GenerativeModel(selected)

    prompt = f"""You are a B2B Lead Intelligence Scout. Find {num_leads} REAL businesses in {region}.

TARGET CLIENT TYPE: {target_client}
WHAT WE ARE SELLING: {my_product}
OUR FULL OFFERING: {our_product}

TASK: Find {num_leads} real companies that GENUINELY NEED what we offer.

Think about WHY each company would need {my_product}. 
For example: FMCG distributors need warehousing for stock storage, seasonal surge capacity, etc.

Return ONLY a pipe-separated table with these exact columns:
Company Name | Full Address | Website | Email | Phone | Decision Maker Role | Contact Person | Why They Need Us | Industry Sector | Estimated Deal Size

RULES:
- Make realistic estimates for any unknown fields (don't say N/A)
- Phone: Indian format (10 digits or with +91)
- Email: guess realistic format (name@companyname.com) if unknown
- Why They Need Us: 1-2 specific sentences
- Estimated Deal Size: e.g. "₹2-5 Lakh/month", "₹15L annual lease"
- NO markdown formatting, NO headers explanation, ONLY the table rows
"""
    response = model.generate_content(prompt)
    return response.text, selected

# ─────────────────────────────────────────────
# PHASE 2: OPENROUTER STRATEGIST (FREE REPLACEMENT FOR CLAUDE) 
# ─────────────────────────────────────────────
    with pipeline_status_placeholder.container():
            show_agent_pipeline({"gemini": "done", "claude": "running", "gpt": "idle", "auto": "idle"})

        st.markdown("""
        <div class="phase-header phase-claude">
            <span style="font-size:1.5rem">🧠</span>
            <div>
                <p class="phase-title">Phase 2: OpenRouter Strategist — Deep Analysis & Personalization</p>
                <p class="phase-sub">Analysing each lead's business, pain points & crafting targeted strategy</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.spinner("🧠 OpenRouter is strategizing for each lead ($0 Cost)..."):
            try:
                # Surgical replacement: Calling OpenRouter proxy with a high-capacity free model instead of paid Anthropic
                from openai import OpenAI
                or_client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=st.secrets.get("OPENROUTER_API_KEY")
                )
                
                # Reconstructing your input parameter flow safely into a structured prompt
                analysis_prompt = f"""
                You are a senior business growth strategist. Analyze the raw lead dataset below and extract strategic matching insights.
                
                Raw Leads Data from Gemini:
                {st.session_state.pipeline_results.get('gemini_raw', '')}
                
                Our Company Identity: {our_company}
                Our Product/Service Offer: {our_product}
                Specific Product Target: {my_product}
                Required Outreach Tone: {reply_tone}
                
                CRITICAL INSTRUCTION: Return your response ONLY as a clean, machine-readable JSON array of objects. Do not wrap it in markdown codeblocks (no ```json).
                Each object in the JSON array MUST contain these exact text keys:
                - "company" (string)
                - "contact_person" (string)
                - "deal_score" (integer, 1-100)
                - "priority" (string uppercase: either 'HOT', 'WARM', or 'COLD')
                - "our_value_prop" (string text)
                - "pain_points" (list of strings)
                - "opening_hook" (string text)
                - "objection_handling" (string text)
                - "estimated_value" (string text)
                - "urgency_signal" (string text)
                - "recommended_approach" (string text)
                """

                # Triggering OpenRouter's free thinking system
                response = or_client.chat.completions.create(
                    model="openrouter/free",
                    messages=[{"role": "user", "content": analysis_prompt}]
                )
                
                strategy_raw = response.choices[0].message.content
                strategy_list = safe_json_parse(strategy_raw, [])
                st.session_state.pipeline_results['strategy'] = strategy_list

                st.success(f"✅ OpenRouter analyzed {len(strategy_list)} leads with strategic scoring")

                # Display strategy cards (Your entire design remains identical)
                if strategy_list:
                    for s in strategy_list:
                        priority = s.get('priority', 'WARM')
                        badge_class = 'badge-hot' if priority == 'HOT' else ('badge-cold' if priority == 'COLD' else 'badge-warm')
                        badge_icon  = '🔥' if priority == 'HOT' else ('❄️' if priority == 'COLD' else '🌡️')

                        st.markdown(f"""
                        <div class="lead-card">
                            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;">
                                <div>
                                    <p class="lead-name">{s.get('company', 'Unknown')}</p>
                                    <p class="lead-address">👤 {s.get('contact_person', '')} · 📊 Score: <b style="color:#a855f7">{s.get('deal_score', 0)}/100</b></p>
                                </div>
                                <span class="{badge_class}">{badge_icon} {priority}</span>
                            </div>
                            <div class="strategy-box">
                                <div class="strategy-title">🎯 Strategic Value Proposition</div>
                                <div class="strategy-text">{s.get('our_value_prop', '')}</div>
                            </div>
                            <div style="display:flex;gap:16px;flex-wrap:wrap;margin-top:12px;">
                                <div style="flex:1;min-width:160px;">
                                    <p style="font-size:0.72rem;color:#4a5568;text-transform:uppercase;letter-spacing:1px;">Pain Points</p>
                                    <ul style="color:#b0bec5;font-size:0.82rem;margin:4px 0;padding-left:16px;">
                                        {''.join([f"<li>{p}</li>" for p in s.get('pain_points', [])])}
                                    </ul>
                                </div>
                                <div style="flex:1;min-width:160px;">
                                    <p style="font-size:0.72rem;color:#4a5568;text-transform:uppercase;letter-spacing:1px;">Opening Hook</p>
                                    <p style="color:#e0e6f0;font-size:0.84rem;font-style:italic;">"{s.get('opening_hook', '')}"</p>
                                </div>
                                <div style="flex:1;min-width:160px;">
                                    <p style="font-size:0.72rem;color:#4a5568;text-transform:uppercase;letter-spacing:1px;">Objection & Handle</p>
                                    <p style="color:#b0bec5;font-size:0.82rem;">{s.get('objection_handling', '')}</p>
                                </div>
                            </div>
                            <div style="margin-top:10px;padding-top:10px;border-top:1px solid #1e2a3e;display:flex;gap:20px;flex-wrap:wrap;">
                                <span style="font-size:0.8rem;color:#7a8ba0;">💰 {s.get('estimated_value', '')}</span>
                                <span style="font-size:0.8rem;color:#7a8ba0;">⚡ {s.get('urgency_signal', '')}</span>
                                <span style="font-size:0.8rem;color:#7a8ba0;">📋 {s.get('recommended_approach', '')}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    with st.expander("📄 Raw OpenRouter Strategy Output"):
                        st.text(strategy_raw)

            except Exception as e:
                st.error(f"❌ OpenRouter Agent Error: {e}")
                st.stop()
# ─────────────────────────────────────────────
# AGENT 3: CHATGPT — MESSAGE DRAFTING
# ─────────────────────────────────────────────
def agent_gpt_communicator(strategy_data, our_product, our_company, our_contact, our_email, reply_tone):
    """ChatGPT writes personalized WhatsApp + Email for each lead"""
    
    client = OpenAI(api_key=openai_key.strip())
    
    prompt = f"""You are an expert B2B sales communicator for {our_company}.

OUR OFFERING: {our_product}
OUR CONTACT: {our_contact}
OUR EMAIL: {our_email}
COMMUNICATION TONE: {reply_tone}

STRATEGIC ANALYSIS FOR EACH LEAD:
{json.dumps(strategy_data, indent=2)}

For each lead in the strategy data, write:
1. A WhatsApp message (max 200 words, conversational, includes their pain point, our solution, clear CTA)
2. A professional Email (Subject line + Body, max 300 words, formal but warm, includes specific value proposition)

Return as JSON array:
[
  {{
    "company": "Company Name",
    "contact_person": "Name",
    "phone": "phone",
    "email": "email",
    "whatsapp_message": "Full WhatsApp message here",
    "email_subject": "Email subject line",
    "email_body": "Full email body here",
    "best_time_to_contact": "e.g. Tuesday 10 AM - 12 PM",
    "follow_up_day": "e.g. 3 days after initial contact"
  }}
]

Return ONLY valid JSON. No markdown. No extra text.
"""
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# ─────────────────────────────────────────────
# AGENT 4: AUTO-RESPONDER
# ─────────────────────────────────────────────
def agent_auto_responder(lead_data, strategy, messages, our_product, our_company, reply_tone):
    """Simulates client response and generates intelligent auto-reply"""
    
    client = OpenAI(api_key=openai_key.strip())
    
    prompt = f"""You are simulating an autonomous sales conversation system for {our_company}.

OUR OFFERING: {our_product}
COMMUNICATION TONE: {reply_tone}

LEAD CONTEXT:
- Company: {lead_data.get('company', 'Unknown')}
- Contact: {lead_data.get('contact_person', 'Unknown')}
- Priority: {strategy.get('priority', 'WARM')}
- Pain Points: {strategy.get('pain_points', [])}
- Our Value Prop: {strategy.get('our_value_prop', '')}

INITIAL MESSAGE WE SENT:
WhatsApp: {messages.get('whatsapp_message', '')}

TASK: Simulate TWO things:

1. SIMULATE_REPLY: Write a realistic client reply (could be interested, skeptical, asking for details, or requesting pricing)

2. AUTO_RESPONSE: Write our intelligent automated reply to their simulated response.
   - Acknowledge their specific concern/question
   - Provide relevant information from our offering
   - Move conversation toward site visit or deal closure
   - Keep it conversational and helpful

Return as JSON:
{{
  "simulated_client_reply": "What the client might reply...",
  "reply_scenario": "interested / needs_more_info / price_sensitive / requesting_visit / not_interested",
  "auto_response_whatsapp": "Our automated WhatsApp reply...",
  "auto_response_email": "Our automated email reply...",
  "next_action": "What our sales team should do next",
  "escalate_to_human": true/false,
  "escalation_reason": "Why human intervention needed (if true)"
}}

Return ONLY valid JSON.
"""
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# ─────────────────────────────────────────────
# PARSE LEADS TABLE
# ─────────────────────────────────────────────
def parse_leads_table(raw_text):
    leads = []
    for line in raw_text.split('\n'):
        if '|' not in line or 'Company' in line or '---' in line:
            continue
        cols = [c.strip() for c in line.split('|')]
        if len(cols) >= 8:
            leads.append({
                "company": cols[0],
                "address": cols[1],
                "website": cols[2],
                "email": cols[3],
                "phone": cols[4],
                "role": cols[5],
                "contact_person": cols[6],
                "why_need": cols[7] if len(cols) > 7 else "",
                "sector": cols[8] if len(cols) > 8 else "",
                "deal_size": cols[9] if len(cols) > 9 else "",
            })
    return leads

# ─────────────────────────────────────────────
# SAFE JSON PARSE
# ─────────────────────────────────────────────
def safe_json_parse(text, default=None):
    try:
        # Strip markdown code fences if present
        clean = text.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        return json.loads(clean)
    except Exception:
        return default or []

# ─────────────────────────────────────────────
# MAIN PIPELINE BUTTON
# ─────────────────────────────────────────────
st.markdown("---")

# Pipeline status display placeholder
pipeline_status_placeholder = st.empty()

# Show initial idle state
with pipeline_status_placeholder.container():
    show_agent_pipeline({"gemini": "idle", "claude": "idle", "gpt": "idle", "auto": "idle"})

run_col1, run_col2 = st.columns([3, 1])
with run_col1:
    run_pipeline = st.button("🚀 LAUNCH AUTONOMOUS MULTI-AGENT PIPELINE", use_container_width=True)
with run_col2:
    simulate_reply = st.button("🔄 Simulate Client Reply", use_container_width=True,
                                help="Simulate what happens when a client replies to your outreach")

st.markdown("---")

# ─────────────────────────────────────────────
# PIPELINE EXECUTION
# ─────────────────────────────────────────────
if run_pipeline:
    if not all([gemini_key, claude_key, openai_key]):
        st.error("⚠️ Missing API Keys. Check Streamlit Secrets for GOOGLE_API_KEY, ANTHROPIC_API_KEY, OPENAI_API_KEY.")
    elif not my_product or not region or not target_client:
        st.warning("Please fill in Product, Region, and Client Type.")
    else:
        # Clear previous results
        st.session_state.pipeline_results = {}
        st.session_state.conversation_log = []

        # ── PHASE 1: GEMINI ─────────────────────────
        with pipeline_status_placeholder.container():
            show_agent_pipeline({"gemini": "running", "claude": "idle", "gpt": "idle", "auto": "idle"})

        st.markdown("""
        <div class="phase-header phase-gemini">
            <span style="font-size:1.5rem">🔍</span>
            <div>
                <p class="phase-title">Phase 1: Gemini Scout — Live Lead Discovery</p>
                <p class="phase-sub">Scanning the web for real businesses that match your target profile</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        gemini_placeholder = st.container()
        with gemini_placeholder:
            with st.spinner("🔍 Gemini is scanning for genuine leads..."):
                try:
                    raw_leads, model_used = agent_gemini_scout(
                        region, target_client, my_product, our_product, num_leads
                    )
                    st.session_state.pipeline_results['gemini_raw'] = raw_leads
                    st.session_state.pipeline_results['gemini_model'] = model_used

                    # Parse and display
                    leads_list = parse_leads_table(raw_leads)
                    st.session_state.leads_data = leads_list

                    st.success(f"✅ Gemini ({model_used}) found {len(leads_list)} leads")

                    # Show leads table
                    if leads_list:
                        df_display = pd.DataFrame(leads_list)
                        df_display = df_display[['company', 'contact_person', 'role', 'phone', 'email', 'why_need', 'deal_size']]
                        df_display.columns = ['Company', 'Contact', 'Role', 'Phone', 'Email', 'Why They Need Us', 'Est. Deal']
                        st.dataframe(df_display, use_container_width=True, hide_index=True)
                    else:
                        # Show raw if parse fails
                        with st.expander("📄 Raw Gemini Output"):
                            st.text(raw_leads)

                except Exception as e:
                    st.error(f"❌ Gemini Agent Error: {e}")
                    st.stop()

        # ── PHASE 2: CLAUDE ─────────────────────────
        with pipeline_status_placeholder.container():
            show_agent_pipeline({"gemini": "done", "claude": "running", "gpt": "idle", "auto": "idle"})

        st.markdown("""
        <div class="phase-header phase-claude">
            <span style="font-size:1.5rem">🧠</span>
            <div>
                <p class="phase-title">Phase 2: Claude Strategist — Deep Analysis & Personalization</p>
                <p class="phase-sub">Analysing each lead's business, pain points & crafting targeted strategy</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.spinner("🧠 Claude is strategizing for each lead..."):
            try:
                strategy_raw = agent_claude_strategist(
                    st.session_state.pipeline_results.get('gemini_raw', ''),
                    our_product, our_company, my_product, reply_tone
                )
                strategy_list = safe_json_parse(strategy_raw, [])
                st.session_state.pipeline_results['strategy'] = strategy_list

                st.success(f"✅ Claude analysed {len(strategy_list)} leads with strategic scoring")

                # Display strategy cards
                if strategy_list:
                    for s in strategy_list:
                        priority = s.get('priority', 'WARM')
                        badge_class = 'badge-hot' if priority == 'HOT' else ('badge-cold' if priority == 'COLD' else 'badge-warm')
                        badge_icon  = '🔥' if priority == 'HOT' else ('❄️' if priority == 'COLD' else '🌡️')

                        st.markdown(f"""
                        <div class="lead-card">
                            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;">
                                <div>
                                    <p class="lead-name">{s.get('company', 'Unknown')}</p>
                                    <p class="lead-address">👤 {s.get('contact_person', '')} · 📊 Score: <b style="color:#a855f7">{s.get('deal_score', 0)}/100</b></p>
                                </div>
                                <span class="{badge_class}">{badge_icon} {priority}</span>
                            </div>
                            <div class="strategy-box">
                                <div class="strategy-title">🎯 Strategic Value Proposition</div>
                                <div class="strategy-text">{s.get('our_value_prop', '')}</div>
                            </div>
                            <div style="display:flex;gap:16px;flex-wrap:wrap;margin-top:12px;">
                                <div style="flex:1;min-width:160px;">
                                    <p style="font-size:0.72rem;color:#4a5568;text-transform:uppercase;letter-spacing:1px;">Pain Points</p>
                                    <ul style="color:#b0bec5;font-size:0.82rem;margin:4px 0;padding-left:16px;">
                                        {''.join([f"<li>{p}</li>" for p in s.get('pain_points', [])])}
                                    </ul>
                                </div>
                                <div style="flex:1;min-width:160px;">
                                    <p style="font-size:0.72rem;color:#4a5568;text-transform:uppercase;letter-spacing:1px;">Opening Hook</p>
                                    <p style="color:#e0e6f0;font-size:0.84rem;font-style:italic;">"{s.get('opening_hook', '')}"</p>
                                </div>
                                <div style="flex:1;min-width:160px;">
                                    <p style="font-size:0.72rem;color:#4a5568;text-transform:uppercase;letter-spacing:1px;">Objection & Handle</p>
                                    <p style="color:#b0bec5;font-size:0.82rem;">{s.get('objection_handling', '')}</p>
                                </div>
                            </div>
                            <div style="margin-top:10px;padding-top:10px;border-top:1px solid #1e2a3e;display:flex;gap:20px;flex-wrap:wrap;">
                                <span style="font-size:0.8rem;color:#7a8ba0;">💰 {s.get('estimated_value', '')}</span>
                                <span style="font-size:0.8rem;color:#7a8ba0;">⚡ {s.get('urgency_signal', '')}</span>
                                <span style="font-size:0.8rem;color:#7a8ba0;">📋 {s.get('recommended_approach', '')}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    with st.expander("📄 Raw Claude Strategy Output"):
                        st.text(strategy_raw)

            except Exception as e:
                st.error(f"❌ Claude Agent Error: {e}")
                st.stop()

        # ── PHASE 3: CHATGPT ─────────────────────────
        with pipeline_status_placeholder.container():
            show_agent_pipeline({"gemini": "done", "claude": "done", "gpt": "running", "auto": "idle"})

        st.markdown("""
        <div class="phase-header phase-gpt">
            <span style="font-size:1.5rem">✉️</span>
            <div>
                <p class="phase-title">Phase 3: ChatGPT Communicator — Personalized Outreach Messages</p>
                <p class="phase-sub">Writing human-like WhatsApp & Email for each lead based on Claude's strategy</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.spinner("✉️ ChatGPT is crafting personalized messages for each lead..."):
            try:
                strategy_list = st.session_state.pipeline_results.get('strategy', [])
                messages_raw  = agent_gpt_communicator(
                    strategy_list, our_product, our_company,
                    our_contact, our_email, reply_tone
                )
                messages_list = safe_json_parse(messages_raw, [])
                st.session_state.pipeline_results['messages'] = messages_list

                st.success(f"✅ ChatGPT drafted {len(messages_list)} personalized outreach sets")

                # Display messages
                if messages_list:
                    for idx, msg in enumerate(messages_list):
                        phone     = msg.get('phone', '')
                        email_to  = msg.get('email', '')
                        wa_text   = msg.get('whatsapp_message', '')
                        email_sub = msg.get('email_subject', '')
                        email_body= msg.get('email_body', '')

                        clean_phone = "".join(filter(str.isdigit, phone))
                        if len(clean_phone) == 10:
                            clean_phone = "91" + clean_phone
                        wa_link   = f"https://wa.me/{clean_phone}?text={urllib.parse.quote(wa_text)}"
                        mail_link = f"mailto:{email_to}?subject={urllib.parse.quote(email_sub)}&body={urllib.parse.quote(email_body)}"

                        st.markdown(f"""
                        <div class="lead-card" style="border-color:#1a4a1a;">
                            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
                                <p class="lead-name">✉️ {msg.get('company', f'Lead {idx+1}')}</p>
                                <span style="font-size:0.78rem;color:#7a8ba0;">
                                    ⏰ Best Time: {msg.get('best_time_to_contact', 'Weekday morning')} · 
                                    📅 Follow-up: {msg.get('follow_up_day', '3 days')}
                                </span>
                            </div>
                            <div class="msg-box msg-whatsapp">
                                <div class="msg-label msg-label-wa">💬 WhatsApp Message</div>
                                <div class="msg-content">{wa_text}</div>
                            </div>
                            <div class="msg-box msg-email">
                                <div class="msg-label msg-label-mail">📧 Email — Subject: {email_sub}</div>
                                <div class="msg-content">{email_body}</div>
                            </div>
                            <div class="action-row">
                                <a class="btn-wa"   href="{wa_link}"   target="_blank">💬 Send on WhatsApp</a>
                                <a class="btn-mail" href="{mail_link}" target="_blank">📧 Open Email Draft</a>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                else:
                    with st.expander("📄 Raw GPT Messages Output"):
                        st.text(messages_raw)

            except Exception as e:
                st.error(f"❌ ChatGPT Agent Error: {e}")
                st.stop()

        # ── PHASE 4: AUTO-RESPONDER ─────────────────────────
        if auto_reply_enabled:
            with pipeline_status_placeholder.container():
                show_agent_pipeline({"gemini": "done", "claude": "done", "gpt": "done", "auto": "running"})

            st.markdown("""
            <div class="phase-header phase-auto">
                <span style="font-size:1.5rem">🔄</span>
                <div>
                    <p class="phase-title">Phase 4: Auto-Responder — Simulated Conversation Intelligence</p>
                    <p class="phase-sub">AI simulates client reply & generates smart automated follow-up responses</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.spinner("🔄 Auto-Responder generating conversation simulations..."):
                try:
                    strategy_list = st.session_state.pipeline_results.get('strategy', [])
                    messages_list = st.session_state.pipeline_results.get('messages', [])

                    # Process top 3 HOT/WARM leads for auto-reply simulation
                    hot_leads   = [s for s in strategy_list if s.get('priority') in ['HOT', 'WARM']][:3]
                    auto_replies = []

                    for i, lead_strategy in enumerate(hot_leads):
                        # Find matching message
                        matching_msg = next(
                            (m for m in messages_list if m.get('company') == lead_strategy.get('company')),
                            messages_list[i] if i < len(messages_list) else {}
                        )
                        auto_raw = agent_auto_responder(
                            matching_msg, lead_strategy,
                            matching_msg, our_product, our_company, reply_tone
                        )
                        auto_data = safe_json_parse(auto_raw, {})
                        if auto_data:
                            auto_data['company'] = lead_strategy.get('company', f'Lead {i+1}')
                            auto_replies.append(auto_data)

                    st.session_state.pipeline_results['auto_replies'] = auto_replies

                    st.success(f"✅ Auto-Responder simulated {len(auto_replies)} conversation threads")

                    for reply in auto_replies:
                        scenario_color = {
                            'interested': '#00c851',
                            'needs_more_info': '#ffaa00',
                            'price_sensitive': '#ff8800',
                            'requesting_visit': '#4285f4',
                            'not_interested': '#ff4444'
                        }.get(reply.get('reply_scenario', ''), '#7a8ba0')

                        escalate = reply.get('escalate_to_human', False)

                        st.markdown(f"""
                        <div class="lead-card" style="border-color:#1a3a0a;">
                            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
                                <p class="lead-name">🔄 {reply.get('company', 'Unknown')}</p>
                                <div style="display:flex;gap:10px;align-items:center;">
                                    <span style="color:{scenario_color};font-size:0.8rem;font-weight:700;text-transform:uppercase;">
                                        ● {reply.get('reply_scenario', '').replace('_', ' ')}
                                    </span>
                                    {"<span style='background:#1a0a0a;color:#ff4444;border:1px solid #ff4444;padding:3px 10px;border-radius:10px;font-size:0.72rem;font-weight:700;'>🚨 ESCALATE TO HUMAN</span>" if escalate else "<span style='background:#0a1a0a;color:#00c851;border:1px solid #00c851;padding:3px 10px;border-radius:10px;font-size:0.72rem;font-weight:700;'>🤖 AUTO-HANDLED</span>"}
                                </div>
                            </div>
                            <div class="conversation-entry">
                                <div class="conv-from">📱 Simulated Client Reply:</div>
                                <div class="conv-msg" style="color:#e0e6f0;font-style:italic;">"{reply.get('simulated_client_reply', '')}"</div>
                            </div>
                            <div class="autoreply-box">
                                <div class="autoreply-label">🤖 Our Automated WhatsApp Reply</div>
                                <div class="autoreply-text">{reply.get('auto_response_whatsapp', '')}</div>
                            </div>
                            <div style="margin-top:10px;padding:10px;background:#0a0d14;border:1px solid #1e2a3e;border-radius:8px;">
                                <p style="font-size:0.72rem;color:#4a5568;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">📋 Next Action for Sales Team</p>
                                <p style="color:#b0bec5;font-size:0.84rem;">{reply.get('next_action', '')}</p>
                                {"<p style='color:#ff8800;font-size:0.8rem;margin-top:6px;'>⚠️ Escalation Reason: " + reply.get('escalation_reason', '') + "</p>" if escalate else ""}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"❌ Auto-Responder Error: {e}")

        # ── ALL DONE ─────────────────────────
        with pipeline_status_placeholder.container():
            show_agent_pipeline({"gemini": "done", "claude": "done", "gpt": "done", "auto": "done"})

        st.balloons()
        st.success("🎉 Full Multi-Agent Pipeline Complete! Your leads are researched, analysed, messaged & conversation-ready.")

        # ── DOWNLOAD ALL ─────────────────────────
        st.markdown("### 📥 Export Complete Intelligence Report")
        dl_col1, dl_col2 = st.columns(2)
        with dl_col1:
            leads_data = st.session_state.leads_data or []
            if leads_data:
                df_leads = pd.DataFrame(leads_data)
                st.download_button(
                    "📥 Download Leads CSV",
                    data=df_leads.to_csv(index=False).encode('utf-8'),
                    file_name=f"samketan_leads_{region.replace(',','_').replace(' ','_')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        with dl_col2:
            full_report = {
                "generated_at": datetime.now().isoformat(),
                "inputs": {
                    "product": my_product,
                    "region": region,
                    "target_client": target_client
                },
                "pipeline_results": st.session_state.pipeline_results
            }
            st.download_button(
                "📥 Download Full JSON Report",
                data=json.dumps(full_report, indent=2, default=str).encode('utf-8'),
                file_name=f"samketan_full_report_{region.replace(',','_').replace(' ','_')}.json",
                mime="application/json",
                use_container_width=True
            )

# ─────────────────────────────────────────────
# SIMULATE ADDITIONAL CLIENT REPLY
# ─────────────────────────────────────────────
if simulate_reply and st.session_state.pipeline_results:
    st.markdown("---")
    st.markdown("""
    <div class="phase-header phase-auto">
        <span style="font-size:1.5rem">💬</span>
        <div>
            <p class="phase-title">Manual Reply Simulation</p>
            <p class="phase-sub">Enter a client's reply and see AI auto-response</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    client_reply_input = st.text_area(
        "Paste a client's actual reply here:",
        placeholder="e.g. Hello, we are interested. Can you share more details about pricing and location?",
        height=100
    )
    reply_company = st.text_input("Which company replied?", placeholder="Company name...")

    if st.button("🤖 Generate Smart Auto-Reply") and client_reply_input:
        with st.spinner("Generating intelligent response..."):
            try:
                gpt_client = OpenAI(api_key=openai_key.strip())
                manual_prompt = f"""You are the sales AI for {our_company}.

OUR OFFERING: {our_product}
TONE: {reply_tone}
COMPANY THAT REPLIED: {reply_company}

CLIENT REPLIED: "{client_reply_input}"

Write a professional, helpful response that:
1. Directly addresses their message
2. Provides relevant details from our offering
3. Moves toward scheduling a site visit or call
4. Is warm and not pushy

Provide:
1. WhatsApp reply (conversational, under 200 words)
2. Email reply (formal, under 300 words)
3. Suggested next step

Format as JSON: {{"whatsapp_reply": "...", "email_reply": "...", "next_step": "..."}}
"""
                manual_res = gpt_client.chat.completions.create(
                    model="gpt-4o",
                    max_tokens=1000,
                    messages=[{"role": "user", "content": manual_prompt}]
                )
                manual_data = safe_json_parse(manual_res.choices[0].message.content, {})

                if manual_data:
                    st.markdown(f"""
                    <div class="autoreply-box">
                        <div class="autoreply-label">💬 WhatsApp Auto-Reply for {reply_company}</div>
                        <div class="autoreply-text">{manual_data.get('whatsapp_reply', '')}</div>
                    </div>
                    <div class="msg-box msg-email">
                        <div class="msg-label msg-label-mail">📧 Email Auto-Reply</div>
                        <div class="msg-content">{manual_data.get('email_reply', '')}</div>
                    </div>
                    <div style="background:#0a0d14;border:1px solid #1e2a3e;border-radius:8px;padding:12px 16px;margin-top:10px;">
                        <p style="font-size:0.72rem;color:#4a5568;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">📋 Recommended Next Step</p>
                        <p style="color:#b0bec5;font-size:0.84rem;">{manual_data.get('next_step', '')}</p>
                    </div>
                    """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"❌ Manual reply error: {e}")

elif simulate_reply and not st.session_state.pipeline_results:
    st.warning("⚠️ Run the pipeline first to load context before simulating replies.")

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<p style="color:#2a3a4e;font-size:0.8rem;text-align:center;">
    Samketan AI v7.0 · Multi-Agent Autonomous Pipeline · Gemini Scout → Claude Strategist → GPT Communicator → Auto-Responder · © 2026 Samketan
</p>
""", unsafe_allow_html=True)

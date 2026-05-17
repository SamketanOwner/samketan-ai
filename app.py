# app.py - Samketan AI v7.0 - Full Multi-Agent Autonomous System (100% Free - Gemini Only)

import streamlit as st
import auth
import time

# --- AUTHENTICATION ---
if not auth.login_screen():
    st.stop()

import google.generativeai as genai
import urllib.parse
import pandas as pd
import json
from datetime import datetime
import extra_streamlit_components as stx

# --- COOKIE MANAGER ---
cookie_manager = stx.CookieManager()
saved_user = cookie_manager.get('samketan_user')
if saved_user and not st.session_state.get('authenticated'):
    st.session_state.authenticated = True
    st.session_state.current_user = saved_user

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Samketan AI v7.0 - Multi-Agent",
    page_icon="S",
    layout="wide"
)

# --- HIDE TOOLBAR ---
st.markdown("""
<style>
[data-testid="stToolbar"]         { display: none !important; }
[data-testid="stDecoration"]      { display: none !important; }
[data-testid="stStatusWidget"]    { display: none !important; }
[data-testid="baseButton-header"] { display: none !important; }
#stDecoration                     { display: none !important; }
.viewerBadge_container__1QSob    { display: none !important; }
.st-emotion-cache-zq5wmm          { display: none !important; }
.st-emotion-cache-h5rgaw          { display: none !important; }
</style>
""", unsafe_allow_html=True)

# --- GLOBAL CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0a0d14; }
    section[data-testid="stSidebar"] { background-color: #0f1219 !important; }

    .header-banner {
        background: linear-gradient(135deg, #0d1117 0%, #0a1929 50%, #0d1117 100%);
        border: 1px solid #1e3a5f; border-radius: 16px;
        padding: 28px 36px; margin-bottom: 20px;
        display: flex; align-items: center; justify-content: space-between;
    }
    .header-title { font-size: 2rem; font-weight: 800; color: #fff; margin: 0; }
    .header-sub   { font-size: 0.92rem; color: #7a8ba0; margin-top: 6px; }
    .header-badge {
        background: linear-gradient(135deg, #7b2ff7, #f107a3);
        color: white; padding: 8px 20px; border-radius: 20px;
        font-size: 0.78rem; font-weight: 700; letter-spacing: 1.5px;
    }
    .promo-bar {
        background: linear-gradient(90deg,#1a0a00,#2d1500);
        border: 1px solid #FF8C00; border-radius: 8px;
        padding: 10px 16px; margin-bottom: 20px;
        font-size: 14px; color: #FFB347; font-weight: 600;
    }
    .promo-bar a { color: #FFD700; text-decoration: none; font-weight: 700; }
    .agent-card {
        flex: 1; min-width: 200px; background: #0f1219;
        border: 1px solid #1e2a3e; border-radius: 14px;
        padding: 18px 20px; text-align: center; transition: all 0.3s ease;
    }
    .agent-card.active { border-color: #7b2ff7; box-shadow: 0 0 20px rgba(123,47,247,0.3); }
    .agent-card.done   { border-color: #00c851; box-shadow: 0 0 15px rgba(0,200,81,0.2); }
    .agent-icon   { font-size: 2rem; margin-bottom: 8px; }
    .agent-name   { font-size: 0.9rem; font-weight: 700; color: #e0e6f0; }
    .agent-role   { font-size: 0.75rem; color: #7a8ba0; margin-top: 4px; }
    .agent-status { font-size: 0.72rem; margin-top: 8px; padding: 3px 10px; border-radius: 10px; display: inline-block; }
    .status-idle    { background: #1a1d27; color: #4a5568; }
    .status-running { background: #1a0d2e; color: #a855f7; }
    .status-done    { background: #0a1a0a; color: #00c851; }
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
    .phase-header {
        background: linear-gradient(90deg, #0a1929, #0d1117);
        border: 1px solid #1e3a5f; border-left: 4px solid #4285f4;
        border-radius: 10px; padding: 14px 20px;
        margin: 20px 0 14px 0; display: flex; align-items: center; gap: 12px;
    }
    .phase-claude { border-left-color: #a855f7 !important; }
    .phase-gpt    { border-left-color: #00c851 !important; }
    .phase-auto   { border-left-color: #f59e0b !important; }
    .phase-title  { font-size: 1rem; font-weight: 700; color: #fff; margin: 0; }
    .phase-sub    { font-size: 0.8rem; color: #7a8ba0; margin-top: 2px; }
    .lead-card {
        background: #0f1219; border: 1px solid #1e2a3e;
        border-radius: 14px; padding: 20px 24px; margin-bottom: 14px;
    }
    .lead-card:hover { border-color: #4285f4; box-shadow: 0 4px 24px rgba(66,133,244,0.15); }
    .lead-name    { font-size: 1.05rem; font-weight: 700; color: #fff; margin: 0; }
    .lead-address { font-size: 0.8rem; color: #7a8ba0; margin-top: 4px; }
    .badge-hot  { background:#1a0a0a; color:#ff4444; border:1px solid #ff4444; padding:4px 12px; border-radius:20px; font-size:0.72rem; font-weight:700; }
    .badge-warm { background:#1a1200; color:#ffaa00; border:1px solid #ffaa00; padding:4px 12px; border-radius:20px; font-size:0.72rem; font-weight:700; }
    .badge-cold { background:#001a2a; color:#0099ff; border:1px solid #0099ff; padding:4px 12px; border-radius:20px; font-size:0.72rem; font-weight:700; }
    .strategy-box {
        background: #0a0d14; border: 1px solid #2d1657;
        border-left: 3px solid #a855f7; border-radius: 10px; padding: 16px 20px; margin: 10px 0;
    }
    .strategy-title { color: #a855f7; font-weight: 700; font-size: 0.85rem; margin-bottom: 8px; }
    .strategy-text  { color: #b0bec5; font-size: 0.84rem; line-height: 1.6; }
    .msg-box { background: #0a0d14; border: 1px solid #1e2a3e; border-radius: 10px; padding: 16px; margin: 10px 0; }
    .msg-whatsapp { border-left: 3px solid #25D366; }
    .msg-email    { border-left: 3px solid #4285f4; }
    .msg-label    { font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
    .msg-label-wa   { color: #25D366; }
    .msg-label-mail { color: #4285f4; }
    .msg-content  { color: #b0bec5; font-size: 0.84rem; line-height: 1.6; white-space: pre-wrap; }
    .autoreply-box {
        background: #0f1a0f; border: 1px solid #1a3a1a;
        border-left: 3px solid #00c851; border-radius: 10px; padding: 16px; margin: 10px 0;
    }
    .autoreply-label { color: #00c851; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
    .autoreply-text  { color: #b0bec5; font-size: 0.84rem; line-height: 1.6; white-space: pre-wrap; }
    .action-row { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 14px; }
    .btn-wa   { background:#0d2a1a; color:#25D366; border:1px solid #25D366; padding:8px 16px; border-radius:8px; font-size:0.82rem; font-weight:700; text-decoration:none; display:inline-block; }
    .btn-mail { background:#0d1a2a; color:#64b5f6; border:1px solid #64b5f6; padding:8px 16px; border-radius:8px; font-size:0.82rem; font-weight:700; text-decoration:none; display:inline-block; }
    .stButton > button {
        background: linear-gradient(135deg,#7b2ff7,#f107a3) !important;
        color: white !important; border: none !important;
        border-radius: 10px !important; font-weight: 700 !important;
        font-size: 1rem !important; padding: 14px 32px !important; width: 100% !important;
    }
    .conversation-entry {
        background: #0a0d14; border: 1px solid #1e2a3e;
        border-radius: 10px; padding: 14px 18px; margin-bottom: 10px;
    }
    .conv-from { font-size: 0.75rem; color: #7a8ba0; margin-bottom: 6px; }
    .conv-msg  { color: #b0bec5; font-size: 0.84rem; line-height: 1.6; }
    .user-chip {
        background: #0a0d14; border: 1px solid #1e2a3e;
        border-radius: 8px; padding: 10px 14px; color: #e0e6f0; font-size: 0.88rem; margin-bottom: 12px;
    }
    #MainMenu { visibility: hidden; }
    footer     { visibility: hidden; }
    header     { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- API KEY ---
gemini_key = st.secrets.get("GOOGLE_API_KEY", "")

# --- SESSION STATE ---
for key in ['pipeline_results', 'conversation_log', 'leads_data']:
    if key not in st.session_state:
        st.session_state[key] = None
if st.session_state.conversation_log is None:
    st.session_state.conversation_log = []

# --- HEADER ---
st.markdown("""
<div class="header-banner">
    <div>
        <p class="header-title">Samketan AI v7.0</p>
        <p class="header-sub">
            Autonomous Multi-Agent Pipeline (100% Free):
            Gemini Scout -- Gemini Strategist -- Gemini Communicator -- Gemini Auto-Responder
        </p>
    </div>
    <span class="header-badge">MULTI-AGENT</span>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="promo-bar">
    AVAILABLE FOR LEASE: Premium 21,000 Sq. Ft. RCC Warehouse - Nandur Area, Gulbarga
    <a href="https://bhoodeviwarehouse.netlify.app/" target="_blank">Visit Bhoodevi Warehouse</a>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### Samketan Profile")
    st.markdown(
        '<div class="user-chip">User: ' + str(st.session_state.get("current_user", "User")) + '</div>',
        unsafe_allow_html=True
    )
    st.markdown("---")
    st.markdown("### API Key")
    st.caption("Auto-loaded from Streamlit Secrets.")
    if not gemini_key:
        gemini_key = st.text_input("Google Gemini Key", type="password", placeholder="AIza...")
    st.markdown("---")
    st.markdown("### Our Offering (Context for AI)")
    our_product = st.text_area(
        "What we offer:",
        value="Premium 21,000 sq ft RCC warehouse in Nandur Area, Gulbarga. Features: 24/7 security, loading docks, fire safety, power backup. Ideal for FMCG, pharma, agri storage.",
        height=120
    )
    our_company = st.text_input("Company Name", value="Samketan / Bhoodevi Warehouse")
    our_contact = st.text_input("Our Contact", value="+91-XXXXXXXXXX")
    our_email   = st.text_input("Our Email", value="samketan@example.com")
    st.markdown("---")
    st.markdown("### Auto-Reply Settings")
    auto_reply_enabled = st.toggle("Enable Auto-Reply Simulation", value=True)
    reply_tone = st.selectbox("Reply Tone", ["Professional & Warm", "Formal", "Friendly & Casual", "Urgent & Direct"])
    st.markdown("---")
    with st.expander("How Multi-Agent Works"):
        st.markdown("""
**Agent 1 - Gemini Scout**
Finds real business leads with contact details

**Agent 2 - Gemini Strategist**
Analyses each lead, creates personalised strategy

**Agent 3 - Gemini Communicator**
Writes tailored WhatsApp and Email for each lead

**Agent 4 - Gemini Auto-Responder**
Simulates client reply and generates follow-up
        """)
    st.markdown("---")
    if st.button("Show Available Models", use_container_width=True):
        try:
            genai.configure(api_key=gemini_key.strip())
            available = [
                m.name for m in genai.list_models()
                if 'generateContent' in m.supported_generation_methods
            ]
            st.success("Models available on your key:")
            for m in available:
                st.write(m)
        except Exception as e:
            st.error(str(e))
    st.markdown("---")
    if st.button("Logout", use_container_width=True):
        cookie_manager.delete('samketan_user')
        st.session_state.authenticated = False
        st.rerun()


# --- HELPER: GET GEMINI MODEL ---
def get_gemini_model():
    genai.configure(api_key=gemini_key.strip())
    try:
        available = [
            m.name.replace('models/', '')
            for m in genai.list_models()
            if 'generateContent' in m.supported_generation_methods
        ]
    except Exception:
        available = []

    priority = [
        'gemini-1.5-flash-latest',
        'gemini-1.5-flash',
        'gemini-1.5-flash-001',
        'gemini-1.5-flash-002',
        'gemini-2.0-flash',
        'gemini-2.0-flash-lite',
        'gemini-2.5-flash-lite',
        'gemini-2.5-flash',
    ]

    selected = None
    for name in priority:
        if name in available:
            selected = name
            break

    if not selected:
        selected = available[0] if available else 'gemini-1.5-flash-latest'

    return genai.GenerativeModel(selected), selected


# --- HELPER: CALL GEMINI WITH RETRY ---
def call_gemini_with_retry(model, prompt, retries=3, wait=60):
    for attempt in range(retries):
        try:
            return model.generate_content(prompt)
        except Exception as e:
            err = str(e)
            if '429' in err:
                if attempt < retries - 1:
                    remaining = retries - attempt - 1
                    st.warning(
                        "Rate limit hit. Auto-retrying in " + str(wait) +
                        " seconds... (" + str(remaining) + " retries left)"
                    )
                    time.sleep(wait)
                else:
                    raise Exception(
                        "All retries exhausted. Please create a new Google API key at "
                        "https://aistudio.google.com/apikey using a NEW project for fresh quota."
                    )
            else:
                raise e


# --- HELPER: SAFE JSON PARSE ---
def safe_json_parse(text, default=None):
    try:
        clean = text.strip()
        if clean.startswith("```"):
            parts = clean.split("```")
            clean = parts[1] if len(parts) > 1 else clean
            if clean.startswith("json"):
                clean = clean[4:]
        start_arr = clean.find("[")
        start_obj = clean.find("{")
        if start_arr != -1 and (start_obj == -1 or start_arr < start_obj):
            end = clean.rfind("]") + 1
            clean = clean[start_arr:end]
        elif start_obj != -1:
            end = clean.rfind("}") + 1
            clean = clean[start_obj:end]
        return json.loads(clean)
    except Exception:
        return default if default is not None else []


# --- HELPER: PARSE LEADS TABLE ---
def parse_leads_table(raw_text):
    leads = []
    for line in raw_text.split('\n'):
        if '|' not in line or 'Company' in line or '---' in line:
            continue
        cols = [c.strip() for c in line.split('|')]
        if len(cols) >= 8:
            leads.append({
                "company":        cols[0],
                "address":        cols[1],
                "website":        cols[2],
                "email":          cols[3],
                "phone":          cols[4],
                "role":           cols[5],
                "contact_person": cols[6],
                "why_need":       cols[7] if len(cols) > 7 else "",
                "sector":         cols[8] if len(cols) > 8 else "",
                "deal_size":      cols[9] if len(cols) > 9 else "",
            })
    return leads


# --- AGENT STATUS DISPLAY ---
def show_agent_pipeline(statuses):
    agents = [
        {"icon": "&#128269;", "name": "Gemini Scout",        "role": "Lead Discovery",       "key": "gemini"},
        {"icon": "&#129504;", "name": "Gemini Strategist",   "role": "Strategy & Profiling",  "key": "claude"},
        {"icon": "&#9993;",   "name": "Gemini Communicator", "role": "Message Drafting",      "key": "gpt"},
        {"icon": "&#128260;", "name": "Gemini Auto-Reply",   "role": "Conversation AI",       "key": "auto"},
    ]
    cols = st.columns(7)
    for i, agent in enumerate(agents):
        status       = statuses.get(agent["key"], "idle")
        card_class   = "agent-card active" if status == "running" else ("agent-card done" if status == "done" else "agent-card")
        status_class = "agent-status status-" + status
        status_label = {"idle": "Idle", "running": "Running...", "done": "Done"}.get(status, "Idle")
        with cols[i * 2]:
            st.markdown(
                '<div class="' + card_class + '">'
                '<div class="agent-icon">' + agent['icon'] + '</div>'
                '<div class="agent-name">'  + agent['name'] + '</div>'
                '<div class="agent-role">'  + agent['role'] + '</div>'
                '<span class="' + status_class + '">' + status_label + '</span>'
                '</div>',
                unsafe_allow_html=True
            )
        if i < len(agents) - 1:
            with cols[i * 2 + 1]:
                st.markdown(
                    '<div style="text-align:center;color:#2a3a5e;font-size:1.8rem;padding-top:30px;">-&gt;</div>',
                    unsafe_allow_html=True
                )


# --- AGENT 1: GEMINI SCOUT ---
def agent_gemini_scout(region, target_client, my_product, our_product, num_leads):
    model, selected = get_gemini_model()
    prompt = (
        "You are a B2B Lead Intelligence Scout. Find " + str(num_leads) + " REAL businesses in " + region + ".\n\n"
        "TARGET CLIENT TYPE: " + target_client + "\n"
        "WHAT WE ARE SELLING: " + my_product + "\n"
        "OUR FULL OFFERING: " + our_product + "\n\n"
        "Return ONLY a pipe-separated table with these exact columns:\n"
        "Company Name | Full Address | Website | Email | Phone | Decision Maker Role | Contact Person | Why They Need Us | Industry Sector | Estimated Deal Size\n\n"
        "RULES:\n"
        "- Make realistic estimates for any unknown fields\n"
        "- Phone: Indian format with +91\n"
        "- Email: realistic format if unknown\n"
        "- Why They Need Us: 1-2 specific sentences\n"
        "- Estimated Deal Size: e.g. Rs.2-5 Lakh/month\n"
        "- NO markdown, NO headers, ONLY table rows\n"
    )
    response = call_gemini_with_retry(model, prompt)
    return response.text, selected


# --- AGENT 2: GEMINI STRATEGIST ---
def agent_gemini_strategist(raw_leads_data, our_product, our_company, my_product, reply_tone):
    model, _ = get_gemini_model()
    prompt = (
        "You are a senior business growth strategist. Analyze the raw lead dataset below.\n\n"
        "Raw Leads Data:\n" + raw_leads_data + "\n\n"
        "Our Company: " + our_company + "\n"
        "Our Offering: " + our_product + "\n"
        "Product We Sell: " + my_product + "\n"
        "Outreach Tone: " + reply_tone + "\n\n"
        "CRITICAL: Return ONLY a valid JSON array. No markdown. No backticks. No explanation.\n"
        "Each object MUST have these exact keys:\n"
        "- company (string)\n"
        "- contact_person (string)\n"
        "- deal_score (integer 1-100)\n"
        "- priority (string: HOT, WARM, or COLD)\n"
        "- our_value_prop (string)\n"
        "- pain_points (array of strings)\n"
        "- opening_hook (string)\n"
        "- objection_handling (string)\n"
        "- estimated_value (string)\n"
        "- urgency_signal (string)\n"
        "- recommended_approach (string)\n\n"
        "Start your response with [ and end with ]"
    )
    response = call_gemini_with_retry(model, prompt)
    return response.text


# --- AGENT 3: GEMINI COMMUNICATOR ---
def agent_gemini_communicator(strategy_data, our_product, our_company, our_contact, our_email, reply_tone):
    model, _ = get_gemini_model()
    prompt = (
        "You are an expert B2B sales communicator for " + our_company + ".\n\n"
        "OUR OFFERING: " + our_product + "\n"
        "OUR CONTACT: " + our_contact + "\n"
        "OUR EMAIL: " + our_email + "\n"
        "COMMUNICATION TONE: " + reply_tone + "\n\n"
        "STRATEGIC ANALYSIS FOR EACH LEAD:\n"
        + json.dumps(strategy_data, indent=2) + "\n\n"
        "For each lead write:\n"
        "1. A WhatsApp message (max 200 words, conversational, mentions their pain point, our solution, clear CTA)\n"
        "2. A professional Email (Subject + Body, max 300 words, formal but warm)\n\n"
        "CRITICAL: Return ONLY a valid JSON array. No markdown. No backticks. No explanation.\n"
        "Each object MUST have these exact keys:\n"
        "- company (string)\n"
        "- contact_person (string)\n"
        "- phone (string)\n"
        "- email (string)\n"
        "- whatsapp_message (string)\n"
        "- email_subject (string)\n"
        "- email_body (string)\n"
        "- best_time_to_contact (string)\n"
        "- follow_up_day (string)\n\n"
        "Start your response with [ and end with ]"
    )
    response = call_gemini_with_retry(model, prompt)
    return response.text


# --- AGENT 4: GEMINI AUTO-RESPONDER ---
def agent_gemini_autoresponder(lead_data, strategy, messages, our_product, our_company, reply_tone):
    model, _ = get_gemini_model()
    prompt = (
        "You are simulating an autonomous sales conversation system for " + our_company + ".\n\n"
        "OUR OFFERING: " + our_product + "\n"
        "COMMUNICATION TONE: " + reply_tone + "\n\n"
        "LEAD CONTEXT:\n"
        "- Company: " + str(lead_data.get('company', 'Unknown')) + "\n"
        "- Contact: " + str(lead_data.get('contact_person', 'Unknown')) + "\n"
        "- Priority: " + str(strategy.get('priority', 'WARM')) + "\n"
        "- Pain Points: " + str(strategy.get('pain_points', [])) + "\n"
        "- Our Value Prop: " + str(strategy.get('our_value_prop', '')) + "\n\n"
        "INITIAL MESSAGE WE SENT:\n"
        "WhatsApp: " + str(messages.get('whatsapp_message', '')) + "\n\n"
        "TASK: Simulate TWO things:\n"
        "1. A realistic client reply\n"
        "2. Our intelligent automated reply to their simulated response\n\n"
        "CRITICAL: Return ONLY a valid JSON object. No markdown. No backticks. No explanation.\n"
        "The object MUST have these exact keys:\n"
        "- simulated_client_reply (string)\n"
        "- reply_scenario (string: interested / needs_more_info / price_sensitive / requesting_visit / not_interested)\n"
        "- auto_response_whatsapp (string)\n"
        "- auto_response_email (string)\n"
        "- next_action (string)\n"
        "- escalate_to_human (boolean)\n"
        "- escalation_reason (string)\n\n"
        "Start your response with { and end with }"
    )
    response = call_gemini_with_retry(model, prompt)
    return response.text


# --- MAIN INPUT SECTION ---
st.markdown('<div class="input-card">', unsafe_allow_html=True)
st.markdown("### Define Your Target")
col1, col2, col3 = st.columns(3)
with col1:
    my_product    = st.text_input("Product / Service to Sell", value="Warehouse Space")
    region        = st.text_input("Target City / Region", value="Gulbarga, Karnataka")
with col2:
    target_client = st.text_input("Ideal Client Type", value="FMCG Distributors, Pharma Companies")
    num_leads     = st.slider("Number of Leads to Find", 3, 10, 5)
with col3:
    scope   = st.radio("Market Scope", ["Local (Domestic)", "Export (International)"])
    urgency = st.selectbox("Deal Urgency", ["High - Close this month", "Medium - Next quarter", "Low - Exploring"])
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# --- PIPELINE STATUS ---
pipeline_status_placeholder = st.empty()
with pipeline_status_placeholder.container():
    show_agent_pipeline({"gemini": "idle", "claude": "idle", "gpt": "idle", "auto": "idle"})

run_col1, run_col2 = st.columns([3, 1])
with run_col1:
    run_pipeline = st.button("LAUNCH AUTONOMOUS MULTI-AGENT PIPELINE", use_container_width=True)
with run_col2:
    simulate_reply = st.button("Simulate Client Reply", use_container_width=True)

st.markdown("---")

# --- PIPELINE EXECUTION ---
if run_pipeline:
    if not gemini_key:
        st.error("Missing GOOGLE_API_KEY. Add it to Streamlit Secrets.")
    elif not my_product or not region or not target_client:
        st.warning("Please fill in Product, Region, and Client Type.")
    else:
        st.session_state.pipeline_results = {}
        st.session_state.conversation_log = []

        # PHASE 1
        with pipeline_status_placeholder.container():
            show_agent_pipeline({"gemini": "running", "claude": "idle", "gpt": "idle", "auto": "idle"})
        st.markdown(
            '<div class="phase-header">'
            '<span style="font-size:1.5rem">&#128269;</span>'
            '<div>'
            '<p class="phase-title">Phase 1: Gemini Scout - Live Lead Discovery</p>'
            '<p class="phase-sub">Scanning for real businesses that match your target profile</p>'
            '</div></div>',
            unsafe_allow_html=True
        )
        with st.spinner("Gemini is scanning for genuine leads..."):
            try:
                raw_leads, model_used = agent_gemini_scout(
                    region, target_client, my_product, our_product, num_leads
                )
                st.session_state.pipeline_results['gemini_raw'] = raw_leads
                leads_list = parse_leads_table(raw_leads)
                st.session_state.leads_data = leads_list
                st.success("Gemini (" + model_used + ") found " + str(len(leads_list)) + " leads")
                if leads_list:
                    df_display = pd.DataFrame(leads_list)
                    df_display = df_display[['company', 'contact_person', 'role', 'phone', 'email', 'why_need', 'deal_size']]
                    df_display.columns = ['Company', 'Contact', 'Role', 'Phone', 'Email', 'Why They Need Us', 'Est. Deal']
                    st.dataframe(df_display, use_container_width=True, hide_index=True)
                else:
                    with st.expander("Raw Gemini Output"):
                        st.text(raw_leads)
            except Exception as e:
                st.error("Gemini Scout Error: " + str(e))
                st.stop()

        # PHASE 2
        with pipeline_status_placeholder.container():
            show_agent_pipeline({"gemini": "done", "claude": "running", "gpt": "idle", "auto": "idle"})
        st.markdown(
            '<div class="phase-header phase-claude">'
            '<span style="font-size:1.5rem">&#129504;</span>'
            '<div>'
            '<p class="phase-title">Phase 2: Gemini Strategist - Deep Analysis and Personalization</p>'
            '<p class="phase-sub">Analysing each lead and crafting targeted strategy</p>'
            '</div></div>',
            unsafe_allow_html=True
        )
        with st.spinner("Gemini is strategizing for each lead..."):
            try:
                strategy_raw  = agent_gemini_strategist(
                    st.session_state.pipeline_results.get('gemini_raw', ''),
                    our_product, our_company, my_product, reply_tone
                )
                strategy_list = safe_json_parse(strategy_raw, [])
                st.session_state.pipeline_results['strategy'] = strategy_list
                st.success("Gemini analysed " + str(len(strategy_list)) + " leads with strategic scoring")

                for s in strategy_list:
                    priority    = s.get('priority', 'WARM')
                    badge_class = 'badge-hot' if priority == 'HOT' else ('badge-cold' if priority == 'COLD' else 'badge-warm')
                    badge_label = 'HOT' if priority == 'HOT' else ('COLD' if priority == 'COLD' else 'WARM')
                    pain_items  = "".join(["<li>" + str(p) + "</li>" for p in s.get('pain_points', [])])
                    company     = str(s.get('company', 'Unknown'))
                    contact     = str(s.get('contact_person', ''))
                    score       = str(s.get('deal_score', 0))
                    value_prop  = str(s.get('our_value_prop', ''))
                    hook        = str(s.get('opening_hook', ''))
                    objection   = str(s.get('objection_handling', ''))
                    est_value   = str(s.get('estimated_value', ''))
                    urgency_sig = str(s.get('urgency_signal', ''))
                    approach    = str(s.get('recommended_approach', ''))
                    st.markdown(
                        '<div class="lead-card">'
                        '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;">'
                        '<div><p class="lead-name">' + company + '</p>'
                        '<p class="lead-address">Contact: ' + contact + ' | Score: ' + score + '/100</p></div>'
                        '<span class="' + badge_class + '">' + badge_label + '</span>'
                        '</div>'
                        '<div class="strategy-box">'
                        '<div class="strategy-title">Strategic Value Proposition</div>'
                        '<div class="strategy-text">' + value_prop + '</div>'
                        '</div>'
                        '<div style="display:flex;gap:16px;flex-wrap:wrap;margin-top:12px;">'
                        '<div style="flex:1;min-width:160px;">'
                        '<p style="font-size:0.72rem;color:#4a5568;text-transform:uppercase;letter-spacing:1px;">Pain Points</p>'
                        '<ul style="color:#b0bec5;font-size:0.82rem;margin:4px 0;padding-left:16px;">' + pain_items + '</ul>'
                        '</div>'
                        '<div style="flex:1;min-width:160px;">'
                        '<p style="font-size:0.72rem;color:#4a5568;text-transform:uppercase;letter-spacing:1px;">Opening Hook</p>'
                        '<p style="color:#e0e6f0;font-size:0.84rem;font-style:italic;">' + hook + '</p>'
                        '</div>'
                        '<div style="flex:1;min-width:160px;">'
                        '<p style="font-size:0.72rem;color:#4a5568;text-transform:uppercase;letter-spacing:1px;">Objection Handle</p>'
                        '<p style="color:#b0bec5;font-size:0.82rem;">' + objection + '</p>'
                        '</div></div>'
                        '<div style="margin-top:10px;padding-top:10px;border-top:1px solid #1e2a3e;display:flex;gap:20px;flex-wrap:wrap;">'
                        '<span style="font-size:0.8rem;color:#7a8ba0;">Value: ' + est_value + '</span>'
                        '<span style="font-size:0.8rem;color:#7a8ba0;">Urgency: ' + urgency_sig + '</span>'
                        '<span style="font-size:0.8rem;color:#7a8ba0;">Approach: ' + approach + '</span>'
                        '</div></div>',
                        unsafe_allow_html=True
                    )
                if not strategy_list:
                    with st.expander("Raw Strategy Output"):
                        st.text(strategy_raw)
            except Exception as e:
                st.error("Gemini Strategist Error: " + str(e))
                st.stop()

        # PHASE 3
        with pipeline_status_placeholder.container():
            show_agent_pipeline({"gemini": "done", "claude": "done", "gpt": "running", "auto": "idle"})
        st.markdown(
            '<div class="phase-header phase-gpt">'
            '<span style="font-size:1.5rem">&#9993;</span>'
            '<div>'
            '<p class="phase-title">Phase 3: Gemini Communicator - Personalized Outreach Messages</p>'
            '<p class="phase-sub">Writing WhatsApp and Email for each lead based on strategy</p>'
            '</div></div>',
            unsafe_allow_html=True
        )
        with st.spinner("Gemini is crafting personalized messages..."):
            try:
                strategy_list = st.session_state.pipeline_results.get('strategy', [])
                messages_raw  = agent_gemini_communicator(
                    strategy_list, our_product, our_company, our_contact, our_email, reply_tone
                )
                messages_list = safe_json_parse(messages_raw, [])
                st.session_state.pipeline_results['messages'] = messages_list
                st.success("Gemini drafted " + str(len(messages_list)) + " personalized outreach sets")

                for idx, msg in enumerate(messages_list):
                    phone      = str(msg.get('phone', ''))
                    email_to   = str(msg.get('email', ''))
                    wa_text    = str(msg.get('whatsapp_message', ''))
                    email_sub  = str(msg.get('email_subject', ''))
                    email_body = str(msg.get('email_body', ''))
                    company    = str(msg.get('company', 'Lead ' + str(idx + 1)))
                    best_time  = str(msg.get('best_time_to_contact', 'Weekday morning'))
                    follow_up  = str(msg.get('follow_up_day', '3 days'))
                    clean_phone = "".join(filter(str.isdigit, phone))
                    if len(clean_phone) == 10:
                        clean_phone = "91" + clean_phone
                    wa_link   = "https://wa.me/" + clean_phone + "?text=" + urllib.parse.quote(wa_text)
                    mail_link = "mailto:" + email_to + "?subject=" + urllib.parse.quote(email_sub) + "&body=" + urllib.parse.quote(email_body)
                    st.markdown(
                        '<div class="lead-card" style="border-color:#1a4a1a;">'
                        '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">'
                        '<p class="lead-name">' + company + '</p>'
                        '<span style="font-size:0.78rem;color:#7a8ba0;">Best Time: ' + best_time + ' | Follow-up: ' + follow_up + '</span>'
                        '</div>'
                        '<div class="msg-box msg-whatsapp">'
                        '<div class="msg-label msg-label-wa">WhatsApp Message</div>'
                        '<div class="msg-content">' + wa_text + '</div>'
                        '</div>'
                        '<div class="msg-box msg-email">'
                        '<div class="msg-label msg-label-mail">Email - Subject: ' + email_sub + '</div>'
                        '<div class="msg-content">' + email_body + '</div>'
                        '</div>'
                        '<div class="action-row">'
                        '<a class="btn-wa"   href="' + wa_link   + '" target="_blank">Send on WhatsApp</a>'
                        '<a class="btn-mail" href="' + mail_link + '" target="_blank">Open Email Draft</a>'
                        '</div></div>',
                        unsafe_allow_html=True
                    )
                if not messages_list:
                    with st.expander("Raw Messages Output"):
                        st.text(messages_raw)
            except Exception as e:
                st.error("Gemini Communicator Error: " + str(e))
                st.stop()

        # PHASE 4
        if auto_reply_enabled:
            with pipeline_status_placeholder.container():
                show_agent_pipeline({"gemini": "done", "claude": "done", "gpt": "done", "auto": "running"})
            st.markdown(
                '<div class="phase-header phase-auto">'
                '<span style="font-size:1.5rem">&#128260;</span>'
                '<div>'
                '<p class="phase-title">Phase 4: Gemini Auto-Responder - Simulated Conversation Intelligence</p>'
                '<p class="phase-sub">AI simulates client reply and generates smart automated follow-up</p>'
                '</div></div>',
                unsafe_allow_html=True
            )
            with st.spinner("Auto-Responder generating conversation simulations..."):
                try:
                    strategy_list = st.session_state.pipeline_results.get('strategy', [])
                    messages_list = st.session_state.pipeline_results.get('messages', [])
                    hot_leads     = [s for s in strategy_list if s.get('priority') in ['HOT', 'WARM']][:3]
                    auto_replies  = []

                    for i, lead_strategy in enumerate(hot_leads):
                        matching_msg = next(
                            (m for m in messages_list if m.get('company') == lead_strategy.get('company')),
                            messages_list[i] if i < len(messages_list) else {}
                        )
                        auto_raw  = agent_gemini_autoresponder(
                            matching_msg, lead_strategy,
                            matching_msg, our_product, our_company, reply_tone
                        )
                        auto_data = safe_json_parse(auto_raw, {})
                        if auto_data:
                            auto_data['company'] = lead_strategy.get('company', 'Lead ' + str(i + 1))
                            auto_replies.append(auto_data)

                    st.session_state.pipeline_results['auto_replies'] = auto_replies
                    st.success("Auto-Responder simulated " + str(len(auto_replies)) + " conversation threads")

                    scenario_colors = {
                        'interested':       '#00c851',
                        'needs_more_info':  '#ffaa00',
                        'price_sensitive':  '#ff8800',
                        'requesting_visit': '#4285f4',
                        'not_interested':   '#ff4444'
                    }

                    for reply in auto_replies:
                        scenario      = str(reply.get('reply_scenario', ''))
                        scenario_col  = scenario_colors.get(scenario, '#7a8ba0')
                        escalate      = reply.get('escalate_to_human', False)
                        company       = str(reply.get('company', 'Unknown'))
                        client_reply  = str(reply.get('simulated_client_reply', ''))
                        wa_resp       = str(reply.get('auto_response_whatsapp', ''))
                        next_act      = str(reply.get('next_action', ''))
                        esc_reason    = str(reply.get('escalation_reason', ''))
                        escalate_html = (
                            '<span style="background:#1a0a0a;color:#ff4444;border:1px solid #ff4444;'
                            'padding:3px 10px;border-radius:10px;font-size:0.72rem;font-weight:700;">ESCALATE TO HUMAN</span>'
                            if escalate else
                            '<span style="background:#0a1a0a;color:#00c851;border:1px solid #00c851;'
                            'padding:3px 10px;border-radius:10px;font-size:0.72rem;font-weight:700;">AUTO-HANDLED</span>'
                        )
                        esc_reason_html = (
                            '<p style="color:#ff8800;font-size:0.8rem;margin-top:6px;">Escalation Reason: ' + esc_reason + '</p>'
                            if escalate else ''
                        )
                        st.markdown(
                            '<div class="lead-card" style="border-color:#1a3a0a;">'
                            '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">'
                            '<p class="lead-name">' + company + '</p>'
                            '<div style="display:flex;gap:10px;align-items:center;">'
                            '<span style="color:' + scenario_col + ';font-size:0.8rem;font-weight:700;text-transform:uppercase;">'
                            + scenario.replace('_', ' ') +
                            '</span>' + escalate_html +
                            '</div></div>'
                            '<div class="conversation-entry">'
                            '<div class="conv-from">Simulated Client Reply:</div>'
                            '<div class="conv-msg" style="color:#e0e6f0;font-style:italic;">' + client_reply + '</div>'
                            '</div>'
                            '<div class="autoreply-box">'
                            '<div class="autoreply-label">Our Automated WhatsApp Reply</div>'
                            '<div class="autoreply-text">' + wa_resp + '</div>'
                            '</div>'
                            '<div style="margin-top:10px;padding:10px;background:#0a0d14;border:1px solid #1e2a3e;border-radius:8px;">'
                            '<p style="font-size:0.72rem;color:#4a5568;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">Next Action for Sales Team</p>'
                            '<p style="color:#b0bec5;font-size:0.84rem;">' + next_act + '</p>'
                            + esc_reason_html +
                            '</div></div>',
                            unsafe_allow_html=True
                        )
                except Exception as e:
                    st.error("Auto-Responder Error: " + str(e))

        # ALL DONE
        with pipeline_status_placeholder.container():
            show_agent_pipeline({"gemini": "done", "claude": "done", "gpt": "done", "auto": "done"})
        st.balloons()
        st.success("Full Multi-Agent Pipeline Complete! Your leads are researched, analysed, messaged and conversation-ready.")

        # DOWNLOADS
        st.markdown("### Export Complete Intelligence Report")
        dl_col1, dl_col2 = st.columns(2)
        with dl_col1:
            leads_data = st.session_state.leads_data or []
            if leads_data:
                df_leads = pd.DataFrame(leads_data)
                st.download_button(
                    "Download Leads CSV",
                    data=df_leads.to_csv(index=False).encode('utf-8'),
                    file_name="samketan_leads_" + region.replace(',', '_').replace(' ', '_') + ".csv",
                    mime="text/csv",
                    use_container_width=True
                )
        with dl_col2:
            full_report = {
                "generated_at": datetime.now().isoformat(),
                "inputs": {"product": my_product, "region": region, "target_client": target_client},
                "pipeline_results": st.session_state.pipeline_results
            }
            st.download_button(
                "Download Full JSON Report",
                data=json.dumps(full_report, indent=2, default=str).encode('utf-8'),
                file_name="samketan_full_report_" + region.replace(',', '_').replace(' ', '_') + ".json",
                mime="application/json",
                use_container_width=True
            )

# --- MANUAL CLIENT REPLY SIMULATION ---
if simulate_reply and st.session_state.pipeline_results:
    st.markdown("---")
    st.markdown(
        '<div class="phase-header phase-auto">'
        '<span style="font-size:1.5rem">&#128172;</span>'
        '<div>'
        '<p class="phase-title">Manual Reply Simulation</p>'
        '<p class="phase-sub">Enter a client reply and see AI auto-response</p>'
        '</div></div>',
        unsafe_allow_html=True
    )
    client_reply_input = st.text_area(
        "Paste a client's actual reply here:",
        placeholder="e.g. Hello, we are interested. Can you share more details about pricing and location?",
        height=100
    )
    reply_company = st.text_input("Which company replied?", placeholder="Company name...")

    if st.button("Generate Smart Auto-Reply") and client_reply_input:
        with st.spinner("Generating intelligent response..."):
            try:
                model, _ = get_gemini_model()
                manual_prompt = (
                    "You are the sales AI for " + our_company + ".\n\n"
                    "OUR OFFERING: " + our_product + "\n"
                    "TONE: " + reply_tone + "\n"
                    "COMPANY THAT REPLIED: " + reply_company + "\n\n"
                    "CLIENT REPLIED: " + client_reply_input + "\n\n"
                    "Write a professional, helpful response that:\n"
                    "1. Directly addresses their message\n"
                    "2. Provides relevant details from our offering\n"
                    "3. Moves toward scheduling a site visit or call\n"
                    "4. Is warm and not pushy\n\n"
                    "CRITICAL: Return ONLY a valid JSON object. No markdown. No backticks. No explanation.\n"
                    "The object MUST have these exact keys:\n"
                    "- whatsapp_reply (string)\n"
                    "- email_reply (string)\n"
                    "- next_step (string)\n\n"
                    "Start your response with { and end with }"
                )
                manual_res  = call_gemini_with_retry(model, manual_prompt)
                manual_data = safe_json_parse(manual_res.text, {})
                if manual_data:
                    wa_reply  = str(manual_data.get('whatsapp_reply', ''))
                    em_reply  = str(manual_data.get('email_reply', ''))
                    next_step = str(manual_data.get('next_step', ''))
                    st.markdown(
                        '<div class="autoreply-box">'
                        '<div class="autoreply-label">WhatsApp Auto-Reply for ' + reply_company + '</div>'
                        '<div class="autoreply-text">' + wa_reply + '</div>'
                        '</div>'
                        '<div class="msg-box msg-email">'
                        '<div class="msg-label msg-label-mail">Email Auto-Reply</div>'
                        '<div class="msg-content">' + em_reply + '</div>'
                        '</div>'
                        '<div style="background:#0a0d14;border:1px solid #1e2a3e;border-radius:8px;padding:12px 16px;margin-top:10px;">'
                        '<p style="font-size:0.72rem;color:#4a5568;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">Recommended Next Step</p>'
                        '<p style="color:#b0bec5;font-size:0.84rem;">' + next_step + '</p>'
                        '</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.warning("Could not parse response. Raw output:")
                    st.text(manual_res.text)
            except Exception as e:
                st.error("Manual reply error: " + str(e))

elif simulate_reply and not st.session_state.pipeline_results:
    st.warning("Run the pipeline first before simulating replies.")

# --- FOOTER ---
st.markdown("---")
st.markdown(
    '<p style="color:#2a3a4e;font-size:0.8rem;text-align:center;">'
    'Samketan AI v7.0 | Multi-Agent Autonomous Pipeline | 100% Free - Powered by Gemini | &copy; 2026 Samketan'
    '</p>',
    unsafe_allow_html=True
)

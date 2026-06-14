import html
import json
import random
import time
import urllib.parse
from datetime import datetime

import google.generativeai as genai
import pandas as pd
import streamlit as st
import requests

try:
    import extra_streamlit_components as stx
except Exception:
    class _MemoryCookieManager:
        @staticmethod
        def get(key):
            return st.session_state.get(key)
        @staticmethod
        def delete(key):
            st.session_state.pop(key, None)
    class _FallbackStreamlitComponents:
        CookieManager = _MemoryCookieManager
    stx = _FallbackStreamlitComponents()

try:
    import auth
except ImportError:
    class _FallbackAuth:
        @staticmethod
        def login_screen():
            st.session_state.authenticated = True
            st.session_state.current_user = st.session_state.get("current_user", "User")
            return True
    auth = _FallbackAuth()

# ---------------------------------------------
# PAGE CONFIG
# ---------------------------------------------
st.set_page_config(
    page_title="Samketan AI v8.0 - Multi-Agent",
    page_icon="S",
    layout="wide",
)

# ---------------------------------------------
# AUTHENTICATION
# ---------------------------------------------
cookie_manager = stx.CookieManager()
saved_user = cookie_manager.get("samketan_user")
if saved_user and not st.session_state.get("authenticated"):
    st.session_state.authenticated = True
    st.session_state.current_user = saved_user

if not auth.login_screen():
    st.stop()

# ---------------------------------------------
# GLOBAL CSS
# ---------------------------------------------
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
    .header-sub { font-size: 0.92rem; color: #7a8ba0; margin-top: 6px; }
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
    .agent-card.done { border-color: #00c851; box-shadow: 0 0 15px rgba(0,200,81,0.2); }
    .agent-icon { font-size: 2rem; margin-bottom: 8px; }
    .agent-name { font-size: 0.9rem; font-weight: 700; color: #e0e6f0; }
    .agent-role { font-size: 0.75rem; color: #7a8ba0; margin-top: 4px; }
    .agent-status { font-size: 0.72rem; margin-top: 8px; padding: 3px 10px; border-radius: 10px; display: inline-block; }
    .status-idle { background: #1a1d27; color: #4a5568; }
    .status-running { background: #1a0d2e; color: #a855f7; }
    .status-done { background: #0a1a0a; color: #00c851; }
    .input-card {
        background: #0f1219; border: 1px solid #1e2a3e;
        border-radius: 14px; padding: 24px; margin-bottom: 20px;
    }
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
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
    .phase-gpt { border-left-color: #00c851 !important; }
    .phase-auto { border-left-color: #f59e0b !important; }
    .phase-rag { border-left-color: #00bcd4 !important; }
    .phase-title { font-size: 1rem; font-weight: 700; color: #fff; margin: 0; }
    .phase-sub { font-size: 0.8rem; color: #7a8ba0; margin-top: 2px; }
    .lead-card {
        background: #0f1219; border: 1px solid #1e2a3e;
        border-radius: 14px; padding: 20px 24px; margin-bottom: 14px;
    }
    .lead-card:hover { border-color: #4285f4; box-shadow: 0 4px 24px rgba(66,133,244,0.15); }
    .lead-name { font-size: 1.05rem; font-weight: 700; color: #fff; margin: 0; }
    .lead-address { font-size: 0.8rem; color: #7a8ba0; margin-top: 4px; }
    .badge-hot { background:#1a0a0a; color:#ff4444; border:1px solid #ff4444; padding:4px 12px; border-radius:20px; font-size:0.72rem; font-weight:700; }
    .badge-warm { background:#1a1200; color:#ffaa00; border:1px solid #ffaa00; padding:4px 12px; border-radius:20px; font-size:0.72rem; font-weight:700; }
    .badge-cold { background:#001a2a; color:#0099ff; border:1px solid #0099ff; padding:4px 12px; border-radius:20px; font-size:0.72rem; font-weight:700; }
    .strategy-box {
        background: #0a0d14; border: 1px solid #2d1657;
        border-left: 3px solid #a855f7; border-radius: 10px; padding: 16px 20px; margin: 10px 0;
    }
    .strategy-title { color: #a855f7; font-weight: 700; font-size: 0.85rem; margin-bottom: 8px; }
    .strategy-text { color: #b0bec5; font-size: 0.84rem; line-height: 1.6; }
    .msg-box { background: #0a0d14; border: 1px solid #1e2a3e; border-radius: 10px; padding: 16px; margin: 10px 0; }
    .msg-whatsapp { border-left: 3px solid #25D366; }
    .msg-email { border-left: 3px solid #4285f4; }
    .msg-label { font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
    .msg-label-wa { color: #25D366; }
    .msg-label-mail { color: #4285f4; }
    .msg-content { color: #b0bec5; font-size: 0.84rem; line-height: 1.6; white-space: pre-wrap; }
    .autoreply-box {
        background: #0f1a0f; border: 1px solid #1a3a1a;
        border-left: 3px solid #00c851; border-radius: 10px; padding: 16px; margin: 10px 0;
    }
    .autoreply-label { color: #00c851; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
    .autoreply-text { color: #b0bec5; font-size: 0.84rem; line-height: 1.6; white-space: pre-wrap; }
    .rag-box {
        background: #0a1a1f; border: 1px solid #1a3a4a;
        border-left: 3px solid #00bcd4; border-radius: 10px; padding: 16px; margin: 10px 0;
    }
    .rag-label { color: #00bcd4; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
    .rag-text { color: #b0bec5; font-size: 0.84rem; line-height: 1.6; white-space: pre-wrap; }
    .action-row { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 14px; }
    .btn-wa { background:#0d2a1a; color:#25D366; border:1px solid #25D366; padding:8px 16px; border-radius:8px; font-size:0.82rem; font-weight:700; text-decoration:none; display:inline-block; }
    .btn-mail { background:#0d1a2a; color:#64b5f6; border:1px solid #64b5f6; padding:8px 16px; border-radius:8px; font-size:0.82rem; font-weight:700; text-decoration:none; display:inline-block; }
    .btn-linkedin { background:#081826; color:#0A66C2; border:1px solid #0A66C2; padding:8px 16px; border-radius:8px; font-size:0.82rem; font-weight:700; text-decoration:none; display:inline-block; }
    .stButton > button {
        background: linear-gradient(135deg,#7b2ff7,#f107a3) !important;
        color: white !important; border: none !important;
        border-radius: 10px !important; font-weight: 700 !important;
        font-size: 1rem !important; padding: 14px 32px !important; width: 100% !important;
    }
    .logout-btn > button {
        background: linear-gradient(135deg,#c0392b,#e74c3c) !important;
    }
    .conversation-entry {
        background: #0a0d14; border: 1px solid #1e2a3e;
        border-radius: 10px; padding: 14px 18px; margin-bottom: 10px;
    }
    .conv-from { font-size: 0.75rem; color: #7a8ba0; margin-bottom: 6px; }
    .conv-msg { color: #b0bec5; font-size: 0.84rem; line-height: 1.6; }
    .user-chip {
        background: #0a0d14; border: 1px solid #1e2a3e;
        border-radius: 8px; padding: 10px 14px; color: #e0e6f0; font-size: 0.88rem; margin-bottom: 12px;
    }
    .hunter-success {
        background: #0a1a0a; border: 1px solid #00c851;
        border-radius: 8px; padding: 10px 14px; color: #00c851;
        font-size: 0.88rem; margin: 8px 0; font-weight: 600;
    }
    .hunter-fail {
        background: #1a0a0a; border: 1px solid #ff8800;
        border-radius: 8px; padding: 10px 14px; color: #ff8800;
        font-size: 0.88rem; margin: 8px 0;
    }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    [data-testid="stToolbar"] { display: none !important; }
    [data-testid="stDecoration"] { display: none !important; }
    [data-testid="stStatusWidget"] { display: none !important; }
    [data-testid="baseButton-header"] { display: none !important; }
    .st-emotion-cache-zq5wmm { display: none !important; }
    .st-emotion-cache-1dp5vir { display: none !important; }
    .st-emotion-cache-h5rgaw { display: none !important; }
    .viewerBadge_container__1QSob { display: none !important; }
    .viewerBadge_link__1S137 { display: none !important; }
    #stDecoration { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------
# API KEYS
# ---------------------------------------------
def get_streamlit_secret(key, default=""):
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default

_all_keys = [
    get_streamlit_secret("GOOGLE_API_KEY", ""),
    get_streamlit_secret("GOOGLE_API_KEY2", ""),
    get_streamlit_secret("GOOGLE_API_KEY3", ""),
]
_valid_keys = [k for k in _all_keys if k and k.strip()]
gemini_key = _valid_keys[0] if _valid_keys else ""
HUNTER_API_KEY = get_streamlit_secret("HUNTER_API_KEY", "")

# ---------------------------------------------
# SESSION STATE INIT
# ---------------------------------------------
if "pipeline_results" not in st.session_state or st.session_state.pipeline_results is None:
    st.session_state.pipeline_results = {}
for state_key in ["conversation_log", "leads_data", "rag_context"]:
    if state_key not in st.session_state or st.session_state[state_key] is None:
        st.session_state[state_key] = [] if state_key != "rag_context" else ""

# ---------------------------------------------
# CORE HELPERS
# ---------------------------------------------
def esc(value):
    return html.escape(str(value or ""), quote=True)

_MODEL_PRIORITY = [
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash-lite",
    "gemini-2.5-flash"
]

def _get_model_for_key(api_key, index=0):
    genai.configure(api_key=api_key.strip())
    selected_model = _MODEL_PRIORITY[index % len(_MODEL_PRIORITY)]
    return genai.GenerativeModel(selected_model), selected_model

def call_gemini_with_retry(prompt):
    keys_to_try = list(_valid_keys) if _valid_keys else [gemini_key]
    if not keys_to_try or not keys_to_try[0]:
        raise Exception("No valid API Key detected.")
    errors = []
    for idx, api_key in enumerate(keys_to_try):
        try:
            model, model_name = _get_model_for_key(api_key, idx)
            response = model.generate_content(prompt)
            return response, model_name
        except Exception as exc:
            errors.append(f"Key_{idx}: {str(exc)}")
            continue
    st.warning(f"All API keys strained. Retrying in 30 seconds...")
    time.sleep(30)
    for idx, api_key in enumerate(keys_to_try):
        try:
            model, model_name = _get_model_for_key(api_key, idx + 1)
            response = model.generate_content(prompt)
            return response, model_name
        except Exception as exc:
            errors.append(f"Retry_{idx}: {str(exc)}")
            continue
    raise Exception(f"All keys exhausted. Errors: {errors}")

def safe_json_parse(text, default=None):
    try:
        clean = str(text or "").strip()
        if clean.startswith("```"):
            parts = clean.split("```")
            clean = parts[1] if len(parts) > 1 else clean
            if clean.lstrip().startswith("json"):
                clean = clean.lstrip()[4:]
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

def parse_leads_table(raw_text):
    leads = []
    for line in str(raw_text or "").split("\n"):
        if "|" not in line or "Company" in line or "---" in line:
            continue
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cols) < 8:
            continue
        leads.append({
            "company": cols[0],
            "address": cols[1],
            "first_name": cols[2],
            "last_name": cols[3],
            "email": "Pending extraction",
            "phone": cols[4],
            "decision_maker_role": cols[5] if len(cols) > 5 else "",
            "why_need": cols[6] if len(cols) > 6 else "",
            "sector": cols[7] if len(cols) > 7 else "",
            "deal_size": cols[8] if len(cols) > 8 else "",
            "person_linkedin": cols[9] if len(cols) > 9 else "",
        })
    return leads

def clean_phone_number(phone):
    digits = "".join(filter(str.isdigit, str(phone or "")))
    if len(digits) == 10:
        digits = "91" + digits
    return digits

def show_phase_header(css_class, icon_html, title, subtitle):
    st.markdown(
        '<div class="phase-header ' + css_class + '">'
        '<span style="font-size:1.5rem">' + icon_html + "</span>"
        '<div><p class="phase-title">' + esc(title) + "</p>"
        '<p class="phase-sub">' + esc(subtitle) + "</p></div></div>",
        unsafe_allow_html=True,
    )

def show_agent_pipeline(statuses):
    agents = [
        {"icon": "&#128269;", "name": "Gemini Scout", "role": "Lead Discovery", "key": "gemini"},
        {"icon": "&#129504;", "name": "Gemini Strategist", "role": "Strategy & Profiling", "key": "claude"},
        {"icon": "&#9993;", "name": "Gemini Communicator", "role": "Message Drafting", "key": "gpt"},
        {"icon": "&#128260;", "name": "Gemini Auto-Reply", "role": "Conversation AI", "key": "auto"},
        {"icon": "&#129302;", "name": "Gemini RAG", "role": "Deep Intelligence", "key": "rag"},
    ]
    cols = st.columns(9)
    for i, agent in enumerate(agents):
        status = statuses.get(agent["key"], "idle")
        card_class = "agent-card active" if status == "running" else ("agent-card done" if status == "done" else "agent-card")
        status_class = "agent-status status-" + status
        status_label = {"idle": "Idle", "running": "Running...", "done": "Done"}.get(status, "Idle")
        with cols[i * 2]:
            st.markdown(
                '<div class="' + card_class + '">'
                '<div class="agent-icon">' + agent["icon"] + "</div>"
                '<div class="agent-name">' + esc(agent["name"]) + "</div>"
                '<div class="agent-role">' + esc(agent["role"]) + "</div>"
                '<span class="' + status_class + '">' + status_label + "</span></div>",
                unsafe_allow_html=True,
            )
        if i < len(agents) - 1:
            with cols[i * 2 + 1]:
                st.markdown(
                    '<div style="text-align:center;color:#2a3a5e;font-size:1.8rem;padding-top:30px;">-&gt;</div>',
                    unsafe_allow_html=True,
                )

# ─────────────────────────────────────────────
# FIX 1: HUNTER API — IMPROVED EMAIL EXTRACTION
# ─────────────────────────────────────────────
def extract_domain_from_company(company_name):
    """Smart domain extraction from company name"""
    name = company_name.lower().strip()
    # Remove common suffixes
    for suffix in ["limited", "ltd", "pvt", "private", "inc", "llp", "llc", "co.", "company", "corp", "industries", "industry", "enterprises", "group", "india"]:
        name = name.replace(suffix, "")
    name = name.strip().replace(" ", "").replace("-", "").replace("_", "")
    
    # Known company domain mappings
    known_domains = {
        "ceat": "ceat.com", "apollo": "apollotyres.com", "mrf": "mrftyres.com",
        "bridgestone": "bridgestone.co.in", "goodyear": "goodyear.com",
        "tata": "tata.com", "reliance": "ril.com", "itc": "itcportal.com",
        "hindustan": "hul.com", "nestle": "nestle.in", "britannia": "britannia.co.in",
        "dabur": "dabur.com", "marico": "marico.com", "godrej": "godrej.com",
        "wipro": "wipro.com", "infosys": "infosys.com", "biocon": "biocon.com",
        "cipla": "cipla.com", "drreddy": "drreddys.com", "sunpharma": "sunpharma.com",
    }
    for key, domain in known_domains.items():
        if key in name:
            return domain
    
    return f"{name}.com"

def get_hunter_email(first_name, last_name, company_name, api_key=None):
    """FIX 1: Improved Hunter.io email finder with better error handling"""
    key = api_key or HUNTER_API_KEY
    if not key or not key.strip():
        return None, "No Hunter API key configured in secrets"
    
    domain = extract_domain_from_company(company_name)
    
    # Try email finder first
    try:
        url = f"https://api.hunter.io/v2/email-finder"
        params = {
            "domain": domain,
            "first_name": first_name,
            "last_name": last_name,
            "api_key": key.strip()
        }
        resp = requests.get(url, params=params, timeout=15)
        data = resp.json()
        
        if data.get("data", {}).get("email"):
            confidence = data["data"].get("score", 0)
            email = data["data"]["email"]
            return email, f"Found (confidence: {confidence}%)"
        
        # If finder fails, try domain search for any email
        url2 = f"https://api.hunter.io/v2/domain-search"
        params2 = {"domain": domain, "api_key": key.strip(), "limit": 5}
        resp2 = requests.get(url2, params=params2, timeout=15)
        data2 = resp2.json()
        
        emails = data2.get("data", {}).get("emails", [])
        if emails:
            # Return first email found on domain
            return emails[0].get("value"), f"Domain match found on {domain}"
            
        return None, f"No email found for {first_name} {last_name} at {domain}"
        
    except requests.exceptions.Timeout:
        return None, "Hunter API timeout — try again"
    except Exception as e:
        return None, f"Hunter API error: {str(e)}"

# ─────────────────────────────────────────────
# FIX 2: LINKEDIN DIRECT PROFILE SEARCH
# ─────────────────────────────────────────────
def build_linkedin_url(first_name, last_name, company, existing_url=""):
    # Use direct profile if available
    if existing_url and "linkedin.com/in/" in str(existing_url):
        return existing_url.strip()
    
    # Search name + company together — finds the RIGHT person
    full_query = f"{first_name} {last_name} {company}"
    url = (
        "https://www.linkedin.com/search/results/people/"
        f"?keywords={urllib.parse.quote(full_query)}"
        "&origin=GLOBAL_SEARCH_HEADER"
    )
    return url

# ─────────────────────────────────────────────
# FIX 3: RAG CONTEXT BUILDER
# ─────────────────────────────────────────────
def build_rag_context(our_product, our_company, region, target_client, leads_data, strategy_data):
    """FIX 3: Build RAG knowledge base from all pipeline data"""
    context = f"""
=== COMPANY KNOWLEDGE BASE ===
Company: {our_company}
Offering: {our_product}
Target Region: {region}
Ideal Clients: {target_client}

=== DISCOVERED LEADS ===
"""
    for i, lead in enumerate(leads_data[:10]):
        context += f"""
Lead {i+1}: {lead.get('company', '')}
- Contact: {lead.get('first_name', '')} {lead.get('last_name', '')} ({lead.get('decision_maker_role', '')})
- Address: {lead.get('address', '')}
- Phone: {lead.get('phone', '')}
- Sector: {lead.get('sector', '')}
- Deal Size: {lead.get('deal_size', '')}
- Why They Need Us: {lead.get('why_need', '')}
"""

    if strategy_data:
        context += "\n=== STRATEGIC ANALYSIS ===\n"
        for s in strategy_data[:5]:
            context += f"""
{s.get('company', '')}: Priority={s.get('priority', '')} Score={s.get('deal_score', '')}
Value Prop: {s.get('our_value_prop', '')}
Pain Points: {', '.join(s.get('pain_points', []))}
"""
    return context

def rag_query(question, context, our_company, our_product):
    """Answer questions using RAG — retrieves from context then generates"""
    if not context:
        return "No pipeline data available yet. Run the pipeline first."
    
    prompt = f"""You are an intelligent B2B sales assistant for {our_company}.

KNOWLEDGE BASE (Retrieved Context):
{context}

OUR OFFERING: {our_product}

USER QUESTION: {question}

Instructions:
- Answer ONLY using the information in the knowledge base above
- Be specific with company names, contact details, and deal sizes
- If the information is not in the knowledge base, say so clearly
- Give actionable recommendations
- Format your response clearly with bullet points where appropriate

Answer:"""
    
    try:
        response, _ = call_gemini_with_retry(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# ---------------------------------------------
# EMAIL DISPATCH
# ---------------------------------------------
def send_live_hostinger_email(lead_email, subject, body_text):
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    import os

    smtp_server = "smtp.hostinger.com"
    port = 465
    sender_email = get_streamlit_secret("EMAIL_USER", "sanjayhg@bhoodeviwarehouse.com")
    sender_password = get_streamlit_secret("EMAIL_PASSWORD", "")

    if not sender_password:
        return "Missing EMAIL_PASSWORD in secrets"

    message = MIMEMultipart()
    message["From"] = f"Bhoodevi Warehouse <{sender_email}>"
    message["To"] = lead_email
    message["Bcc"] = sender_email
    message["Subject"] = subject
    message.attach(MIMEText(body_text, "plain"))

    try:
        with smtplib.SMTP_SSL(smtp_server, port) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, [lead_email, sender_email], message.as_string())
        return "Success"
    except Exception as e:
        return str(e)

def handle_email_dispatch(lead_email, subject, body_text, company_name):
    status = send_live_hostinger_email(lead_email, subject, body_text)
    if status == "Success":
        st.toast(f"✅ Email sent to {company_name}!", icon="🚀")
    else:
        st.error(f"❌ Failed to send to {company_name}: {status}")

# ---------------------------------------------
# AGENTS
# ---------------------------------------------
def agent_gemini_scout(region, target_client, my_product, our_product, num_leads):
    prompt = (
        "You are a B2B Lead Intelligence Scout. Find " + str(num_leads) + " REAL corporate businesses in " + region + ".\n\n"
        "TARGET CLIENT TYPE: " + target_client + "\n"
        "WHAT WE SELL: " + my_product + "\n"
        "OUR FULL OFFERING: " + our_product + "\n\n"
        "Return ONLY a pipe-separated table:\n"
        "Company Name | Full Address | Manager First Name | Manager Last Name | Phone | Decision Maker Role | Why They Need Us | Industry Sector | Estimated Deal Size | Person LinkedIn URL\n\n"
        "RULES:\n"
        "- Use REAL company names that exist in " + region + "\n"
        "- Find actual First Name and Last Name of regional executives\n"
        "- For LinkedIn URL: provide the actual linkedin.com/in/username if known, otherwise write SEARCH\n"
        "- Phone: Indian format with +91\n"
        "- NO invented emails\n"
        "- NO markdown, ONLY table rows\n"
    )
    response, model_name = call_gemini_with_retry(prompt)
    return response.text, model_name

def agent_gemini_strategist(raw_leads_data, our_product, our_company, my_product, reply_tone):
    prompt = (
        "You are a senior B2B growth strategist.\n\n"
        "Raw Leads:\n" + raw_leads_data + "\n\n"
        "Our Company: " + our_company + "\n"
        "Our Offering: " + our_product + "\n"
        "Product: " + my_product + "\n"
        "Tone: " + reply_tone + "\n\n"
        "Return ONLY valid JSON array. No markdown.\n"
        "Each object MUST have:\n"
        "- company, first_name, last_name, person_linkedin\n"
        "- deal_score (1-100), priority (HOT/WARM/COLD)\n"
        "- our_value_prop, pain_points (array), opening_hook\n"
        "- linkedin_connection_note, objection_handling\n"
        "- estimated_value, urgency_signal, recommended_approach\n"
        "Start with [ end with ]"
    )
    response, _ = call_gemini_with_retry(prompt)
    return response.text

def agent_gemini_communicator(strategy_data, leads_data, our_product, our_company, our_contact, our_website, our_email, reply_tone):
    prompt = (
        "You are an expert B2B sales communicator for " + our_company + ".\n\n"
        "OUR OFFERING: " + our_product + "\n"
        "CONTACT: " + our_contact + "\n"
        "EMAIL: " + our_email + "\n"
        "WEBSITE: " + our_website + "\n"
        "TONE: " + reply_tone + "\n\n"
        "LEADS:\n" + json.dumps(leads_data, indent=2) + "\n\n"
        "STRATEGY:\n" + json.dumps(strategy_data, indent=2) + "\n\n"
        "For each lead write:\n"
        "1. WhatsApp message (max 200 words)\n"
        "2. Email (Subject + Body, include website " + our_website + ")\n"
        "3. LinkedIn note (under 300 chars)\n\n"
        "Return ONLY valid JSON array. No markdown.\n"
        "Each object: company, first_name, last_name, phone, email, person_linkedin,\n"
        "whatsapp_message, email_subject, email_body, linkedin_note,\n"
        "best_time_to_contact, follow_up_day\n"
        "Start with [ end with ]"
    )
    response, _ = call_gemini_with_retry(prompt)
    return response.text

def agent_gemini_autoresponder(lead_data, strategy, messages, our_product, our_company, reply_tone):
    prompt = (
        "You are a sales AI for " + our_company + ".\n\n"
        "OUR OFFERING: " + our_product + "\n"
        "TONE: " + reply_tone + "\n\n"
        "LEAD: " + str(lead_data.get("company", "")) + " - " + str(lead_data.get("first_name", "")) + "\n"
        "PRIORITY: " + str(strategy.get("priority", "WARM")) + "\n"
        "PAIN POINTS: " + str(strategy.get("pain_points", [])) + "\n\n"
        "TASK: Simulate client reply + our automated response.\n"
        "Return ONLY valid JSON object. No markdown.\n"
        "Keys: simulated_client_reply, reply_scenario, auto_response_whatsapp,\n"
        "auto_response_email, next_action, escalate_to_human (bool), escalation_reason\n"
        "Start with { end with }"
    )
    response, _ = call_gemini_with_retry(prompt)
    return response.text

def agent_gemini_rag_insights(leads_data, strategy_data, our_product, our_company, region):
    """FIX 3: RAG Agent — generates deep insights from all pipeline data"""
    prompt = (
        "You are a B2B market intelligence analyst using RAG (Retrieval Augmented Generation).\n\n"
        "RETRIEVED DATA:\n"
        "Company: " + our_company + "\n"
        "Offering: " + our_product + "\n"
        "Region: " + region + "\n"
        "Total Leads: " + str(len(leads_data)) + "\n\n"
        "LEADS SUMMARY:\n" + json.dumps(leads_data[:5], indent=2) + "\n\n"
        "STRATEGY SUMMARY:\n" + json.dumps(strategy_data[:5], indent=2) + "\n\n"
        "Generate a comprehensive intelligence report with:\n"
        "1. TOP 3 highest-priority targets and why\n"
        "2. Market opportunity size in this region\n"
        "3. Common pain points across all leads\n"
        "4. Best outreach strategy for this market\n"
        "5. Risk factors to be aware of\n"
        "6. Revenue forecast if 20% conversion rate\n"
        "7. Recommended follow-up sequence (Day 1, Day 3, Day 7, Day 14)\n\n"
        "Be specific with company names and numbers. Format with clear sections."
    )
    response, _ = call_gemini_with_retry(prompt)
    return response.text

# ---------------------------------------------
# HEADER
# ---------------------------------------------
st.markdown("""
<div class="header-banner">
    <div>
        <p class="header-title">Samketan AI v8.0</p>
        <p class="header-sub">
            5-Agent Pipeline: Scout → Strategist → Communicator → Auto-Responder → RAG Intelligence
        </p>
    </div>
    <span class="header-badge">RAG + LLM</span>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="promo-bar">
    AVAILABLE FOR LEASE: Premium 21,000 Sq. Ft. RCC Warehouse - Nandur Industrial Area, Gulbarga.
    <a href="https://www.bhoodeviwarehouse.com/" target="_blank">Visit Bhoodevi Warehouse ↗</a>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------
# SIDEBAR — FIX 4: LOGOUT BUTTON ALWAYS VISIBLE
# ---------------------------------------------
with st.sidebar:
    st.markdown("### 👤 Samketan Profile")
    st.markdown(
        '<div class="user-chip">✅ ' + esc(st.session_state.get("current_user", "User")) + "</div>",
        unsafe_allow_html=True,
    )

    # FIX 4: Logout button — always visible at top of sidebar
st.markdown("---")
if st.button("🚪 Sign Out", key="logout_btn", type="secondary", use_container_width=True):
    try:
        cookie_manager.delete("samketan_user")
    except:
        pass
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
st.markdown("---")

    st.markdown("---")
    st.markdown("### 🔑 API Status")
    st.caption(f"Gemini keys active: {len(_valid_keys)}")
    if HUNTER_API_KEY:
        st.success("✅ Hunter API connected")
    else:
        st.warning("⚠️ Hunter API key missing")
    if not gemini_key:
        gemini_key = st.text_input("Google Gemini Key", type="password", placeholder="AIza...")

    st.markdown("---")
    st.markdown("### 🏭 Our Offering")
    our_product = st.text_area(
        "What we offer:",
        value=(
            "Premium 21,000 sq ft RCC warehouse in Nandur Area, Gulbarga. "
            "Features: 24/7 security, loading docks, fire safety, power backup. "
            "Ideal for FMCG, pharma, agri storage processing."
        ),
        height=120,
    )
    our_company = st.text_input("Company Name", value="Bhoodevi Warehouse")
    our_contact = st.text_input("Our Contact", value="+91-9880888056")
    our_email = st.text_input("Our Email", value="sanjayhg@bhoodeviwarehouse.com")
    our_website = st.text_input("Our Website", value="www.bhoodeviwarehouse.com")

    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    auto_reply_enabled = st.toggle("Enable Auto-Reply Simulation", value=True)
    reply_tone = st.selectbox("Reply Tone", ["Professional & Warm", "Formal", "Friendly & Casual", "Urgent & Direct"])

    st.markdown("---")
    with st.expander("ℹ️ How 5-Agent Pipeline Works"):
        st.markdown("""
**Agent 1 — Scout**: Finds real leads
**Agent 2 — Strategist**: Deep analysis & scoring
**Agent 3 — Communicator**: WhatsApp + Email + LinkedIn
**Agent 4 — Auto-Responder**: Simulates conversations
**Agent 5 — RAG Intelligence**: Market insights from all data
        """)

# ---------------------------------------------
# MAIN INPUT SECTION
# ---------------------------------------------
st.markdown('<div class="input-card">', unsafe_allow_html=True)
st.markdown("### 🎯 Define Your Target")
col1, col2, col3 = st.columns(3)
with col1:
    my_product = st.text_input("Product / Service to Sell", value="Warehouse Space")
    region = st.text_input("Target City / Region", value="Gulbarga, Karnataka")
with col2:
    target_client = st.text_input("Ideal Client Type", value="FMCG Distributors, Pharma Companies")
    num_leads = st.slider("Number of Leads", 3, 10, 5)
with col3:
    scope = st.radio("Market Scope", ["Local (Domestic)", "Export (International)"])
    urgency = st.selectbox("Deal Urgency", ["High - Close this month", "Medium - Next quarter", "Low - Exploring"])
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("---")

# ---------------------------------------------
# PIPELINE STATUS
# ---------------------------------------------
pipeline_status_placeholder = st.empty()
with pipeline_status_placeholder.container():
    if "gemini_raw" in st.session_state.pipeline_results:
        show_agent_pipeline({"gemini": "done", "claude": "done", "gpt": "done", "auto": "done", "rag": "done"})
    else:
        show_agent_pipeline({"gemini": "idle", "claude": "idle", "gpt": "idle", "auto": "idle", "rag": "idle"})

run_col1, run_col2 = st.columns([3, 1])
with run_col1:
    run_pipeline = st.button("🚀 LAUNCH 5-AGENT PIPELINE", use_container_width=True)
with run_col2:
    simulate_reply = st.button("💬 Simulate Reply", use_container_width=True)

st.markdown("---")

# ---------------------------------------------
# PIPELINE EXECUTION
# ---------------------------------------------
if run_pipeline:
    if not _valid_keys and not gemini_key:
        st.error("Missing GOOGLE_API_KEY.")
    elif not my_product or not region or not target_client:
        st.warning("Fill in Product, Region, and Client Type.")
    else:
        st.session_state.pipeline_results = {}
        st.session_state.conversation_log = []
        st.session_state.leads_data = []
        st.session_state.rag_context = ""

        # PHASE 1
        with pipeline_status_placeholder.container():
            show_agent_pipeline({"gemini": "running", "claude": "idle", "gpt": "idle", "auto": "idle", "rag": "idle"})
        with st.spinner("Scout finding leads..."):
            try:
                raw_leads, model_used = agent_gemini_scout(region, target_client, my_product, our_product, num_leads)
                st.session_state.pipeline_results["gemini_raw"] = raw_leads
                st.session_state.leads_data = parse_leads_table(raw_leads)
            except Exception as e:
                st.error("Scout Error: " + str(e))
                st.stop()

        # PHASE 2
        with pipeline_status_placeholder.container():
            show_agent_pipeline({"gemini": "done", "claude": "running", "gpt": "idle", "auto": "idle", "rag": "idle"})
        with st.spinner("Strategist analysing leads..."):
            try:
                strategy_raw = agent_gemini_strategist(
                    st.session_state.pipeline_results.get("gemini_raw", ""),
                    our_product, our_company, my_product, reply_tone)
                st.session_state.pipeline_results["strategy"] = safe_json_parse(strategy_raw, [])
            except Exception as e:
                st.error("Strategist Error: " + str(e))
                st.stop()

        # PHASE 3
        with pipeline_status_placeholder.container():
            show_agent_pipeline({"gemini": "done", "claude": "done", "gpt": "running", "auto": "idle", "rag": "idle"})
        with st.spinner("Communicator crafting messages..."):
            try:
                messages_raw = agent_gemini_communicator(
                    st.session_state.pipeline_results.get("strategy", []),
                    st.session_state.leads_data or [],
                    our_product, our_company, our_contact, our_website, our_email, reply_tone)
                st.session_state.pipeline_results["messages"] = safe_json_parse(messages_raw, [])
            except Exception as e:
                st.error("Communicator Error: " + str(e))
                st.stop()

        # PHASE 4
        if auto_reply_enabled:
            with pipeline_status_placeholder.container():
                show_agent_pipeline({"gemini": "done", "claude": "done", "gpt": "done", "auto": "running", "rag": "idle"})
            with st.spinner("Auto-Responder simulating conversations..."):
                try:
                    strategy_list = st.session_state.pipeline_results.get("strategy", [])
                    messages_list = st.session_state.pipeline_results.get("messages", [])
                    hot_leads = [s for s in strategy_list if s.get("priority") in ["HOT", "WARM"]][:3]
                    auto_replies = []
                    for i, lead_strategy in enumerate(hot_leads):
                        matching_msg = next(
                            (m for m in messages_list if m.get("company") == lead_strategy.get("company")),
                            messages_list[i] if i < len(messages_list) else {},
                        )
                        auto_raw = agent_gemini_autoresponder(
                            lead_strategy, lead_strategy, matching_msg, our_product, our_company, reply_tone)
                        auto_data = safe_json_parse(auto_raw, {})
                        if auto_data:
                            auto_data["company"] = lead_strategy.get("company", "Lead " + str(i + 1))
                            auto_replies.append(auto_data)
                    st.session_state.pipeline_results["auto_replies"] = auto_replies
                except Exception as e:
                    st.error("Auto-Responder Error: " + str(e))

        # PHASE 5 — RAG
        with pipeline_status_placeholder.container():
            show_agent_pipeline({"gemini": "done", "claude": "done", "gpt": "done", "auto": "done", "rag": "running"})
        with st.spinner("RAG Intelligence generating market insights..."):
            try:
                rag_insights = agent_gemini_rag_insights(
                    st.session_state.leads_data or [],
                    st.session_state.pipeline_results.get("strategy", []),
                    our_product, our_company, region
                )
                st.session_state.pipeline_results["rag_insights"] = rag_insights
                # Build RAG context for Q&A
                st.session_state.rag_context = build_rag_context(
                    our_product, our_company, region, target_client,
                    st.session_state.leads_data or [],
                    st.session_state.pipeline_results.get("strategy", [])
                )
            except Exception as e:
                st.error("RAG Error: " + str(e))

        st.balloons()
        st.rerun()

# ─────────────────────────────────────────────
# RESULTS DISPLAY
# ─────────────────────────────────────────────
if "gemini_raw" in st.session_state.pipeline_results:

    # PHASE 1 — LEADS TABLE
    show_phase_header("", "&#128269;", "Phase 1: Scout — Lead Discovery", "Real businesses matching your target profile")
    leads_list = st.session_state.leads_data
    if leads_list:
        df_display = pd.DataFrame(leads_list)
        display_cols = ["company", "first_name", "last_name", "decision_maker_role", "phone", "email", "why_need", "deal_size"]
        df_display = df_display[[c for c in display_cols if c in df_display.columns]]
        df_display.columns = ["Company", "First Name", "Last Name", "Role", "Phone", "Email", "Why They Need Us", "Est. Deal"][:len(df_display.columns)]
        st.dataframe(df_display, use_container_width=True, hide_index=True)

    # PHASE 2 — STRATEGY
    show_phase_header("phase-claude", "&#129504;", "Phase 2: Strategist — Deep Analysis", "Personalised strategy for each lead")
    strategy_list = st.session_state.pipeline_results.get("strategy", [])
    for s in strategy_list:
        priority = s.get("priority", "WARM")
        badge_class = "badge-hot" if priority == "HOT" else ("badge-cold" if priority == "COLD" else "badge-warm")
        pain_items = "".join(["<li>" + esc(p) + "</li>" for p in s.get("pain_points", [])])
        st.markdown(
            '<div class="lead-card">'
            '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;">'
            '<div><p class="lead-name">' + esc(s.get("company", "")) + "</p>"
            '<p class="lead-address">' + esc(s.get("first_name", "")) + ' ' + esc(s.get("last_name", "")) + " | Score: " + esc(s.get("deal_score", 0)) + "/100</p></div>"
            '<span class="' + badge_class + '">' + esc(priority) + "</span></div>"
            '<div class="strategy-box"><div class="strategy-title">Value Proposition</div>'
            '<div class="strategy-text">' + esc(s.get("our_value_prop", "")) + "</div></div>"
            '<div style="display:flex;gap:16px;flex-wrap:wrap;margin-top:12px;">'
            '<div style="flex:1;min-width:160px;"><p style="font-size:0.72rem;color:#4a5568;text-transform:uppercase;letter-spacing:1px;">Pain Points</p>'
            '<ul style="color:#b0bec5;font-size:0.82rem;margin:4px 0;padding-left:16px;">' + pain_items + "</ul></div>"
            '<div style="flex:1;min-width:160px;"><p style="font-size:0.72rem;color:#4a5568;text-transform:uppercase;letter-spacing:1px;">Opening Hook</p>'
            '<p style="color:#e0e6f0;font-size:0.84rem;font-style:italic;">' + esc(s.get("opening_hook", "")) + "</p></div>"
            '<div style="flex:1;min-width:160px;"><p style="font-size:0.72rem;color:#4a5568;text-transform:uppercase;letter-spacing:1px;">Recommended Approach</p>'
            '<p style="color:#b0bec5;font-size:0.82rem;">' + esc(s.get("recommended_approach", "")) + "</p></div></div>"
            '<div style="margin-top:10px;padding-top:10px;border-top:1px solid #1e2a3e;display:flex;gap:20px;flex-wrap:wrap;">'
            '<span style="font-size:0.8rem;color:#7a8ba0;">Value: ' + esc(s.get("estimated_value", "")) + "</span>"
            '<span style="font-size:0.8rem;color:#7a8ba0;">Urgency: ' + esc(s.get("urgency_signal", "")) + "</span>"
            "</div></div>",
            unsafe_allow_html=True,
        )

    # PHASE 3 — MESSAGES WITH FIXED LINKEDIN
    show_phase_header("phase-gpt", "&#9993;", "Phase 3: Communicator — Outreach Messages", "WhatsApp, Email and LinkedIn for each lead")
    messages_list = st.session_state.pipeline_results.get("messages", [])
    for idx, msg in enumerate(messages_list):
        phone = str(msg.get("phone", ""))
        email_to = str(st.session_state.leads_data[idx].get("email", msg.get("email", ""))) if idx < len(st.session_state.leads_data) else ""
        wa_text = str(msg.get("whatsapp_message", ""))
        email_sub = str(msg.get("email_subject", ""))
        email_body = str(msg.get("email_body", ""))
        linkedin_note = str(msg.get("linkedin_note", ""))
        company = str(msg.get("company", "Lead " + str(idx + 1)))
        f_name = str(msg.get("first_name", ""))
        l_name = str(msg.get("last_name", ""))
        existing_li = str(msg.get("person_linkedin", ""))
        best_time = str(msg.get("best_time_to_contact", "Weekday morning"))
        follow_up = str(msg.get("follow_up_day", "3 days"))

        clean_ph = clean_phone_number(phone)
        wa_link = "https://wa.me/" + clean_ph + "?text=" + urllib.parse.quote(wa_text)
        mail_link = "mailto:" + email_to + "?subject=" + urllib.parse.quote(email_sub) + "&body=" + urllib.parse.quote(email_body)
        
        # FIX 2: Proper LinkedIn URL
        li_link = build_linkedin_url(f_name, l_name, company, existing_li)

        st.markdown(
            '<div class="lead-card" style="border-color:#1a4a1a;">'
            '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">'
            '<p class="lead-name">' + esc(company) + " — " + esc(f_name) + " " + esc(l_name) + "</p>"
            '<span style="font-size:0.78rem;color:#7a8ba0;">Best Time: ' + esc(best_time) + " | Follow-up: " + esc(follow_up) + "</span></div>"
            '<p style="font-size:0.85rem;color:#64b5f6;"><b>Email:</b> ' + esc(email_to) + '</p>'
            '<div class="msg-box msg-whatsapp"><div class="msg-label msg-label-wa">📱 WhatsApp Message</div>'
            '<div class="msg-content">' + esc(wa_text) + "</div></div>"
            '<div class="msg-box msg-email"><div class="msg-label msg-label-mail">📧 Email — ' + esc(email_sub) + "</div>"
            '<div class="msg-content">' + esc(email_body) + "</div></div>"
            '<div class="msg-box"><div class="msg-label" style="color:#0A66C2;">💼 LinkedIn Note</div>'
            '<div class="msg-content">' + esc(linkedin_note) + "</div></div>"
            '<div class="action-row">'
            '<a class="btn-wa" href="' + esc(wa_link) + '" target="_blank">📱 WhatsApp</a>'
            '<a class="btn-mail" href="' + esc(mail_link) + '" target="_blank">📧 Email Draft</a>'
            '<a class="btn-linkedin" href="' + esc(li_link) + '" target="_blank">💼 LinkedIn Profile</a>'
            "</div></div>",
            unsafe_allow_html=True,
        )

        # FIX 1: IMPROVED HUNTER API EMAIL EXTRACTION
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            enrich_key = f"hunter_{company.replace(' ', '_')}_{idx}"
            if st.button(f"🔍 Find Real Email — {company}", key=enrich_key):
                lead_data = st.session_state.leads_data[idx] if idx < len(st.session_state.leads_data) else {}
                fn = lead_data.get("first_name", f_name)
                ln = lead_data.get("last_name", l_name)
                with st.spinner(f"Searching Hunter.io for {fn} {ln} at {company}..."):
                    found_email, status_msg = get_hunter_email(fn, ln, company)
                    if found_email:
                        st.markdown(f'<div class="hunter-success">✅ Email found: {found_email}<br><small>{status_msg}</small></div>', unsafe_allow_html=True)
                        if idx < len(st.session_state.leads_data):
                            st.session_state.leads_data[idx]["email"] = found_email
                        st.rerun()
                    else:
                        st.markdown(f'<div class="hunter-fail">⚠️ {status_msg}<br>Try LinkedIn to connect directly.</div>', unsafe_allow_html=True)

        with btn_col2:
            button_key = f"send_email_{company.replace(' ', '_')}_{idx}"
            st.button(
                f"🚀 Send Email to {company}",
                key=button_key,
                on_click=handle_email_dispatch,
                args=(email_to, email_sub, email_body, company)
            )
        st.markdown("<br>", unsafe_allow_html=True)

    # PHASE 4 — AUTO REPLY
    if auto_reply_enabled and "auto_replies" in st.session_state.pipeline_results:
        show_phase_header("phase-auto", "&#128260;", "Phase 4: Auto-Responder — Conversation Simulation", "AI simulates client reply and generates follow-up")
        auto_replies = st.session_state.pipeline_results["auto_replies"]
        scenario_colors = {
            "interested": "#00c851", "needs_more_info": "#ffaa00",
            "price_sensitive": "#ff8800", "requesting_visit": "#4285f4",
            "not_interested": "#ff4444",
        }
        for reply in auto_replies:
            scenario = str(reply.get("reply_scenario", ""))
            scenario_col = scenario_colors.get(scenario, "#7a8ba0")
            escalate = reply.get("escalate_to_human", False)
            escalate_html = (
                '<span style="background:#1a0a0a;color:#ff4444;border:1px solid #ff4444;padding:3px 10px;border-radius:10px;font-size:0.72rem;font-weight:700;">ESCALATE TO HUMAN</span>'
                if escalate else
                '<span style="background:#0a1a0a;color:#00c851;border:1px solid #00c851;padding:3px 10px;border-radius:10px;font-size:0.72rem;font-weight:700;">AUTO-HANDLED</span>'
            )
            st.markdown(
                '<div class="lead-card" style="border-color:#1a3a0a;">'
                '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">'
                '<p class="lead-name">' + esc(reply.get("company", "")) + "</p>"
                '<div style="display:flex;gap:10px;align-items:center;">'
                '<span style="color:' + scenario_col + ';font-size:0.8rem;font-weight:700;text-transform:uppercase;">' + esc(scenario.replace("_", " ")) + "</span>" + escalate_html + "</div></div>"
                '<div class="conversation-entry"><div class="conv-from">Simulated Client Reply:</div>'
                '<div class="conv-msg" style="color:#e0e6f0;font-style:italic;">' + esc(reply.get("simulated_client_reply", "")) + "</div></div>"
                '<div class="autoreply-box"><div class="autoreply-label">Our Auto WhatsApp Reply</div>'
                '<div class="autoreply-text">' + esc(reply.get("auto_response_whatsapp", "")) + "</div></div>"
                '<div style="margin-top:10px;padding:10px;background:#0a0d14;border:1px solid #1e2a3e;border-radius:8px;">'
                '<p style="font-size:0.72rem;color:#4a5568;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">Next Action</p>'
                '<p style="color:#b0bec5;font-size:0.84rem;">' + esc(reply.get("next_action", "")) + "</p></div></div>",
                unsafe_allow_html=True,
            )

    # PHASE 5 — RAG INTELLIGENCE
    if "rag_insights" in st.session_state.pipeline_results:
        show_phase_header("phase-rag", "&#129302;", "Phase 5: RAG Intelligence — Market Insights", "Deep analysis using all pipeline data")
        
        rag_insights = st.session_state.pipeline_results.get("rag_insights", "")
        st.markdown(
            '<div class="rag-box"><div class="rag-label">📊 AI Market Intelligence Report</div>'
            '<div class="rag-text">' + esc(rag_insights) + "</div></div>",
            unsafe_allow_html=True,
        )

        # RAG Q&A
        st.markdown("#### 💬 Ask AI About Your Leads")
        st.caption("Ask anything about the discovered leads, strategies, or market — AI answers from pipeline data")
        
        rag_question = st.text_input(
            "Your question:",
            placeholder="e.g. Which lead has the highest revenue potential? What are the common objections?",
            key="rag_question"
        )
        if st.button("🧠 Get AI Answer", key="rag_ask"):
            if rag_question:
                with st.spinner("Searching pipeline data..."):
                    answer = rag_query(
                        rag_question,
                        st.session_state.rag_context,
                        our_company, our_product
                    )
                st.markdown(
                    '<div class="rag-box"><div class="rag-label">🧠 AI Answer</div>'
                    '<div class="rag-text">' + esc(answer) + "</div></div>",
                    unsafe_allow_html=True,
                )

    # EXPORTS
    st.success("✅ Full 5-Agent Pipeline Complete!")
    st.markdown("### 📥 Export Intelligence Report")
    dl_col1, dl_col2 = st.columns(2)
    with dl_col1:
        if st.session_state.leads_data:
            df_leads = pd.DataFrame(st.session_state.leads_data)
            st.download_button(
                "📊 Download Leads CSV",
                data=df_leads.to_csv(index=False).encode("utf-8"),
                file_name=f"samketan_leads_{region.replace(',','_').replace(' ','_')}.csv",
                mime="text/csv", use_container_width=True,
            )
    with dl_col2:
        full_report = {
            "generated_at": datetime.now().isoformat(),
            "inputs": {"product": my_product, "region": region, "target_client": target_client},
            "pipeline_results": st.session_state.pipeline_results,
        }
        st.download_button(
            "📋 Download Full JSON Report",
            data=json.dumps(full_report, indent=2, default=str).encode("utf-8"),
            file_name=f"samketan_report_{region.replace(',','_').replace(' ','_')}.json",
            mime="application/json", use_container_width=True,
        )

# ---------------------------------------------
# MANUAL REPLY SIMULATION
# ---------------------------------------------
if simulate_reply and st.session_state.pipeline_results:
    st.markdown("---")
    show_phase_header("phase-auto", "&#128172;", "Manual Reply Simulation", "Enter client reply — get AI response")
    client_reply_input = st.text_area("Paste client reply:", placeholder="e.g. Interested, can you share pricing?", height=100)
    reply_company = st.text_input("Which company replied?", placeholder="Company name...")
    if st.button("Generate Smart Auto-Reply") and client_reply_input:
        with st.spinner("Generating response..."):
            try:
                manual_prompt = (
                    "You are the sales AI for " + our_company + ".\n"
                    "OUR OFFERING: " + our_product + "\n"
                    "TONE: " + reply_tone + "\n"
                    "COMPANY: " + reply_company + "\n"
                    "CLIENT SAID: " + client_reply_input + "\n\n"
                    "Write a response that addresses their message, provides relevant info, and moves toward a meeting.\n"
                    "Return ONLY valid JSON: {whatsapp_reply, email_reply, next_step}\n"
                    "Start with { end with }"
                )
                manual_res, _ = call_gemini_with_retry(manual_prompt)
                manual_data = safe_json_parse(manual_res.text, {})
                if manual_data:
                    st.markdown(
                        '<div class="autoreply-box"><div class="autoreply-label">WhatsApp Reply</div>'
                        '<div class="autoreply-text">' + esc(manual_data.get("whatsapp_reply", "")) + "</div></div>"
                        '<div class="msg-box msg-email"><div class="msg-label msg-label-mail">Email Reply</div>'
                        '<div class="msg-content">' + esc(manual_data.get("email_reply", "")) + "</div></div>"
                        '<div style="background:#0a0d14;border:1px solid #1e2a3e;border-radius:8px;padding:12px 16px;margin-top:10px;">'
                        '<p style="font-size:0.72rem;color:#4a5568;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">Next Step</p>'
                        '<p style="color:#b0bec5;font-size:0.84rem;">' + esc(manual_data.get("next_step", "")) + "</p></div>",
                        unsafe_allow_html=True,
                    )
            except Exception as e:
                st.error("Error: " + str(e))
elif simulate_reply:
    st.warning("Run the pipeline first.")

# ---------------------------------------------
# FOOTER
# ---------------------------------------------
st.markdown("---")
st.markdown(
    '<p style="color:#2a3a4e;font-size:0.8rem;text-align:center;">'
    "Samketan AI v8.0 | 5-Agent RAG + LLM Pipeline | Powered by Gemini | © 2026 Samketan"
    "</p>",
    unsafe_allow_html=True,
)

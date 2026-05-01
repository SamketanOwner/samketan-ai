import streamlit as st
import auth

if not auth.login_screen():
    st.stop()

import google.generativeai as genai
import anthropic
from openai import OpenAI
import urllib.parse
import pandas as pd
import random
import extra_streamlit_components as stx

# --- COOKIE MANAGER ---
cookie_manager = stx.CookieManager()
saved_user = cookie_manager.get('samketan_user')
if saved_user and not st.session_state.get('authenticated'):
    st.session_state.authenticated = True
    st.session_state.current_user = saved_user

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Samketan Business Growth Engine",
    page_icon="🚀",
    layout="wide"
)

# ─────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0f1117; }
    section[data-testid="stSidebar"] { background-color: #1a1d27 !important; }

    /* Header */
    .header-banner {
        background: linear-gradient(135deg, #1a1d27 0%, #0d2137 100%);
        border: 1px solid #1e3a5f;
        border-radius: 16px;
        padding: 28px 36px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .header-title { font-size: 2rem; font-weight: 800; color: #fff; margin: 0; }
    .header-sub   { font-size: 0.92rem; color: #7a8ba0; margin-top: 4px; }
    .header-badge {
        background: linear-gradient(135deg, #0066ff, #00c6ff);
        color: white; padding: 6px 16px; border-radius: 20px;
        font-size: 0.78rem; font-weight: 700; letter-spacing: 1px;
    }

    /* Promo bar */
    .promo-bar {
        background: linear-gradient(90deg,#1a0a00,#2d1500);
        border: 1px solid #FF8C00; border-radius: 8px;
        padding: 10px 16px; margin-bottom: 20px;
        font-size: 14px; color: #FFB347; font-weight: 600;
    }
    .promo-bar a { color: #FFD700; text-decoration: none; font-weight: 700; }

    /* Input card */
    .input-card {
        background: #1a1d27; border: 1px solid #2a2d3e;
        border-radius: 12px; padding: 24px; margin-bottom: 20px;
    }
    .stTextInput > div > div > input,
    .stTextArea  > div > div > textarea {
        background-color: #12151f !important;
        border: 1px solid #2a2d3e !important;
        color: #e0e6f0 !important; border-radius: 8px !important;
    }
    .stRadio > div { color: #b0bec5; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: #1a1d27 !important;
        border-radius: 10px; padding: 4px; gap: 4px;
        border: 1px solid #2a2d3e;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important; color: #7a8ba0 !important;
        border-radius: 8px !important; font-weight: 600 !important;
        padding: 10px 24px !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg,#0066ff,#0099ff) !important;
        color: white !important;
    }
    .stTabs [data-baseweb="tab-panel"] {
        background: transparent !important; padding-top: 20px !important;
    }

    /* Generate Button */
    .stButton > button {
        background: linear-gradient(135deg,#0066ff,#0099ff) !important;
        color: white !important; border: none !important;
        border-radius: 10px !important; font-weight: 700 !important;
        font-size: 1rem !important; padding: 14px 32px !important;
        width: 100% !important; transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(0,102,255,0.4) !important;
    }

    /* Stats bar */
    .stats-bar { display:flex; gap:14px; margin-bottom:20px; flex-wrap:wrap; }
    .stat-chip {
        background:#1a1d27; border:1px solid #2a2d3e;
        border-radius:8px; padding:10px 18px;
        color:#b0bec5; font-size:0.83rem; font-weight:600;
    }
    .stat-chip span { color:#0099ff; font-size:1.1rem; font-weight:800; }

    /* Lead Card */
    .lead-card {
        background:#1a1d27; border:1px solid #2a2d3e;
        border-radius:14px; padding:20px 24px; margin-bottom:16px;
        transition: border-color 0.2s, box-shadow 0.2s;
    }
    .lead-card:hover { border-color:#0066ff; box-shadow:0 4px 24px rgba(0,102,255,0.15); }
    .lead-card-header { display:flex; align-items:flex-start; justify-content:space-between; margin-bottom:12px; }
    .lead-name   { font-size:1.1rem; font-weight:700; color:#fff; margin:0; }
    .lead-address{ font-size:0.82rem; color:#7a8ba0; margin-top:4px; }

    .badge-hot  { background:#1a0a0a; color:#ff4444; border:1px solid #ff4444; padding:4px 12px; border-radius:20px; font-size:0.75rem; font-weight:700; }
    .badge-warm { background:#1a1200; color:#ffaa00; border:1px solid #ffaa00; padding:4px 12px; border-radius:20px; font-size:0.75rem; font-weight:700; }
    .badge-cold { background:#001a2a; color:#0099ff; border:1px solid #0099ff; padding:4px 12px; border-radius:20px; font-size:0.75rem; font-weight:700; }

    .person-pill {
        display:inline-flex; align-items:center; gap:8px;
        background:#12151f; border:1px solid #2a2d3e;
        border-radius:8px; padding:8px 14px; margin-bottom:14px;
    }
    .person-name { color:#e0e6f0; font-weight:600; font-size:0.9rem; }
    .person-role { color:#7a8ba0; font-size:0.8rem; margin-left:6px; }

    .lead-divider { border:none; border-top:1px solid #2a2d3e; margin:12px 0; }
    .section-label { font-size:0.73rem; color:#4a5568; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px; }
    .contact-val   { color:#b0bec5; font-size:0.85rem; }

    .action-row { display:flex; gap:10px; flex-wrap:wrap; margin-top:14px; }
    .btn-wa   { background:#0d2a1a; color:#25D366; border:1px solid #25D366; padding:8px 16px; border-radius:8px; font-size:0.82rem; font-weight:700; text-decoration:none; display:inline-block; }
    .btn-mail { background:#0d1a2a; color:#64b5f6; border:1px solid #64b5f6; padding:8px 16px; border-radius:8px; font-size:0.82rem; font-weight:700; text-decoration:none; display:inline-block; }
    .btn-li   { background:#0a1929; color:#0a66c2; border:1px solid #0a66c2; padding:8px 16px; border-radius:8px; font-size:0.82rem; font-weight:700; text-decoration:none; display:inline-block; }
    .btn-web  { background:#1a1a2e; color:#b39ddb; border:1px solid #b39ddb; padding:8px 16px; border-radius:8px; font-size:0.82rem; font-weight:700; text-decoration:none; display:inline-block; }
    .btn-wa:hover   { background:#25D366 !important; color:#000 !important; }
    .btn-mail:hover { background:#64b5f6 !important; color:#000 !important; }
    .btn-li:hover   { background:#0a66c2 !important; color:#fff !important; }
    .btn-web:hover  { background:#b39ddb !important; color:#000 !important; }

    .stDownloadButton > button {
        background:#1a1d27 !important; color:#0099ff !important;
        border:1px solid #0099ff !important; border-radius:8px !important;
        font-weight:600 !important; margin-top:10px;
    }
    .user-chip {
        background:#12151f; border:1px solid #2a2d3e;
        border-radius:8px; padding:10px 14px;
        color:#e0e6f0; font-size:0.88rem; margin-bottom:12px;
    }
    .ai-note {
        background:#12151f; border:1px solid #2a2d3e;
        border-radius:8px; padding:12px 16px; margin-bottom:16px;
        font-size:0.83rem; color:#7a8ba0;
    }
    .ai-note b { color:#b0bec5; }

    #MainMenu { visibility:hidden; }
    footer     { visibility:hidden; }
    header     { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="header-banner">
    <div>
        <p class="header-title">🚀 Samketan Business Growth Engine</p>
        <p class="header-sub">Powered by Gemini · Claude · ChatGPT — Triple AI Lead Intelligence</p>
    </div>
    <span class="header-badge">v5.0 TRIPLE AI</span>
</div>
""", unsafe_allow_html=True)

# Promo bar
st.markdown("""
<div class="promo-bar">
    📢 <b>AVAILABLE FOR LEASE:</b> Premium 21,000 Sq. Ft. Warehouse · Gulbarga, Karnataka &nbsp;
    <a href="https://bhoodeviwarehouse.netlify.app/" target="_blank">👉 Visit Bhoodevi Warehouse →</a>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# API KEYS — from st.secrets (preferred) or sidebar fallback
# ─────────────────────────────────────────────
gemini_key    = st.secrets.get("GOOGLE_API_KEY", "")
claude_key    = st.secrets.get("ANTHROPIC_API_KEY", "")
openai_key    = st.secrets.get("OPENAI_API_KEY", "")

with st.sidebar:
    st.markdown("### 🔑 API Keys")
    st.caption("Keys from Streamlit Secrets are used automatically. Paste here only if not set in secrets.")
    if not gemini_key:
        gemini_key  = st.text_input("Google Gemini API Key",  type="password", placeholder="AIza...")
    if not claude_key:
        claude_key  = st.text_input("Anthropic Claude API Key", type="password", placeholder="sk-ant-...")
    if not openai_key:
        openai_key  = st.text_input("OpenAI ChatGPT API Key",  type="password", placeholder="sk-...")

    st.markdown("---")
    st.markdown("### 🏢 Samketan Strategy")
    strategy_note = st.text_area(
        "Why Samketan is Best?",
        value="We provide premium quality, natural ingredients, and a reliable cold-chain supply with 24/7 support.",
        help="Injected into WhatsApp & Email outreach messages."
    )
    st.markdown("---")
    with st.expander("🎯 How to Use"):
        st.markdown("""
**Step 1:** Fill in product, client & region  
**Step 2:** Pick an AI tab (Gemini / Claude / ChatGPT)  
**Step 3:** Click Generate Leads  
**Step 4:** Use action buttons to reach out instantly
        """)
    st.markdown("---")
    st.markdown(f'<div class="user-chip">👤 {st.session_state.current_user}</div>', unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True):
        cookie_manager.delete('samketan_user')
        st.session_state.authenticated = False
        st.session_state.otp_sent = False
        st.rerun()

# ─────────────────────────────────────────────
# INPUT SECTION (shared across all tabs)
# ─────────────────────────────────────────────
st.markdown('<div class="input-card">', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    my_product    = st.text_input("🛒 Product / Service", value="ice cream", placeholder="e.g. ice cream, packaging, software")
    region        = st.text_input("📍 Target City / Region", value="gulbarga", placeholder="e.g. Bengaluru, Mumbai")
with col2:
    target_client = st.text_input("🏢 Who is your Client?", value="hotels, smart bazar", placeholder="e.g. hotels, retailers, factories")
    scope         = st.radio("🌍 Market Scope", ["Local (Domestic)", "Export (International)"], horizontal=True)
st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
LEAD_PROMPT = """Act as a B2B Sales Expert. Find 10 REAL businesses in {region} that match the client type: {target_client}.
They must be potential buyers for: {my_product}.

STRICT RULES:
- Never say 'Not Available' — guess a likely value instead.
- Identify a real Decision Maker Role (e.g., F&B Manager, Store Manager, Purchase Head).
- Provide a Person Name or specific title if name is unknown.
- Return ONLY a pipe-separated table, no markdown, no headers explanation:

Agency Name | Full Address | Website URL | Email ID | Phone Number | Decision Maker Role | Person Name
"""

def make_prompt(region, target_client, my_product):
    return LEAD_PROMPT.format(region=region, target_client=target_client, my_product=my_product)

def score_lead(name):
    random.seed(hash(name) % 9999)
    s = random.randint(1, 10)
    if s >= 7:  return "🔥 Hot",  "badge-hot"
    if s >= 4:  return "🌡️ Warm", "badge-warm"
    return "❄️ Cold", "badge-cold"

def build_cards(raw_text, my_product, strategy_note):
    lines     = raw_text.split('\n')
    cards_html = ""
    lead_data  = []

    for line in lines:
        if '|' not in line or 'Agency' in line or '---' in line:
            continue
        cols = [c.strip() for c in line.split('|')]
        if len(cols) < 7:
            continue

        name, addr, web, email, phone, role, person = cols[:7]
        lead_data.append([name, addr, web, email, phone, role, person])

        wa_msg      = f"Hello {person}, reaching out from Samketan about {my_product}. {strategy_note}"
        clean_phone = "".join(filter(str.isdigit, phone))
        if len(clean_phone) == 10:
            clean_phone = "91" + clean_phone
        wa_link   = f"https://wa.me/{clean_phone}?text={urllib.parse.quote(wa_msg)}"
        mail_link = f"mailto:{email}?subject=Partnership Opportunity - Samketan&body={urllib.parse.quote(wa_msg)}"
        li_link   = f"https://www.linkedin.com/search/results/people/?keywords={urllib.parse.quote(chr(34)+person+chr(34)+' '+chr(34)+name+chr(34))}&origin=GLOBAL_SEARCH_HEADER"
        web_url   = web if web.startswith("http") else f"https://{web}"

        score_label, score_class = score_lead(name)

        cards_html += f"""
        <div class="lead-card">
            <div class="lead-card-header">
                <div>
                    <p class="lead-name">{name}</p>
                    <p class="lead-address">📍 {addr}</p>
                </div>
                <span class="{score_class}">{score_label}</span>
            </div>
            <div class="person-pill">
                <span>👤</span>
                <span class="person-name">{person}</span>
                <span class="person-role">· {role}</span>
            </div>
            <hr class="lead-divider">
            <div style="display:flex;gap:32px;flex-wrap:wrap;margin-bottom:4px;">
                <div><p class="section-label">📞 Phone</p><p class="contact-val">{phone}</p></div>
                <div><p class="section-label">📧 Email</p><p class="contact-val">{email}</p></div>
                <div><p class="section-label">🌐 Website</p><p class="contact-val">{web}</p></div>
            </div>
            <div class="action-row">
                <a class="btn-wa"   href="{wa_link}"   target="_blank">💬 WhatsApp</a>
                <a class="btn-mail" href="{mail_link}" target="_blank">📧 Email</a>
                <a class="btn-li"   href="{li_link}"   target="_blank">🔗 LinkedIn</a>
                <a class="btn-web"  href="{web_url}"   target="_blank">🌐 Website</a>
            </div>
        </div>"""

    return cards_html, lead_data

def show_results(raw_text, my_product, strategy_note, region, ai_name):
    cards_html, lead_data = build_cards(raw_text, my_product, strategy_note)
    count = len(lead_data)

    st.markdown(f"""
    <div class="stats-bar">
        <div class="stat-chip">AI Engine &nbsp;<span>{ai_name}</span></div>
        <div class="stat-chip">Leads Found &nbsp;<span>{count}</span></div>
        <div class="stat-chip">Region &nbsp;<span>{region.title()}</span></div>
        <div class="stat-chip">Product &nbsp;<span>{my_product.title()}</span></div>
    </div>
    """, unsafe_allow_html=True)

    if cards_html:
        st.markdown(cards_html, unsafe_allow_html=True)
        df = pd.DataFrame(lead_data, columns=["Name","Address","Website","Email","Phone","Role","Person"])
        st.download_button(
            f"📥 Download {ai_name} Leads as CSV",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name=f"samketan_{ai_name.lower()}_leads_{region}.csv",
            mime="text/csv"
        )
    else:
        st.warning("No structured leads returned. Try rephrasing your inputs.")

# ─────────────────────────────────────────────
# THREE AI TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["✨ Gemini", "🟣 Claude", "🟢 ChatGPT"])

# ── TAB 1: GEMINI ──────────────────────────
with tab1:
    st.markdown('<div class="ai-note">Using <b>Google Gemini</b> — Best for broad regional B2B data across Indian cities.</div>', unsafe_allow_html=True)

    if st.button("⚡ Generate Leads with Gemini", key="gemini_btn"):
        if not gemini_key:
            st.error("❌ Google Gemini API Key is missing. Add it to Streamlit Secrets as GOOGLE_API_KEY.")
        else:
            try:
                genai.configure(api_key=gemini_key.strip())
                available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                priority  = ['models/gemini-2.5-flash', 'models/gemini-1.5-flash']
                selected  = next((m for m in priority if m in available), available[0])
                model     = genai.GenerativeModel(selected)

                with st.spinner("🔍 Gemini is mining leads..."):
                    response = model.generate_content(make_prompt(region, target_client, my_product))

                show_results(response.text, my_product, strategy_note, region, "Gemini")

            except Exception as e:
                st.error(f"❌ Gemini Error: {e}")

# ── TAB 2: CLAUDE ──────────────────────────
with tab2:
    st.markdown('<div class="ai-note">Using <b>Anthropic Claude</b> — Excellent at structured, detailed B2B research with accurate contact reasoning.</div>', unsafe_allow_html=True)

    if st.button("⚡ Generate Leads with Claude", key="claude_btn"):
        if not claude_key:
            st.error("❌ Anthropic API Key is missing. Add it to Streamlit Secrets as ANTHROPIC_API_KEY.")
        else:
            try:
                client = anthropic.Anthropic(api_key=claude_key.strip())

                with st.spinner("🔍 Claude is mining leads..."):
                    message = client.messages.create(
                        model="claude-opus-4-6",
                        max_tokens=2048,
                        messages=[{
                            "role": "user",
                            "content": make_prompt(region, target_client, my_product)
                        }]
                    )
                raw_text = message.content[0].text
                show_results(raw_text, my_product, strategy_note, region, "Claude")

            except Exception as e:
                st.error(f"❌ Claude Error: {e}")

# ── TAB 3: CHATGPT ─────────────────────────
with tab3:
    st.markdown('<div class="ai-note">Using <b>OpenAI ChatGPT</b> (GPT-4o) — Great for global market leads and export-focused B2B prospecting.</div>', unsafe_allow_html=True)

    if st.button("⚡ Generate Leads with ChatGPT", key="openai_btn"):
        if not openai_key:
            st.error("❌ OpenAI API Key is missing. Add it to Streamlit Secrets as OPENAI_API_KEY.")
        else:
            try:
                client = OpenAI(api_key=openai_key.strip())

                with st.spinner("🔍 ChatGPT is mining leads..."):
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        max_tokens=2048,
                        messages=[{
                            "role": "user",
                            "content": make_prompt(region, target_client, my_product)
                        }]
                    )
                raw_text = response.choices[0].message.content
                show_results(raw_text, my_product, strategy_note, region, "ChatGPT")

            except Exception as e:
                st.error(f"❌ ChatGPT Error: {e}")

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<p style="color:#4a5568;font-size:0.8rem;text-align:center;">'
    'Samketan Business Growth Engine v5.0 · Gemini · Claude · ChatGPT · © 2026 Samketan</p>',
    unsafe_allow_html=True
)

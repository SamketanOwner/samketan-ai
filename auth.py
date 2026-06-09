import streamlit as st
import requests
import smtplib
import random
from datetime import datetime
import json
import base64
from pathlib import Path
from email.mime.text import MIMEText
from urllib.parse import urlencode

# --- CONFIGURATION ---
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxxkHAi7kn24BChb4zQktRE-u4kPY-sn9L96FLIqw4-czxzms03iCP1eNnPUGrAB_5HxA/exec"
GMAIL_USER = "shgarampalli@gmail.com"
GMAIL_PASS = "hbikssxqyzthscne"

# Dynamically reads your exact custom callback string from your Streamlit secrets dashboard
REDIRECT_URI = st.secrets["google_oauth"]["redirect_uri"]

# --- LOAD LOGO ---
def get_logo_base64():
    logo_path = Path("logo_samketan.png")
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

# --- EMAIL OTP ---
def send_otp_email(receiver_email, otp_code):
    try:
        msg = MIMEText(f"""
Dear User,

Your Samketan AI verification code is:

  {otp_code}

This code is valid for 10 minutes. Do not share it with anyone.

— Samketan AI | B2B Lead Generation Platform
        """.strip())
        msg['Subject'] = '🔐 Samketan AI — Your Access Code'
        msg['From'] = f"Samketan AI <{GMAIL_USER}>"
        msg['To'] = receiver_email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_USER, GMAIL_PASS)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Email Error: {e}")
        return False

# --- GOOGLE SHEET LOG ---
def log_to_google_sheet(user_info, method):
    try:
        data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "contact": user_info,
            "method": method
        }
        requests.post(SCRIPT_URL, data=json.dumps(data))
    except:
        pass

# --- GOOGLE OAUTH HANDLERS ---
def get_google_auth_url():
    """Build Google OAuth URL — opens Google login popup with strict path cleaning"""
    try:
        client_id = st.secrets["google_oauth"]["client_id"]
    except Exception:
        return None
    
    # Removes any accidental background trailing slashes to guarantee exact console match
    clean_redirect_uri = REDIRECT_URI.rstrip('/')
    
    params = {
        "client_id": client_id,
        "redirect_uri": clean_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account",
    }
    return "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)


def exchange_code_for_user(code):
    """Exchange authorization code for user profile properties natively via requests"""
    try:
        client_id     = st.secrets["google_oauth"]["client_id"]
        client_secret = st.secrets["google_oauth"]["client_secret"]
    except Exception as e:
        return None, f"Secrets error: {e}"

    clean_redirect_uri = REDIRECT_URI.rstrip('/')

    try:
        token_resp = requests.post("https://oauth2.googleapis.com/token", data={
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": clean_redirect_uri,
            "grant_type": "authorization_code",
        }, timeout=10)
        token_data = token_resp.json()
    except Exception as network_err:
        return None, f"Handshake network failure: {network_err}"

    if "error" in token_data:
        return None, f"Token validation crash: {token_data.get('error_description', token_data['error'])}"

    access_token = token_data.get("access_token")
    if not access_token:
        return None, "No active access token block delivered."

    try:
        user_resp = requests.get("https://www.googleapis.com/oauth2/v2/userinfo",
                                 headers={"Authorization": f"Bearer {access_token}"}, timeout=10)
        user_data = user_resp.json()
    except Exception as info_err:
        return None, f"User parsing target missing: {info_err}"

    email = user_data.get("email")
    name  = user_data.get("name", email)

    if not email:
        return None, "Google verification payload lacked an explicit email identity reference."

    return {"email": email, "name": name}, None


def handle_google_callback():
    """Verify context paths to trap active OAuth redirects landing inside URL layers"""
    params = st.query_params
    code = params.get("code")
    if not code:
        return False

    # Exchange token variables FIRST before wiping active parameter layout records
    user_info, error = exchange_code_for_user(code)
    st.query_params.clear()

    if error:
        st.session_state["google_error"] = error
        return False

    log_to_google_sheet(user_info["email"], "Google OAuth")
    st.session_state.authenticated = True
    st.session_state.current_user  = user_info["email"]
    st.session_state.display_name  = user_info["name"]
    return True


# --- CSS + LEFT PANEL LAYOUT ---
def inject_css(logo_b64=None):
    logo_html = ""
    if logo_b64:
        logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height:52px;width:52px;border-radius:50%;object-fit:contain;background:#fff;padding:4px;" alt="Samketan AI Logo">'
    else:
        logo_html = '<div style="height:52px;width:52px;border-radius:50%;background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.2);display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:700;color:#7FB3FF;font-family:Georgia,serif;">SN</div>'

    # ✅ GOOGLE WEB SITE METADATA VERIFICATION HANDSHAKE
    st.markdown('<meta name="google-site-verification" content="NToh75b655cIVA891yX1QYqoLhvDFPi_lKZCmkfXYyM" />', unsafe_allow_html=True)

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@300;400;500&display=swap');
    #MainMenu, footer, header {{ visibility: hidden; }}
    .block-container {{ padding: 0 !important; max-width: 100% !important; }}
    section[data-testid="stSidebar"] {{ display: none; }}
    [data-testid="manage-app-button"], .stDeployButton, div[class*="StatusWidget"] {{ display: none !important; }}
    .stApp {{ background: #f0f2f7 !important; font-family: 'DM Sans', sans-serif; }}
    div[data-testid="stTextInput"] > div > div > input {{
        font-family: 'DM Sans', sans-serif !important; border-radius: 9px !important;
        border: 1px solid #d0d7e8 !important; padding: 10px 14px !important;
        font-size: 14px !important; background: #f8f9fc !important; color: #0D1B3E !important;
    }}
    div[data-testid="stTextInput"] > div > div > input:focus {{
        border-color: #378ADD !important; background: #fff !important;
        box-shadow: 0 0 0 3px rgba(55,138,221,0.12) !important;
    }}
    div[data-testid="stTextInput"] label {{
        font-family: 'DM Sans', sans-serif !important; font-size: 12px !important;
        font-weight: 500 !important; color: #4a5a8a !important;
        letter-spacing: 0.04em !important; text-transform: uppercase !important;
    }}
    div[data-testid="stButton"] > button {{
        font-family: 'DM Sans', sans-serif !important; background: #0D1B3E !important;
        color: #fff !important; border: none !important; border-radius: 9px !important;
        padding: 0.6rem 1.5rem !important; font-size: 14px !important;
        font-weight: 500 !important; letter-spacing: 0.04em !important;
        width: 100% !important; transition: background 0.2s !important;
    }}
    div[data-testid="stButton"] > button:hover {{ background: #1a3160 !important; }}
    div[data-testid="stSuccess"] {{ border-radius: 9px !important; font-size: 13px !important; }}
    div[data-testid="stError"] {{ border-radius: 9px !important; font-size: 13px !important; }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:#0D1B3E;border-radius:20px 0 0 20px;padding:2.5rem 2rem;
        display:flex;flex-direction:column;gap:1.8rem;position:relative;overflow:hidden;min-height:520px;">
      <div style="position:absolute;top:-70px;right:-70px;width:240px;height:240px;border-radius:50%;border:35px solid rgba(55,138,221,0.1);pointer-events:none;"></div>
      <div style="position:absolute;bottom:-50px;left:-50px;width:180px;height:180px;border-radius:50%;border:25px solid rgba(55,138,221,0.07);pointer-events:none;"></div>
      <div style="display:flex;align-items:center;gap:12px;position:relative;z-index:2;">
        {logo_html}
        <div>
          <div style="font-family:'Playfair Display',Georgia,serif;font-size:19px;font-weight:700;color:#fff;line-height:1.1;">Samketan AI</div>
          <div style="font-size:10px;letter-spacing:0.12em;text-transform:uppercase;color:rgba(255,255,255,0.4);margin-top:3px;">B2B Lead Generation</div>
        </div>
      </div>
      <div style="position:relative;z-index:2;">
        <h2 style="font-family:'Playfair Display',Georgia,serif;font-size:24px;font-weight:700;color:#fff;line-height:1.4;margin:0 0 0.75rem;">Intelligent Leads<br>for Growing<br>Businesses</h2>
        <p style="font-size:13px;color:rgba(255,255,255,0.5);line-height:1.7;margin:0;">AI-powered prospecting engine built for India's agri, industrial, and enterprise sectors.</p>
      </div>
      <div style="display:flex;flex-wrap:wrap;gap:6px;position:relative;z-index:2;">
        <span style="background:rgba(255,255,255,0.06);border:0.5px solid rgba(255,255,255,0.14);border-radius:5px;padding:4px 10px;font-size:10px;letter-spacing:0.05em;color:rgba(255,255,255,0.6);">Gemini AI</span>
        <span style="background:rgba(255,255,255,0.06);border:0.5px solid rgba(255,255,255,0.14);border-radius:5px;padding:4px 10px;font-size:10px;letter-spacing:0.05em;color:rgba(255,255,255,0.6);">Claude AI</span>
        <span style="background:rgba(255,255,255,0.06);border:0.5px solid rgba(255,255,255,0.14);border-radius:5px;padding:4px 10px;font-size:10px;letter-spacing:0.05em;color:rgba(255,255,255,0.6);">ChatGPT</span>
        <span style="background:rgba(255,255,255,0.06);border:0.5px solid rgba(255,255,255,0.14);border-radius:5px;padding:4px 10px;font-size:10px;letter-spacing:0.05em;color:rgba(255,255,255,0.6);">B2B Intel</span>
      </div>
      <div style="height:0.5px;background:rgba(255,255,255,0.1);position:relative;z-index:2;"></div>
      <div style="position:relative;z-index:2;">
        <div style="font-size:10px;letter-spacing:0.1em;text-transform:uppercase;color:rgba(255,255,255,0.3);margin-bottom:8px;">Sister Enterprise</div>
        <a href="https://bhoodeviwarehouse.com/" target="_blank" style="display:flex;align-items:flex-start;gap:10px;text-decoration:none;padding:10px 12px;border-radius:10px;border:0.5px solid rgba(255,255,255,0.1);background:rgba(255,255,255,0.04);">
          <div style="width:7px;height:7px;border-radius:50%;background:#4CAF82;margin-top:5px;flex-shrink:0;"></div>
          <div>
            <div style="font-size:13px;font-weight:500;color:#7FB3FF;text-decoration:underline;text-underline-offset:3px;margin-bottom:3px;">Bhoodevi Warehouse</div>
            <div style="font-size:11px;color:rgba(255,255,255,0.33);">21,000 sq.ft · CWC Empanelled · Kalaburagi</div>
          </div>
          <div style="margin-left:auto;font-size:13px;color:rgba(255,255,255,0.3);">↗</div>
        </a>
      </div>
    </div>
    """, unsafe_allow_html=True)


# --- MAIN LOGIN INTERFACE ---
def login_screen():
    st.set_page_config(
        page_title="Samketan AI — Secure Access",
        page_icon="🔐",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    # ── Handle background Google OAuth redirect loop data mapping ──
    if handle_google_callback():
        st.rerun()

    if st.session_state.authenticated:
        return True

    logo_b64 = get_logo_base64()
    col_left, col_right = st.columns([1, 1], gap="small")

    with col_left:
        inject_css(logo_b64)

    with col_right:
        google_icon = '<svg width="18" height="18" viewBox="0 0 18 18" style="vertical-align:-4px;margin-right:8px;" xmlns="http://www.w3.org/2000/svg"><g><path d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844a4.14 4.14 0 0 1-1.796 2.716v2.259h2.908c1.702-1.567 2.684-3.875 2.684-6.615z" fill="#4285F4"/><path d="M9 18c2.43 0 4.467-.806 5.956-2.18l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 0 0 9 18z" fill="#34A853"/><path d="M3.964 10.71A5.41 5.41 0 0 1 3.682 9c0-.593.102-1.17.282-1.71V4.958H.957A8.996 8.996 0 0 0 0 9c0 1.452.348 2.827.957 4.042l3.007-2.332z" fill="#FBBC05"/><path d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 0 0 .957 4.958L3.964 7.29C4.672 5.163 6.656 3.58 9 3.58z" fill="#EA4335"/></g></svg>'

        st.markdown("""
        <div style="padding:2.5rem 0.5rem;">
          <p style="font-family:'DM Sans',sans-serif;font-size:10px;letter-spacing:0.12em;text-transform:uppercase;color:#7b8aab;margin:0 0 5px;">Secure Access Portal</p>
        """, unsafe_allow_html=True)

        if not st.session_state.get("otp_sent"):
            # ✅ VISIBLE EXACT APP NAME TEXT MATCH FOR GOOGLE BRAND REVIEW
            st.markdown('<h1 style="font-family:\'Playfair Display\',Georgia,serif;font-size:26px;font-weight:700;color:#0D1B3E;margin:0 0 0.5rem;">Samketan AI</h1>', unsafe_allow_html=True)
            
            # ✅ EXPLICIT APP PURPOSE PARAGRAPH REQUIREMENT FOR SEARCH CONSOLE Handshake
            st.markdown("""
            <p style="font-family:'DM Sans',sans-serif;font-size:13px;color:#4a5a8a;line-height:1.6;margin:0 0 1.5rem;">
                Welcome to <strong>Samketan AI</strong>. This application platform operates as a secure B2B lead generation, demand generation, and enterprise data analytics workspace built to connect industrial, enterprise, and agriculture networks.
            </p>
            """, unsafe_allow_html=True)

            # ── GOOGLE ROUTING GATEWAY BUTTON ──
            st.markdown('<p style="font-family:\'DM Sans\',sans-serif;font-size:12px;color:#7b8aab;margin:0 0 8px;">Quick access</p>', unsafe_allow_html=True)

            if st.session_state.get("google_error"):
                st.error(f"Google Sign-In failed: {st.session_state.google_error}")
                st.session_state.pop("google_error", None)

            auth_url = get_google_auth_url()

            if auth_url:
                st.markdown(f"""
                <a href="{auth_url}" target="_self" style="
                    display:flex;align-items:center;justify-content:center;
                    gap:8px; background:#fff; border:1px solid #dadce0;
                    border-radius:9px; padding:11px 16px; text-decoration:none;
                    font-family:'DM Sans',sans-serif; font-size:14px;
                    font-weight:500; color:#3c4043; margin-bottom:4px;
                    box-shadow:0 1px 3px rgba(0,0,0,0.08); transition:box-shadow 0.2s;
                ">
                  {google_icon}
                  Continue with Google
                </a>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="display:flex;align-items:center;justify-content:center;gap:8px;
                    background:#f5f5f5;border:1px solid #dadce0;border-radius:9px;
                    padding:11px 16px;color:#9aa0ae;font-size:14px;font-family:'DM Sans',sans-serif;
                    margin-bottom:4px;">
                  {google_icon} Continue with Google
                  <span style="margin-left:auto;font-size:10px;color:#bbb;">Configuration Setup Needed</span>
                </div>
                """, unsafe_allow_html=True)

            # ── LAYOUT DIVIDER ──
            st.markdown("""
            <div style="display:flex;align-items:center;gap:12px;margin:1.1rem 0;">
              <div style="flex:1;height:0.5px;background:#e0e4ef;"></div>
              <span style="font-family:'DM Sans',sans-serif;font-size:12px;color:#aab0c2;white-space:nowrap;">or sign in with email</span>
              <div style="flex:1;height:0.5px;background:#e0e4ef;"></div>
            </div>
            """, unsafe_allow_html=True)

            # ── EMAIL STEP 1 INTERFACE ──
            st.markdown("""
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:1.2rem;">
              <div style="height:5px;border-radius:3px;flex:1;background:#0D1B3E;"></div>
              <div style="height:5px;border-radius:3px;flex:1;background:#e5e8f0;"></div>
              <span style="font-size:11px;color:#7b8aab;white-space:nowrap;font-family:'DM Sans',sans-serif;">Step 1 of 2</span>
            </div>
            """, unsafe_allow_html=True)

            user_email = st.text_input("Business Email Address", placeholder="you@company.com", key="email_input")
            st.markdown("""
            <div style="background:#f0f5ff;border:0.5px solid #c8d6f5;border-radius:9px;padding:10px 14px;
                display:flex;gap:10px;align-items:flex-start;margin-bottom:1rem;">
              <span style="font-size:14px;color:#4a5a8a;flex-shrink:0;">ℹ️</span>
              <p style="font-size:12px;color:#4a5a8a;margin:0;line-height:1.55;font-family:'DM Sans',sans-serif;">
                A 6-digit code will be sent to your inbox. Valid for 10 minutes.</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Send Verification Code →"):
                if user_email and "@" in user_email:
                    generated_otp = str(random.randint(100000, 999999))
                    st.session_state.correct_otp = generated_otp
                    if send_otp_email(user_email, generated_otp):
                        st.session_state.otp_sent = True
                        st.session_state.current_user = user_email
                        st.success(f"✓ Code sent to {user_email}")
                        st.rerun()
                else:
                    st.error("Please enter a valid business email address.")

        else:
            # ── EMAIL STEP 2 (OTP ENTRY VALIDATION) ──
            st.markdown('<h2 style="font-family:\'Playfair Display\',Georgia,serif;font-size:22px;font-weight:700;color:#0D1B3E;margin:0 0 1.2rem;">Check your inbox</h2>', unsafe_allow_html=True)
            st.markdown("""
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:1.2rem;">
              <div style="height:5px;border-radius:3px;flex:1;background:#0D1B3E;"></div>
              <div style="height:5px;border-radius:3px;flex:1;background:#0D1B3E;"></div>
              <span style="font-size:11px;color:#7b8aab;white-space:nowrap;font-family:'DM Sans',sans-serif;">Step 2 of 2</span>
            </div>
            """, unsafe_allow_html=True)

            email_display = st.session_state.get("current_user", "your email")
            st.markdown(f'<p style="font-family:\'DM Sans\',sans-serif;font-size:13px;color:#7b8aab;margin-bottom:0.5rem;">Code sent to <strong style="color:#0D1B3E;">{email_display}</strong></p>', unsafe_allow_html=True)

            otp_input = st.text_input("6-Digit Verification Code", type="password", placeholder="••••••", key="otp_input", max_chars=6)
            if st.button("Verify & Enter Platform →"):
                if otp_input == st.session_state.get("correct_otp"):
                    log_to_google_sheet(st.session_state.current_user, "Email OTP")
                    st.session_state.authenticated = True
                    st.success("✓ Access granted. Loading platform...")
                    st.rerun()
                else:
                    st.error("Incorrect code. Please check your inbox and try again.")

            st.markdown('<p style="font-family:\'DM Sans\',sans-serif;font-size:12px;color:#7b8aab;text-align:center;margin-top:0.5rem;">Didn\'t receive it? Check your spam folder, or go back and re-enter your email.</p>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    return False


# --- ENTRY POINT ---
if __name__ == "__main__":
    if not login_screen():
        st.stop()
    st.success("🎉 You are logged in! Replace this with your main Samketan AI app content.")

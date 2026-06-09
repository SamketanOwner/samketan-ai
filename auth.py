import streamlit as st
import requests
import smtplib
import random
from datetime import datetime
import json
import base64
from pathlib import Path
from email.mime.text import MIMEText

# --- CONFIGURATION ---
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxxkHAi7kn24BChb4zQktRE-u4kPY-sn9L96FLIqw4-czxzms03iCP1eNnPUGrAB_5HxA/exec"
GMAIL_USER = "shgarampalli@gmail.com"
GMAIL_PASS = "hbikssxqyzthscne"

def get_logo_base64():
    logo_path = Path("logo_samketan.png")
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

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

def inject_css(logo_b64=None):
    logo_html = ""
    if logo_b64:
        logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height:52px;width:52px;border-radius:50%;object-fit:contain;background:#fff;padding:4px;" alt="Samketan AI Logo">'
    else:
        logo_html = '<div style="height:52px;width:52px;border-radius:50%;background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.2);display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:700;color:#7FB3FF;font-family:Georgia,serif;">SN</div>'

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


def login_screen():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    logo_b64 = get_logo_base64()
    col_left, col_right = st.columns([1, 1], gap="small")

    with col_left:
        inject_css(logo_b64)

    with col_right:
        st.markdown("""
        <div style="padding:2.5rem 0.5rem;">
          <p style="font-family:'DM Sans',sans-serif;font-size:10px;letter-spacing:0.12em;text-transform:uppercase;color:#7b8aab;margin:0 0 5px;">Secure Access Portal</p>
        """, unsafe_allow_html=True)

        if not st.session_state.get("otp_sent"):
            st.markdown('<h2 style="font-family:\'Playfair Display\',Georgia,serif;font-size:22px;font-weight:700;color:#0D1B3E;margin:0 0 1.2rem;">Sign in to your account</h2>', unsafe_allow_html=True)

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

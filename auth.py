import streamlit as st
import requests
import smtplib
import random
from datetime import datetime
import json
from email.mime.text import MIMEText

# --- CONFIGURATION ---
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxxkHAi7kn24BChb4zQktRE-u4kPY-sn9L96FLIqw4-czxzms03iCP1eNnPUGrAB_5HxA/exec" 
GMAIL_USER = "shgarampalli@gmail.com"  # Enter your Gmail
GMAIL_PASS = "hbikssxqyzthscne" # Enter the 16-digit code from Step 1

def send_otp_email(receiver_email, otp_code):
    try:
        msg = MIMEText(f"Your Samketan Growth Engine verification code is: {otp_code}")
        msg['Subject'] = '🔐 Samketan Access Code'
        msg['From'] = GMAIL_USER
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
        data = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "contact": user_info, "method": method}
        requests.post(SCRIPT_URL, data=json.dumps(data))
    except:
        pass

def login_screen():
    st.title("🔐 Samketan Secure Access")
    
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        user_email = st.text_input("Enter your Business Email to receive a code")

        if st.button("Send Verification Code"):
            if user_email and "@" in user_email:
                # Generate a random 6-digit code
                generated_otp = str(random.randint(100000, 999999))
                st.session_state.correct_otp = generated_otp
                
                # Send the real email
                if send_otp_email(user_email, generated_otp):
                    st.session_state.otp_sent = True
                    st.session_state.current_user = user_email
                    st.success(f"A real code has been sent to {user_email}")
                    st.rerun()
            else:
                st.error("Please enter a valid email address.")

        if st.session_state.get("otp_sent"):
            otp_input = st.text_input("Enter the 6-digit code from your inbox", type="password")
            if st.button("Verify & Enter"):
                if otp_input == st.session_state.get("correct_otp"):
                    log_to_google_sheet(st.session_state.current_user, "Email")
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Wrong code! Please check your email.")
        return False
    return True

import streamlit as st
import requests
from datetime import datetime
import json

# 1. PASTE YOUR WEB APP URL HERE
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxxkHAi7kn24BChb4zQktRE-u4kPY-sn9L96FLIqw4-czxzms03iCP1eNnPUGrAB_5HxA/exec" 

def log_to_google_sheet(user_info, method):
    try:
        # Prepare the data for the Google Sheet row
        data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "contact": user_info,
            "method": method
        }
        # Send the data to the Google Apps Script "Bridge"
        requests.post(SCRIPT_URL, data=json.dumps(data))
    except Exception as e:
        st.error(f"Logging error: {e}")

def login_screen():
    st.title("🔐 Samketan Secure Access")
    
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.info("Verification Required")
        
        method = st.radio("Method:", ["Email", "Phone"])
        user_input = st.text_input(f"Enter {method}")

        if st.button("Send Code"):
            if user_input:
                st.session_state.otp_sent = True
                st.session_state.current_user = user_input
                st.session_state.current_method = method
                st.success("Code sent!")
            else:
                st.error("Please enter details.")

        if st.session_state.get("otp_sent"):
            otp = st.text_input("Enter OTP (123456)", type="password")
            if st.button("Verify"):
                if otp == "123456":
                    # 2. THIS LINE SENDS DATA TO YOUR SHEET
                    log_to_google_sheet(st.session_state.current_user, st.session_state.current_method)
                    
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Wrong code!")
        return False
    return True

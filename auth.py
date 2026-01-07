import streamlit as st

def login_screen():
    st.title("🔐 Samketan Secure Access")
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.info("Verification Required")
        method = st.radio("Method:", ["Email", "Phone"])
        user_input = st.text_input(f"Enter {method}")
        if st.button("Send Code"):
            st.session_state.otp_sent = True
            st.success("Code sent!")
        if st.session_state.get("otp_sent"):
            otp = st.text_input("Enter OTP (123456)", type="password")
            if st.button("Verify"):
                if otp == "123456":
                    st.session_state.authenticated = True
                    st.rerun()
        return False
    return True

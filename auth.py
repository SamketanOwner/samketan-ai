import streamlit as st

def login_screen():
    st.title("🔐 Samketan Secure Access")
    
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.info("Verification Required to Access Growth Engine")
        
        method = st.radio("Choose Verification Method:", ["Email", "Phone (SMS)"])
        user_input = st.text_input(f"Enter your {method}")

        if st.button("Send Verification Code"):
            if user_input:
                st.session_state.otp_sent = True
                st.success(f"A code has been sent to {user_input}")
            else:
                st.error("Please enter your details.")

        if st.session_state.get("otp_sent"):
            otp = st.text_input("Enter 6-Digit OTP (Use 123456)", type="password")
            if st.button("Verify & Open Engine"):
                if otp == "123456":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Wrong code!")
        return False
    return True

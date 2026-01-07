import streamlit as st
import auth  # This connects to the new file you just made

# THIS IS THE GATEKEEPER:
if not auth.login_screen():
    st.stop() # This stops the app here if they haven't logged in
import streamlit as st

def login_screen():
    st.title("🔐 Samketan Secure Access")
    
    # Check if the user is already logged in
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.info("Verification Required to Access Growth Engine")
        
        # 1. Ask for verification method
        method = st.radio("Choose Verification Method:", ["Email", "Phone (SMS)"])
        
        if method == "Email":
            user_input = st.text_input("Enter your Email")
        else:
            user_input = st.text_input("Enter your Phone Number")

        # 2. Simulate sending a code
        if st.button("Send Verification Code"):
            if user_input:
                st.session_state.otp_sent = True
                st.success(f"A 6-digit code has been sent to {user_input}")
            else:
                st.error("Please enter your details.")

        # 3. Enter the code to unlock
        if st.session_state.get("otp_sent"):
            otp = st.text_input("Enter 6-Digit OTP (Use 123456 for testing)", type="password")
            if st.button("Verify & Open Engine"):
                if otp == "123456": # You can change this test code
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Wrong code! Try again.")
        
        return False # This keeps the door locked
    return True # This opens the door

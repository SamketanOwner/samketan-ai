import streamlit as st
import firebase_admin
from firebase_admin import auth, credentials
import google.generativeai as genai
import json

# --- 1. INITIALIZE FIREBASE (Only once) ---
if not firebase_admin._apps:
    fb_creds = dict(st.secrets["FIREBASE_SERVICE_ACCOUNT"])
    cred = credentials.Certificate(fb_creds)
    firebase_admin.initialize_app(cred)

# --- 2. THE "GATEKEEPER" (Session State) ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# --- 3. LOGIN SCREEN (The Only Thing visible if NOT logged in) ---
if not st.session_state['authenticated']:
    st.title("🔐 Samketan Login")
    email = st.text_input("Business Email")
    password = st.text_input("Password", type="password")
    
    if st.button("Sign In"):
        try:
            # Check Firebase for genuine user
            user = auth.get_user_by_email(email)
            st.session_state['authenticated'] = True
            st.session_state['user_email'] = email
            st.rerun() # Refresh to show the engine
        except:
            st.error("Invalid user. Please sign up.")
            
    if st.button("Sign Up"):
        try:
            auth.create_user(email=email, password=password)
            st.success("Account created! Now click Sign In.")
        except Exception as e:
            st.error(f"Error: {e}")
            
    st.stop() # CRITICAL: This stops the search engine from loading!

# --- 4. YOUR EXISTING PATTERN (Visible ONLY after login) ---
st.header("🚀 Samketan Business Growth Engine")
st.sidebar.success(f"Verified: {st.session_state['user_email']}")

if st.sidebar.button("Logout"):
    st.session_state['authenticated'] = False
    st.rerun()

# --- PASTE YOUR 4 QUESTIONS & TABLE CODE BELOW THIS LINE ---
# (Keep all your existing logic for Lead Gen here)

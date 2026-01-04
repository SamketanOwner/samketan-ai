import streamlit as st
import requests

# 1. SETUP PAGE
st.set_page_config(page_title="Samketan", page_icon="🚀", layout="centered")

# 2. LOGIN SYSTEM
st.sidebar.header("Login")
password = st.sidebar.text_input("Enter Password", type="password")

if password != "Samketan2026":
    st.warning("🔒 Please enter the password to unlock.")
    st.stop()

# 3. THE APP INTERFACE
st.title("🚀 Samketan Agent")
st.write("Welcome to your Lead Generation App")

# Inputs
domain = st.selectbox("Select Domain", ["Software", "Warehouse", "Art", "Food", "Export"])
region = st.text_input("Enter Region", "Gulbarga")

# Button
if st.button("Find Leads"):
    st.info(f"Searching for {domain} leads in {region}...")
    # We will connect the Brain (n8n) here later.

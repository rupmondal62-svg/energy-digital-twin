import streamlit as st
import pandas as pd
import pydeck as pdk
import random
import requests
import os
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from streamlit_autorefresh import st_autorefresh

# ---------------- CONFIG ---------------- #
st.set_page_config(layout="wide")

# ---------------- LOAD LOGIN CONFIG ---------------- #
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# ---------------- AUTH ---------------- #
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# SAFE LOGIN
try:
    name, authentication_status, username = authenticator.login("Login", "main")
except TypeError:
    try:
        name, authentication_status, username = authenticator.login(location="main")
    except:
        name, authentication_status, username = authenticator.login()

# ---------------- LOGIN CONTROL ---------------- #
if authentication_status is False:
    st.error("❌ Incorrect Username/Password")
    st.stop()

elif authentication_status is None:
    st.warning("⚠️ Please enter your login credentials")
    st.stop()

# ---------------- AFTER LOGIN ---------------- #
authenticator.logout("Logout", "sidebar")
st.sidebar.success(f"👤 {name}")

# ---------------- HERO ---------------- #
st.markdown("""
<div style="
    background: linear-gradient(135deg,#0f172a,#1e293b);
    padding:40px;
    border-radius:20px;
    color:white;
    text-align:left;
">
    <h1>⚡ EnerSight AI</h1>
    <h3>Global Energy Intelligence Platform</h3>
    <p>Track Oil, LPG & Energy Supply Chains in Real-Time</p>
</div>
""", unsafe_allow_html=True)

# ---------------- FEATURE CARDS ---------------- #
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="news-card">
    <h4>🚢 Ship Tracking</h4>
    Real-time oil & LPG vessel monitoring
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="news-card">
    <h4>📊 AI Intelligence</h4>
    Predict supply chain disruptions
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="news-card">
    <h4>🌍 Global Data</h4>
    Energy insights across regions
    </div>
    """, unsafe_allow_html=True)

# ---------------- GLOBAL ENERGY VISUAL SECTION ---------------- #
st.markdown("## 🌍 Global Energy Movement")

st.markdown("""
Track global movement of Oil, LPG and strategic energy resources across key maritime routes.
""")

# ---------------- INDIA ENERGY TRUST SECTION ---------------- #
st.markdown("## 🇮🇳 Energy Infrastructure Intelligence")

st.markdown("""
Track and analyze energy logistics including:

- Oil Tankers  
- LPG Distribution  
- Government Energy Networks  
- Strategic Supply Chains  
""")

# ---------------- ROLE SYSTEM ---------------- #
def check_paid_user(username):
    try:
        with open("paid_users.txt", "r") as f:
            users = f.read().splitlines()
            return username in users
    except:
        return False

if check_paid_user(username):
    user_role = "pro"
else:
    user_role = config['credentials']['usernames'][username].get('role', 'free')

# ---------------- UI ---------------- #
st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.main {
    background: #f8fafc;
    color: #0f172a;
}

section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e2e8f0;
}

section[data-testid="stSidebar"] * {
    color: #0f172a !important;
}

.news-card {
    padding: 16px;
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    margin-bottom: 12px;
}

.news-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    transition: 0.3s;
}

.qr-box {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 15px;
    text-align: center;
}

</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ---------------- #
with st.sidebar:
    st.title("⚡ EnerSight AI")
    page = st.radio("", ["Dashboard", "Live Map", "News Intelligence", "Data Table"])

    if user_role != "pro":
        st.markdown("## 🚀 Upgrade to PRO")

        st.markdown('<div class="qr-box">', unsafe_allow_html=True)
        st.image("qr.png", width=220)
        st.markdown("Scan QR to upgrade")
        st.markdown('</div>', unsafe_allow_html=True)

# ---------------- HEADER ---------------- #
st.markdown("# 🌍 EnerSight AI")
st.markdown("### ⚡ Intelligence Platform")

st_autorefresh(interval=10000, key="refresh")

# ---------------- DATA ---------------- #
def fetch_news():
    API_KEY = os.getenv("NEWS_API_KEY")
    if not API_KEY:
        return []
    try:
        res = requests.get(f"https://newsapi.org/v2/everything?q=energy&apiKey={API_KEY}")
        data = res.json()
        return data.get("articles", [])[:5]
    except:
        return []

def generate_ships():
    return pd.DataFrame([
        {"lat": 25, "lon": 60},
        {"lat": 18, "lon": 70}
    ])

df = generate_ships()
news = fetch_news()

# ---------------- PAGES ---------------- #
if page == "Dashboard":
    st.markdown("## 📊 Overview")

elif page == "Live Map":
    st.markdown("## 🌍 Live Map")

elif page == "News Intelligence":
    st.markdown("## 📰 Energy News")

elif page == "Data Table":
    st.dataframe(df)

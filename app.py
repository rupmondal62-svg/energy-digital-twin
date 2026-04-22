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
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.stButton>button {
    border-radius: 10px;
    background: linear-gradient(135deg, #6366f1, #4f46e5);
    color: white;
    border: none;
    padding: 8px 16px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ---------------- #
with st.sidebar:
    st.title("⚡ EnerSight AI")
    st.markdown("### Navigation")

    page = st.radio("", ["Dashboard", "Live Map", "News Intelligence", "Data Table"])

    if user_role != "pro":
        st.markdown("## 🚀 Upgrade to PRO")

        st.markdown("### 💳 Scan & Pay")

        st.markdown('<div class="qr-box">', unsafe_allow_html=True)
        st.image("qr.png", width=220)
        st.markdown("**Scan QR to upgrade**")
        st.markdown("Pay ₹199 to unlock PRO 🚀")
        st.markdown('</div>', unsafe_allow_html=True)

        utr = st.text_input("Enter UTR / Transaction ID")

        if st.button("Verify Payment"):
            if utr:
                with open("paid_users.txt", "a") as f:
                    f.write(username + "\n")
                st.success("Payment recorded! Refresh page in 5 seconds.")
            else:
                st.error("Please enter transaction ID")

        st.markdown("### 💎 PRO Benefits")
        st.markdown("""
        - Unlimited ship tracking  
        - Full news intelligence  
        - Advanced analytics  
        - Priority updates  
        """)

# ---------------- HEADER ---------------- #
st.markdown("# 🌍 EnerSight AI")
st.markdown("### ⚡ Intelligence Platform")

st_autorefresh(interval=10000, key="refresh")

# ---------------- DATA ---------------- #
def fetch_news():
    API_KEY = os.getenv("NEWS_API_KEY")
    if not API_KEY:
        return []
    url = f"https://newsapi.org/v2/everything?q=energy&apiKey={API_KEY}"
    try:
        res = requests.get(url)
        data = res.json()
        return [{"title": a["title"], "source": a["source"]["name"]} for a in data.get("articles", [])[:5]]
    except:
        return []

def generate_ships():
    base = [(26,56),(25,57),(24,60),(22,63),(20,66)]
    ships = []
    for lat, lon in base:
        ships.append({
            "lat": lat,
            "lon": lon,
            "type": random.choice(["Oil Tanker","LPG Carrier"])
        })
    return pd.DataFrame(ships)

df = generate_ships()
news = fetch_news()

# ---------------- PAGES ---------------- #
if page == "Dashboard":

    st.markdown("## 📊 Overview")

    col1, col2, col3 = st.columns(3)

    ships_to_show = df if user_role == "pro" else df.head(5)
    col1.metric("🚢 Ships", len(ships_to_show))

    col2.metric("⚠ Risk", "Medium")
    col3.metric("📡 Status", "LIVE")

    if user_role == "free":
        st.warning("🔒 Upgrade to PRO for full access")

elif page == "Live Map":

    st.markdown("## 🌍 Live Map")

    map_df = df if user_role == "pro" else df.head(5)

    st.pydeck_chart(pdk.Deck(
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=map_df,
                get_position='[lon, lat]',
                get_radius=200000,
                get_color='[255, 100, 0]'
            )
        ],
        initial_view_state=pdk.ViewState(
            latitude=22,
            longitude=65,
            zoom=3
        )
    ))

elif page == "News Intelligence":

    st.markdown("## 📰 Energy News")

    if not news:
        st.info("No news available")
    else:
        news_to_show = news if user_role == "pro" else news[:3]

        for article in news_to_show:
            st.markdown(f"""
            <div class="news-card">
            <b>{article['title']}</b><br>
            {article['source']}
            </div>
            """, unsafe_allow_html=True)

elif page == "Data Table":

    st.markdown("## 📋 Data")
    st.dataframe(df)

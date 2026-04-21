import streamlit as st
import pandas as pd
import pydeck as pdk
import math
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

name, authentication_status, username = authenticator.login("🔐 Login", "main")

# ---------------- LOGIN CONTROL ---------------- #
if authentication_status == False:
    st.error("❌ Incorrect Username/Password")
    st.stop()

elif authentication_status == None:
    st.warning("⚠️ Please enter your credentials")
    st.stop()

# ---------------- AFTER LOGIN ---------------- #
authenticator.logout("Logout", "sidebar")
st.sidebar.success(f"👤 {name}")

# ---------------- PREMIUM CSS ---------------- #
st.markdown("""
<style>
.main {
    background: linear-gradient(135deg, #0f172a, #020617);
    color: #e2e8f0;
}
section[data-testid="stSidebar"] {
    background: #020617;
}
h1, h2, h3 {
    color: #f1f5f9;
}
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(14px);
    border-radius: 16px;
    padding: 20px;
}
.news-card {
    padding: 14px;
    background: rgba(255,255,255,0.07);
    border-radius: 12px;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ---------------- #
with st.sidebar:
    st.title("⚡ EnerSight AI")
    st.markdown("### Navigation")
    page = st.radio("", ["Dashboard", "Live Map", "News Intelligence", "Data Table"])

# ---------------- HEADER ---------------- #
st.markdown("# 🌍 EnerSight AI")
st.markdown("### ⚡ Intelligence Layer for Global Energy Supply Chains")

st_autorefresh(interval=10000, key="datarefresh")

# ---------------- YOUR ORIGINAL LOGIC (UNCHANGED) ---------------- #

def fetch_news():
    API_KEY = os.getenv("NEWS_API_KEY")
    url = f"https://newsapi.org/v2/everything?q=energy&apiKey={API_KEY}"
    try:
        res = requests.get(url)
        data = res.json()
        return [{"title": a["title"], "source": a["source"]["name"]} for a in data["articles"][:5]]
    except:
        return []

def generate_ships():
    base = [(26,56),(25,57),(24,60),(22,63),(20,66)]
    ships = []
    for i,(lat,lon) in enumerate(base):
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
    col1.metric("🚢 Ships", len(df))
    col2.metric("⚠ Risk", "Medium")
    col3.metric("📡 Status", "LIVE")

elif page == "Live Map":

    st.markdown("## 🌍 Live Map")

    st.pydeck_chart(pdk.Deck(
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=df,
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

    for article in news:
        st.markdown(f"""
        <div class="news-card">
        <b>{article['title']}</b><br>
        {article['source']}
        </div>
        """, unsafe_allow_html=True)

elif page == "Data Table":

    st.markdown("## 📋 Data Table")
    st.dataframe(df)
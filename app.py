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
import smtplib

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

try:
    name, authentication_status, username = authenticator.login("Login", "main")
except TypeError:
    try:
        name, authentication_status, username = authenticator.login(location="main")
    except:
        name, authentication_status, username = authenticator.login()

if authentication_status is False:
    st.error("❌ Incorrect Username/Password")
    st.stop()

elif authentication_status is None:
    st.warning("⚠️ Please enter your login credentials")
    st.stop()

authenticator.logout("Logout", "sidebar")
st.sidebar.success(f"👤 {name}")

# ---------------- FUNCTIONS (FIXED POSITION) ---------------- #

def get_oil_price():
    try:
        url = "https://api.oilpriceapi.com/v1/prices/latest"
        headers = {"Authorization": "Token YOUR_API_KEY"}
        res = requests.get(url, headers=headers)
        data = res.json()
        return float(data['data']['price'])
    except:
        return 82.5

def get_price_history():
    try:
        API_KEY = "YOUR_API_KEY"
        url = f"https://www.alphavantage.co/query?function=WTI&interval=daily&apikey={API_KEY}"
        res = requests.get(url)
        data = res.json()

        df = pd.DataFrame(data["data"])
        df["date"] = pd.to_datetime(df["date"])
        df["value"] = df["value"].astype(float)
        return df.sort_values("date")
    except:
        return None

def send_email_alert(message):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login("your_email@gmail.com", "APP_PASSWORD")
        server.sendmail("your_email@gmail.com", "client@email.com", message)
        server.quit()
    except Exception as e:
        print("Email error:", e)

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

def fetch_news():
    API_KEY = os.getenv("ALPHA_API_KEY")
    if not API_KEY:
        return []
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=USO&apikey={API_KEY}"
    try:
        res = requests.get(url)
        data = res.json()
        return [{"title": "Market Update", "source": "Alpha"}]
    except:
        return []

# ---------------- DATA ---------------- #
df = generate_ships()
news = fetch_news()

# ---------------- ROLE SYSTEM ---------------- #
def check_paid_user(username):
    try:
        with open("paid_users.txt", "r") as f:
            return username in f.read().splitlines()
    except:
        return False

user_role = "pro" if check_paid_user(username) else config['credentials']['usernames'][username].get('role', 'free')

# ---------------- SIDEBAR ---------------- #
with st.sidebar:
    st.title("⚡ EnerSight AI")
    page = st.radio("", ["Dashboard", "Live Map", "News Intelligence", "Data Table", "Trader Intelligence"])

# ---------------- HEADER ---------------- #
st.markdown("# 🌍 EnerSight AI")
st.markdown("### ⚡ Intelligence Platform")

st_autorefresh(interval=10000, key="refresh")

# ---------------- PAGES ---------------- #

if page == "Dashboard":
    st.markdown("## 📊 Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("🚢 Ships", len(df))
    col2.metric("⚠ Risk", "Medium")
    col3.metric("📡 Status", "LIVE")

elif page == "Live Map":
    st.markdown("## 🌍 Live Map")

elif page == "News Intelligence":
    st.markdown("## 📰 Energy News")

elif page == "Data Table":
    st.markdown("## 📋 Data")
    st.dataframe(df)

elif page == "Trader Intelligence":

    if user_role == "free":
        st.warning("🔒 Trader Intelligence is a PRO feature")
        st.stop()

    st.markdown("# 📈 Trader Intelligence")

    oil_price = get_oil_price()

    # ---------------- SIGNAL ---------------- #
    st.markdown("## 📊 Market Signal")

    if oil_price > 85:
        st.error("📈 BULLISH — Prices rising")
    elif oil_price < 75:
        st.success("📉 BEARISH — Prices falling")
    else:
        st.warning("⚖ SIDEWAYS")

    st.markdown("---")

    # ---------------- CHART ---------------- #
    history = get_price_history()
    if history is not None:
        st.line_chart(history.set_index("date")["value"])

    # ---------------- DELAY ---------------- #
    weather = random.choice(["Calm", "Rough"])
    congestion = random.choice(["Low", "High"])

    delay = 0
    if weather == "Rough":
        delay += random.randint(10, 30)
    if congestion == "High":
        delay += random.randint(10, 25)

    st.metric("Weather", weather)
    st.metric("Congestion", congestion)

    # ---------------- DECISION ---------------- #
    st.markdown("## 🧠 Trading Decision")

    if oil_price > 85 and delay > 20:
        st.error("🔥 STRONG BUY")
    elif oil_price < 75 and delay < 10:
        st.success("💧 SELL")
    else:
        st.warning("⚖ HOLD")

    # ---------------- ALERTS ---------------- #
    st.markdown("## 🔔 Market Alerts")

    alerts = []
    if oil_price > 90:
        alerts.append("🚨 Oil spike")
    if delay > 30:
        alerts.append("🚨 Delay risk")

    if alerts:
        for a in alerts:
            st.error(a)
    else:
        st.success("No alerts")

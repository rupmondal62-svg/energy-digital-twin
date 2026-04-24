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
import time

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

# ---------------- FUNCTIONS ---------------- #

def get_intraday_price(symbol="USO"):
    API_KEY = os.getenv("ALPHA_API_KEY")

    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={API_KEY}"

    try:
        res = requests.get(url)
        data = res.json()
        ts = data["Time Series (5min)"]

        df = pd.DataFrame([
            {"date": k, "value": float(v["4. close"])}
            for k, v in ts.items()
        ])

        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")

        return df
    except:
        return None

def get_oil_price():
    try:
        url = "https://api.oilpriceapi.com/v1/prices/latest"
        headers = {"Authorization": "Token YOUR_API_KEY"}
        res = requests.get(url, headers=headers)
        data = res.json()
        return float(data['data']['price'])
    except:
        return 82.5

def send_email_alert(message):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login("your_email@gmail.com", "APP_PASSWORD")
        server.sendmail("your_email@gmail.com", "client@email.com", message)
        server.quit()
    except:
        pass

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

# ---------------- DATA ---------------- #
df = generate_ships()

# ---------------- ROLE ---------------- #
def check_paid_user(username):
    try:
        with open("paid_users.txt", "r") as f:
            return username in f.read().splitlines()
    except:
        return False

user_role = "pro" if check_paid_user(username) else "free"

# ---------------- SIDEBAR ---------------- #
with st.sidebar:
    st.title("⚡ EnerSight AI")
    page = st.radio("", ["Dashboard", "Live Map", "Trader Intelligence"])

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

elif page == "Trader Intelligence":

    oil_price = get_oil_price()

    # SIGNAL
    st.markdown("## 📊 Market Signal")
    if oil_price > 85:
        st.error("📈 BULLISH")
    elif oil_price < 75:
        st.success("📉 BEARISH")
    else:
        st.warning("⚖ SIDEWAYS")

    st.markdown("---")

    # CHART
    history = get_intraday_price("USO")

    if history is not None:
        history["MA"] = history["value"].rolling(5).mean()

        st.line_chart(history.set_index("date")[["value", "MA"]])

        latest = history["value"].iloc[-1]
        previous = history["value"].iloc[-5]

        st.metric("Current Price", round(latest, 2))

        if latest > previous:
            st.success("📈 Uptrend")
        elif latest < previous:
            st.error("📉 Downtrend")
        else:
            st.warning("⚖ Sideways")

    # DELAY
    weather = random.choice(["Calm", "Rough"])
    congestion = random.choice(["Low", "High"])

    delay = 0
    if weather == "Rough":
        delay += random.randint(10, 30)
    if congestion == "High":
        delay += random.randint(10, 25)

    st.metric("Weather", weather)
    st.metric("Congestion", congestion)

    # ALERTS
    alerts = []

    if oil_price > 90:
        alerts.append("🚨 Oil breakout")

    if delay > 30:
        alerts.append("🚢 Delay risk")

    if alerts:
        for a in alerts:
            st.error(a)
    else:
        st.success("No alerts")

    # EMAIL COOLDOWN
    if "last_alert_time" not in st.session_state:
        st.session_state.last_alert_time = 0

    current_time = time.time()

    if alerts and current_time - st.session_state.last_alert_time > 300:
        send_email_alert("\n".join(alerts))
        st.session_state.last_alert_time = current_time
        st.success("📧 Email sent")

    # DECISION
    st.markdown("## 🧠 Decision")

    if oil_price > 85 and delay > 20:
        st.error("🔥 STRONG BUY")
    elif oil_price < 75 and delay < 10:
        st.success("💧 SELL")
    else:
        st.warning("⚖ HOLD")

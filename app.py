import streamlit as st
import pandas as pd
import pydeck as pdk
import random
import requests
import os
import yaml
import time
import smtplib
import plotly.graph_objects as go
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from streamlit_autorefresh import st_autorefresh


# ================= REAL-TIME API FUNCTION ================= #

def get_realtime_price(symbol="USO"):
    API_KEY = st.secrets["TWELVE_API_KEY"]

    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=5min&outputsize=100&apikey={API_KEY}"

    try:
        res = requests.get(url)
        data = res.json()

        if "values" not in data:
            st.write("API RESPONSE:", data)
            return None

        df = pd.DataFrame(data["values"])

        df["datetime"] = pd.to_datetime(df["datetime"])
        df = df.sort_values("datetime")

        for col in ["open", "high", "low", "close"]:
            df[col] = df[col].astype(float)

        return df

    except Exception as e:
        st.write("ERROR:", e)
        return None
# ---------------- CONFIG ---------------- #
st.set_page_config(layout="wide")

# ---------------- LOAD CONFIG ---------------- #
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# ---------------- AUTH ---------------- #
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status is False:
    st.error("❌ Incorrect Username/Password")
    st.stop()

elif authentication_status is None:
    st.warning("⚠️ Please login")
    st.stop()

authenticator.logout("Logout", "sidebar")
st.sidebar.success(f"👤 {name}")

# ---------------- FUNCTIONS ---------------- #

def get_oil_price():
    try:
        return get_realtime_price("CL1")["close"].iloc[-1]
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


def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = -delta.clip(upper=0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

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

# ---------------- DASHBOARD ---------------- #
if page == "Dashboard":
    col1, col2, col3 = st.columns(3)
    col1.metric("🚢 Ships", len(df))
    col2.metric("⚠ Risk", "Medium")
    col3.metric("📡 Status", "LIVE")

# ---------------- MAP ---------------- #
elif page == "Live Map":
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
        initial_view_state=pdk.ViewState(latitude=22, longitude=65, zoom=3)
    ))

# ---------------- TRADER ---------------- #
elif page == "Trader Intelligence":

    if user_role == "free":
        st.warning("🔒 PRO Feature")
        st.stop()

    st.markdown("## 📊 Market Signal")
    st.markdown("### 🛢 Select Market")

    market = st.selectbox(
    "Choose asset",
    ["Crude Oil (WTI)", "Brent Oil", "Natural Gas"]
    )
    if market == "Crude Oil (WTI)":
        symbol = "WTI"
    elif market == "Brent Oil":
        symbol = "WTI"   # fallback
        st.warning("⚠ Brent not available in free API — showing WTI proxy")
    elif market == "Natural Gas":
        symbol = "NG"

    history = get_realtime_price(symbol)

    if history is None:
        st.error("⚠ API failed or limit reached")
        st.stop()

    latest = history["close"].iloc[-1]

    # ---------------- CANDLESTICK ---------------- #
    fig = go.Figure(data=[go.Candlestick(
        x=history['datetime'],
        open=history['open'],
        high=history['high'],
        low=history['low'],
        close=history['close']
    )])

    st.plotly_chart(fig, use_container_width=True)

    # ---------------- INDICATORS ---------------- #
    history["MA"] = history["close"].rolling(5).mean()
    history["RSI"] = calculate_rsi(history["close"])

    st.line_chart(history.set_index("datetime")[["close", "MA"]])

    st.metric("Current Price", round(latest, 2))
    st.metric("RSI", round(history["RSI"].iloc[-1], 2))

    # ---------------- SIGNAL LOGIC ---------------- #
    signal = "HOLD"

    if latest > history["MA"].iloc[-1] and history["RSI"].iloc[-1] < 70:
        signal = "BUY"
        st.success("📈 BUY SIGNAL")

    elif latest < history["MA"].iloc[-1] and history["RSI"].iloc[-1] > 30:
        signal = "SELL"
        st.error("📉 SELL SIGNAL")

    else:
        st.warning("⚖ HOLD")

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

    # ---------------- ALERT ---------------- #
    alerts = []

    if latest > 90:
        alerts.append("🚨 Price breakout")

    if delay > 30:
        alerts.append("🚢 Delay risk")

    if alerts:
        for a in alerts:
            st.error(a)
    else:
        st.success("No alerts")

    # ---------------- EMAIL COOLDOWN ---------------- #
    if "last_alert_time" not in st.session_state:
        st.session_state.last_alert_time = 0

    now = time.time()

    if alerts and now - st.session_state.last_alert_time > 300:
        send_email_alert("\n".join(alerts))
        st.session_state.last_alert_time = now
        st.success("📧 Alert Sent")

    # ---------------- DECISION ---------------- #
    st.markdown("## 🧠 Final Decision")

    if signal == "BUY" and delay > 20:
        st.error("🔥 STRONG BUY")
    elif signal == "SELL":
        st.success("💧 SELL")
    else:
        st.warning("⚖ WAIT")

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
st.markdown("""
<style>

/* -------- BACKGROUND -------- */
.stApp {
    background: radial-gradient(circle at top left, #0f172a, #020617);
    color: white;
}

/* -------- HERO -------- */
.hero {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    padding: 40px;
    border-radius: 25px;
    margin-bottom: 30px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.6);
    animation: fadeIn 1s ease-in-out;
}

/* -------- GLASS CARDS -------- */
.card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(20px);
    padding: 25px;
    border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.08);
    transition: 0.3s;
}
.card:hover {
    transform: translateY(-6px);
    box-shadow: 0 20px 50px rgba(0,0,0,0.6);
}

/* -------- METRICS -------- */
.metric {
    font-size: 32px;
    font-weight: bold;
    background: linear-gradient(90deg, #22c55e, #4ade80);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* -------- GLOW TEXT -------- */
.glow {
    text-shadow: 0 0 10px rgba(34,197,94,0.6);
}

/* -------- SIDEBAR -------- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020617, #0f172a);
}

/* -------- ANIMATION -------- */
@keyframes fadeIn {
    from {opacity:0; transform: translateY(20px);}
    to {opacity:1; transform: translateY(0);}
}

/* -------- SCROLLBAR -------- */
::-webkit-scrollbar {
    width: 6px;
}
::-webkit-scrollbar-thumb {
    background: #22c55e;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
/* MAIN BACKGROUND */
body {
    background: #f5f7fb;
}

/* APP CONTAINER */
[data-testid="stAppViewContainer"] {
    background: #f5f7fb;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: #ffffff;
}

/* CARDS */
.card {
    background: #ffffff;
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.05);
    transition: 0.3s;
}

.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

/* HERO */
.hero {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    padding: 40px;
    border-radius: 20px;
    color: white;
}

/* TEXT */
h1, h2, h3 {
    color: #111827;
}
</style>
""", unsafe_allow_html=True)
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
    st_autorefresh(interval=10000, key="refresh")


# ---------------- DASHBOARD ---------------- #
if page == "Dashboard":

    # HERO
    st.markdown("""
    <div class="hero">
        <h1 class="glow">⚡ EnerSight AI</h1>
        <p style="color:#94a3b8;">
            Real-time Energy Intelligence & Trading Platform
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("## 📊 Overview")

    # INFOGRAPHICS (✅ INSIDE IF)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="card">
            <h4>🚢 Active Ships</h4>
            <p class="metric">{len(df)}</p>
            <p style="color:#94a3b8;">Live tracking</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card">
            <h4>⚠ Risk Level</h4>
            <p class="metric" style="color:#f59e0b;">Medium</p>
            <p style="color:#94a3b8;">Supply tension</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="card">
            <h4>📡 System Status</h4>
            <p class="metric">LIVE</p>
            <p style="color:#94a3b8;">Streaming data</p>
        </div>
        """, unsafe_allow_html=True)

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
    st.markdown("""
<div style="
    background: linear-gradient(135deg, #111827, #1f2937);
    padding: 30px;
    border-radius: 20px;
    margin-bottom: 25px;
">
    <h1>📈 Trading Intelligence</h1>
    <p style="color:#9CA3AF;">
        AI-powered oil & gas signals
    </p>
</div>
""", unsafe_allow_html=True)

    st.markdown("## 📊 Market Signal")

    if user_role == "free":
        st.markdown("""
        <div class="card">
            <h2>🔒 Premium Feature</h2>
            <p>Upgrade to Pro to access advanced trading intelligence, real-time signals, and AI predictions.</p>
            <hr>
            <p style="color:#22C55E; font-weight:bold;">🚀 Upgrade now to unlock full power</p>
        </div>
        """, unsafe_allow_html=True)

        st.stop()

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
    fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white"),
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=False),
    height=500
)

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

    if signal == "BUY":
        st.markdown('<div class="card">📈 <b style="color:#22c55e;">BUY SIGNAL</b></div>', unsafe_allow_html=True)

    elif signal == "SELL":
        st.markdown('<div class="card">📉 <b style="color:#ef4444;">SELL SIGNAL</b></div>', unsafe_allow_html=True)

    else:
        st.markdown('<div class="card">⚖ HOLD</div>', unsafe_allow_html=True)


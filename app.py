import streamlit as st
import pandas as pd
import pydeck as pdk
import math
import random
import requests
import os
from streamlit_autorefresh import st_autorefresh

# ---------------- CONFIG ---------------- #
st.set_page_config(layout="wide")

# ---------------- PREMIUM CSS ---------------- #
st.markdown("""
<style>

/* ---------- GLOBAL BACKGROUND ---------- */
.main {
    background: linear-gradient(135deg, #0f172a, #020617);
    color: #e2e8f0;
}

/* ---------- SIDEBAR ---------- */
section[data-testid="stSidebar"] {
    background: #020617;
    border-right: 1px solid rgba(255,255,255,0.05);
}

/* ---------- HEADINGS ---------- */
h1, h2, h3 {
    color: #f1f5f9;
    font-weight: 600;
}

/* ---------- METRIC CARDS (GLASS FIXED) ---------- */
[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(14px);
    border-radius: 16px;
    padding: 20px;
    border: 1px solid rgba(255,255,255,0.12);
    box-shadow: 0 10px 40px rgba(0,0,0,0.5);
}

/* TEXT VISIBILITY FIX */
[data-testid="stMetric"] label {
    color: #94a3b8 !important;
}
[data-testid="stMetric"] div {
    color: #ffffff !important;
    font-weight: 600;
}

/* ---------- NEWS CARDS (FIXED) ---------- */
.news-card {
    padding: 14px;
    margin-bottom: 12px;
    background: rgba(255,255,255,0.07);
    backdrop-filter: blur(12px);
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.1);
    transition: 0.2s ease;
}
.news-card:hover {
    background: rgba(255,255,255,0.1);
}

/* ---------- ALERT ---------- */
.stAlert {
    border-radius: 12px;
}

/* ---------- SPACING ---------- */
.block-container {
    padding: 2rem;
}

small {
    color: #94a3b8;
}

</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ---------------- #
with st.sidebar:
    st.title("⚡ EnerSight AI")
    st.markdown("### Navigation")
    page = st.radio("", ["Dashboard", "Live Map", "News Intelligence", "Data Table"])
    st.markdown("---")
    st.caption("v1 • Energy Intelligence System")

# ---------------- HERO ---------------- #
st.markdown("# 🌍 EnerSight AI\n### ⚡ Intelligence Layer for Global Energy Supply Chains")
st.caption("🚀 Built for real-world energy decision making")

colA, colB, colC = st.columns([2,1,1])

colA.success("🚀 Real-time monitoring • AI risk detection • Supply prediction")
colB.metric("⚡ Status", "LIVE")
colC.metric("🧠 AI Engine", "ACTIVE")

st.caption("🔄 Auto-refreshing every 10 seconds")
st_autorefresh(interval=10000, key="datarefresh")

st.divider()

# ---------------- NEWS FETCH ---------------- #
def fetch_news():
    API_KEY = os.getenv("NEWS_API_KEY")
    url = f"https://newsapi.org/v2/everything?q=oil+OR+lpg+OR+energy+crisis+OR+strait+of+hormuz&sortBy=publishedAt&language=en&domains=bbc.co.uk,reuters.com,aljazeera.com,bloomberg.com,cnn.com&apiKey={API_KEY}"

    try:
        res = requests.get(url)
        data = res.json()

        if data.get("status") != "ok":
            return []

        return [{"title": a["title"], "source": a["source"]["name"]} for a in data["articles"][:5]]

    except:
        return []

# ---------------- NLP ---------------- #
def analyze_news_risk(headlines):
    weights = {"war":3,"attack":3,"blockade":4,"conflict":2,"sanction":2,"tension":1,"disruption":2}
    score = 0

    for h in headlines:
        text = h["title"].lower()
        for word, w in weights.items():
            if word in text:
                score += w

    return score

# ---------------- REGION AI ---------------- #
def detect_region_risk(headlines):
    flags = {"hormuz": False, "arabian_sea": False}

    for h in headlines:
        t = h["title"].lower()

        if any(w in t for w in ["iran","hormuz","gulf","middle east"]):
            flags["hormuz"] = True

        if any(w in t for w in ["cyclone","storm","arabian sea"]):
            flags["arabian_sea"] = True

    return flags

# ---------------- SHIP DATA ---------------- #
def generate_ships():
    base = [(26,56),(25,57),(24,60),(22,63),(20,66),(18,68),(16,70),(15,72)]
    ships = []

    for i,(lat,lon) in enumerate(base):
        ships.append({
            "lat": lat - random.uniform(0.1,0.5),
            "lon": lon + random.uniform(0.2,0.6),
            "type": random.choice(["Oil Tanker","LPG Carrier"]),
            "name": f"Vessel_{i+1}"
        })

    return pd.DataFrame(ships)

df = generate_ships()

# ---------------- FILTER ---------------- #
ship_type = st.selectbox("Filter Shipment Type", ["All","Oil Tanker","LPG Carrier"])
event = st.selectbox("🌍 Global Scenario", [
    "Normal Conditions",
    "Hormuz Blockade",
    "Middle East Conflict",
    "Cyclone in Arabian Sea"
])

if ship_type != "All":
    df = df[df["type"] == ship_type]

# ---------------- NEWS PROCESS ---------------- #
headlines = fetch_news()

if not headlines:
    st.warning("⚠️ Using fallback news")
    headlines = [
        {"title":"Oil market stable globally","source":"Fallback"},
        {"title":"Shipping routes normal","source":"Fallback"}
    ]

headlines = [h for h in headlines if any(k in h["title"].lower() for k in ["oil","energy","lpg","iran","hormuz","shipping"])]

news_risk = analyze_news_risk(headlines)
region_flags = detect_region_risk(headlines)

# ---------------- RISK ENGINE ---------------- #
def get_risk(lat, lon, event, region):
    base = "LOW"

    if 24<=lat<=28 and 54<=lon<=60:
        base="HIGH"
    elif 15<=lat<=25 and 60<=lon<=70:
        base="MEDIUM"

    if event=="Hormuz Blockade" and 24<=lat<=28:
        return "HIGH"

    if event=="Middle East Conflict" and base=="MEDIUM":
        return "HIGH"

    if event=="Cyclone in Arabian Sea" and 15<=lat<=22:
        return "HIGH"

    if region["hormuz"] and 24<=lat<=28:
        return "HIGH"

    if region["arabian_sea"] and 15<=lat<=22:
        return "HIGH"

    return base

def adjust_risk(risk, score):
    if score>=8: return "HIGH"
    elif score>=4: return "HIGH" if risk=="MEDIUM" else "MEDIUM"
    elif score>=2: return "MEDIUM"
    return risk

df["risk"] = df.apply(lambda r: adjust_risk(get_risk(r.lat,r.lon,event,region_flags), news_risk), axis=1)

df["color"] = df["risk"].apply(lambda r: [255,0,0] if r=="HIGH" else [255,165,0] if r=="MEDIUM" else [0,200,0])

# ---------------- ETA ---------------- #
INDIA_LAT, INDIA_LON = 20, 72

df["distance"] = df.apply(lambda r: math.sqrt((INDIA_LAT-r.lat)**2+(INDIA_LON-r.lon)**2)*111, axis=1)
df["ETA"] = df["distance"].apply(lambda d: round((d/30)/24,1))
df["india_bound"] = df["lon"] < 75

# ---------------- METRICS ---------------- #
total = len(df)
india = len(df[df["india_bound"]])
high = len(df[df["risk"]=="HIGH"])
risk_pct = (high/total)*100 if total else 0

st.markdown("## 📊 System Intelligence Overview")

c1,c2,c3 = st.columns(3)
c1.metric("🚢 Total Ships", total)
c2.metric("🇮🇳 India-bound", india)
c3.metric("⚠️ Risk %", f"{risk_pct:.1f}%")

st.divider()

# ---------------- SPLIT LAYOUT ---------------- #
left, right = st.columns([2,1])

with left:
    st.markdown("## 🌍 Live Tracking")

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position='[lon,lat]',
        get_color='color',
        get_radius=200000
    )

    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=pdk.ViewState(latitude=22, longitude=65, zoom=3)
    ))

with right:
    st.markdown("## 🚨 Risk Intelligence")

    critical = df[(df["risk"]=="HIGH") & (df["india_bound"])]
    cpct = (len(critical)/total)*100 if total else 0

    if cpct > 40:
        st.error("🚨 CRITICAL: Supply chain breakdown risk detected")
    elif cpct > 20:
        st.warning("⚠️ Disruption signals detected")
    else:
        st.success("✅ Supply chain stable")

    st.markdown("### 🔮 AI Prediction")

    india_df = df[df["india_bound"]]
    ratio = len(critical)/len(india_df) if len(india_df) else 0
    avg_eta = india_df["ETA"].mean() if len(india_df) else 0

    if ratio > 0.6:
        days = max(1, round(avg_eta*0.5))
        st.error(f"🚨 Shortage in ~{days} days")
    elif ratio > 0.3:
        days = round(avg_eta*0.8)
        st.warning(f"⚠️ Disruption in ~{days} days")
    else:
        days = round(avg_eta+2)
        st.success(f"✅ Stable (~{days} days)")

st.divider()

# ---------------- NEWS ---------------- #
st.markdown("## 📰 Energy Intelligence")

for h in headlines:
    st.markdown(f"""
    <div class="news-card">
        <b>{h['title']}</b><br>
        <small>{h['source']}</small>
    </div>
    """, unsafe_allow_html=True)

st.caption(f"AI Risk Score: {news_risk}")

st.divider()

# ---------------- TABLE ---------------- #
st.markdown("## 📋 Shipment Data")
st.dataframe(df)

# ---------------- FOOTER ---------------- #
st.markdown("---")
st.caption("EnerSight AI v1 • Real-time energy intelligence system")
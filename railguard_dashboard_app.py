import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import random

st.set_page_config(
    page_title="RailGuard | Wildlife Protection",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Styling ----------
st.markdown("""
<style>
    .stApp { background: #0b1220; color: #e8eef8; }
    [data-testid="stSidebar"] { background: #111b2d; }
    .hero {
        padding: 22px 26px; border-radius: 18px; margin-bottom: 18px;
        background: linear-gradient(120deg, #132b43 0%, #173b43 55%, #1b3048 100%);
        border: 1px solid #2b4a61;
    }
    .hero h1 { margin: 0; color: #f3f7fb; font-size: 30px; }
    .hero p { color: #b8c8d9; margin: 8px 0 0 0; }
    div[data-testid="stMetric"] {
        background: #121e30; padding: 16px; border: 1px solid #26374d;
        border-radius: 14px;
    }
    .small-note { color: #8ea2bb; font-size: 12px; }
    .status-pill {
        display: inline-block; padding: 5px 10px; border-radius: 999px;
        background: #153c32; color: #8ef0c4; font-size: 12px;
        border: 1px solid #286653;
    }
</style>
""", unsafe_allow_html=True)

# ---------- Sample data (simulated only) ----------
@st.cache_data
def make_data():
    random.seed(21)
    species = ["Elephant", "Deer", "Cattle", "Wild boar", "Monkey"]
    zones = ["Zone A — Forest Edge", "Zone B — River Crossing", "Zone C — Open Track", "Zone D — Village Boundary"]
    rows = []
    now = datetime.now()
    for i in range(42):
        ts = now - timedelta(hours=random.randint(0, 24 * 7), minutes=random.randint(0, 59))
        animal = random.choice(species)
        rows.append({
            "Detection time": ts,
            "Species": animal,
            "Track zone": random.choice(zones),
            "Confidence (%)": random.randint(72, 99),
            "Distance to track (m)": random.randint(3, 120),
            "Alert status": random.choice(["Warning sent", "Monitoring", "Cleared"]),
        })
    return pd.DataFrame(rows).sort_values("Detection time", ascending=False).reset_index(drop=True)

if "detections" not in st.session_state:
    st.session_state.detections = make_data()

df = st.session_state.detections.copy()

# ---------- Sidebar ----------
st.sidebar.markdown("## 🚆 RailGuard")
st.sidebar.caption("Wildlife intrusion monitoring")
page = st.sidebar.radio("Navigation", ["Overview", "Detection Log", "Analytics", "System Status"])
st.sidebar.divider()
st.sidebar.markdown("**Prototype mode**")
st.sidebar.info("All detections and sensor states shown here are simulated sample data. No live railway or sensor connection is active.")
if st.sidebar.button("＋ Simulate new detection", use_container_width=True):
    new = pd.DataFrame([{
        "Detection time": datetime.now(),
        "Species": random.choice(["Elephant", "Deer", "Cattle", "Wild boar", "Monkey"]),
        "Track zone": random.choice(["Zone A — Forest Edge", "Zone B — River Crossing", "Zone C — Open Track", "Zone D — Village Boundary"]),
        "Confidence (%)": random.randint(75, 99),
        "Distance to track (m)": random.randint(3, 100),
        "Alert status": "Warning sent",
    }])
    st.session_state.detections = pd.concat([new, st.session_state.detections], ignore_index=True)
    st.rerun()

# ---------- Header ----------
st.markdown("""
<div class="hero">
  <h1>RailGuard <span style="color:#6ee7b7;">/</span> Wildlife Protection</h1>
  <p>Railway-track wildlife detection, early-warning overview and incident analytics</p>
</div>
""", unsafe_allow_html=True)

st.caption(f"Dashboard time: {datetime.now().strftime('%d %b %Y, %I:%M:%S %p')}  ·  DEMO DATA")
if page == "Overview":
    # Metrics
    today = df[df["Detection time"].dt.date == datetime.now().date()]
    warnings = int((df["Alert status"] == "Warning sent").sum())
    high_risk = int((df["Distance to track (m)"] <= 20).sum())
    species_count = int(df["Species"].nunique())
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Detections today", len(today), "Simulated")
    c2.metric("Warnings logged", warnings)
    c3.metric("Near-track events", high_risk, "≤ 20 m")
    c4.metric("Species detected", species_count)

    st.markdown("### Current track-zone overview")
    zone_cols = st.columns(4)
    zone_status = [
        ("Zone A", "Forest Edge", "Monitoring", "🟢"),
        ("Zone B", "River Crossing", "Animal alert", "🟠"),
        ("Zone C", "Open Track", "Clear", "🟢"),
        ("Zone D", "Village Boundary", "Monitoring", "🟢"),
    ]
    for col, (zone, desc, status, dot) in zip(zone_cols, zone_status):
        with col:
            st.markdown(f"""
            <div style="background:#121e30;border:1px solid #26374d;border-radius:14px;padding:16px;min-height:125px;">
              <div style="font-size:13px;color:#91a7c0;">{zone}</div>
              <div style="font-size:17px;font-weight:700;margin:7px 0;">{desc}</div>
              <div>{dot} {status}</div>
            </div>
            """, unsafe_allow_html=True)

    left, right = st.columns([1.35, 1])
    with left:
        st.markdown("### Detection activity")
        trend = df.copy()
        trend["Day"] = trend["Detection time"].dt.date
        daily = trend.groupby("Day").size().reset_index(name="Detections")
        fig = px.line(daily, x="Day", y="Detections", markers=True, template="plotly_dark")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10,r=10,t=10,b=10), height=300)
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.markdown("### Species distribution")
        counts = df["Species"].value_counts().reset_index()
        counts.columns = ["Species", "Count"]
        fig = px.pie(counts, names="Species", values="Count", hole=0.58, template="plotly_dark")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0,r=0,t=10,b=10), height=300, legend_title="")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Latest detection events")
    st.dataframe(df.head(8).style.format({"Confidence (%)": "{:.0f}%", "Distance to track (m)": "{:.0f} m"}), use_container_width=True, hide_index=True)

elif page == "Detection Log":
    st.markdown("### Detection log")
    col1, col2, col3 = st.columns(3)
    species_filter = col1.multiselect("Species", sorted(df["Species"].unique()), default=sorted(df["Species"].unique()))
    status_filter = col2.multiselect("Alert status", sorted(df["Alert status"].unique()), default=sorted(df["Alert status"].unique()))
    min_conf = col3.slider("Minimum confidence (%)", 0, 100, 70)
    filtered = df[
        df["Species"].isin(species_filter)
        & df["Alert status"].isin(status_filter)
        & (df["Confidence (%)"] >= min_conf)
    ]
    st.dataframe(filtered, use_container_width=True, hide_index=True)
    st.download_button("Download filtered log as CSV", filtered.to_csv(index=False).encode("utf-8"), "railguard_detection_log.csv", "text/csv")

elif page == "Analytics":
    st.markdown("### Wildlife analytics")
    left, right = st.columns(2)
    with left:
        counts = df.groupby("Species").size().reset_index(name="Detections").sort_values("Detections", ascending=False)
        fig = px.bar(counts, x="Species", y="Detections", template="plotly_dark", title="Detections by species")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=350)
        st.plotly_chart(fig, use_container_width=True)
    with right:
        zone_counts = df.groupby("Track zone").size().reset_index(name="Detections").sort_values("Detections", ascending=False)
        fig = px.bar(zone_counts, x="Detections", y="Track zone", orientation="h", template="plotly_dark", title="Detections by track zone")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=350)
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("### Key observations from demo data")
    most_common = df["Species"].mode().iloc[0] if not df.empty else "N/A"
    most_active_zone = df["Track zone"].mode().iloc[0] if not df.empty else "N/A"
    st.write(f"- Most frequently recorded species in this sample: **{most_common}**.")
    st.write(f"- Most active zone in this sample: **{most_active_zone}**.")
    st.caption("These are observations from generated demo data, not real wildlife statistics.")

elif page == "System Status":
    st.markdown("### System status")
    st.warning("Demo interface only — these statuses are placeholders and do not represent connected hardware.")
    status_data = pd.DataFrame([
        {"Component": "Camera / vision unit", "Status": "Demo mode", "Last check": "Not connected"},
        {"Component": "Motion sensor", "Status": "Demo mode", "Last check": "Not connected"},
        {"Component": "Wireless link", "Status": "Demo mode", "Last check": "Not connected"},
        {"Component": "Control-room dashboard", "Status": "Running locally", "Last check": datetime.now().strftime("%I:%M:%S %p")},
        {"Component": "Alert delivery", "Status": "Simulation only", "Last check": "Not connected"},
    ])
    st.dataframe(status_data, use_container_width=True, hide_index=True)
    st.markdown("### Prototype safety note")
    st.info("This dashboard is for demonstration and research. It does not connect to railway signalling, train-control, or braking systems.")

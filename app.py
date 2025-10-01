# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# ---------------------------
# 1. Page Config
# ---------------------------
st.set_page_config(
    page_title="Search Before Action: Delivery Wars",
    page_icon="🍔",
    layout="wide"
)

st.title("Search Before Action: Google Trends & India’s Delivery Wars")
st.markdown("### Swiggy 🟠 | Zomato 🔴 | Blinkit 🟢")

# ---------------------------
# 2. Load Data (Replace with real Google Trends CSVs)
# ---------------------------
@st.cache_data
def load_data():
    # Dummy sample dataset (replace with your Trends data)
    dates = pd.date_range("2022-01-01", periods=100, freq="W")
    df = pd.DataFrame({
        "date": dates,
        "Swiggy": np.random.randint(30, 90, size=len(dates)),
        "Zomato": np.random.randint(40, 95, size=len(dates)),
        "Blinkit": np.random.randint(20, 100, size=len(dates)),
        "state": np.random.choice(["Delhi", "Karnataka", "Maharashtra", "Tamil Nadu", "UP"], size=len(dates))
    })
    return df

df = load_data()

# ---------------------------
# 3. Sidebar Navigation
# ---------------------------
st.sidebar.title("📊 Dashboard Navigation")
page = st.sidebar.radio("Go to:", [
    "Overview",
    "Trends Over Time",
    "Regional Insights",
    "Search Intent",
    "Stats & Correlations",
    "Challenges & Story"
])

# ---------------------------
# 4. Page 1: Overview
# ---------------------------
if page == "Overview":
    st.subheader("📌 Big Picture: Who’s Winning?")
    
    # KPI Cards
    col1, col2, col3 = st.columns(3)
    col1.metric("Swiggy Peak", f"{df['Swiggy'].max()} index")
    col2.metric("Zomato Peak", f"{df['Zomato'].max()} index")
    col3.metric("Blinkit Peak", f"{df['Blinkit'].max()} index")

    # Time-series chart
    fig = px.line(df, x="date", y=["Swiggy", "Zomato", "Blinkit"],
                  title="📈 Search Popularity Over Time",
                  labels={"value": "Search Index", "date": "Date"})
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# 5. Page 2: Trends Over Time
# ---------------------------
elif page == "Trends Over Time":
    st.subheader("📈 Interactive Time-Series")
    state_filter = st.selectbox("Filter by State:", ["All"] + sorted(df["state"].unique().tolist()))
    
    if state_filter != "All":
        dff = df[df["state"] == state_filter]
    else:
        dff = df
    
    fig = px.line(dff, x="date", y=["Swiggy", "Zomato", "Blinkit"],
                  title=f"Search Trends ({state_filter})")
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# 6. Page 3: Regional Insights
# ---------------------------
elif page == "Regional Insights":
    st.subheader("🗺️ Regional Heatmap")
    # Aggregate by state
    state_avg = df.groupby("state")[["Swiggy", "Zomato", "Blinkit"]].mean().reset_index()
    state_avg["winner"] = state_avg[["Swiggy", "Zomato", "Blinkit"]].idxmax(axis=1)
    
    # Show table
    st.dataframe(state_avg)
    
    # Fake map (replace with India shapefile integration later)
    fig = px.bar(state_avg, x="state", y=["Swiggy", "Zomato", "Blinkit"],
                 title="State-wise Average Search Interest", barmode="group")
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# 7. Page 4: Search Intent
# ---------------------------
elif page == "Search Intent":
    st.subheader("🔍 What Are People Searching?")
    
    # Dummy queries
    queries = {
        "Swiggy": ["Swiggy coupon", "Swiggy One offer", "Swiggy pizza"],
        "Zomato": ["Zomato Pro", "Zomato discount", "Zomato near me"],
        "Blinkit": ["Blinkit milk", "Blinkit grocery", "Blinkit near me"]
    }
    
    app_choice = st.selectbox("Choose App:", list(queries.keys()))
    st.write("Top related queries:")
    st.write(queries[app_choice])
    
    # Word cloud
    text = " ".join(queries[app_choice])
    wc = WordCloud(width=800, height=400, background_color="white").generate(text)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)

# ---------------------------
# 8. Page 5: Stats & Correlations
# ---------------------------
elif page == "Stats & Correlations":
    st.subheader("📊 Math Behind the Insights")
    
    corr = df[["Swiggy", "Zomato", "Blinkit"]].corr()
    st.write("Correlation Matrix:")
    st.dataframe(corr)
    
    st.markdown("**Key formulas used:**")
    st.latex(r"Z = \frac{x - \mu}{\sigma}")
    st.latex(r"\text{Correlation}(X,Y) = \frac{\text{cov}(X,Y)}{\sigma_X \sigma_Y}")

# ---------------------------
# 9. Page 6: Challenges & Story
# ---------------------------
elif page == "Challenges & Story":
    st.subheader("⚡ Challenges vs Solutions")
    
    challenges = {
        "Relative Scaling": "Anchored to 'food delivery' query",
        "Festival Spikes": "Smoothed with rolling averages",
        "Sparse Data": "Focused on top 10 states"
    }
    
    for ch, sol in challenges.items():
        st.markdown(f"**{ch}** → {sol}")
    
    st.info("💡 Eureka Moment: Blinkit’s Delhi surge appeared in Trends months before headlines!")

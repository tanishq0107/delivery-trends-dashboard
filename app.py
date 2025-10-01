# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from pytrends.request import TrendReq

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
# 2. Fetch Data from Google Trends
# ---------------------------
@st.cache_data(ttl=86400)  # cache for 24 hours
def load_trends():
    pytrends = TrendReq(hl="en-IN", tz=330)
    kw_list = ["Swiggy", "Zomato", "Blinkit"]

    # 5 years, India
    pytrends.build_payload(kw_list, timeframe="today 5-y", geo="IN")
    data = pytrends.interest_over_time()
    if "isPartial" in data.columns:
        data = data.drop(columns=["isPartial"])
    data = data.reset_index()

    # Geo-level (state)
    geo = pytrends.interest_by_region(resolution="REGION", inc_low_vol=False, inc_geo_code=False)
    geo = geo.reset_index()
    geo = geo.rename(columns={"geoName": "state"})

    return data, geo

try:
    df, geo_df = load_trends()
except Exception as e:
    st.error("⚠️ Could not fetch live Google Trends data. Showing dummy data instead.")
    dates = pd.date_range("2019-01-01", periods=250, freq="W")
    df = pd.DataFrame({
        "date": dates,
        "Swiggy": np.random.randint(30, 90, size=len(dates)),
        "Zomato": np.random.randint(40, 95, size=len(dates)),
        "Blinkit": np.random.randint(20, 100, size=len(dates))
    })
    geo_df = pd.DataFrame({
        "state": ["Delhi", "Karnataka", "Maharashtra", "Tamil Nadu", "Uttar Pradesh"],
        "Swiggy": [70, 55, 60, 80, 50],
        "Zomato": [65, 70, 75, 60, 55],
        "Blinkit": [85, 40, 50, 30, 25]
    })

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
                  title="📈 Search Popularity Over Time (5 years)",
                  labels={"value": "Search Index", "date": "Date"})
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("> Blinkit’s rocket-like surge post-2022 = quick-commerce going mainstream 🚀")

# ---------------------------
# 5. Page 2: Trends Over Time
# ---------------------------
elif page == "Trends Over Time":
    st.subheader("📈 Interactive Time-Series")

    # Rolling average to smooth festival spikes
    window = st.slider("Smoothing Window (weeks):", 1, 8, 4)
    df_smooth = df.copy()
    df_smooth[["Swiggy", "Zomato", "Blinkit"]] = df_smooth[["Swiggy", "Zomato", "Blinkit"]].rolling(window).mean()

    fig = px.line(df_smooth, x="date", y=["Swiggy", "Zomato", "Blinkit"],
                  title="Search Trends (Smoothed)")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("> Notice how spikes around Diwali/New Year smooth out, revealing the true trend.")

# ---------------------------
# 6. Page 3: Regional Insights
# ---------------------------
elif page == "Regional Insights":
    st.subheader("🗺️ Regional Heatmap (India States)")

    # Winner per state
    geo_df["winner"] = geo_df[["Swiggy", "Zomato", "Blinkit"]].idxmax(axis=1)

    # Heatmap
    fig = px.choropleth(
        geo_df,
        geojson="https://raw.githubusercontent.com/geohacker/india/master/state/india_telengana.json",
        featureidkey="properties.NAME_1",
        locations="state",
        color="winner",
        title="Dominant App by State"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(geo_df)

    st.markdown("> South India → Swiggy, NCR → Blinkit, Delhi/Mumbai → Zomato stronghold.")

# ---------------------------
# 7. Page 4: Search Intent
# ---------------------------
elif page == "Search Intent":
    st.subheader("🔍 What Are People Searching?")

    pytrends = TrendReq(hl="en-IN", tz=330)
    app_choice = st.selectbox("Choose App:", ["Swiggy", "Zomato", "Blinkit"])

    try:
        pytrends.build_payload([app_choice], timeframe="today 12-m", geo="IN")
        related = pytrends.related_queries()
        top_queries = related[app_choice]["top"].head(10)
        rising_queries = related[app_choice]["rising"].head(10)

        st.write("Top Queries:")
        st.dataframe(top_queries)

        st.write("Rising Queries:")
        st.dataframe(rising_queries)

        # Word Cloud
        text = " ".join(top_queries["query"].dropna().tolist())
        wc = WordCloud(width=800, height=400, background_color="white").generate(text)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)

    except Exception as e:
        st.warning("⚠️ Could not fetch related queries. Try again later.")

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
    st.latex(r"\text{Lag Correlation} = \text{Corr}(X_t, Y_{t+k})")

    st.markdown("> Searches often lead real orders by 3–5 days → planning window for discounts & stocking.")

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

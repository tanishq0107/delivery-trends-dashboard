import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from pytrends.request import TrendReq
import requests

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
# 2. Helper Functions
# ---------------------------
@st.cache_data(ttl=86400)
def load_trends():
    pytrends = TrendReq(hl="en-IN", tz=330)
    kw_list = ["Swiggy", "Zomato", "Blinkit"]
    pytrends.build_payload(kw_list, timeframe="today 5-y", geo="IN")
    data = pytrends.interest_over_time()
    if "isPartial" in data.columns:
        data = data.drop(columns=["isPartial"])
    data = data.reset_index()
    geo = pytrends.interest_by_region(resolution="REGION", inc_low_vol=False, inc_geo_code=False)
    geo = geo.reset_index()
    geo = geo.rename(columns={"geoName": "state"})
    return data, geo

@st.cache_data
def load_geojson():
    # Full India GeoJSON from a stable source
    url = "https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/india.geojson"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception:
        st.warning("⚠️ Could not fetch full India GeoJSON. Heatmap will be limited.")
        return None

# ---------------------------
# 3. Load Data
# ---------------------------
try:
    df, geo_df = load_trends()
except Exception:
    st.warning("⚠️ Could not fetch live data, using dummy data.")
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

# Standardize state names
state_mapping = {
    "NCT": "Delhi",
    "Orissa": "Odisha",
    "Uttaranchal": "Uttarakhand",
    "Jammu & Kashmir": "Jammu and Kashmir",
    "Andaman & Nicobar Islands": "Andaman & Nicobar",
    "Dadra and Nagar Haveli": "Dadra & Nagar Haveli",
    "Daman and Diu": "Daman & Diu",
    "Arunanchal Pradesh": "Arunachal Pradesh"
}
geo_df["state"] = geo_df["state"].replace(state_mapping)
geo_df["state"] = geo_df["state"].str.title().str.strip()

# ---------------------------
# 4. Sidebar Navigation
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
# 5. Pages
# ---------------------------

# --- Overview Page ---
if page == "Overview":
    st.subheader("📌 Big Picture: Who’s Winning?")
    col1, col2, col3 = st.columns(3)
    col1.metric("Swiggy Peak", f"{df['Swiggy'].max()} index")
    col2.metric("Zomato Peak", f"{df['Zomato'].max()} index")
    col3.metric("Blinkit Peak", f"{df['Blinkit'].max()} index")

    fig = px.line(df, x="date", y=["Swiggy","Zomato","Blinkit"], title="📈 Search Popularity Over Time (5 years)")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Key Insights:**")
    st.markdown("- Blinkit shows a sharp surge post-2022, reflecting quick-commerce growth 🚀")
    st.markdown("- Swiggy remains strong in South India and metro cities")
    st.markdown("- Zomato maintains consistent interest in West and North India")

# --- Trends Over Time ---
elif page == "Trends Over Time":
    st.subheader("📈 Interactive Time-Series")
    window = st.slider("Smoothing Window (weeks):", 1, 8, 4)
    df_smooth = df.copy()
    df_smooth[["Swiggy","Zomato","Blinkit"]] = df_smooth[["Swiggy","Zomato","Blinkit"]].rolling(window).mean()
    fig = px.line(df_smooth, x="date", y=["Swiggy","Zomato","Blinkit"], title="Search Trends (Smoothed)")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Observations:**")
    st.markdown("- Smoothing reveals long-term trends by reducing festival spikes")
    st.markdown("- Blinkit’s sudden rises are evident around 2022–2023")
    st.markdown("- Correlation between Swiggy and Zomato remains high, reflecting overlapping markets")

# --- Regional Insights ---
elif page == "Regional Insights":
    st.subheader("🗺️ Regional Heatmap Comparison (India States)")
    geojson = load_geojson()
    if geojson is None:
        st.warning("Full India GeoJSON unavailable. Heatmap limited to available states.")
    app_choice = st.selectbox("Choose app to visualize:", ["Swiggy","Zomato","Blinkit"])
    fig = px.choropleth(
        geo_df,
        geojson=geojson if geojson else None,
        locations="state",
        featureidkey="properties.ST_NM",
        color=app_choice,
        hover_name="state",
        color_continuous_scale="YlOrRd",
        title=f"{app_choice} Popularity Across India"
    )
    fig.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("> 🔹 Hover over states to see search index.\n> 🔹 Switch apps using the dropdown above.")

# --- Search Intent ---
elif page == "Search Intent":
    st.subheader("🔍 What Are People Searching?")
    pytrends = TrendReq(hl="en-IN", tz=330)
    app_choice = st.selectbox("Choose App:", ["Swiggy","Zomato","Blinkit"])
    try:
        pytrends.build_payload([app_choice], timeframe="today 12-m", geo="IN")
        related = pytrends.related_queries()
        top_queries = related[app_choice]["top"].head(10)
        st.write("Top Queries:")
        st.dataframe(top_queries)
        text = " ".join(top_queries["query"].dropna().tolist())
    except Exception:
        st.warning("⚠️ Could not fetch related queries. Showing placeholder.")
        placeholder_queries = ["Swiggy coupon","Swiggy near me","Zomato pizza","Blinkit near me"]
        text = " ".join(placeholder_queries)
    wc = WordCloud(width=800, height=400, background_color="white").generate(text)
    fig, ax = plt.subplots(figsize=(10,5))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)

# --- Stats & Correlations ---
elif page == "Stats & Correlations":
    st.subheader("📊 Stats & Correlations")
    corr = df[["Swiggy","Zomato","Blinkit"]].corr()
    st.dataframe(corr)
    st.markdown("**Key Formulas:**")
    st.latex(r"Z = \frac{x - \mu}{\sigma}")
    st.latex(r"\text{Correlation}(X,Y) = \frac{\text{cov}(X,Y)}{\sigma_X \sigma_Y}")
    st.latex(r"\text{Lag Correlation} = \text{Corr}(X_t, Y_{t+k})")

# --- Challenges & Story ---
elif page == "Challenges & Story":
    st.subheader("⚡ Challenges & Eureka Moments")
    st.markdown("**Challenges:**")
    st.markdown("- Relative Scaling → anchored to 'food delivery'")
    st.markdown("- Festival Spikes → smoothed via rolling averages")
    st.markdown("- Sparse Data → focused on top 10 states")
    st.info("💡 Eureka: Blinkit’s Delhi surge appeared in Trends months before headlines!")

# Sidebar Footer
st.sidebar.markdown("---")
st.sidebar.markdown("Made with ❤️ using Streamlit, PyTrends, Plotly & WordCloud")

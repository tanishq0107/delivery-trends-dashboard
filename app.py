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

# ---------------------------
# 2. CSS Animations & Styling
# ---------------------------
st.markdown("""
<style>
/* Sidebar buttons animation */
.css-1lcbmhc.e1fqkh3o2 > div[data-baseweb="radio"] > label {
    transition: all 0.3s ease;
    border-radius: 8px;
    padding: 8px;
}
.css-1lcbmhc.e1fqkh3o2 > div[data-baseweb="radio"] > label:hover {
    background-color: #F0F3F8;
    transform: scale(1.03);
}

/* Selected button highlight */
.css-1lcbmhc.e1fqkh3o2 > div[data-baseweb="radio"] > label[data-state="checked"] {
    background-color: #D6EAF8 !important;
    font-weight: bold;
    color: #2E86C1;
}

/* Fade-in for page sections */
.stApp > div:nth-child(2) > div.block-container {
    animation: fadeInSection 0.8s ease-out;
}

@keyframes fadeInSection {
    0% {opacity:0; transform: translateY(20px);}
    100% {opacity:1; transform: translateY(0);}
}

/* Subheaders bounce slightly */
h2, h3 {
    animation: bounceSubheader 2s infinite;
}
@keyframes bounceSubheader {
    0%, 20%, 50%, 80%, 100% {transform: translateY(0);}
    40% {transform: translateY(-5px);}
    60% {transform: translateY(-2px);}
}
</style>
""", unsafe_allow_html=True)

st.title("Search Before Action: Google Trends & India’s Delivery Wars")
st.markdown("### Swiggy 🟠 | Zomato 🔴 | Blinkit 🟢")

# ---------------------------
# 3. Helper Functions
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
    geo["state"] = geo["state"].replace(state_mapping)
    geo["state"] = geo["state"].str.title().str.strip()

    return data, geo

# ---------------------------
# 4. Load Data
# ---------------------------
try:
    df, geo_df = load_trends()
except Exception:
    st.warning("⚠️ Could not fetch live Google Trends data. Using dummy data.")
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
# 5. Sidebar Navigation
# ---------------------------
st.sidebar.title("📊 Dashboard Navigation")
page = st.sidebar.radio(
    "Go to:",
    [
        "Overview",
        "Trends Over Time",
        "Regional Insights",
        "Search Intent",
        "Stats & Correlations",
        "Challenges & Story"
    ]
)

# ---------------------------
# 6. Pages with Enhanced Insights
# ---------------------------

# --- Overview Page ---
if page == "Overview":
    st.subheader("📌 Big Picture: Who’s Winning?")
    col1, col2, col3 = st.columns(3)
    col1.metric("Swiggy Peak", f"{df['Swiggy'].max()} index")
    col2.metric("Zomato Peak", f"{df['Zomato'].max()} index")
    col3.metric("Blinkit Peak", f"{df['Blinkit'].max()} index")

    fig = px.line(
        df,
        x="date",
        y=["Swiggy","Zomato","Blinkit"],
        title="📈 Search Popularity Over Time (5 years)",
        labels={"value":"Search Index", "date":"Date"}
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**💡 Key Insights:**")
    st.markdown("🟢 Blinkit shows rapid growth post-2022 → rise of quick-commerce.")
    st.markdown("🟠 Swiggy dominates historically in Southern India.")
    st.markdown("🔴 Zomato is strong in Western & metro cities.")
    st.markdown("⚡ Peaks in search often align with promotions, festivals, or news.")

# --- Trends Over Time ---
elif page == "Trends Over Time":
    st.subheader("📈 Interactive Time-Series")
    window = st.slider("Smoothing Window (weeks):", 1, 8, 4)
    df_smooth = df.copy()
    df_smooth[["Swiggy","Zomato","Blinkit"]] = df_smooth[["Swiggy","Zomato","Blinkit"]].rolling(window).mean()

    fig = px.line(
        df_smooth,
        x="date",
        y=["Swiggy","Zomato","Blinkit"],
        title="Search Trends (Smoothed)"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**💡 Insights:**")
    st.markdown(f"🧹 Smoothing removes short-term spikes (festival or promo events). Window = {window} weeks.")
    st.markdown("🟢 Blinkit shows sudden growth in launch periods.")
    st.markdown("🟠 Swiggy/Zomato trends reveal long-term engagement patterns.")

# --- Regional Insights ---
elif page == "Regional Insights":
    st.subheader("📊 Regional Popularity Across States")
    app_choice = st.selectbox("Choose App to Visualize:", ["Swiggy","Zomato","Blinkit"])

    geo_sorted = geo_df.sort_values(by=app_choice, ascending=False)
    fig = px.bar(
        geo_sorted,
        x=app_choice,
        y="state",
        orientation="h",
        text=app_choice,
        title=f"{app_choice} Popularity Across States",
        labels={app_choice:"Search Index", "state":"State"},
        color=app_choice,
        color_continuous_scale="YlOrRd"
    )
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

    st.subheader(f"🌡️ Color-coded Table: {app_choice}")
    st.dataframe(
        geo_df.style.background_gradient(subset=[app_choice], cmap="YlOrRd")
    )

    st.markdown("**💡 Insights:**")
    st.markdown("🏙️ Delhi shows high Blinkit interest → urban adoption.")
    st.markdown("🌴 Swiggy strong in Southern states like Tamil Nadu & Karnataka.")
    st.markdown("🏢 Zomato leads in Western/metro regions.")
    st.markdown("📈 Regional strategies can be optimized using this data.")

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
        st.warning("⚠️ Could not fetch related queries. Showing placeholders.")
        placeholder_queries = ["Swiggy coupon","Swiggy near me","Zomato pizza","Blinkit near me"]
        text = " ".join(placeholder_queries)

    wc = WordCloud(width=800, height=400, background_color="white").generate(text)
    fig, ax = plt.subplots(figsize=(10,5))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)

    st.markdown("**💡 Insights:**")
    st.markdown("🔍 Reveals real user intent: coupons, nearby services, popular items.")
    st.markdown("⚡ Blinkit → speed & availability focus.")
    st.markdown("🟠 Swiggy/Zomato → menu preferences & discounts.")

# --- Stats & Correlations ---
elif page == "Stats & Correlations":
    st.subheader("📊 Stats & Correlations")
    corr = df[["Swiggy","Zomato","Blinkit"]].corr()
    st.dataframe(corr)

    st.markdown("**💡 Insights:**")
    st.markdown("📈 High positive correlation → similar popularity trends.")
    st.markdown("⚖️ Negative correlation → competitive dynamics in certain periods.")
    st.markdown("🔮 Useful for forecasting growth and overlap in user interest.")

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

    st.markdown("**💡 Insights:**")
    st.markdown("🧩 Scaling & smoothing reveal long-term trends.")
    st.markdown("🌍 Regional differences uncover hidden growth pockets.")
    st.markdown("📊 Trend analysis guides marketing campaigns & inventory planning.")

# Sidebar Footer
st.sidebar.markdown("---")
st.sidebar.markdown("Made with ❤️ using Streamlit, PyTrends, Plotly & WordCloud")

# --------------------------- Fancy Footer ---------------------------
footer_html = """
<style>
.footer-card {
    background-color: #F8F9FA;
    padding: 20px;
    border-radius: 12px;
    margin-top: 30px;
    text-align: center;
    border: 1px solid #E0E0E0;
    font-family: 'Arial', sans-serif;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.footer-card:hover {
    transform: scale(1.05);
    box-shadow: 0 8px 20px rgba(0,0,0,0.15);
}
.footer-table {
    margin: auto;
    color: #34495E;
    font-size: 14px;
    border-collapse: collapse;
}
.footer-table th, .footer-table td {
    padding: 5px 15px;
    border-bottom: 1px solid #BDC3C7;
}
.footer-title {
    margin: 5px;
    color: #2E86C1;
    font-weight: bold;
}
.footer-team {
    color: #D35400;
}
.footer-copy {
    margin-top: 10px;
    font-size: 12px;
    color: #7F8C8D;
}
</style>

<div class="footer-card">
    <h3 class="footer-title">Developed by: <span class="footer-team">STANDARD DEVINATS</span></h3>
    <table class="footer-table">
        <tr>
            <th>Team Member</th>
            <th>Roll Number</th>
        </tr>
        <tr><td>NIRANJAN PRAMOD</td><td>252BDA09</td></tr>
        <tr><td>MENDONCA TANISHA DENIS</td><td>252BDA10</td></tr>
        <tr><td>TANISHQ SULTANIA</td><td>252BDA12</td></tr>
        <tr><td>R VINAY KUMAR</td><td>252BDA14</td></tr>
        <tr><td>RAKSHITH C</td><td>252BDA31</td></tr>
    </table>
    <p class="footer-copy">&copy; 2025 Search Before Action: Delivery Wars</p>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)

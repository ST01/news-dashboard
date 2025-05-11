import streamlit as st
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime

# ------------ API KEYS (from secrets.toml) ------------
NEWS_API_KEY = st.secrets["NEWS_API_KEY"]
GNEWS_API_KEY = st.secrets["GNEWS_API_KEY"]
TWELVE_DATA_API_KEY = st.secrets["TWELVE_DATA_API_KEY"]

# ------------ CONSTANTS ------------
CATEGORIES = ["general", "business", "technology", "science", "health", "sports", "entertainment"]
COUNTRIES = {
    "Global": "", "US": "us", "UK": "gb", "India": "in", "Germany": "de", "China": "cn", "Japan": "jp"
}
INDEX_SYMBOLS = {
    "Apple": "AAPL",
    "Tesla": "TSLA",
    "Amazon": "AMZN",
    "Microsoft": "MSFT",
    "Google": "GOOGL"
}
analyzer = SentimentIntensityAnalyzer()

# ------------ PAGE CONFIG & STYLE ------------
st.set_page_config(page_title="🗞️ The Streamlit Times", layout="wide")
st.markdown("""
<style>
body, html, [class*="css"] {
    font-family: 'Georgia', serif !important;
    background-color: #f4f4f4;
    color: #222;
}
.title-bar {
    background-color: #fff1e0;
    padding: 15px;
    border-bottom: 2px solid #d8b171;
    text-align: center;
}
.title-bar h1 {
    font-size: 44px;
    margin: 0;
    font-weight: bold;
    letter-spacing: -1px;
}
.headline {
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 0.2em;
}
.subline {
    font-size: 16px;
    color: #555;
    font-style: italic;
    margin-bottom: 0.5em;
}
.article-text {
    font-size: 16px;
    text-align: justify;
    margin-bottom: 2em;
}
a {
    text-decoration: none;
    color: #000;
}
a:hover {
    text-decoration: underline;
}
</style>
""", unsafe_allow_html=True)

# ------------ HEADER ------------
st.markdown(f"""
<div class='title-bar'>
    <h1>The Streamlit Times</h1>
    <div style='font-size:18px; color:#444;'>{datetime.now().strftime('%A, %d %B %Y')}</div>
</div>
""", unsafe_allow_html=True)

# ------------ FETCH MARKET DATA ------------
@st.cache_data(ttl=1800)
def fetch_index_data():
    base_url = "https://api.twelvedata.com/time_series"
    results = []
    for name, symbol in INDEX_SYMBOLS.items():
        params = {
            "symbol": symbol,
            "interval": "1day",
            "apikey": TWELVE_DATA_API_KEY,
            "outputsize": 1
        }
        res = requests.get(base_url, params=params)
        if res.status_code == 200:
            data = res.json()
            values = data.get("values", [{}])
            if values:
                close = values[0].get("close", "N/A")
                results.append((name, close, ""))
            else:
                results.append((name, "N/A", ""))
        else:
            results.append((name, "N/A", ""))
    return results

# ------------ DISPLAY MARKET BAR ------------
index_data = fetch_index_data()
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<h3 style='font-family:Georgia;'>📊 Market Summary (Previous Close)</h3>", unsafe_allow_html=True)
cols = st.columns(len(index_data))
for col, (name, price, _) in zip(cols, index_data):
    col.markdown(f"""
        <div style="font-family:Georgia;">
            <b>{name}</b><br>
            ${price}
        </div>
    """, unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# ------------ FILTERS ------------
st.sidebar.header("🗂️ Filters")
country = st.sidebar.selectbox("🌍 Region", list(COUNTRIES.keys()))
category = st.sidebar.selectbox("📰 Category", CATEGORIES)
country_code = COUNTRIES[country]

# ------------ FETCH NEWS

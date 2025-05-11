import streamlit as st
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime

# ------------ API KEYS ------------
NEWS_API_KEY = "d7813219bd10464ea297dcb09b7f2ff7"      # ← Replace with your NewsAPI key
GNEWS_API_KEY = "93a46de2d1562332a70982b11fa616e8"   # ← Replace with your GNews API key
TWELVE_DATA_API_KEY = "2bad82437a5c401b85929fb11767b54a"  # ← Replace with your Twelve Data key

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

# ------------ FETCH MARKET DATA (Twelve Data) ------------
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

# ------------ NEWS FETCHING ------------
@st.cache_data(ttl=3600)
def get_newsapi_articles(category, country_code):
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "apiKey": NEWS_API_KEY,
        "category": category,
        "pageSize": 12
    }
    if country_code:
        params["country"] = country_code
    res = requests.get(url, params=params)
    return res.json().get("articles", []) if res.status_code == 200 else []

@st.cache_data(ttl=3600)
def get_gnews_articles(query):
    url = "https://gnews.io/api/v4/search"
    params = {
        "q": query,
        "lang": "en",
        "max": 10,
        "token": GNEWS_API_KEY
    }
    res = requests.get(url, params=params)
    articles = []
    if res.status_code == 200:
        for a in res.json().get("articles", []):
            articles.append({
                "title": a["title"],
                "description": a["description"],
                "url": a["url"],
                "source": {"name": a["source"]["name"]},
                "publishedAt": a["publishedAt"]
            })
    return articles

def get_sentiment(text):
    score = analyzer.polarity_scores(text)['compound']
    if score >= 0.2:
        return "📈 Positive"
    elif score <= -0.2:
        return "📉 Negative"
    else:
        return "😐 Neutral"

# ------------ FETCH AND DISPLAY ARTICLES ------------
articles = get_newsapi_articles(category, country_code)

# Fallback to GNews if empty
if not articles and country != "Global":
    st.info("🔁 No local articles found via NewsAPI. Showing global results from GNews instead.")
    articles = get_gnews_articles(country)

if articles:
    cols = st.columns(2)
    for i, article in enumerate(articles):
        with cols[i % 2]:
            title = article.get("title", "No Title")
            url = article.get("url", "#")
            summary = article.get("description", "No description.")
            source = article.get("source", {}).get("name", "Unknown Source")
            sentiment = get_sentiment(summary)
            time_published = article.get("publishedAt", "")[:10]

            st.markdown(f"""
                <div class='headline'><a href="{url}" target="_blank">{title}</a></div>
                <div class='subline'>{source} • {time_published} • {sentiment}</div>
                <div class='article-text'>{summary}</div>
            """, unsafe_allow_html=True)
else:
    st.warning("No articles found for this region or topic.")

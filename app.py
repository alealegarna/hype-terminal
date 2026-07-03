import streamlit as st
import feedparser
import pandas as pd
import requests

# --- PENGATURAN TAMPILAN TERMINAL ---
st.set_page_config(page_title="HYPE & TREND TERMINAL", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #39FF14; }
    h1, h2, h3, p, div, span { color: #39FF14 !important; font-family: 'Courier New', Courier, monospace; }
    .stDataFrame { background-color: #111111; }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 MEDIA INTELLIGENCE: ECONOMIC & BUSINESS TRENDS")
st.markdown("---")

# "Topeng" agar mesin dikenali sebagai peramban Chrome
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}

# --- FUNGSI MENARIK BERITA ---
@st.cache_data(ttl=900) 
def get_news(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        feed = feedparser.parse(response.content)
        data = [{"Judul Berita Terhangat": entry.title, "Tautan": entry.link} for entry in feed.entries[:15]]
        
        if not data:
            return pd.DataFrame([{"Judul Berita Terhangat": "Tidak ada data saat ini", "Tautan": ""}])
        return pd.DataFrame(data)
    except:
        return pd.DataFrame([{"Judul Berita Terhangat": "Gagal memuat berita", "Tautan": ""}])

# --- FUNGSI MENARIK GOOGLE TRENDS VIA API PIHAK KETIGA (ANTI-BLOKIR) ---
@st.cache_data(ttl=3600)
def get_google_trends():
    try:
        url_id = "https://api.rss2json.com/v1/api.json?rss_url=https://trends.google.com/trends/trendingsearches/daily/rss?geo=ID"
        url_us = "https://api.rss2json.com/v1/api.json?rss_url=https://trends.google.com/trends/trendingsearches/daily/rss?geo=US"
        
        # Tarik data ID
        res_id = requests.get(url_id, timeout=15).json()
        data_id = [item['title'] for item in res_id.get('items', [])[:10]]
        df_id = pd.DataFrame(data_id, columns=['Top Keywords (ID)'])
        
        # Tarik data US
        res_us = requests.get(url_us, timeout=15).json()
        data_us = [item['title'] for item in res_us.get('items', [])[:10]]
        df_us = pd.DataFrame(data_us, columns=['Top Keywords (Global)'])
        
        # Jika data masih kosong
        if df_id.empty: df_id = pd.DataFrame(["Data gagal ditarik"], columns=['Top Keywords (ID)'])
        if df_us.empty: df_us = pd.DataFrame(["Data gagal ditarik"], columns=['Top Keywords (Global)'])
        
        return df_id, df_us
    except Exception as e:
        kosong = pd.DataFrame(["Sistem Error"], columns=["Status"])
        return kosong, kosong

# --- LAYOUT 3 KOLOM ---
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📰 HYPE NASIONAL (ID)")
    url_id = "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=id&gl=ID&ceid=ID:id"
    df_news_id = get_news(url_id)
    st.data_editor(df_news_id, hide_index=True, column_config={"Tautan": st.column_config.LinkColumn("Buka Artikel")}, use_container_width=True)

with col2:
    st.subheader("🌍 HYPE GLOBAL (US)")
    url_global = "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-US&gl=US&ceid=US:en"
    df_news_global = get_news(url_global)
    st.data_editor(df_news_global, hide_index=True, column_config={"Tautan": st.column_config.LinkColumn("Buka Artikel")}, use_container_width=True)

with col3:
    st.subheader("🔥 BREAKOUT KEYWORDS")
    df_trend_id, df_trend_us = get_google_trends()
    
    st.markdown("**Pencarian Terpanas - Indonesia**")
    st.dataframe(df_trend_id, hide_index=True, use_container_width=True)
    
    st.markdown("**Pencarian Terpanas - Global**")
    st.dataframe(df_trend_us, hide_index=True, use_container_width=True)

st.markdown("---")
st.markdown("*Data diperbarui secara real-time dari agregasi RSS Google News dan Google Trends via pihak ketiga.*")

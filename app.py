import streamlit as st
import feedparser
import pandas as pd
from pytrends.request import TrendReq

# --- PENGATURAN TAMPILAN TERMINAL ---
st.set_page_config(page_title="HYPE & TREND TERMINAL", layout="wide")

# CSS Kustom ala Bloomberg Terminal
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #39FF14; }
    h1, h2, h3, p, div, span { color: #39FF14 !important; font-family: 'Courier New', Courier, monospace; }
    .stDataFrame { background-color: #111111; }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 MEDIA INTELLIGENCE: ECONOMIC & BUSINESS TRENDS")
st.markdown("---")

# --- FUNGSI MENARIK BERITA (CACHE 15 MENIT) ---
@st.cache_data(ttl=900) 
def get_news(url):
    feed = feedparser.parse(url)
    data = []
    # Mengambil 15 berita terpopuler saat ini
    for entry in feed.entries[:15]:
        data.append({"Judul Berita Terhangat": entry.title, "Tautan": entry.link})
    return pd.DataFrame(data)

# --- FUNGSI MENARIK GOOGLE TRENDS (CACHE 1 JAM) ---
@st.cache_data(ttl=3600)
def get_google_trends():
    try:
        pytrend = TrendReq(hl='id-ID', tz=420)
        # Menarik pencarian yang sedang meledak di Indonesia hari ini
        df_id = pytrend.trending_searches(pn='indonesia')
        df_id.columns = ['Top Keywords (ID)']
        
        # Menarik pencarian yang sedang meledak secara Global (US)
        df_us = pytrend.trending_searches(pn='united_states')
        df_us.columns = ['Top Keywords (Global)']
        
        return df_id.head(10), df_us.head(10)
    except Exception:
        # Fallback jika server Google membatasi akses sementara
        kosong = pd.DataFrame(["Sedang sinkronisasi... coba beberapa saat lagi."])
        return kosong, kosong

# --- LAYOUT 3 KOLOM ---
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📰 HYPE NASIONAL (ID)")
    # RSS Google News topik Bisnis region Indonesia
    url_id = "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=id&gl=ID&ceid=ID:id"
    df_news_id = get_news(url_id)
    st.data_editor(df_news_id, hide_index=True, column_config={"Tautan": st.column_config.LinkColumn("Buka Artikel")}, use_container_width=True)

with col2:
    st.subheader("🌍 HYPE GLOBAL (US/INTL)")
    # RSS Google News topik Bisnis region Amerika/Global
    url_global = "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-US&gl=US&ceid=US:en"
    df_news_global = get_news(url_global)
    st.data_editor(df_news_global, hide_index=True, column_config={"Tautan": st.column_config.LinkColumn("Buka Artikel")}, use_container_width=True)

with col3:
    st.subheader("🔥 BREAKOUT KEYWORDS")
    df_trend_id, df_trend_us = get_google_trends()
    
    st.markdown("**Pencarian Terpanas Google - Indonesia**")
    st.dataframe(df_trend_id, hide_index=True, use_container_width=True)
    
    st.markdown("**Pencarian Terpanas Google - Global**")
    st.dataframe(df_trend_us, hide_index=True, use_container_width=True)

st.markdown("---")
st.markdown("*Data diperbarui secara real-time dari agregasi algoritma Google News dan Google Trends.*")

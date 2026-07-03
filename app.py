import streamlit as st
import feedparser
import pandas as pd

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

# --- FUNGSI MENARIK BERITA ---
@st.cache_data(ttl=900) 
def get_news(url):
    try:
        feed = feedparser.parse(url)
        data = [{"Judul Berita Terhangat": entry.title, "Tautan": entry.link} for entry in feed.entries[:15]]
        return pd.DataFrame(data)
    except:
        return pd.DataFrame([{"Judul Berita Terhangat": "Gagal memuat berita", "Tautan": ""}])

# --- FUNGSI MENARIK GOOGLE TRENDS VIA RSS ---
@st.cache_data(ttl=3600)
def get_google_trends():
    try:
        rss_id = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=ID"
        rss_us = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US"
        
        feed_id = feedparser.parse(rss_id)
        df_id = pd.DataFrame([entry.title for entry in feed_id.entries[:10]], columns=['Top Keywords (ID)'])
        
        feed_us = feedparser.parse(rss_us)
        df_us = pd.DataFrame([entry.title for entry in feed_us.entries[:10]], columns=['Top Keywords (Global)'])
        
        return df_id, df_us
    except:
        kosong = pd.DataFrame(["Gagal memuat data."], columns=["Error"])
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
st.markdown("*Data diperbarui secara real-time dari agregasi RSS Google News dan Google Trends.*")

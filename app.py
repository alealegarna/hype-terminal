import streamlit as st
import feedparser
import pandas as pd
import requests

# --- PENGATURAN TAMPILAN TERMINAL ---
st.set_page_config(page_title="CONTENT COVERAGE RADAR", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #39FF14; }
    h1, h2, h3, p, div, span, th, td { color: #39FF14 !important; font-family: 'Courier New', Courier, monospace; }
    .stDataFrame { background-color: #111111; }
    .stButton>button { background-color: #39FF14; color: #000000; font-weight: bold; border: 1px solid #39FF14; }
    .stButton>button:hover { background-color: #000000; color: #39FF14; border: 1px solid #39FF14; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER TERMINAL ---
col_head1, col_head2 = st.columns([4, 1])
with col_head1:
    st.title("📟 CONTENT COVERAGE RADAR")
with col_head2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⚡ FORCE SYNC"):
        st.cache_data.clear()

st.markdown("---")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# --- FUNGSI MENARIK BERITA ---
@st.cache_data(ttl=900) 
def get_news(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        feed = feedparser.parse(response.content)
        data = [{"Headline": entry.title, "Tautan": entry.link} for entry in feed.entries[:15]]
        if not data: return pd.DataFrame([{"Headline": "Data Kosong", "Tautan": ""}])
        return pd.DataFrame(data)
    except:
        return pd.DataFrame([{"Headline": "Koneksi Terputus", "Tautan": ""}])

# --- FUNGSI MENARIK TREN VIA PROKSI PUBLIK ---
@st.cache_data(ttl=1800)
def get_trends(geo_code):
    # Target asli RSS Google Trends
    rss_url = f"https://trends.google.com/trends/trendingsearches/daily/rss?geo={geo_code}"
    
    # Rute Proksi untuk menyembunyikan IP Streamlit Cloud
    proxy_url = f"https://api.allorigins.win/raw?url={rss_url}"
    
    try:
        # Menyerang menggunakan jalur proksi
        response = requests.get(proxy_url, timeout=15)
        
        # Jika proksi gagal, lakukan penetrasi langsung sebagai cadangan
        if response.status_code != 200:
            response = requests.get(rss_url, headers=HEADERS, timeout=15)
            
        feed = feedparser.parse(response.content)
        
        hasil = []
        for entry in feed.entries[:10]:
            keyword = entry.title
            # Mengambil data volume traffic dari elemen XML 'ht:approx_traffic'
            traffic = getattr(entry, 'ht_approx_traffic', 'N/A')
            hasil.append({"Keyword Teratas": keyword, "Volume": traffic})
            
        if not hasil:
            return pd.DataFrame([{"Keyword Teratas": "Menunggu Pembaruan Google", "Volume": ""}])
        
        return pd.DataFrame(hasil)
    
    except Exception:
        return pd.DataFrame([{"Keyword Teratas": "Server Sibuk, Coba Refresh", "Volume": "Error"}])

# --- PENGAMBILAN DATA ---
df_news_id = get_news("https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=id&gl=ID&ceid=ID:id")
df_news_us = get_news("https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-US&gl=US&ceid=US:en")
df_trend_id = get_trends("ID")
df_trend_us = get_trends("US")

# --- LAYOUT 3 KOLOM ---
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📰 HYPE NASIONAL (ID)")
    st.data_editor(df_news_id, hide_index=True, column_config={"Tautan": st.column_config.LinkColumn("Baca Artikel")}, use_container_width=True)

with col2:
    st.subheader("🌍 HYPE GLOBAL (US)")
    st.data_editor(df_news_us, hide_index=True, column_config={"Tautan": st.column_config.LinkColumn("Baca Artikel")}, use_container_width=True)

with col3:
    st.subheader("🔥 BREAKOUT KEYWORDS")
    
    st.markdown("**Radar Pencarian Indonesia**")
    st.dataframe(df_trend_id, hide_index=True, use_container_width=True)
    
    st.markdown("**Radar Pencarian Global**")
    st.dataframe(df_trend_us, hide_index=True, use_container_width=True)

st.markdown("---")
st.markdown("*Mesin stabil. Ditenagai oleh perutean Proksi Publik dengan ekstraksi XML langsung.*")

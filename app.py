import streamlit as st
import feedparser
import pandas as pd
import json
from curl_cffi import requests

# --- PENGATURAN TAMPILAN TERMINAL ---
st.set_page_config(page_title="2026 CONTENT COVERAGE RADAR", layout="wide")

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
    st.title("📟 2026 CONTENT COVERAGE RADAR")
with col_head2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⚡ FORCE SYNC"):
        st.cache_data.clear()

st.markdown("---")

# --- FUNGSI NEWS BERBASIS TLS SPOOFING ---
@st.cache_data(ttl=900) 
def get_news(url):
    try:
        # Menggunakan impersonate="chrome120" untuk menipu sistem Cloudflare dan Google
        response = requests.get(url, impersonate="chrome120", timeout=15)
        feed = feedparser.parse(response.content)
        data = [{"Headline": entry.title, "Tautan": entry.link} for entry in feed.entries[:15]]
        
        if not data: return pd.DataFrame([{"Headline": "Koneksi Terputus", "Tautan": ""}])
        return pd.DataFrame(data)
    except:
        return pd.DataFrame([{"Headline": "Gagal memuat sistem berita", "Tautan": ""}])

# --- FUNGSI INTERNAL GOOGLE TRENDS (HIDDEN API) ---
@st.cache_data(ttl=1800)
def get_internal_trends(geo_code):
    try:
        # Membidik API internal Google yang digunakan oleh website resmi mereka
        url = f"https://trends.google.com/trends/api/dailytrends?hl=id&tz=-420&geo={geo_code}"
        response = requests.get(url, impersonate="chrome120", timeout=15)
        
        # API internal Google selalu mengembalikan karakter sampah ")]}',\n" di awal JSON untuk mencegah eksekusi
        # Kita potong karakter tersebut agar JSON bisa dibaca
        raw_text = response.text.replace(")]}',", "").strip()
        data = json.loads(raw_text)
        
        # Ekstraksi Data
        hari_ini = data['default']['trendingSearchesDays'][0]['trendingSearches']
        
        hasil = []
        for item in hari_ini[:10]:
            keyword = item['title']['query']
            traffic = item.get('formattedTraffic', 'N/A')
            hasil.append({"Keyword Teratas": keyword, "Volume (Traffic)": traffic})
            
        return pd.DataFrame(hasil)
    except Exception as e:
        return pd.DataFrame([{"Keyword Teratas": "⚠️ Anti-Bot Memblokir", "Volume (Traffic)": "Error"}])

# --- PROSES PENGAMBILAN DATA (MULTITHREADING SIMULATION) ---
df_news_id = get_news("https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=id&gl=ID&ceid=ID:id")
df_news_us = get_news("https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-US&gl=US&ceid=US:en")
df_trend_id = get_internal_trends("ID")
df_trend_us = get_internal_trends("US")

# --- LAYOUT 3 KOLOM ---
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📰 HYPE NASIONAL (ID)")
    st.data_editor(df_news_id, hide_index=True, column_config={"Tautan": st.column_config.LinkColumn("Baca")}, use_container_width=True)

with col2:
    st.subheader("🌍 HYPE GLOBAL (US)")
    st.data_editor(df_news_us, hide_index=True, column_config={"Tautan": st.column_config.LinkColumn("Baca")}, use_container_width=True)

with col3:
    st.subheader("🔥 BREAKOUT & TRAFFIC")
    
    st.markdown("**Radar Pencarian Indonesia**")
    st.dataframe(df_trend_id, hide_index=True, use_container_width=True)
    
    st.markdown("**Radar Pencarian Global**")
    st.dataframe(df_trend_us, hide_index=True, use_container_width=True)

st.markdown("---")
st.markdown("*DIENKRIPSI & DIPALSUSKAN VIA CURL_CFFI (TLS SPOOFING) • API INTERNAL GOOGLE BYPASS AKTIF*")

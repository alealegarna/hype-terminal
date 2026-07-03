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
    .stButton>button { background-color: #39FF14; color: #000000; font-weight: bold; border-radius: 5px; border: 1px solid #39FF14; }
    .stButton>button:hover { background-color: #000000; color: #39FF14; border: 1px solid #39FF14; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER & KENDALI MANUAL ---
col_head1, col_head2 = st.columns([4, 1])
with col_head1:
    st.title("📈 MEDIA INTELLIGENCE TERMINAL")
with col_head2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 FORCE REFRESH DATA"):
        st.cache_data.clear() # Menghapus paksa memori cache yang macet

st.markdown("---")

# "Topeng" Identitas
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# --- FUNGSI MENARIK BERITA ---
@st.cache_data(ttl=900) 
def get_news(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        feed = feedparser.parse(response.content)
        data = [{"Judul Berita Terhangat": entry.title, "Tautan": entry.link} for entry in feed.entries[:15]]
        if not data: return pd.DataFrame([{"Judul Berita Terhangat": "Tidak ada data", "Tautan": ""}])
        return pd.DataFrame(data)
    except:
        return pd.DataFrame([{"Judul Berita Terhangat": "Koneksi Berita Gagal", "Tautan": ""}])

# --- FUNGSI HYDRA: PENARIK GOOGLE TRENDS BERLAPIS ---
@st.cache_data(ttl=3600)
def get_trends_hydra(geo_code):
    url = f"https://trends.google.com/trends/trendingsearches/daily/rss?geo={geo_code}"
    
    # Strategi 1: Serangan Langsung
    try:
        r = requests.get(url, headers=HEADERS, timeout=5)
        feed = feedparser.parse(r.content)
        if feed.entries: return [entry.title for entry in feed.entries[:10]]
    except: pass

    # Strategi 2: Jalur Tikus (AllOrigins Proxy)
    try:
        r = requests.get(f"https://api.allorigins.win/get?url={url}", timeout=8).json()
        feed = feedparser.parse(r['contents'])
        if feed.entries: return [entry.title for entry in feed.entries[:10]]
    except: pass

    # Strategi 3: Jalur Tikus (CorsProxy)
    try:
        r = requests.get(f"https://corsproxy.io/?{url}", timeout=8)
        feed = feedparser.parse(r.content)
        if feed.entries: return [entry.title for entry in feed.entries[:10]]
    except: pass
    
    # Strategi 4: API Format JSON (RSS2JSON)
    try:
        r = requests.get(f"https://api.rss2json.com/v1/api.json?rss_url={url}", timeout=8).json()
        if 'items' in r and r['items']: return [item['title'] for item in r['items'][:10]]
    except: pass

    # Jika Google memblokir ke-4 lapis pertahanan (Sangat jarang terjadi)
    return ["⚠️ Diblokir Google", "🔄 Klik Force Refresh"]

def fetch_all_trends():
    data_id = get_trends_hydra('ID')
    data_us = get_trends_hydra('US')
    return pd.DataFrame(data_id, columns=['Top Keywords (ID)']), pd.DataFrame(data_us, columns=['Top Keywords (Global)'])

# --- LAYOUT 3 KOLOM UTAMA ---
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
    df_trend_id, df_trend_us = fetch_all_trends()
    
    st.markdown("**Pencarian Terpanas - Indonesia**")
    st.dataframe(df_trend_id, hide_index=True, use_container_width=True)
    
    st.markdown("**Pencarian Terpanas - Global**")
    st.dataframe(df_trend_us, hide_index=True, use_container_width=True)

st.markdown("---")
st.markdown("*Mesin ditenagai oleh Sistem Hydra Multi-Proxy. Jika data stagnan, gunakan tombol Force Refresh.*")

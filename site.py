import streamlit as st
import pandas as pd
import requests

# --- TARAYICI AYARLARI ---
st.set_page_config(page_title="SE-SE Triko & Giyim | Toptan İmalat", page_icon="🧶", layout="wide")

# ⚠️ TELEFON NUMARANIZI BURAYA YAZIN (Başında 90 olacak şekilde, boşluksuz)
WHATSAPP_NO = "905523019281" 

# Google Apps Script Web App URL'niz (Stok sistemindeki verileri otomatik çeker)
API_URL = "https://script.google.com/macros/s/AKfycbyAZJ5Z-qDshFqzlcHhnxnCOAuqkDtDA2DEr7OuuGGPhOrfoT_LMY9eMs3RirFaw_iJ/exec"

# --- BULUTTAN ÜRÜNLERİ ÇEKME FONKSİYONU ---
def buluttan_urunleri_getir():
    try:
        r = requests.get(API_URL, timeout=10)
        data = r.json()
        stok_rows = data.get("stok", [])
        if len(stok_rows) > 1:
            df = pd.DataFrame(stok_rows[1:], columns=stok_rows[0])
            return df
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# --- CSS İLE MODERN TASARIM DOKUNUŞLARI ---
st.markdown("""
<style>
    .main-title { font-size: 50px !important; font-weight: 800; text-align: center; color: #F8FAFC; margin-bottom: 5px; letter-spacing: 2px; }
    .sub-title { font-size: 20px !important; text-align: center; color: #38BDF8; margin-bottom: 40px; font-weight: 500; }
    .urun-kart { background-color: #1E293B; padding: 20px; border-radius: 15px; border: 1px solid #334155; margin-bottom: 25px; text-align: center; }
    .urun-baslik { font-size: 22px !important; font-weight: 700; color: #F1F5F9; margin-top: 10px; }
    .urun-kod { font-size: 14px !important; color: #94A3B8; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

# --- ANA SAYFA ÜST KISIM (BANNER) ---
st.markdown("<h1 class='main-title'>SE-SE TRİKO & GİYİM</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Gaziantep'ten Dünyaya, Yüksek Kalite Toptan Triko İmalatı</p>", unsafe_allow_html=True)

st.markdown("---")

# --- HAKKIMIZDA / ÜRETİM GÜCÜ ALANI ---
col_h1, col_h2 = st.columns(2)
with col_h1:
    st.subheader("🧶 Üretim Kapasitemiz ve Kalitemiz")
    st.write(
        "SE-SE Triko olarak, tekstilin ve üretimin merkezi Gaziantep'te, en son teknoloji makine parkurumuz ve "
        "yılların getirdiği sektörel tecrübeyle toptan kazak, hırka ve triko imalatı yapmaktayız. "
        "Ürünlerimizde en kaliteli iplikleri kullanıyor, dokudan dikime kadar her aşamada kusursuzluğu hedefliyoruz."
    )
with col_h2:
    st.subheader("💼 Toptan Sipariş ve Fason Üretim")
    st.write(
        "Gerek kendi modellerimiz, gerekse markanıza özel fason üretim talepleriniz için esnek çözümler sunuyoruz. "
        "Yüksek adetli üretim gücümüz ve hızlı sevkiyat ağımızla, dükkanınızın ve markanızın stok ihtiyacını "
        "kesintisiz olarak karşılıyoruz."
    )

st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("## 📦 Güncel Ürün Kataloğumuz")
st.markdown("Beğendiğiniz ürünün altındaki butona basarak doğrudan toptan fiyat teklifi alabilirsiniz.")
st.markdown("---")

# --- KATALOG ALANI ---
df_urunler = buluttan_urunleri_getir()

if df_urunler.empty:
    st.info("Katalog şu anda güncelleniyor. Lütfen daha sonra tekrar deneyin veya doğrudan bizimle iletişime geçin.")
else:
    # Sadece fotoğrafı olan ve stoğu 0 olmayan ürünleri sergileyelim
    sergi_listesi = df_urunler[df_urunler["Fotoğraf"].str.startswith("http", na=False)].values.tolist()
    
    if not sergi_listesi:
        st.info("Katalogda şu an sergilenen ürün bulunmamaktadır.")
    else:
        # Ürünleri şık bir 3'lü ızgara (Grid) şeklinde gösterelim
        for i in range(0, len(sergi_listesi), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(sergi_listesi):
                    urun = sergi_listesi[i + j]
                    u_adi = urun[0]
                    u_kodu = urun[1]
                    u_foto = urun[3]
                    
                    with cols[j]:
                        st.markdown(f"""
                        <div class='urun-kart'>
                            <img src='{u_foto}' style='width:100%; height:280px; object-fit:cover; border-radius:10px;'>
                            <div class='urun-baslik'>{u_adi}</div>
                            <div class='urun-kod'>Ürün Kodu: {u_kodu}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # WhatsApp Sipariş Mesajı Oluşturma
                        mesaj = f"Merhaba SE-SE Triko, web sitenizde gördüğüm '{u_adi}' (Kod: {u_kodu}) modeli için toptan fiyat teklifi ve detaylı bilgi alabilir miyim?"
                        mesaj_kodlu = requests.utils.quote(mesaj)
                        wa_link = f"https://wa.me/{WHATSAPP_NO}?text={mesaj_kodlu}"
                        
                        st.inner_button = st.link_button("🟢 Toptan Fiyat Al (WhatsApp)", wa_link, use_container_width=True)

st.markdown("<br><br><br><br>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748B; font-size: 14px;'>© 2026 SE-SE TRİKO. Tüm Hakları Saklıdır. | By Samet SEVİM</p>", unsafe_allow_html=True)

import streamlit as st
import pandas as pd
import requests
import datetime
import base64
from PIL import Image
import io
import os

# --- TARAYICI AYARLARI ---
st.set_page_config(page_title="stok sistemi", page_icon="📦", layout="wide")

# ⚠️ TELEGRAM VE IMGBB BİLGİLERİNİZ ⚠️
TELEGRAM_TOKEN = "8634222820:AAECU62Pp_8TWpKGvWcRz5EQ0uJ8v0iyVs0"
TELEGRAM_CHAT_ID = "-1004652233827"  # Yeni grubunun ID'si (Eksiksiz ve doğru)
IMGBB_API_KEY = "2c2815895db4d37d80cce798d6114692"

# Google Apps Script Web App URL'niz
API_URL = "https://script.google.com/macros/s/AKfycbyAZJ5Z-qDshFqzlcHhnxnCOAuqkDtDA2DEr7OuuGGPhOrfoT_LMY9eMs3RirFaw_iJ/exec"

# --- YÜKSEK KALİTE FOTOĞRAF YÜKLEME FONKSİYONU ---
def imgbb_yukle(foto_dosyasi):
    try:
        url = "https://api.imgbb.com/1/upload"
        payload = {"key": IMGBB_API_KEY}
        files = {"image": foto_dosyasi.getvalue()}
        r = requests.post(url, data=payload, files=files, timeout=15)
        if r.json().get("success"):
            return r.json()["data"]["url"]
        return ""
    except:
        return ""

# --- TELEGRAM BİLDİRİM FONKSİYONU (EN GÜVENLİ VE HATASIZ HALİ) ---
def telegram_bildirim_gonder(mesaj):
    if TELEGRAM_TOKEN != "" and TELEGRAM_CHAT_ID != "":
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": mesaj
        }
        try:
            # İstek gönderiliyor
            requests.post(url, json=payload, timeout=5)
        except Exception as e:
            pass

# --- BULUT VERİ FONKSİYONLARI ---
def buluttan_veri_cek():
    try:
        r = requests.get(API_URL, timeout=10)
        data = r.json()
        
        stok_rows = data.get("stok", [])
        if len(stok_rows) > 1:
            df_stok = pd.DataFrame(stok_rows[1:], columns=stok_rows[0])
        else:
            df_stok = pd.DataFrame(columns=["Ürün Adı", "Ürün Kodu", "Adet", "Fotoğraf"])
            
        sev_rows = data.get("sevkiyat", [])
        if len(sev_rows) > 1:
            df_sevkiyat = pd.DataFrame(sev_rows[1:], columns=sev_rows[0])
        else:
            df_sevkiyat = pd.DataFrame(columns=["Tarih", "Müşteri İsmi", "Ürün Kodu", "Ürün Adı", "Adet"])
            
        df_stok["Adet"] = pd.to_numeric(df_stok["Adet"], errors='coerce').fillna(0).astype(int)
        df_sevkiyat["Adet"] = pd.to_numeric(df_sevkiyat["Adet"], errors='coerce').fillna(0).astype(int)
        
        return df_stok, df_sevkiyat
    except Exception as e:
        st.error(f"Bulut veritabanına bağlanılamadı: {e}")
        return pd.DataFrame(columns=["Ürün Adı", "Ürün Kodu", "Adet", "Fotoğraf"]), pd.DataFrame(columns=["Tarih", "Müşteri İsmi", "Ürün Kodu", "Ürün Adı", "Adet"])

def buluta_veri_gonder(df_stok, df_sevkiyat):
    try:
        stok_list = [df_stok.columns.tolist()] + df_stok.values.tolist()
        sevkiyat_list = [df_sevkiyat.columns.tolist()] + df_sevkiyat.values.tolist()
        
        payload = {
            "stok": stok_list,
            "sevkiyat": sevkiyat_list
        }
        r = requests.post(API_URL, json=payload, timeout=10)
        return r.json().get("status") == "success"
    except Exception as e:
        st.error(f"Veri buluta kaydedilirken hata oluştu: {e}")
        return False

# --- KULLANICI GİRİŞ SİSTEMİ ---
if 'giris_yapildi' not in st.session_state:
    st.session_state.giris_yapildi = False

if not st.session_state.giris_yapildi:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.title("🔐 stok sistemi")
        st.subheader("Yönetim Paneli Girişi")
        with st.form("giris_formu"):
            kullanici = st.text_input("Kullanıcı Adı")
            sifre = st.text_input("Şifre", type="password")
            giris_butonu = st.form_submit_button("Giriş Yap", type="primary", use_container_width=True)
            
            if giris_butonu:
                if kullanici == "admin" and sifre == "1234":
                    st.session_state.giris_yapildi = True
                    st.session_state.stok, st.session_state.sevkiyat = buluttan_veri_cek()
                    st.rerun()
                else:
                    st.error("❌ Hatalı kullanıcı adı veya şifre!")
        
        st.markdown("<p style='text-align: center; color: #888888; font-size: 15px; margin-top: 10px; margin-bottom: 0px; font-weight: 500;'>By Samet SEVİM</p>", unsafe_allow_html=True)
        
        col_im1, col_im2, col_im3 = st.columns([1, 1, 1])
        with col_im2:
            try:
                if os.path.exists("imza.png"):
                    st.image("imza.png", use_container_width=True)
                elif os.path.exists("imza.webp"):
                    st.image("imza.webp", use_container_width=True)
                elif os.path.exists("imza.jpg"):
                    st.image("imza.jpg", use_container_width=True)
            except:
                pass

else:
    # --- UYGULAMA AÇILDI ---
    st.sidebar.title("Kullanıcı Paneli")
    st.sidebar.success("Hoş geldin, Admin")
    
    if st.sidebar.button("🔄 Verileri Yenile", use_container_width=True):
        st.session_state.stok, st.session_state.sevkiyat = buluttan_veri_cek()
        st.success("Veriler güncellendi!")
        st.rerun()
        
    if st.sidebar.button("🚪 Çıkış Yap", type="primary", use_container_width=True):
        st.session_state.giris_yapildi = False
        st.rerun()

    if 'stok' not in st.session_state or 'sevkiyat' not in st.session_state:
        st.session_state.stok, st.session_state.sevkiyat = buluttan_veri_cek()

    st.title("📦 stok sistemi")
    st.markdown("---")

    sekme_stok, sekme_sevkiyat = st.tabs(["📦 Stok Yönetimi", "🚚 Sevkiyat Sistemi"])

    with sekme_stok:
        st.header("Yeni Ürün Girişi")
        with st.form("urun_ekle_form"):
            urun_adi = st.text_input("Ürün Adı")
            urun_kodu = st.text_input("Ürün Kodu")
            
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                adet = st.number_input("Adet", min_value=0, step=1)
            with col_f2:
                foto_dosyasi = st.file_uploader("Ürün Fotoğrafı Seçin (Orijinal Kalite)", type=["png", "jpg", "jpeg", "webp"])
            
            kaydet_butonu = st.form_submit_button("Stoka Ekle")

            if kaydet_butonu:
                if urun_adi != "" and urun_kodu != "":
                    if urun_kodu in st.session_state.stok["Ürün Kodu"].astype(str).values:
                        st.error("⚠️ Bu ürün kodu zaten mevcut! Farklı bir kod girin.")
                    else:
                        foto_yolu = ""
                        if foto_dosyasi is not None:
                            with st.spinner("Fotoğraf orijinal kalitede buluta yükleniyor..."):
                                foto_yolu = imgbb_yukle(foto_dosyasi)
                        
                        yeni_urun = pd.DataFrame([{
                            "Ürün Adı": urun_adi, "Ürün Kodu": urun_kodu, "Adet": adet, "Fotoğraf": foto_yolu
                        }])
                        
                        gecici_stok = pd.concat([st.session_state.stok, yeni_urun], ignore_index=True)
                        if buluta_veri_gonder(gecici_stok, st.session_state.sevkiyat):
                            st.session_state.stok = gecici_stok
                            st.success(f"✅ {urun_adi} başarıyla buluta kaydedildi!")
                            st.rerun()
                else:
                    st.error("Lütfen Ürün Adı ve Ürün Kodu alanlarını doldurun.")

        st.markdown("---")
        st.header("Mevcut Stok Durumu")
        if st.session_state.stok.empty:
            st.info("Henüz stokta ürün bulunmuyor.")
        else:
            tablo_gosterim = st.session_state.stok[["Ürün Kodu", "Ürün Adı", "Adet"]]
            st.dataframe(tablo_gosterim, use_container_width=True, hide_index=True)
            
            toplam_urun = st.session_state.stok["Adet"].sum()
            st.metric(label="Depodaki Toplam Ürün Sayısı", value=toplam_urun)

            st.markdown("---")
            st.header("🔍 Ürün Detay İnceleme ve Silme")
            
            secim_listesi = st.session_state.stok.apply(lambda row: f"{row['Ürün Kodu']} - {row['Ürün Adı']}", axis=1).tolist()
            secilen_urun = st.selectbox("Detayını görmek veya silmek istediğiniz ürünü seçin:", secim_listesi)
            
            if secilen_urun:
                secilen_indeks = secim_listesi.index(secilen_urun)
                satir = st.session_state.stok.iloc[secilen_indeks]
                
                col_detay, col_foto = st.columns([2, 1])
                with col_detay:
                    st.subheader("Ürün Bilgileri")
                    st.write(f"**Ürün Adı:** {satir['Ürün Adı']}")
                    st.write(f"**Ürün Kodu:** {satir['Ürün Kodu']}")
                    st.write(f"**Güncel Stok Adedi:** {satir['Adet']}")
                    
                    st.markdown("<br><br>", unsafe_allow_html=True)
                    sil_butonu = st.button("Bu Ürünü Stoktan Tamamen Sil", type="primary")
                    
                    if sil_butonu:
                        gecici_stok = st.session_state.stok.drop(secilen_indeks).reset_index(drop=True)
                        if buluta_veri_gonder(gecici_stok, st.session_state.sevkiyat):
                            st.session_state.stok = gecici_stok
                            st.success("❌ Ürün sistemden kaldırıldı!")
                            st.rerun()
                            
                with col_foto:
                    st.subheader("Ürün Fotoğrafı")
                    foto_p = satir['Fotoğraf']
                    if pd.notna(foto_p) and str(foto_p).startswith("http"):
                        st.image(str(foto_p), use_container_width=True)
                    else:
                        st.info("Bu ürüne ait fotoğraf yok.")

    with sekme_sevkiyat:
        st.header("Yeni Sevkiyat Yap")
        with st.form("sevkiyat_form"):
            sevkiyat_secim_listesi = st.session_state.stok.apply(lambda row: f"{row['Ürün Kodu']} - {row['Ürün Adı']}", axis=1).tolist()
            secilen_sevkiyat = st.selectbox("Sevkiyat Yapılacak Ürün", sevkiyat_secim_listesi if sevkiyat_secim_listesi else ["Mevcut ürün yok"])
            musteri_ismi = st.text_input("Müşteri İsmi")
            sevkiyat_adedi = st.number_input("Sevkiyat Adedi", min_value=1, step=1)
            
            st.markdown("**Sevkiyat Tarihi**")
            col_gun, col_ay, col_yil = st.columns(3)
            aylar_listesi = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
            bugun = datetime.date.today()
            
            with col_gun:
                sec_gun = st.number_input("Gün", min_value=1, max_value=31, value=bugun.day, step=1)
            with col_ay:
                sec_ay = st.selectbox("Ay", aylar_listesi, index=bugun.month - 1)
            with col_yil:
                sec_yil = st.number_input("Yıl", min_value=2020, max_value=2050, value=bugun.year, step=1)
            
            tam_turkce_tarih = f"{sec_gun} {sec_ay} {sec_yil}"
            sevkiyat_butonu = st.form_submit_button("Sevkiyatı Tamamla")

            if sevkiyat_butonu:
                if secilen_sevkiyat != "Mevcut ürün yok" and musteri_ismi != "":
                    islem_kodu = secilen_sevkiyat.split(" - ")[0]
                    idx = st.session_state.stok[st.session_state.stok["Ürün Kodu"].astype(str) == islem_kodu].index[0]
                    mevcut_adet = st.session_state.stok.loc[idx, "Adet"]
                    urun_adi = st.session_state.stok.loc[idx, "Ürün Adı"]
                    
                    if mevcut_adet >= sevkiyat_adedi:
                        gecici_stok = st.session_state.stok.copy()
                        gecici_stok.loc[idx, "Adet"] = mevcut_adet - sevkiyat_adedi
                        
                        yeni_sevkiyat = pd.DataFrame([{
                            "Tarih": tam_turkce_tarih, "Müşteri İsmi": musteri_ismi, 
                            "Ürün Kodu": islem_kodu, "Ürün Adı": urun_adi, "Adet": sevkiyat_adedi
                        }])
                        gecici_sevkiyat = pd.concat([st.session_state.sevkiyat, yeni_sevkiyat], ignore_index=True)
                        
                        if buluta_veri_gonder(gecici_stok, gecici_sevkiyat):
                            st.session_state.stok = gecici_stok
                            st.session_state.sevkiyat = gecici_sevkiyat
                            
                            tg_mesaj = f"🚚 YENİ SEVKİYAT YAPILDI!\n\n" \
                                       f"📦 Ürün: {urun_adi} ({islem_kodu})\n" \
                                       f"👤 Müşteri: {musteri_ismi}\n" \
                                       f"🔢 Adet: {sevkiyat_adedi} Adet\n" \
                                       f"📅 Tarih: {tam_turkce_tarih}"
                            telegram_bildirim_gonder(tg_mesaj)
                            
                            st.success(f"✅ {sevkiyat_adedi} adet ürün sevk edildi ve Telegram grubuna bildirildi.")
                            st.rerun()
                    else:
                        st.error(f"⚠️ Yetersiz stok! Depoda {mevcut_adet} adet var.")
                else:
                    st.error("Lütfen tüm alanları doldurun.")

        st.markdown("---")
        st.header("Giden Ürünler (Sevkiyat Geçmişi)")
        if st.session_state.sevkiyat.empty:
            st.info("Henüz yapılmış bir sevkiyat bulunmuyor.")
        else:
            ters_tablo = st.session_state.sevkiyat.iloc[::-1]
            st.dataframe(ters_tablo, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            st.header("❌ Sevkiyat İptal Paneli")
            iptal_secim_listesi = st.session_state.sevkiyat.apply(
                lambda row: f"{row.name} | {row['Tarih']} - {row['Müşteri İsmi']} -> {row['Ürün Kodu']} ({row['Adet']} Adet)", axis=1
            ).tolist()
            secilen_iptal_str = st.selectbox("İptal edilecek sevkiyat:", iptal_secim_listesi)
            iptal_onay_butonu = st.button("Seçili Sevkiyatı İptal Et", type="primary")
            
            if iptal_onay_butonu:
                sevkiyat_idx = int(secilen_iptal_str.split(" | ")[0])
                sevkiyat_satiri = st.session_state.sevkiyat.iloc[sevkiyat_idx]
                iptal_kodu, iptal_adedi, iptal_adi = str(sevkiyat_satiri['Ürün Kodu']), int(sevkiyat_satiri['Adet']), sevkiyat_satiri['Ürün Adı']
                iptal_musteri = sevkiyat_satiri['Müşteri İsmi']
                
                gecici_stok = st.session_state.stok.copy()
                if iptal_kodu in gecici_stok["Ürün Kodu"].astype(str).values:
                    stok_idx = gecici_stok[gecici_stok["Ürün Kodu"].astype(str) == iptal_kodu].index[0]
                    gecici_stok.loc[stok_idx, "Adet"] += iptal_adedi
                else:
                    gecici_stok = pd.concat([gecici_stok, pd.DataFrame([{"Ürün Adı": iptal_adi, "Ürün Kodu": iptal_kodu, "Adet": iptal_adedi, "Fotoğraf": ""}])], ignore_index=True)
                
                gecici_sevkiyat = st.session_state.sevkiyat.drop(sevkiyat_idx).reset_index(drop=True)
                
                if buluta_veri_gonder(gecici_stok, gecici_sevkiyat):
                    st.session_state.stok = gecici_stok
                    st.session_state.sevkiyat = gecici_sevkiyat
                    
                    tg_iptal_mesaj = f"⚠️ SEVKİYAT İPTAL EDİLDİ!\n\n" \
                                     f"📦 Ürün: {iptal_adi} ({iptal_kodu})\n" \
                                     f"👤 Müşteri: {iptal_musteri}\n" \
                                     f"🔄 İade Edilen Adet: {iptal_adedi} Adet\n" \
                                     f"ℹ️ Durum: Stoklar depoya geri eklendi."
                    telegram_bildirim_gonder(tg_iptal_mesaj)
                    
                    st.success(f"🔄 Sevkiyat iptal edildi! Rakamlar Telegram grubuna bildirildi.")
                    st.rerun()

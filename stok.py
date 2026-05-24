import streamlit as st
import pandas as pd
import os
import datetime

# --- TARAYICI AYARLARI ---
st.set_page_config(page_title="stok sistemi", page_icon="📦", layout="wide")

# --- KULLANICI GİRİŞ SİSTEMİ ---
if 'giris_yapildi' not in st.session_state:
    st.session_state.giris_yapildi = False

# Eğer giriş yapılmadıysa sadece bu ekranı göster
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
                # Şifre ve Kullanıcı Adı Ayarı
                if kullanici == "admin" and sifre == "1234":
                    st.session_state.giris_yapildi = True
                    st.rerun()
                else:
                    st.error("❌ Hatalı kullanıcı adı veya şifre!")
else:
    # --- GİRİŞ YAPILDIYSA UYGULAMAYI GÖSTER ---
    
    # Çıkış Yap Butonu (Sol Menüde)
    st.sidebar.title("Kullanıcı Paneli")
    st.sidebar.success("Hoş geldin, Admin")
    if st.sidebar.button("🚪 Çıkış Yap", type="primary", use_container_width=True):
        st.session_state.giris_yapildi = False
        st.rerun()

    # Dosya Yolları
    VERI_DOSYASI = "stok_verisi.csv"
    SEVKIYAT_DOSYASI = "sevkiyat_gecmisi.csv"
    FOTO_KLASORU = "urun_fotograflari"

    if not os.path.exists(FOTO_KLASORU):
        os.makedirs(FOTO_KLASORU)

    def stok_yukle():
        gerekli_sutunlar = ["Ürün Adı", "Ürün Kodu", "Adet", "Fotoğraf"]
        if os.path.exists(VERI_DOSYASI):
            try:
                df = pd.read_csv(VERI_DOSYASI)
                for sutun in gerekli_sutunlar:
                    if sutun not in df.columns:
                        df[sutun] = "" if sutun == "Fotoğraf" else 0
                return df[gerekli_sutunlar]
            except:
                return pd.DataFrame(columns=gerekli_sutunlar)
        else:
            return pd.DataFrame(columns=gerekli_sutunlar)

    def sevkiyat_yukle():
        gerekli_sutunlar = ["Tarih", "Müşteri İsmi", "Ürün Kodu", "Ürün Adı", "Adet"]
        if os.path.exists(SEVKIYAT_DOSYASI):
            try:
                return pd.read_csv(SEVKIYAT_DOSYASI)
            except:
                return pd.DataFrame(columns=gerekli_sutunlar)
        else:
            return pd.DataFrame(columns=gerekli_sutunlar)

    if 'stok' not in st.session_state:
        st.session_state.stok = stok_yukle()
    if 'sevkiyat' not in st.session_state:
        st.session_state.sevkiyat = sevkiyat_yukle()

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
                foto_dosyasi = st.file_uploader("Ürün Fotoğrafı Seçin", type=["png", "jpg", "jpeg"])
            
            kaydet_butonu = st.form_submit_button("Stoka Ekle")

            if kaydet_butonu:
                if urun_adi != "" and urun_kodu != "":
                    if urun_kodu in st.session_state.stok["Ürün Kodu"].astype(str).values:
                        st.error("⚠️ Bu ürün kodu zaten mevcut! Farklı bir kod girin.")
                    else:
                        foto_yolu = ""
                        if foto_dosyasi is not None:
                            uzanti = foto_dosyasi.name.split(".")[-1]
                            foto_yolu = os.path.join(FOTO_KLASORU, f"{urun_kodu}.{uzanti}")
                            with open(foto_yolu, "wb") as f:
                                f.write(foto_dosyasi.getbuffer())
                        
                        yeni_urun = pd.DataFrame([{
                            "Ürün Adı": urun_adi, 
                            "Ürün Kodu": urun_kodu, 
                            "Adet": adet,
                            "Fotoğraf": foto_yolu
                        }])
                        st.session_state.stok = pd.concat([st.session_state.stok, yeni_urun], ignore_index=True)
                        st.session_state.stok.to_csv(VERI_DOSYASI, index=False)
                        st.success(f"✅ {urun_adi} başarıyla stoka eklendi!")
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
            secilen_urun = st.selectbox("Fotoğrafını görmek veya silmek istediğiniz ürünü seçin:", secim_listesi)
            
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
                        if pd.notna(satir['Fotoğraf']) and satir['Fotoğraf'] != "" and os.path.exists(str(satir['Fotoğraf'])):
                            try: os.remove(str(satir['Fotoğraf']))
                            except: pass
                        
                        st.session_state.stok = st.session_state.stok.drop(secilen_indeks).reset_index(drop=True)
                        st.session_state.stok.to_csv(VERI_DOSYASI, index=False)
                        st.success("❌ Ürün ve fotoğrafı sistemden kaldırıldı!")
                        st.rerun()
                        
                with col_foto:
                    st.subheader("Ürün Fotoğrafı")
                    foto_p = satir['Fotoğraf']
                    if pd.notna(foto_p) and foto_p != "" and os.path.exists(str(foto_p)):
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
                        st.session_state.stok.loc[idx, "Adet"] = mevcut_adet - sevkiyat_adedi
                        st.session_state.stok.to_csv(VERI_DOSYASI, index=False)
                        
                        yeni_sevkiyat = pd.DataFrame([{
                            "Tarih": tam_turkce_tarih, "Müşteri İsmi": musteri_ismi, 
                            "Ürün Kodu": islem_kodu, "Ürün Adı": urun_adi, "Adet": sevkiyat_adedi
                        }])
                        st.session_state.sevkiyat = pd.concat([st.session_state.sevkiyat, yeni_sevkiyat], ignore_index=True)
                        st.session_state.sevkiyat.to_csv(SEVKIYAT_DOSYASI, index=False)
                        
                        st.success(f"✅ {sevkiyat_adedi} adet '{urun_adi}' sevk edildi.")
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
                
                if iptal_kodu in st.session_state.stok["Ürün Kodu"].astype(str).values:
                    stok_idx = st.session_state.stok[st.session_state.stok["Ürün Kodu"].astype(str) == iptal_kodu].index[0]
                    st.session_state.stok.loc[stok_idx, "Adet"] += iptal_adedi
                else:
                    st.session_state.stok = pd.concat([st.session_state.stok, pd.DataFrame([{"Ürün Adı": iptal_adi, "Ürün Kodu": iptal_kodu, "Adet": iptal_adedi, "Fotoğraf": ""}])], ignore_index=True)
                
                st.session_state.sevkiyat = st.session_state.sevkiyat.drop(sevkiyat_idx).reset_index(drop=True)
                st.session_state.stok.to_csv(VERI_DOSYASI, index=False)
                st.session_state.sevkiyat.to_csv(SEVKIYAT_DOSYASI, index=False)
                st.success(f"🔄 Sevkiyat iptal edildi! {iptal_adedi} adet stoğa geri yüklendi.")
                st.rerun()
# ----------------------------------------------------
# 1. KÜTÜPHANE VE TARİH AYARLARI
# ----------------------------------------------------
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

# Tarih ayarları: 1 yıllık veri aralığı
end_date = datetime.now()
start_date = end_date - timedelta(days=365)

# Sembol listeleri
bist30_symbols = [
    "AEFES.IS", "AKBNK.IS", "ASELS.IS", "ASTOR.IS", "BIMAS.IS",
    "ENKAI.IS", "EREGL.IS", "FROTO.IS", "GARAN.IS", "GUBRF.IS",
    "ISCTR.IS", "KCHOL.IS", "KRDMD.IS", "MGROS.IS", "PETKM.IS",
    "PGSUS.IS", "SAHOL.IS", "SASA.IS", "SISE.IS", "TAVHL.IS",
    "TCELL.IS", "THYAO.IS", "TOASO.IS", "TTKOM.IS", "TUPRS.IS",
    "ULKER.IS", "VAKBN.IS", "YKBNK.IS", "SKBNK.IS", "KOZAL.IS"
]
index_symbols = ["XU100.IS", "XU030.IS"]


# ----------------------------------------------------
# 2. VERİ ÇEKME İŞLEMİ
# ----------------------------------------------------

print("👉 BIST-30 ve Endeks Verileri Çekiliyor...")
# BIST-30 hisselerinin verilerini çekme
bist30_data = yf.download(
    tickers=bist30_symbols,
    start=start_date,
    end=end_date,
    progress=False
)

# Endeks verilerini çekme
indices_data = yf.download(
    tickers=index_symbols,
    start=start_date,
    end=end_date,
    progress=False
)


# ----------------------------------------------------
# 3. VERİ TEMİZLEME VE FİYAT SERİLERİ
# ----------------------------------------------------

# Kapanış fiyatlarını ayırma
bist30_close = bist30_data['Close']
bist100_close = indices_data['Close']['XU100.IS']
bist30_index_close = indices_data['Close']['XU030.IS']
# 1. BIST 30 Kapanış fiyatlarını kullanarak günlük getirileri hesaplama
# pct_change() günlük yüzde değişimi verir.
returns = bist30_close.pct_change().dropna() # NaN satırları temizliyoruz.

# --- NOT: USD/TRY verisi bu kodda çekilmediği için analiz dışında bırakılmıştır ---


# ----------------------------------------------------
# 4. TEMEL FİNANSAL ANALİZ (1 YILLIK GETİRİ)
# ----------------------------------------------------

# 1️⃣ BIST 30 Hisseleri – 1 yıllık getiri (%)
# Formül: (Son Fiyat / İlk Fiyat - 1) * 100
bist30_1y_return = (bist30_close.iloc[-1] / bist30_close.iloc[0] - 1) * 100

# 2️⃣ Endeksler – 1 yıllık getiri (%)
bist30_index_1y = (bist30_index_close.iloc[-1] / bist30_index_close.iloc[0] - 1) * 100
bist100_index_1y = (bist100_close.iloc[-1] / bist100_close.iloc[0] - 1) * 100


# 3️⃣ Hepsini tek tabloda birleştirme (DataFrame oluşturma)
returns_table = pd.DataFrame({
    "1Y_Getiri_%": bist30_1y_return
})

# Endeks verilerini tabloya ekleme
returns_table.loc["BIST30_INDEX"] = bist30_index_1y
returns_table.loc["BIST100_INDEX"] = bist100_index_1y


# 4️⃣ Büyükten küçüğe sıralama ve final çıktı
returns_table = returns_table.sort_values("1Y_Getiri_%", ascending=False)



print("\n----------------------------------------------------")
print("✅ BIST-30 ve ENDEKS 1 YILLIK GETİRİ ANALİZİ (Yüzde)")
print("----------------------------------------------------")
print(returns_table)

# 2. Yıllık Volatiliteyi (Risk) Hesaplama
# Günlük standart sapmayı (std) alıp, yıllık işlem günü (252) ile çarparak yıllık riske çeviriyoruz.
# Finansta zamanı ölçeklemek için kök(T) kullanılır (sqrt(252)).
yillik_volatilite = returns.std() * np.sqrt(252)

# 3. Korelasyon Matrisini Hesaplama
korelasyon_matrisi = returns.corr()

print("\n--- YILLIK RİSK (Volatilite) ANALİZİ ---")
# Volatiliteyi büyükten küçüğe sıralayarak en riskli hisseleri görelim
print((yillik_volatilite * 100).sort_values(ascending=False).round(2))

print("\n--- KORELASYON MATRİSİ (Çeşitlendirme Potansiyeli) ---")
# Matrisi yazdırmak
print(korelasyon_matrisi.round(3))
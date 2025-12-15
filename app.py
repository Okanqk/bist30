import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# ----------------------------------------------------------------------
# SAYFA YAPILANDIRMASI
# ----------------------------------------------------------------------
st.set_page_config(layout="wide", page_title="BIST Portföy Analizi")
st.title("📊 BIST Portföy Analiz Platformu")
st.markdown("---")

# ----------------------------------------------------------------------
# 1. BIST 30 HİSSE LİSTESİ VE SEÇİM
# ----------------------------------------------------------------------
bist30_hisseler = [
    "AKBNK.IS", "ASELS.IS", "BIMAS.IS", "ENKAI.IS", "EREGL.IS",
    "FROTO.IS", "GARAN.IS", "GUBRF.IS", "ISCTR.IS", "KCHOL.IS",
    "KOZAL.IS", "MGROS.IS", "PETKM.IS", "PGSUS.IS", "SAHOL.IS",
    "SASA.IS", "SISE.IS", "SKBNK.IS", "TAVHL.IS", "TCELL.IS",
    "THYAO.IS", "TOASO.IS", "TTKOM.IS", "TUPRS.IS", "ULKER.IS",
    "VAKBN.IS", "YKBNK.IS", "ASTOR.IS", "AEFES.IS", "KRDMD.IS"
]

selected_stocks = st.multiselect(
    "👉 **Adım 1:** Portföye eklemek istediğin hisseleri seç (Minimum 1 hisse)",
    bist30_hisseler
)

st.write("Seçilen hisseler:", selected_stocks)

# ----------------------------------------------------------------------
# 2. ANALİZ BAŞLANGICI VE VERİ ÇEKME
# ----------------------------------------------------------------------
if selected_stocks:
    st.markdown("### 🔍 Analiz Sonuçları (Son 1 Yıl)")

    end_date = datetime.today()
    start_date = end_date - timedelta(days=365)

    # ------------------------------------------------------------------
    # Veri çekme fonksiyonu (Caching ile)
    # ------------------------------------------------------------------
    @st.cache_data
    def get_data(tickers, start, end):
        try:
            data = yf.download(tickers, start=start, end=end, auto_adjust=True)["Close"]
            if isinstance(data, pd.Series):
                data = data.to_frame(name=tickers if isinstance(tickers, str) else tickers[0])
            return data
        except:
            return pd.DataFrame()

    prices = get_data(selected_stocks, start_date, end_date)
    bist30_prices_all = get_data(bist30_hisseler, start_date, end_date)
    bist30_endeks = get_data("XU030.IS", start_date, end_date)
    usdtry = get_data("USDTRY=X", start_date, end_date)

    # ------------------------------------------------------------------
    # 2.1 GETİRİ HESAPLAMALARI
    # ------------------------------------------------------------------
    returns = prices.pct_change().dropna()
    portfolio_daily_returns = returns.mean(axis=1)
    portfolio_return = (1 + portfolio_daily_returns).prod() - 1

    bist30_returns_all = bist30_prices_all.pct_change().dropna()
    bist30_cumulative_returns = (1 + bist30_returns_all).prod() - 1
    absolute_top_3_stocks = bist30_cumulative_returns.nlargest(3)
    top_3_portfolio_returns = bist30_returns_all[absolute_top_3_stocks.index]
    top_3_daily_returns = top_3_portfolio_returns.mean(axis=1)
    absolute_top_3_return = (1 + top_3_daily_returns).prod() - 1

    bist30_return = float((bist30_endeks.iloc[-1] / bist30_endeks.iloc[0]) - 1)
    usdtry_return = float((usdtry.iloc[-1] / usdtry.iloc[0]) - 1)
    deposit_rate = 0.45

    # ------------------------------------------------------------------
    # 3. GRAFİKSEL KARŞILAŞTIRMA
    # ------------------------------------------------------------------
    st.markdown("### 📈 Portföy Performans Grafiği")
    cum_returns_selected = (1 + portfolio_daily_returns).cumprod()
    cum_returns_top3 = (1 + top_3_daily_returns).cumprod()
    cum_returns_bist30 = (bist30_endeks / bist30_endeks.iloc[0])

    comparison_df = pd.DataFrame({
        "Senin Portföyün": cum_returns_selected,
        "Mutlak En İyi 3": cum_returns_top3,
        "BIST 30 Endeksi": cum_returns_bist30.squeeze()
    }).fillna(0) * 100

    st.line_chart(comparison_df)
    st.markdown("---")

    # ------------------------------------------------------------------
    # 4. GETİRİ KIYASLAMALARI
    # ------------------------------------------------------------------
    st.markdown("### 📊 Yıllık Getiri Kıyas Tablosu")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("🎯 Seçilen Portföy (Eşit Ağırlıklı)", f"% {portfolio_return * 100:.2f}")
        st.write(f"Seçilen Hisseler: **{', '.join(selected_stocks)}**")

    with col2:
        st.metric("🌟 Mutlak En İyi 3 Portföy",
                  f"% {absolute_top_3_return * 100:.2f}",
                  delta=f"% {((absolute_top_3_return - portfolio_return) * 100):.2f} Fark")
        st.write(f"Mutlak En İyi 3: **{', '.join(absolute_top_3_stocks.index.tolist())}**")

    with col3:
        st.metric("📉 BIST 30 Endeksi (XU030)", f"% {bist30_return * 100:.2f}",
                  delta=f"% {((portfolio_return - bist30_return) * 100):.2f} Endekse Göre")
        st.write("TL Bazlı Kıyaslama")

    with col4:
        st.metric("💲 USD/TRY Getirisi", f"% {usdtry_return * 100:.2f}")
        st.metric("🏦 Mevduat Getirisi (Varsayım)", f"% {deposit_rate * 100:.2f}")

    st.markdown("---")

    # ------------------------------------------------------------------
    # 5. EĞİTİM VİDEOSU VE FORM
    # ------------------------------------------------------------------
    st.markdown("### 🎓 Ücretsiz Eğitim Videoları")
    st.video("https://youtu.be/nMgkz3nOZloQ")  # Sen kendi videonu ekle

    st.markdown("### 📝 Ücretsiz Eğitim Kaydı")
    with st.form("kayit_formu"):
        isim = st.text_input("İsim")
        mail = st.text_input("E-mail")
        telefon = st.text_input("Telefon")
        submit = st.form_submit_button("Kaydı Tamamla")

        if submit:
            st.success(f"Teşekkürler {isim}! Kayıt başarılı, eğitim videolarına erişebilirsiniz 🎓")

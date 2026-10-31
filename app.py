import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="Bot de Trading BTC", layout="wide")

st.title("🤖 Bot de Trading Automático - BTC/USDT")
st.write(
    "Panel de control, gestión de riesgo y simulación (Paper Trading) en tiempo"
    " real."
)

# Configuración lateral
st.sidebar.header("⚙️ Configuración de Riesgo")
capital_inicial = st.sidebar.number_input(
    "Capital Virtual Inicial ($ USDT)", value=10000.0
)
riesgo_pct = st.sidebar.slider(
    "Porcentaje de capital a arriesgar por operación (%)", 1, 100, 50
)

# Mostrar saldos
col1, col2 = st.columns(2)
with col1:
  st.metric("💰 Saldo USDT Disponible", f"${capital_inicial:,.2f}")
with col2:
  st.metric("🪙 Bitcoin en Posesión", "0.0000 BTC")

st.info(
    f"Estado actual de la posición: **LIBRE** (Riesgo configurado: {riesgo_pct}%"
    " del capital)"
)


# Función para obtener datos de Bitcoin desde CoinGecko (Sin bloqueos de Binance)
def get_btc_data():
  url = 'https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=30'
  response = requests.get(url)
  data = response.json()
  prices = data['prices']
  df = pd.DataFrame(prices, columns=['timestamp', 'close'])
  df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
  df['SMA5'] = df['close'].rolling(window=5).mean()
  df['SMA20'] = df['close'].rolling(window=20).mean()
  return df


if st.button("🔄 Ejecutar Análisis del Mercado Ahora"):
  with st.spinner("Consultando precio del mercado..."):
    try:
      df = get_btc_data()
      precio_actual = df['close'].iloc[-1]
      sma5_actual = df['SMA5'].iloc[-1]
      sma20_actual = df['SMA20'].iloc[-1]

      st.success(f"**Precio actual de BTC:** ${precio_actual:,.2f} USDT")
      st.write(f"Media Móvil 5 períodos (SMA5): ${sma5_actual:,.2f}")
      st.write(f"Media Móvil 20 períodos (SMA20): ${sma20_actual:,.2f}")

      if sma5_actual > sma20_actual:
        st.success(
            "🟢 **SEÑAL DE COMPRA:** La tendencia es alcista (SMA5 superó a"
            " SMA20)."
        )
      else:
        st.warning(
            "🔴 **SEÑAL DE VENTA / ESPERA:** La tendencia no confirma compra"
            " en este momento."
        )
    except Exception as e:
      st.error(f"Error al obtener los datos del mercado: {e}")

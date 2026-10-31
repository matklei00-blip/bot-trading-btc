import streamlit as st
import ccxt
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Bot de Trading BTC", page_icon="🤖", layout="centered")

st.title("🤖 Bot de Trading Automático - BTC/USDT")
st.write("Panel de control, gestión de riesgo y simulación (Paper Trading) en tiempo real.")

# Panel lateral para configuración de riesgo
st.sidebar.header("⚙️ Configuración de Riesgo")
capital_inicial = st.sidebar.number_input("Capital Virtual Inicial ($ USDT)", value=10000.0, step=500.0)
porcentaje_riesgo = st.sidebar.slider("Porcentaje de capital a arriesgar por operación (%)", min_value=10, max_value=100, value=50, step=5)

# Inicializar variables de sesión en Streamlit
if 'saldo_usdt' not in st.session_state or st.session_state.get('capital_base') != capital_inicial:
    st.session_state.capital_base = capital_inicial
    st.session_state.saldo_usdt = capital_inicial
    st.session_state.cantidad_btc = 0.0
    st.session_state.precio_compra = 0.0
    st.session_state.estado_posicion = "LIBRE"

# Función para obtener datos
def obtener_datos_mercado():
    try:
        exchange = ccxt.binance()
        velas = exchange.fetch_ohlcv('BTC/USDT', timeframe='1m', limit=30)
        df = pd.DataFrame(velas, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        st.error(f"Error al conectar con el mercado: {e}")
        return None

# Métricas visuales
col1, col2 = st.columns(2)
col1.metric("💰 Saldo USDT Disponible", f"${st.session_state.saldo_usdt:,.2f}")
col2.metric("🪙 Bitcoin en Posesión", f"{st.session_state.cantidad_btc:.4f} BTC")

st.info(f"Estado actual de la posición: **{st.session_state.estado_posicion}** (Riesgo configurado: {porcentaje_riesgo}% del capital)")

if st.button("🔄 Ejecutar Análisis del Mercado Ahora"):
    with st.spinner("Analizando velas de Bitcoin en Binance..."):
        df = obtener_datos_mercado()
        if df is not None:
            df['SMA_rapida'] = df['close'].rolling(window=5).mean()
            df['SMA_lenta'] = df['close'].rolling(window=20).mean()
            
            precio_actual = df.iloc[-1]['close']
            sma_rapida = df.iloc[-1]['SMA_rapida']
            sma_lenta = df.iloc[-1]['SMA_lenta']
            
            sma_rapida_previa = df.iloc[-2]['SMA_rapida']
            sma_lenta_previa = df.iloc[-2]['SMA_lenta']
            
            st.write(f"**Precio actual BTC:** ${precio_actual:,.2f}")
            st.write(f"**SMA Rápida (5):** ${sma_rapida:,.2f} | **SMA Lenta (20):** ${sma_lenta:,.2f}")
            
            # Lógica de señales
            if (sma_rapida_previa <= sma_lenta_previa) and (sma_rapida > sma_lenta):
                señal = "COMPRA 🟢"
            elif (sma_rapida_previa >= sma_lenta_previa) and (sma_rapida < sma_lenta):
                señal = "VENTA 🔴"
            else:
                señal = "MANTENER 🟡"
                
            st.success(f"Señal generada: **{señal}**")
            
            # Ejecución simulada con gestión de riesgo
            if señal == "COMPRA 🟢" and st.session_state.estado_posicion == "LIBRE":
                # Calcular monto a invertir basado en el porcentaje seleccionado
                dinero_a_invertir = st.session_state.saldo_usdt * (porcentaje_riesgo / 100.0)
                st.session_state.saldo_usdt -= dinero_a_invertir
                st.session_state.cantidad_btc = dinero_a_invertir / precio_actual
                st.session_state.precio_compra = precio_actual
                st.session_state.estado_posicion = "COMPRADO"
                st.warning(f"⚡ ¡Compra ejecutada usando el {porcentaje_riesgo}% de tu saldo (${dinero_a_invertir:,.2f})!")
                st.rerun()
                
            elif señal == "VENTA 🔴" and st.session_state.estado_posicion == "COMPRADO":
                dinero_obtenido = st.session_state.cantidad_btc * precio_actual
                ganancia = dinero_obtenido - (st.session_state.cantidad_btc * st.session_state.precio_compra)
                st.session_state.saldo_usdt += dinero_obtenido
                st.session_state.cantidad_btc = 0.0
                st.session_state.estado_posicion = "LIBRE"
                st.success(f"⚡ ¡Venta ejecutada! Resultado de la operación: ${ganancia:+,.2f} USDT")
                st.rerun()

            # Gráfico de precios
            st.line_chart(df.set_index('timestamp')['close'])

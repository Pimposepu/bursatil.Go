import streamlit as st
import yfinance as yf
import processor
import ia_brain
import os
import pandas as pd

st.set_page_config(page_title="BursatilGO Web", layout="centered")
st.title("📊 BursatilGO - IA Maestra")

simbolo = st.text_input("Ingresá el Ticker (ej: ALUA.BA, BTC-USD)", "ALUA.BA").upper()

if st.button("🚀 ANALIZAR AHORA"):
    with st.spinner("Procesando mercado..."):
        # Descarga directa para la nube
        df = yf.download(simbolo, period="5y", interval="1d", progress=False)
        if df.empty:
            st.error("Ticker no encontrado.")
        else:
            if not os.path.exists('data'): os.makedirs('data')
            ruta_raw = f"data/raw_{simbolo}.json"
            df.reset_index().to_json(ruta_raw, orient='records', date_format='iso')

            # Usar tus archivos originales
            processor.analizar_datos_expertos(ruta_raw, simbolo)
            ia_brain.ejecutar_ia_maestra(simbolo)

            # Mostrar resultados en el celu
            st.success(f"Análisis de {simbolo} completo")
            st.image(f"data/velas_{simbolo}.png", caption="Velas y Niveles")
            st.image(f"data/riesgo_{simbolo}.png", caption="Gestión de Riesgo")
import streamlit as st
import yfinance as yf
import processor
import ia_brain
import os
import pandas as pd
import time

st.set_page_config(page_title="BursatilGO Web", layout="centered")
st.title("📊 BursatilGO - IA Maestra")

simbolo = st.text_input("Ingresá el Ticker (ej: ALUA.BA, BTC-USD)", "ALUA.BA").upper()

if st.button("🚀 ANALIZAR AHORA"):
    with st.spinner("Procesando mercado..."):
        # 1. Descarga de datos
        df = yf.download(simbolo, period="5y", interval="1d", progress=False)
        
        if df.empty:
            st.error("Ticker no encontrado.")
        else:
            # Crear carpeta si no existe y definir rutas de imágenes
            if not os.path.exists('data'): 
                os.makedirs('data')
            
            img_velas = f"data/velas_{simbolo}.png"
            img_riesgo = f"data/riesgo_{simbolo}.png"
            
            # Limpiar versiones anteriores para no mostrar datos viejos
            if os.path.exists(img_velas): os.remove(img_velas)
            if os.path.exists(img_riesgo): os.remove(img_riesgo)

            ruta_raw = f"data/raw_{simbolo}.json"
            df.reset_index().to_json(ruta_raw, orient='records', date_format='iso')

            # 2. Ejecutar la lógica de tus archivos originales
            processor.analizar_datos_expertos(ruta_raw, simbolo)
            ia_brain.ejecutar_ia_maestra(simbolo)

            # 3. ESPERA INTELIGENTE (Crucial para que no falle en el celular)
            # Le damos hasta 3 segundos al servidor para que termine de escribir las imágenes
            encontrado = False
            for _ in range(6):
                if os.path.exists(img_velas) and os.path.exists(img_riesgo):
                    encontrado = True
                    break
                time.sleep(0.5)

            # 4. Mostrar resultados de forma segura
            if encontrado:
                st.success(f"Análisis de {simbolo} completo")
                st.image(img_velas, caption="Velas y Niveles")
                st.image(img_riesgo, caption="Gestión de Riesgo")
            else:
                st.error("Los gráficos tardaron mucho en generarse. Probá tocar el botón una vez más.")

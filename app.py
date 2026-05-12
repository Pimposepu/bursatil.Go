import streamlit as st
import yfinance as yf
import processor
import ia_brain
import os
import pandas as pd
import time  # <--- Agregado para dar tiempo al sistema

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
            if not os.path.exists('data'): os.makedirs('data')
            
            # Limpieza previa de imágenes viejas para evitar conflictos
            img_velas = f"data/velas_{simbolo}.png"
            img_riesgo = f"data/riesgo_{simbolo}.png"
            if os.path.exists(img_velas): os.remove(img_velas)
            if os.path.exists(img_riesgo): os.remove(img_riesgo)

            ruta_raw = f"data/raw_{simbolo}.json"
            df.reset_index().to_json(ruta_raw, orient='records', date_format='iso')

            # 2. Ejecución de lógica
            processor.analizar_datos_expertos(ruta_raw, simbolo)
            ia_brain.ejecutar_ia_maestra(simbolo)

            # 3. VERIFICACIÓN CRÍTICA (El "seguro" para el celular)
            # Esperamos hasta 2 segundos a que los archivos existan físicamente
            intentos = 0
            while not (os.path.exists(img_velas) and os.path.exists(img_riesgo)) and intentos < 4:
                time.sleep(0.5)
                intentos += 1

            # 4. Mostrar resultados
            if os.path.exists(img_velas):
                st.success(f"Análisis de {simbolo} completo")
                st.image(img_velas, caption="Velas y Niveles")
                st.image(img_riesgo, caption="Gestión de Riesgo")
            else:
                st.error("Los gráficos se están generando. Por favor, toca 'Analizar' una vez más.")            st.image(f"data/riesgo_{simbolo}.png", caption="Gestión de Riesgo")

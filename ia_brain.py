import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf
import yfinance as yf
import os

def ejecutar_ia_maestra(simbolo):
    ruta = f"data/processed_{simbolo}.json"
    if not os.path.exists(ruta): 
        print(f"❌ No se encontró el archivo: {ruta}")
        return
        
    df = pd.read_json(ruta)
    
    # 1. Normalización total a minúsculas
    df.columns = [col.lower() for col in df.columns]
    
    # Preparación para gráficos
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)

    # --- LÓGICA DE VOTOS ---
    voto_velas = df['voto_velas'].iloc[-1] if 'voto_velas' in df.columns else 0
    rsi = df['rsi'].iloc[-1] if 'rsi' in df.columns else 50
    voto_rsi = 1 if rsi < 45 else (-1 if rsi > 70 else 0)
    
    # Filtro Hermano Mayor y VIX (con manejo de errores)
    voto_hermano = 0
    try:
        spy = yf.download("SPY", period="5d", progress=False)['Close']
        voto_hermano = 1 if float(spy.iloc[-1]) > float(spy.iloc[-2]) else -1
    except: pass

    voto_sentimiento = 0
    try:
        vix = yf.download("^VIX", period="1d", progress=False)['Close']
        voto_sentimiento = 1 if float(vix.iloc[-1]) < 22 else -1
    except: pass

    total_puntos = voto_velas + voto_rsi + voto_hermano + voto_sentimiento
    decision = "COMPRAR" if total_puntos >= 2 else "ESPERAR / EVITAR"

    # Soporte y Resistencia
    precio_actual = df['close'].iloc[-1]
    soporte = df['soporte'].iloc[-1] if 'soporte' in df.columns else (precio_actual * 0.95)
    resistencia = df['resistencia'].iloc[-1] if 'resistencia' in df.columns else (precio_actual * 1.05)

    # --- GENERACIÓN DE GRÁFICOS ---
    if not os.path.exists('data'): os.makedirs('data')

    # Gráfico 1: Velas (Mplfinance requiere nombres Capitalizados)
    df_graf = df.tail(30).copy()
    df_graf.columns = [col.capitalize() for col in df_graf.columns]
    
    mc = mpf.make_marketcolors(up='green', down='red', inherit=True)
    s = mpf.make_mpf_style(marketcolors=mc, gridstyle='--')
    
    try:
        mpf.plot(df_graf, type='candle', style=s, 
                 title=f"Velas - {simbolo}", 
                 hlines=dict(hlines=[soporte, resistencia], colors=['blue', 'orange'], linestyle='-.'),
                 savefig=dict(fname=f"data/velas_{simbolo}.png", dpi=100))
    except Exception as e:
        print(f"Error gráfico velas: {e}")

    # Gráfico 2: Riesgo
    try:
        plt.figure(figsize=(10, 4))
        plt.plot(df.index[-30:], df['close'].tail(30), label="Precio Cierre", color='black')
        plt.axhline(y=precio_actual * 0.90, color='red', linestyle='--', label="Stop Loss (10%)")
        plt.axhline(y=soporte, color='blue', linestyle=':', label="Soporte")
        plt.title(f"Riesgo - {simbolo}")
        plt.legend()
        plt.savefig(f"data/riesgo_{simbolo}.png")
        plt.close()
    except Exception as e:
        print(f"Error gráfico riesgo: {e}")

    print(f"✅ Análisis completo para {simbolo}")

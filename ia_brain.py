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
    
    # FORZADO ABSOLUTO: Pasamos todo a minúsculas apenas cargamos
    df.columns = [col.lower() for col in df.columns]
    
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)

    # --- LÓGICA DE VOTOS ---
    voto_velas = df['voto_velas'].iloc[-1] if 'voto_velas' in df.columns else 0
    
    # Buscamos RSI sin que importe la mayúscula
    col_rsi = [c for c in df.columns if c.lower() == 'rsi']
    rsi = df[col_rsi[0]].iloc[-1] if col_rsi else 50
    voto_rsi = 1 if rsi < 45 else (-1 if rsi > 70 else 0)
    
    # Filtros externos
    voto_hermano = 0
    try:
        spy = yf.download("SPY", period="5d", progress=False)
        # yfinance a veces devuelve MultiIndex, forzamos columna Close
        spy_close = spy['Close'] if 'Close' in spy.columns else spy.iloc[:, 0]
        voto_hermano = 1 if float(spy_close.iloc[-1]) > float(spy_close.iloc[-2]) else -1
    except: pass

    total_puntos = voto_velas + voto_rsi + voto_hermano
    decision = "COMPRAR" if total_puntos >= 1 else "ESPERAR"

    # --- CORRECCIÓN LÍNEA 46 (ERROR KEYERROR CLOSE) ---
    # Buscamos la columna que se parezca a 'close'
    col_close = [c for c in df.columns if c.lower() == 'close']
    if not col_close:
        print("❌ Error crítico: No hay columna de precio de cierre")
        return
    
    precio_actual = df[col_close[0]].iloc[-1]
    
    # Soporte y Resistencia seguros
    soporte = df['soporte'].iloc[-1] if 'soporte' in df.columns else (precio_actual * 0.95)
    resistencia = df['resistencia'].iloc[-1] if 'resistencia' in df.columns else (precio_actual * 1.05)

    # --- GRÁFICOS ---
    if not os.path.exists('data'): os.makedirs('data')

    # Para mplfinance necesitamos nombres específicos Capitalizados
    df_graf = df.tail(30).copy()
    # Mapeo manual para no errar
    mapeo = {c: c.capitalize() for c in df_graf.columns}
    df_graf = df_graf.rename(columns=mapeo)
    
    try:
        mc = mpf.make_marketcolors(up='green', down='red', inherit=True)
        s = mpf.make_mpf_style(marketcolors=mc, gridstyle='--')
        mpf.plot(df_graf, type='candle', style=s, 
                 title=f"Velas - {simbolo}", 
                 hlines=dict(hlines=[soporte, resistencia], colors=['blue', 'orange'], linestyle='-.'),
                 savefig=dict(fname=f"data/velas_{simbolo}.png", dpi=100))
        
        plt.figure(figsize=(10, 4))
        plt.plot(df.index[-30:], df[col_close[0]].tail(30), color='black')
        plt.axhline(y=precio_actual * 0.90, color='red', linestyle='--', label="SL 10%")
        plt.title(f"Riesgo - {simbolo}")
        plt.savefig(f"data/riesgo_{simbolo}.png")
        plt.close()
    except Exception as e:
        print(f"Error en gráficos: {e}")

    print(f"✅ Análisis completo para {simbolo}")

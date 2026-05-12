import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf
import os

def ejecutar_ia_maestra(simbolo):
    ruta = f"data/processed_{simbolo}.json"
    if not os.path.exists(ruta): return
        
    df = pd.read_json(ruta)

    # LIMPIEZA CRÍTICA: Forzamos que todo sea minúscula para trabajar internamente
    df.columns = [col.lower() for col in df.columns]
    
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)

    # --- LÓGICA DE VOTOS (Todo en minúsculas) ---
    voto_velas = df['voto_velas'].iloc[-1] if 'voto_velas' in df.columns else 0
    rsi = df['rsi'].iloc[-1] if 'rsi' in df.columns else 50
    
    # Verificación de historial para Media Móvil
    voto_trend = 0
    if len(df) >= 50 and 'close' in df.columns:
        ma50 = df['close'].rolling(50).mean().iloc[-1]
        voto_trend = 1 if df['close'].iloc[-1] > ma50 else 0

    decision = "COMPRAR" if (voto_velas + (1 if rsi < 45 else 0) + voto_trend) >= 2 else "ESPERAR"

    # --- GRÁFICOS (Necesitan nombres específicos para mplfinance) ---
    if not os.path.exists('data'): os.makedirs('data')
    
    # Clon para gráfico: mplfinance requiere 'Open', 'High', 'Low', 'Close'
    df_plot = df.copy()
    df_plot.columns = [col.capitalize() for col in df_plot.columns]

    try:
        mpf.plot(df_plot.tail(30), type='candle', style='charles', 
                 title=f"{simbolo}", savefig=f"data/velas_{simbolo}.png")
        
        plt.figure(figsize=(10, 4))
        plt.plot(df.index[-30:], df['close'].tail(30))
        plt.savefig(f"data/riesgo_{simbolo}.png")
        plt.close()
    except Exception as e:
        print(f"Error en gráficos: {e}")

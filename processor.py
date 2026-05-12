import pandas as pd
import ta
import os

def analizar_datos_expertos(ruta_json, simbolo):
    if not os.path.exists(ruta_json): return None
    df = pd.read_json(ruta_json)

    # 1. Indicadores Profesionales
    df['RSI'] = ta.momentum.RSIIndicator(df['Close']).rsi()
    df['Vol_Avg'] = df['Volume'].rolling(window=20).mean()
    
    # --- NUEVO: SOPORTE Y RESISTENCIA (20 días) ---
    df['Soporte'] = df['Low'].rolling(window=20).min()
    df['Resistencia'] = df['High'].rolling(window=20).max()
    
    # 2. Identificación de Patrones (Libro de Velas)
    df['Voto_Velas'] = 0
    df['Patron'] = "Ninguno"

    for i in range(1, len(df)):
        open_p = df['Open'].iloc[i]; close_p = df['Close'].iloc[i]
        high_p = df['High'].iloc[i]; low_p = df['Low'].iloc[i]
        vol = df['Volume'].iloc[i]; v_avg = df['Vol_Avg'].iloc[i]

        # MARTILLO
        cuerpo = abs(close_p - open_p)
        mecha_inf = min(close_p, open_p) - low_p
        if mecha_inf > (cuerpo * 2) and vol > v_avg:
            df.at[i, 'Voto_Velas'] = 1
            df.at[i, 'Patron'] = "Martillo + Vol"

        # ENVOLVENTE
        if df['Close'].iloc[i-1] < df['Open'].iloc[i-1] and close_p > open_p and close_p > df['Open'].iloc[i-1]:
            if vol > v_avg:
                df.at[i, 'Voto_Velas'] = 1
                df.at[i, 'Patron'] = "Envolvente + Vol"

    ruta_salida = f"data/processed_{simbolo}.json"
    df.to_json(ruta_salida, orient='records', indent=4)
    return ruta_salida
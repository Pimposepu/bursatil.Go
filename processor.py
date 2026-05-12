import pandas as pd
import ta
import os

def analizar_datos_expertos(ruta_json, simbolo):
    if not os.path.exists(ruta_json): return None
    df = pd.read_json(ruta_json)

    # CORRECCIÓN: Asegurar que las columnas tengan nombres estándar
    # Esto evita el error KeyError: 'Close'
    df.columns = [col.capitalize() for col in df.columns]

    # 1. Indicadores Profesionales
    if 'Close' in df.columns:
        df['RSI'] = ta.momentum.RSIIndicator(df['Close']).rsi()
    
    if 'Volume' in df.columns:
        df['Vol_Avg'] = df['Volume'].rolling(window=20).mean()
    
    # 2. Identificación de Patrones (Libro de Velas)
    df['Voto_Velas'] = 0
    df['Patron'] = "Ninguno"

    for i in range(1, len(df)):
        # Verificamos que existan las columnas necesarias para los patrones
        try:
            open_p = df['Open'].iloc[i]
            close_p = df['Close'].iloc[i]
            high_p = df['High'].iloc[i]
            low_p = df['Low'].iloc[i]
            vol = df['Volume'].iloc[i] if 'Volume' in df.columns else 0
            v_avg = df['Vol_Avg'].iloc[i] if 'Vol_Avg' in df.columns else 0

            # MARTILLO (Hammer)
            cuerpo = abs(close_p - open_p)
            mecha_inf = min(close_p, open_p) - low_p
            if mecha_inf > (cuerpo * 2) and vol > v_avg:
                df.at[i, 'Voto_Velas'] = 1
                df.at[i, 'Patron'] = "Martillo + Vol"

            # ENVOLVENTE (Engulfing)
            if df['Close'].iloc[i-1] < df['Open'].iloc[i-1] and close_p > open_p and close_p > df['Open'].iloc[i-1]:
                if vol > v_avg:
                    df.at[i, 'Voto_Velas'] = 1
                    df.at[i, 'Patron'] = "Envolvente + Vol"
        except Exception:
            continue

    ruta_salida = f"data/processed_{simbolo}.json"
    df.to_json(ruta_salida, orient='records', indent=4)
    return ruta_salida
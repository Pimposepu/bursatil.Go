import pandas as pd
import ta
import os

def analizar_datos_expertos(ruta_json, simbolo):
    if not os.path.exists(ruta_json): return None
    df = pd.read_json(ruta_json)

    # ESTÁNDAR: Pasamos todo a minúsculas para evitar errores de nombres
    df.columns = [col.lower() for col in df.columns]

    # 1. Indicadores Profesionales
    if 'close' in df.columns:
        df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi()
    
    if 'volume' in df.columns:
        df['vol_avg'] = df['volume'].rolling(window=20).mean()
    
    # 2. Identificación de Patrones
    df['voto_velas'] = 0
    df['patron'] = "Ninguno"

    for i in range(1, len(df)):
        try:
            open_p = df['open'].iloc[i]
            close_p = df['close'].iloc[i]
            high_p = df['high'].iloc[i]
            low_p = df['low'].iloc[i]
            vol = df['volume'].iloc[i] if 'volume' in df.columns else 0
            v_avg = df['vol_avg'].iloc[i] if 'vol_avg' in df.columns else 0

            # MARTILLO (Hammer)
            cuerpo = abs(close_p - open_p)
            mecha_inf = min(close_p, open_p) - low_p
            if mecha_inf > (cuerpo * 2) and vol > v_avg:
                df.at[i, 'voto_velas'] = 1
                df.at[i, 'patron'] = "Martillo + Vol"

            # ENVOLVENTE (Engulfing)
            if df['close'].iloc[i-1] < df['open'].iloc[i-1] and close_p > open_p and close_p > df['open'].iloc[i-1]:
                if vol > v_avg:
                    df.at[i, 'voto_velas'] = 1
                    df.at[i, 'patron'] = "Envolvente + Vol"
        except Exception:
            continue

    # Guardamos todo procesado
    ruta_salida = f"data/processed_{simbolo}.json"
    df.to_json(ruta_salida, orient='records', indent=4)
    return ruta_salida

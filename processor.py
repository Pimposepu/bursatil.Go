import pandas as pd
import ta
import os

def analizar_datos_expertos(ruta_json, simbolo):
    if not os.path.exists(ruta_json): return None
    df = pd.read_json(ruta_json)

    # Limpieza inicial
    df.columns = [col.lower() for col in df.columns]

    if 'close' in df.columns:
        df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi()
        df['vol_avg'] = df['volume'].rolling(window=20).mean() if 'volume' in df.columns else 0
    
    df['voto_velas'] = 0
    # Lógica de patrones (simplificada para evitar errores de índice)
    for i in range(1, len(df)):
        try:
            if df['close'].iloc[i] > df['open'].iloc[i] and df['close'].iloc[i-1] < df['open'].iloc[i-1]:
                df.at[df.index[i], 'voto_velas'] = 1
        except: continue

    ruta_salida = f"data/processed_{simbolo}.json"
    df.to_json(ruta_salida, orient='records', indent=4)
    return ruta_salida

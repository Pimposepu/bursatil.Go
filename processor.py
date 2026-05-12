import pandas as pd
import ta
import os

def analizar_datos_expertos(ruta_json, simbolo):
    if not os.path.exists(ruta_json): return None
    df = pd.read_json(ruta_json)

    # ESTÁNDAR: Forzar minúsculas para procesar y luego Capitalizar para guardar
    df.columns = [col.lower() for col in df.columns]

    # 1. Indicadores (usando minúsculas)
    if 'close' in df.columns:
        df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi()
    
    if 'volume' in df.columns:
        df['vol_avg'] = df['volume'].rolling(window=20).mean()
    
    df['voto_velas'] = 0
    # ... (resto de tu lógica de patrones usando df['open'], df['close'], etc.)

    # ANTES DE GUARDAR: Pasamos todo a Capitalized (Ej: 'Close', 'Rsi')
    df.columns = [col.capitalize() for col in df.columns]
    
    ruta_salida = f"data/processed_{simbolo}.json"
    df.to_json(ruta_salida, orient='records', indent=4)
    return ruta_salida

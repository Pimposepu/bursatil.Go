import yfinance as yf
import json
import os

def descargar_a_json(simbolo):
    if not os.path.exists('data'):
        os.makedirs('data')
        
    print(f"Buscando {simbolo}...")
    ticker = yf.Ticker(simbolo)
    df = ticker.history(period="5y", interval="1d")
    
    if df.empty:
        print(f"❌ No se hallaron datos para {simbolo}")
        return None

    df.reset_index(inplace=True)
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
    datos = df.to_dict(orient='records')

    ruta = f"data/raw_{simbolo}.json"
    with open(ruta, 'w') as f:
        json.dump(datos, f, indent=4)
    
    return ruta
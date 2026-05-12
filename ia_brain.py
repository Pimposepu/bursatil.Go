import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf
import yfinance as yf
import os

def ejecutar_ia_maestra(simbolo):
    # Intentar cargar el archivo procesado generado por processor.py
    ruta = f"data/processed_{simbolo}.json"
    if not os.path.exists(ruta): 
        print(f"❌ No se encontró el archivo: {ruta}")
        return
        
    df = pd.read_json(ruta)
    
    # 1. Normalización de nombres de columnas a minúsculas
    df.columns = [col.lower() for col in df.columns]
    
    # Preparación de DataFrame para gráficos (mplfinance requiere índices de tiempo y Capitalize)
    df_grafico = df.copy()
    df_grafico.columns = [col.capitalize() for col in df_grafico.columns]
    
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        df_grafico.index = df.index

    # --- LÓGICA DE VOTOS (SISTEMA DE DECISIÓN) ---
    
    # Voto 1: Patrones de Velas (calculados en processor.py)
    voto_velas = df['voto_velas'].iloc[-1] if 'voto_velas' in df.columns else 0
    
    # Voto 2: RSI (Fuerza Relativa)
    rsi = df['rsi'].iloc[-1] if 'rsi' in df.columns else 50
    voto_rsi = 1 if rsi < 45 else (-1 if rsi > 70 else 0)
    
    # Voto 3: Hermano Mayor (SPY - Mercado General)
    try:
        spy = yf.download("SPY", period="5d", interval="1d", progress=False)['Close']
        ultimo_spy = float(spy.iloc[-1])
        previo_spy = float(spy.iloc[-2])
        voto_hermano = 1 if ultimo_spy > previo_spy else -1
    except:
        voto_hermano = 0 # Neutral si falla la descarga

    # Voto 4: Sentimiento de Miedo (VIX)
    try:
        vix_data = yf.download("^VIX", period="1d", progress=False)['Close']
        vix = float(vix_data.iloc[-1])
        voto_sentimiento = 1 if vix < 22 else -1
    except:
        voto_sentimiento = 0

    # Cálculo de decisión final
    total_puntos = voto_velas + voto_rsi + voto_hermano + voto_sentimiento
    decision = "COMPRAR" if total_puntos >= 2 else "ESPERAR / EVITAR"

    # --- DATOS TÉCNICOS ---
    # Se asume que el procesador calcula soporte/resistencia. Si no, usamos valores por defecto.
    soporte = df['soporte'].iloc[-1] if 'soporte' in df.columns else (df['close'].iloc[-1] * 0.95)
    resistencia = df['resistencia'].iloc[-1] if 'resistencia' in df.columns else (df['close'].iloc[-1] * 1.05)
    precio_actual = df['close'].iloc[-1]

    # --- SIMILITUD HISTÓRICA (Búsqueda de patrones pasados) ---
    ventana = 3
    actual = df['close'].tail(ventana).values
    similitudes = []
    
    # Recorrer el historial comparando la forma de la curva
    for i in range(len(df) - (ventana + 2)):
        pasado = df['close'].iloc[i : i + ventana].values
        distancia = np.linalg.norm(actual - pasado)
        similitudes.append((distancia, i))
    
    similitudes.sort(key=lambda x: x[0])
    mejores_5 = similitudes[:5]

    # --- SALIDA POR CONSOLA ---
    print(f"\n" + "="*45)
    print(f"📊 TERMINAL DE INTELIGENCIA: {simbolo}")
    print(f"="*45)
    print(f"1. Velas Japonesas:  {'✅' if voto_velas > 0 else '⚪'}")
    print(f"2. Filtro RSI:       {'✅' if voto_rsi > 0 else '❌' if voto_rsi < 0 else '⚪'}")
    print(f"3. Hermano (SPY):    {'✅' if voto_hermano > 0 else '❌' if voto_hermano < 0 else '⚪'}")
    print(f"4. Sentimiento(VIX): {'✅' if voto_sentimiento > 0 else '❌' if voto_sentimiento < 0 else '⚪'}")
    print(f"---------------------------------------------")
    print(f"SOPORTE CLAVE:       ${soporte:.2f}")
    print(f"RESISTENCIA CLAVE:   ${resistencia:.2f}")
    print(f"DECISIÓN FINAL:      {decision}")
    print(f"---------------------------------------------")
    print("Las últimas veces que pasó esto fue:")
    for i, (dist, idx) in enumerate(mejores_5, 1):
        fecha = df.index[idx + ventana - 1]
        valor = df['close'].iloc[idx + ventana - 1]
        var = ((df['close'].iloc[idx + ventana] - valor) / valor) * 100
        print(f"{i}: {fecha.date()} | Valor: ${valor:.2f} | Var: {var:+.2f}%")
    print(f"="*45)

    # --- GENERACIÓN DE GRÁFICOS ---
    
    # Asegurar que existe la carpeta data
    if not os.path.exists('data'): os.makedirs('data')

    # Gráfico 1: Velas Japonesas y Niveles
    mc = mpf.make_marketcolors(up='green', down='red', inherit=True)
    s = mpf.make_mpf_style(marketcolors=mc, gridstyle='--')
    
    mpf.plot(df_grafico.tail(30), type='candle', style=s, 
             title=f"Velas y Niveles - {simbolo}", 
             hlines=dict(hlines=[soporte, resistencia], colors=['blue', 'orange'], linestyle='-.'),
             savefig=f"data/velas_{simbolo}.png")

    # Gráfico 2: Gestión de Riesgo (Stop Loss y Cierre)
    plt.figure(figsize=(10, 4))
    plt.plot(df.index[-30:], df['close'].tail(30), label="Precio Cierre", color='black', linewidth=1.5)
    
    sl_10 = precio_actual * 0.90
    plt.axhline(y=sl_10, color='red', linestyle='--', label="Stop Loss (10%)")
    plt.axhline(y=soporte, color='blue', linestyle=':', label="Soporte Técnico")
    
    plt.title(f"Riesgo y Soporte - {simbolo}")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(f"data/riesgo_{simbolo}.png")
    
    # IMPORTANTE: Cerrar el gráfico para liberar memoria del servidor
    plt.close()

    print(f"✅ Análisis completo. Archivos guardados en /data/")
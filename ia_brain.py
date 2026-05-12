import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf
import os

def ejecutar_ia_maestra(simbolo):
    ruta = f"data/processed_{simbolo}.json"
    if not os.path.exists(ruta): 
        print(f"❌ No se encontró el archivo: {ruta}")
        return
        
    df = pd.read_json(ruta)

    # 1. NORMALIZACIÓN TOTAL: Forzar nombres con mayúscula inicial
    df.columns = [col.capitalize() for col in df.columns]
    
    # Preparación de fechas
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)

    # 2. VERIFICACIÓN DE DATOS MÍNIMOS
    # Si tenemos menos de 50 filas, no podemos calcular la MA50
    cantidad_datos = len(df)
    
    # --- LÓGICA DE VOTOS CON PROTECCIÓN ---
    voto_velas = df['Voto_velas'].iloc[-1] if 'Voto_velas' in df.columns else 0
    
    rsi = df['Rsi'].iloc[-1] if 'Rsi' in df.columns else 50
    voto_rsi = 1 if rsi < 45 else (-1 if rsi > 70 else 0)
    
    # Voto de tendencia: Solo si hay más de 50 velas de historial
    voto_trend = 0
    if cantidad_datos >= 50:
        ma50 = df['Close'].rolling(50).mean().iloc[-1]
        voto_trend = 1 if df['Close'].iloc[-1] > ma50 else 0
    else:
        print(f"⚠️ Datos insuficientes para Media Móvil ({cantidad_datos}/50)")

    total_votos = voto_velas + voto_rsi + voto_trend
    decision = "COMPRAR" if total_votos >= 2 else "ESPERAR / EVITAR"

    # --- LÓGICA DE SIMILITUD (Mínimo 10 datos para comparar) ---
    mejores_5 = []
    if cantidad_datos > 10:
        ventana = 3
        actual = df['Close'].tail(ventana).values
        similitudes = []
        for i in range(len(df) - (ventana + 2)):
            pasado = df['Close'].iloc[i : i + ventana].values
            distancia = np.linalg.norm(actual - pasado)
            similitudes.append((distancia, i))
        
        similitudes.sort(key=lambda x: x[0])
        mejores_5 = similitudes[:5]

    # --- SALIDA POR CONSOLA ---
    print(f"\n" + "="*45)
    print(f"📊 REPORTE MAESTRO: {simbolo}")
    print(f"DECISIÓN FINAL: {decision}")
    print(f"Votos: {total_votos} (Velas: {voto_velas}, RSI: {voto_rsi}, Trend: {voto_trend})")
    print(f"="*45)

    # --- GRÁFICOS ---
    if not os.path.exists('data'): os.makedirs('data')

    # Gráfico de Velas (Últimas 30)
    try:
        mc = mpf.make_marketcolors(up='green', down='red', inherit=True)
        s = mpf.make_mpf_style(marketcolors=mc, gridstyle='--')
        mpf.plot(df.tail(30), type='candle', style=s, 
                 title=f"Velas - {simbolo}", savefig=f"data/velas_{simbolo}.png")
    except Exception as e:
        print(f"⚠️ Error al crear gráfico de velas: {e}")

    # Gráfico de Riesgo
    try:
        plt.figure(figsize=(10, 4))
        plt.plot(df.index[-30:], df['Close'].tail(30), label="Cierre", color='blue')
        sl = df['Close'].iloc[-1] * 0.90
        plt.axhline(y=sl, color='red', linestyle='--', label=f"Stop Loss 10% (${sl:.2f})")
        plt.title(f"Gestión de Riesgo - {simbolo}")
        plt.legend()
        plt.savefig(f"data/riesgo_{simbolo}.png")
        plt.close()
    except Exception as e:
        print(f"⚠️ Error al crear gráfico de riesgo: {e}")

    print(f"✅ Análisis completado")

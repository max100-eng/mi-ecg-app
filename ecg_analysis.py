import neurokit2 as nk
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from ecg_analysis import analizar_archivo

def analizar_archivo(ecg_signal, sampling_rate=1000):
    """Procesa y visualiza un ECG."""
    # Procesamiento
    signals, info = nk.ecg_process(ecg_signal, sampling_rate=sampling_rate)
    
    # Métricas clave
    heart_rate = nk.ecg_rate(signals, sampling_rate=sampling_rate)
    hrv = nk.hrv(signals, sampling_rate=sampling_rate)
    
    # Visualización
    nk.ecg_plot(signals, sampling_rate=sampling_rate)
    plt.suptitle("Análisis de ECG", fontsize=16)
    
    # Resultados
    print("\n--- Resultados ---")
    print(f"Frecuencia cardíaca: {heart_rate:.1f} lpm")
    print(f"Intervalo QRS: {info['duration_QRS']} ms")
    print(f"Variabilidad RR: {hrv['HRV_RMSSD'][0]:.2f} ms")
    
    return signals, info

# Ejemplo con señal simulada (reemplaza con tus datos reales)
ecg_simulated = nk.ecg_simulate(duration=10, heart_rate=75, noise=0.05)
analizar_archivo(ecg_simulated)
plt.show() 
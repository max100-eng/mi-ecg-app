import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, butter, filtfilt

def cargar_ecg:
    """Carga datos de ECG desde un archivo (simulado aquí)"""
    # En una aplicación real, cargarías datos reales de un archivo
    # Esto es un ejemplo con datos simulados
    fs = 360  # Frecuencia de muestreo típica (Hz)
    t = np.arange(0, 10, 1/fs)  # 10 segundos de datos
    ecg = np.sin(2 * np.pi * 1 * t)  # Onda base
    ecg += 0.5 * np.sin(2 * np.pi * 0.2 * t)  # Componente de baja frecuencia
    ecg += 0.2 * np.random.randn(len(t))  # Ruido
    
    # Añadir complejos QRS simulados
    for i in range(5, len(t), int(fs * 0.8)):  # ~80 latidos por minuto
        ecg[i:i+20] += 1.5 * np.exp(-0.1 * np.arange(0, 20))
    
    return t, ecg

def filtrar_ecg(ecg, fs=360):
    """Filtra la señal de ECG para eliminar ruido"""
    # Filtro pasa banda (0.5-40 Hz)
    nyq = 0.5 * fs
    low = 0.5 / nyq
    high = 40.0 / nyq
    b, a = butter(4, [low, high], btype='band')
    ecg_filtrado = filtfilt(b, a, ecg)
    return ecg_filtrado

def detectar_latidos(ecg, fs=360):
    """Detecta los complejos QRS (latidos)"""
    # Encontrar picos R (los más altos en el QRS)
    peaks, _ = find_peaks(ecg, height=0.5, distance=fs*0.6)  # Distancia mínima 0.6s
    
    # Calcular frecuencia cardíaca
    if len(peaks) > 1:
        rr_intervals = np.diff(peaks) / fs
        heart_rate = 60 / np.mean(rr_intervals)
    else:
        heart_rate = 0
    
    return peaks, heart_rate

def analizar_ecg(t, ecg):
    """Realiza análisis completo del ECG"""
    # Filtrar señal
    ecg_filtrado = filtrar_ecg(ecg)
    
    # Detectar latidos
    peaks, heart_rate = detectar_latidos(ecg_filtrado)
    
    # Visualización
    plt.figure(figsize=(12, 6))
    plt.plot(t, ecg, label='ECG crudo', alpha=0.5)
    plt.plot(t, ecg_filtrado, label='ECG filtrado')
    plt.plot(peaks/360, ecg_filtrado[peaks], "x", label='Picos R detectados')
    plt.title(f'Análisis de ECG - Frecuencia Cardíaca: {heart_rate:.1f} lpm')
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Amplitud')
    plt.legend()
    plt.grid()
    plt.show()
    
    # Interpretación básica
    print("\nInterpretación básica:")
    print(f"- Frecuencia cardíaca: {heart_rate:.1f} lpm")
    
    if heart_rate > 100:
        print("- Taquicardia detectada (FC > 100 lpm)")
    elif heart_rate < 60:
        print("- Bradicardia detectada (FC < 60 lpm)")
    else:
        print("- Frecuencia cardíaca normal (60-100 lpm)")
    
    if len(peaks) > 0:
        rr_intervals = np.diff(peaks) / 360
        rr_variability = np.std(rr_intervals)
        print(f"- Variabilidad RR: {rr_variability:.3f} s")
        if rr_variability > 0.16:
            print("  - Variabilidad RR aumentada (posible arritmia)")

# Ejemplo de uso
if __name__ == "__main__":
    t, ecg = cargar_ecg("datos_ecg.txt")  # En la práctica, cargaría datos reales
    analizar_ecg(t, ecg)
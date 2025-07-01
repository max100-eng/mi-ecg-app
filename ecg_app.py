import streamlit as st
import neurokit2 as nk
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

st.title("Analizador de ECG")

# Sidebar para parámetros
st.sidebar.header("Parámetros")
duration = st.sidebar.slider("Duración (segundos)", 5, 30, 10)
heart_rate = st.sidebar.slider("Frecuencia cardíaca", 40, 200, 75)
noise = st.sidebar.slider("Nivel de ruido", 0.0, 0.5, 0.05, 0.01)

# Opción para cargar archivo o usar simulación
option = st.sidebar.radio("Fuente de datos", ["Simular ECG", "Cargar archivo"])

if option == "Simular ECG":
    # Simular ECG
    ecg_signal = nk.ecg_simulate(duration=duration, heart_rate=heart_rate, noise=noise)
    sampling_rate = 1000
    st.info(f"ECG simulado: {duration}s, {heart_rate} lpm")
else:
    # Cargar archivo
    uploaded_file = st.sidebar.file_uploader("Cargar archivo CSV de ECG", type=["csv"])
    if uploaded_file is not None:
        try:
            data = pd.read_csv(uploaded_file)
            st.info("Archivo cargado correctamente")
            # Asume que la primera columna es el ECG
            ecg_signal = data.iloc[:, 0].values
            sampling_rate = st.sidebar.number_input("Frecuencia de muestreo (Hz)", 100, 2000, 1000)
        except Exception as e:
            st.error(f"Error al cargar el archivo: {e}")
            st.stop()
    else:
        st.warning("Por favor carga un archivo o selecciona 'Simular ECG'")
        st.stop()

# Procesar la señal
with st.spinner('Procesando señal ECG...'):
    signals, info = nk.ecg_process(ecg_signal, sampling_rate=sampling_rate)
    hrv = nk.hrv(signals, sampling_rate=sampling_rate)

# Extraer métricas clave
metrics = {
    "Frecuencia cardíaca": hrv["HRV_MeanHR"][0],
    "Intervalo QRS (ms)": info["duration_QRS"],
    "Intervalo PR (ms)": info["duration_PR"],
    "Intervalo QT (ms)": info["duration_QT"]
}

# Diagnóstico básico
def interpret_ecg(metrics):
    diagnosis = []
    if metrics["Frecuencia cardíaca"] > 100:
        diagnosis.append("Taquicardia (>100 lpm)")
    elif metrics["Frecuencia cardíaca"] < 60:
        diagnosis.append("Bradicardia (<60 lpm)")
    else:
        diagnosis.append("Ritmo sinusal normal (60-100 lpm)")

    if metrics["Intervalo PR (ms)"] > 200:
        diagnosis.append("Posible bloqueo AV (PR prolongado)")
    
    if metrics["Intervalo QT (ms)"] > 420:
        diagnosis.append("QT prolongado (riesgo de arritmia)")
    
    return diagnosis

diagnosis = interpret_ecg(metrics)

# Visualización
st.header("Visualización del ECG")
fig, ax = plt.subplots(figsize=(12, 6))
nk.ecg_plot(signals, sampling_rate=sampling_rate, ax=ax)
plt.tight_layout()
st.pyplot(fig)

# Mostrar resultados
st.header("Métricas del ECG")
metrics_df = pd.DataFrame({"Valor": [f"{v:.2f}" for v in metrics.values()]}, index=metrics.keys())
st.table(metrics_df)

st.header("Diagnóstico")
for condition in diagnosis:
    st.write(f"- {condition}")

# Añadir opción para descargar resultados
csv = metrics_df.to_csv().encode('utf-8')
st.download_button(
    label="Descargar métricas como CSV",
    data=csv,
    file_name='ecg_metrics.csv',
    mime='text/csv',
)
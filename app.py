import streamlit as st
from dotenv import load_dotenv
load_dotenv() # Carga las variables de entorno desde .env
import neurokit2 as nk
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from io import StringIO

# Configuración de la página de Streamlit
st.set_page_config(
    page_title="Analizador de ECG",
    page_icon="❤️",
    layout="wide" # Utiliza un diseño amplio para mejor visualización
)

# CSS personalizado para mejorar la apariencia de la aplicación
st.markdown("""
<style>
    /* Ajusta el padding superior del contenido principal */
    .main {padding-top: 2rem;}
    /* Ajusta el padding superior del contenido de la barra lateral */
    .sidebar .sidebar-content {padding-top: 2rem;}
    /* Reduce el padding de las alertas para hacerlas más compactas */
    .stAlert {padding: 0.5rem;}
    /* Añade un borde inferior a ciertos elementos de Streamlit (clase interna) */
    .st-bb {border-bottom: 1px solid #eee;}
</style>
""", unsafe_allow_html=True) # Permite la inserción de HTML/CSS

# Título y descripción de la aplicación
st.title("❤️ Analizador de ECG")
st.markdown("""
Esta aplicación analiza señales ECG simuladas o cargadas desde archivos, 
proporcionando métricas clave y diagnóstico básico.
""")

# Barra lateral para la configuración de parámetros
with st.sidebar:
    st.header("⚙️ Parámetros") # Encabezado para la sección de parámetros
    # Slider para la duración de la señal simulada
    duration = st.slider("Duración (segundos)", 5, 30, 10, help="Duración de la señal simulada")
    # Slider para la frecuencia cardíaca de la señal simulada
    heart_rate = st.slider("Frecuencia cardíaca (lpm)", 40, 200, 75)
    # Slider para el nivel de ruido en la señal simulada
    noise = st.slider("Nivel de ruido", 0.0, 0.5, 0.05, 0.01, 
                      help="Intensidad del ruido en la señal simulada")
    
    # Opción para elegir la fuente de datos (simulación o archivo)
    option = st.radio("Fuente de datos", ["Simular ECG", "Cargar archivo"], 
                      help="Elige entre simular una señal o cargar datos reales")

# Función para procesar la señal ECG
@st.cache_data # Cachea los resultados para evitar reprocesar si los inputs no cambian
def process_ecg(ecg_signal, sampling_rate):
    """
    Procesa la señal ECG y extrae métricas utilizando NeuroKit2.
    
    Args:
        ecg_signal (np.array): La señal ECG.
        sampling_rate (int): La frecuencia de muestreo de la señal en Hz.
        
    Returns:
        tuple: Una tupla que contiene:
            - signals (pd.DataFrame): DataFrame con la señal procesada y sus componentes.
            - info (dict): Diccionario con información sobre los picos y duraciones.
            - hrv (pd.DataFrame): DataFrame con las métricas de variabilidad de la frecuencia cardíaca.
    """
    with st.spinner('Procesando señal ECG...'): # Muestra un spinner mientras se procesa
        # Procesa la señal ECG para identificar picos R, segmentos, etc.
        signals, info = nk.ecg_process(ecg_signal, sampling_rate=sampling_rate)
        # Calcula las métricas de variabilidad de la frecuencia cardíaca (HRV)
        hrv = nk.hrv(signals, sampling_rate=sampling_rate)
    return signals, info, hrv

# Función para interpretar el ECG y generar un diagnóstico básico
def interpret_ecg(metrics):
    """
    Genera una interpretación básica del ECG basada en las métricas clave.
    
    Args:
        metrics (dict): Diccionario que contiene las métricas clave del ECG.
        
    Returns:
        list: Una lista de tuplas, donde cada tupla contiene (condición, icono de estado).
    """
    diagnosis = []
    
    # Asegúrate de que la métrica de frecuencia cardíaca exista y no sea NaN
    hr = metrics.get("Frecuencia cardíaca", np.nan)
    
    if not np.isnan(hr):
        # Heart rate analysis
        if hr > 100:
            diagnosis.append(("Taquicardia (>100 lpm)", "⚠️")) # Advertencia
        elif hr < 60:
            diagnosis.append(("Bradicardia (<60 lpm)", "⚠️")) # Advertencia
        else:
            diagnosis.append(("Ritmo sinusal normal (60-100 lpm)", "✅")) # Correcto
    else:
        diagnosis.append(("Frecuencia cardíaca no disponible", "❓"))

    # Análisis del intervalo PR
    pr_interval = metrics.get("Intervalo PR (ms)", np.nan)
    if not np.isnan(pr_interval):
        if pr_interval > 200:
            diagnosis.append(("Posible bloqueo AV (PR prolongado)", "⚠️")) # Advertencia
        elif pr_interval < 120:
            diagnosis.append(("PR corto", "ℹ️")) # Información
    else:
        diagnosis.append(("Intervalo PR no disponible", "❓"))
    
    # Análisis del intervalo QT
    qt = metrics.get("Intervalo QT (ms)", np.nan)
    if not np.isnan(qt):
        if qt > 420:
            diagnosis.append(("QT prolongado (riesgo de arritmia)", "❗")) # Alerta crítica
        elif qt < 350:
            diagnosis.append(("QT corto", "ℹ️")) # Información
    else:
        diagnosis.append(("Intervalo QT no disponible", "❓"))
    
    return diagnosis

# Lógica principal de la aplicación
ecg_signal = None # Inicializa la señal ECG
sampling_rate = None # Inicializa la frecuencia de muestreo

if option == "Simular ECG":
    # Simula la señal ECG usando NeuroKit2
    ecg_signal = nk.ecg_simulate(
        duration=duration, 
        heart_rate=heart_rate, 
        noise=noise,
        sampling_rate=1000 # Frecuencia de muestreo fija para la simulación
    )
    sampling_rate = 1000
    st.success(f"✅ ECG simulado: {duration} segundos, {heart_rate} lpm, ruido: {noise:.2f}")
else: # Si la opción es "Cargar archivo"
    # Manejo de la carga de archivos
    uploaded_file = st.sidebar.file_uploader(
        "Subir archivo CSV/Excel", 
        type=["csv", "xlsx"], # Tipos de archivo permitidos
        help="El archivo debe contener la señal ECG en la primera columna"
    )
    
    if uploaded_file is not None:
        try:
            # Lee el archivo dependiendo de su tipo
            if uploaded_file.name.endswith('.csv'):
                data = pd.read_csv(uploaded_file)
            else: # Asume .xlsx
                data = pd.read_excel(uploaded_file)
            
            # Asume que la primera columna contiene la señal ECG
            ecg_signal = data.iloc[:, 0].values
            # Permite al usuario introducir la frecuencia de muestreo del archivo cargado
            sampling_rate = st.sidebar.number_input(
                "Frecuencia de muestreo (Hz)", 
                100, 2000, 1000, # Rango y valor predeterminado
                help="Frecuencia a la que se adquirió la señal"
            )
            st.success("✅ Archivo cargado correctamente")
        except Exception as e:
            # Muestra un mensaje de error si la carga falla
            st.error(f"❌ Error al cargar el archivo: {str(e)}")
            st.stop() # Detiene la ejecución del script para evitar errores posteriores
    else:
        # Pide al usuario que suba un archivo si no se ha seleccionado ninguno
        st.warning("⚠️ Por favor sube un archivo o selecciona 'Simular ECG'")
        st.stop() # Detiene la ejecución hasta que se cumpla la condición

# Procesa la señal ECG solo si ecg_signal y sampling_rate están definidos
if ecg_signal is not None and sampling_rate is not None:
    try:
        signals, info, hrv = process_ecg(ecg_signal, sampling_rate)
    except Exception as e:
        st.error(f"❌ Error al procesar la señal ECG: {str(e)}")
        st.stop()

    # Extrae las métricas clave del procesamiento de forma robusta
    metrics = {}
    
    # Métricas de HRV (pueden faltar si no se detectan picos R o si hrv está vacío)
    if not hrv.empty:
        metrics["Frecuencia cardíaca"] = hrv.get("HRV_MeanHR", [np.nan])[0]
        metrics["RMSSD (ms)"] = hrv.get("HRV_RMSSD", [np.nan])[0]
        metrics["SDNN (ms)"] = hrv.get("HRV_SDNN", [np.nan])[0]
        metrics["pNN50"] = hrv.get("HRV_pNN50", [np.nan])[0]
        metrics["LF/HF"] = hrv.get("HRV_LFHF", [np.nan])[0]
    else:
        st.warning("No se pudieron calcular las métricas de Variabilidad de Frecuencia Cardíaca (HRV). La señal podría ser de baja calidad o demasiado corta para un análisis HRV completo.")
        metrics["Frecuencia cardíaca"] = np.nan
        metrics["RMSSD (ms)"] = np.nan
        metrics["SDNN (ms)"] = np.nan
        metrics["pNN50"] = np.nan
        metrics["LF/HF"] = np.nan

    # Métricas de la información de procesamiento (info dictionary)
    metrics["Intervalo QRS (ms)"] = info.get("duration_QRS", np.nan)
    metrics["Intervalo PR (ms)"] = info.get("duration_PR", np.nan)
    metrics["Intervalo QT (ms)"] = info.get("duration_QT", np.nan)


    # Muestra los resultados en pestañas para una mejor organización
    tab1, tab2, tab3 = st.tabs(["📈 Visualización", "📊 Métricas", "🩺 Diagnóstico"])

    with tab1:
        # Visualización de la señal ECG procesada
        st.subheader("Señal ECG procesada")
        fig, ax = plt.subplots(figsize=(12, 4)) # Crea una figura de Matplotlib
        # Plotea los primeros 3 segundos de la señal procesada
        # Asegura que signals no esté vacío y contenga la columna 'ECG_Clean'
        if not signals.empty and 'ECG_Clean' in signals.columns:
            nk.ecg_plot(signals[:3000], sampling_rate=sampling_rate, ax=ax) 
            plt.tight_layout() # Ajusta el layout para evitar solapamientos
            st.pyplot(fig) # Muestra la figura en Streamlit
        else:
            st.warning("No se pudo generar la visualización de la señal procesada. La señal podría ser inválida o faltar la columna 'ECG_Clean'.")
            plt.close(fig) # Cierra la figura vacía para liberar memoria
        
        # Opción para mostrar la señal ECG cruda
        if st.checkbox("Mostrar señal ECG cruda"):
            fig_raw, ax_raw = plt.subplots(figsize=(12, 4))
            ax_raw.plot(ecg_signal[:3000]) # Plotea los primeros 3 segundos de la señal cruda
            ax_raw.set_title("Señal ECG cruda")
            ax_raw.set_xlabel("Muestras")
            ax_raw.set_ylabel("Amplitud")
            st.pyplot(fig_raw)

    with tab2:
        # Muestra las métricas clave en un DataFrame
        st.subheader("Métricas clave")
        metrics_df = pd.DataFrame.from_dict(metrics, orient='index', columns=['Valor'])
        st.dataframe(metrics_df.style.format({"Valor": "{:.2f}"})) # Formatea los valores a 2 decimales
        
        # Muestra las métricas de Variabilidad de Frecuencia Cardíaca (HRV)
        st.subheader("Variabilidad de Frecuencia Cardíaca (HRV)")
        # Usa las métricas de HRV ya extraídas en el diccionario 'metrics'
        hrv_metrics_display = {
            "RMSSD": metrics.get("RMSSD (ms)", np.nan),
            "SDNN": metrics.get("SDNN (ms)", np.nan),
            "pNN50": metrics.get("pNN50", np.nan),
            "LF/HF": metrics.get("LF/HF", np.nan)
        }
        st.dataframe(pd.DataFrame.from_dict(hrv_metrics_display, orient='index', columns=['Valor']))

    with tab3:
        # Muestra el diagnóstico básico
        diagnosis = interpret_ecg(metrics)
        
        st.subheader("Interpretación ECG")
        for condition, icon in diagnosis:
            st.markdown(f"{icon} {condition}") # Muestra cada condición con su icono
        
        # Añade recomendaciones generales
        st.subheader("Recomendaciones")
        # Si hay alguna advertencia o alerta crítica, recomienda consulta médica
        if any(icon in ["⚠️", "❗"] for _, icon in diagnosis):
            st.warning("Se recomienda consultar con un cardiólogo para evaluación adicional.")
        else:
            st.success("Los resultados parecen normales. Para una evaluación completa, consulte con su médico.")

    # Opciones de descarga en la barra lateral
    st.sidebar.header("📤 Exportar resultados")
    if st.sidebar.button("Guardar métricas como CSV"):
        # Convierte las métricas a un DataFrame y luego a CSV
        csv = pd.DataFrame.from_dict(metrics, orient='index').to_csv()
        st.sidebar.download_button(
            label="Descargar CSV",
            data=csv,
            file_name='ecg_metrics.csv',
            mime='text/csv'
        )

# Pie de página de la aplicación
st.markdown("---")
st.caption("Aplicación desarrollada para análisis ECG básico. No sustituye evaluación médica profesional.")

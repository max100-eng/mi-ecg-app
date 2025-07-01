import streamlit as st

st.set_page_config(page_title="ECG Cloud - Análisis Cardíaco", layout="centered")

st.title("ECG Cloud")
st.markdown("### Análisis cardíaco avanzado con inteligencia artificial")

st.markdown("""
Analiza tus electrocardiogramas en segundos.  
Nuestra plataforma utiliza algoritmos de última generación para procesar tus registros ECG y detectar anomalías cardíacas con precisión médica.
""")

st.header("¿Listo para analizar tus ECG?")
uploaded_file = st.file_uploader("Sube tu archivo ECG", type=["csv", "txt"])

if uploaded_file is not None:
    st.success("Archivo subido correctamente. (Aquí iría el análisis de ECG)")
    # Aquí puedes agregar el análisis real del archivo ECG
    # Por ejemplo: mostrar gráficos, métricas, etc.
else:
    st.info("Por favor, sube un archivo para comenzar el análisis.")

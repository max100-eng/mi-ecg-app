import streamlit as st
from ecg_analysis import analizar_archivo

st.set_page_config(layout="wide")
archivo = st.file_uploader("Sube tu ECG")
if archivo:
    with st.spinner("Analizando..."):
        resultados, fig = analizar_archivo(archivo)
        st.pyplot(fig)
        st.json(resultados)
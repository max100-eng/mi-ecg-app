import streamlit as st
import asyncio

async def fetch_data_from_api():
    st.write("Conectando a la API...")
    await asyncio.sleep(2) # Simula una llamada a la API
    return "Datos obtenidos de la API"

st.title("Aplicación con operación asíncrona")

if st.button("Obtener Datos"):
    # Solución: Usa 'await' directamente.
    # Streamlit maneja el bucle de eventos.
    data = await fetch_data_from_api()
    st.write(data)

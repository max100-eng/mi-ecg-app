from dotenv import load_dotenv
load_dotenv()
import os
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from google.cloud import aiplatform # Para la integración con Vertex AI
import base64
import json
import logging
import openai # Para el chatbot

# Configurar logging para ver mensajes en la consola del backend
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
# Habilitar CORS para permitir solicitudes desde tu frontend HTML
# En producción, reemplaza "*" con el dominio específico de tu frontend (ej. "https://tu-dominio.com")
CORS(app)

# --- Configuración para Google Cloud Vertex AI ---
# IMPORTANTE: Reemplaza con tu ID de Proyecto de Google Cloud y la Región
PROJECT_ID = os.environ.get('GOOGLE_CLOUD_PROJECT_ID', 'your-google-cloud-project-id')
LOCATION = os.environ.get('GOOGLE_CLOUD_LOCATION', 'us-central1')

# IMPORTANTE: Reemplaza con el ID del Endpoint de tu modelo de Vertex AI desplegado
# Puedes encontrar esto en la Consola de Google Cloud en Vertex AI -> Endpoints
ENDPOINT_ID = os.environ.get('VERTEX_AI_ENDPOINT_ID', 'YOUR_VERTEX_AI_ENDPOINT_ID')

# Inicializar cliente de Vertex AI
vertex_ai_endpoint = None
try:
    if PROJECT_ID != 'your-google-cloud-project-id' and ENDPOINT_ID != 'YOUR_VERTEX_AI_ENDPOINT_ID':
        aiplatform.init(project=PROJECT_ID, location=LOCATION)
        endpoint_name = f"projects/{PROJECT_ID}/locations/{LOCATION}/endpoints/{ENDPOINT_ID}"
        vertex_ai_endpoint = aiplatform.Endpoint(endpoint_name=endpoint_name)
        logging.info(f"Cliente de Vertex AI inicializado y conectado al endpoint: {endpoint_name}")
    else:
        logging.warning("Variables de entorno GOOGLE_CLOUD_PROJECT_ID o VERTEX_AI_ENDPOINT_ID no configuradas. La integración con Vertex AI estará simulada.")
except Exception as e:
    logging.error(f"Error al inicializar el cliente de Vertex AI o conectar al endpoint: {e}")
    vertex_ai_endpoint = None

# --- Configuración para OpenAI (Chatbot) ---
# IMPORTANTE: Obtén tu clave de API de OpenAI y configúrala como variable de entorno
# No la pongas directamente en el código en producción
openai.api_key = os.environ.get('OPENAI_API_KEY', 'tu-api-key-de-openai')
if openai.api_key == 'tu-api-key-de-openai':
    logging.warning("OPENAI_API_KEY no configurada como variable de entorno. El chatbot de OpenAI usará una clave de placeholder (no funcionará sin una clave real).")


# --- Rutas de la Aplicación Flask ---

# Ruta principal (puedes usarla para servir tu index.html si lo deseas, o dejarlo como una API simple)
@app.route('/')
def home():
    # Esto es solo un ejemplo. Tu frontend HTML ya sirve la interfaz principal.
    return "Backend de ECG Cloud funcionando. Accede a la interfaz de usuario a través de tu archivo index.html."

# Ruta para analizar ECG (recibe imágenes del frontend)
@app.route('/analyze-ecg', methods=['POST'])
def analyze_ecg():
    if 'ecg_image' not in request.files:
        return jsonify({'error': 'No se encontró la imagen de ECG en la solicitud'}), 400

    ecg_files = request.files.getlist('ecg_image')

    if not ecg_files:
        return jsonify({'error': 'No se encontraron archivos válidos para procesar'}), 400

    results = []
    for ecg_file in ecg_files:
        file_name = ecg_file.filename
        file_bytes = ecg_file.read()

        try:
            if vertex_ai_endpoint:
                # --- Preparar la imagen para la Predicción de Vertex AI ---
                # La mayoría de los modelos de imagen de Vertex AI esperan bytes codificados en base64
                encoded_image_string = base64.b64encode(file_bytes).decode("utf-8")

                # La estructura de 'instances' depende de la firma de entrada de tu modelo.
                # Para clasificación/detección de imágenes, comúnmente es una clave 'bytes_base64'.
                instances = [
                    {"bytes_base64": encoded_image_string}
                ]

                logging.info(f"Enviando solicitud de predicción para {file_name} a Vertex AI...")
                prediction_response = vertex_ai_endpoint.predict(instances=instances)
                logging.info(f"Respuesta de predicción recibida para {file_name}.")

                # --- Procesar la respuesta de predicción ---
                # La estructura de prediction_response.predictions depende COMPLETAMENTE de la salida de tu modelo.
                # Este es un ejemplo para un modelo de clasificación de imágenes típico (como AutoML Vision)
                
                if prediction_response.predictions:
                    prediction_data = prediction_response.predictions[0] # Asumiendo una sola imagen por solicitud

                    diagnosis = "No se pudo determinar el diagnóstico."
                    metrics = {}

                    if "display_names" in prediction_data and "confidences" in prediction_data:
                        display_names = prediction_data["display_names"]
                        confidences = prediction_data["confidences"]
                        
                        # Encontrar la clase con la mayor confianza
                        max_confidence_index = confidences.index(max(confidences))
                        diagnosis = display_names[max_confidence_index]
                        
                        metrics = {
                            "predicted_class": diagnosis,
                            "confidence": f"{confidences[max_confidence_index]:.4f}",
                            "all_confidences": dict(zip(display_names, [f"{c:.4f}" for c in confidences]))
                        }
                    elif isinstance(prediction_data, dict):
                        # Si la salida de tu modelo es un diccionario personalizado (ej. de un modelo Keras personalizado)
                        # Deberás parsearlo según la capa de salida de tu modelo
                        diagnosis = prediction_data.get("label", "Diagnóstico personalizado no encontrado")
                        metrics = prediction_data.get("details", {})
                    else:
                        # Fallback para formato de salida inesperado
                        diagnosis = "Formato de predicción desconocido."
                        metrics = {"raw_prediction": prediction_data}

                    results.append({
                        'file_name': file_name,
                        'status': 'success',
                        'diagnosis': diagnosis,
                        'metrics': metrics,
                        'message': 'Análisis completado con éxito por Vertex AI.'
                    })
                else:
                    results.append({
                        'file_name': file_name,
                        'status': 'warning',
                        'message': 'Vertex AI no retornó predicciones para esta imagen.'
                    })
            else:
                # --- Simulación si Vertex AI no está configurado ---
                simulated_diagnosis = "Ritmo Sinusal Normal (Simulado)"
                simulated_metrics = {
                    "heart_rate": 75,
                    "pr_interval": "160ms",
                    "qrs_duration": "90ms",
                    "qt_interval": "380ms",
                    "rhythm_variability": "Normal"
                }
                if "abnormal" in file_name.lower() or "arritmia" in file_name.lower():
                    simulated_diagnosis = "Posible Arritmia Detectada (Simulado)"
                    simulated_metrics["heart_rate"] = 130
                    simulated_metrics["rhythm_variability"] = "Irregular"

                results.append({
                    'file_name': file_name,
                    'status': 'success',
                    'diagnosis': simulated_diagnosis,
                    'metrics': simulated_metrics,
                    'message': 'Análisis simulado. Configura Vertex AI para resultados reales.'
                })

        except Exception as e:
            logging.error(f"Error al procesar el archivo {file_name} con Vertex AI/Simulación: {e}")
            results.append({
                'file_name': file_name,
                'status': 'error',
                'error': str(e),
                'message': 'Error al comunicarse con Vertex AI o al procesar la imagen.'
            })

    return jsonify(results), 200

# Ruta para el Chatbot con IA (OpenAI)
@app.route('/ask-chatbot', methods=['POST'])
def ask_chatbot():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "Mensaje de usuario no proporcionado"}), 400

    if not openai.api_key or openai.api_key == 'tu-api-key-de-openai':
        return jsonify({"error": "La clave de API de OpenAI no está configurada en el backend."}), 500

    try:
        logging.info(f"Recibiendo mensaje para chatbot: {user_message}")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", # Puedes usar "gpt-4" o "gpt-4o" si tienes acceso
            messages=[{"role": "user", "content": user_message}]
        )
        chatbot_response = response.choices[0].message['content']
        logging.info(f"Respuesta del chatbot: {chatbot_response}")
        return jsonify({"response": chatbot_response})
    except Exception as e:
        logging.error(f"Error al comunicarse con la API de OpenAI: {e}")
        return jsonify({"error": f"Error al obtener respuesta del chatbot: {str(e)}"}), 500

# --- Punto de entrada para ejecutar la aplicación Flask ---
if __name__ == '__main__':
    # Para desarrollo, ejecuta con debug=True.
    # En producción, usa un servidor WSGI como Gunicorn (ej: gunicorn -w 4 -b 0.0.0.0:5000 app:app)
    app.run(debug=True, host='0.0.0.0', port=5000)



            
    
    

    


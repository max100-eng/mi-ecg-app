from flask import Flask, request, jsonify, render_template
import wfdb
import neurokit2 as nk
import os
import openai  # Para el chatbot (opcional)

app = Flask(__name__)

# Clave de OpenAI (opcional, para el chatbot)
openai.api_key = "tu-api-key-de-openai"  # Reemplaza con tu clave

# Ruta principal
from flask import Flask
app = Flask(__name__)  # Primero esto

@app.route('/')       # Luego las rutas
def home():
    return "Hola Mundo"

from flask import Flask  # Los imports deben estar AL PRINCIPIO del archivo

# ... resto de tu código ...

if __name__ == '__main__':
    app.run()  # Esto debe estar al FINAL del archivo

@app.route('/')       # Luego las rutas
def home():
    return "Hola Mundo"

if __name__ == '__main__':
    app.run()
def home():
    return render_template('index.html')

# Analizar ECG desde PhysioNet o archivo local
@app.route('/analyze-ecg', methods=['POST'])
def analyze_ecg():
    data = request.json
    if 'record_name' in data:  # Si es un registro de PhysioNet
        try:
            record = wfdb.rdrecord(data['record_name'], pb_dir='mitdb')
            ecg_signal = record.p_signal[:, 0]
            sampling_rate = record.fs
        except Exception as e:
            return jsonify({"error": f"Error al descargar el registro: {str(e)}"}), 500
    else:  # Si es un archivo local (simulado aquí)
        return jsonify({"error": "Sube un archivo primero"}), 400

    # Procesar ECG con NeuroKit2
    signals, info = nk.ecg_process(ecg_signal, sampling_rate=sampling_rate)
    return jsonify({
        "heart_rate": info['heart_rate'],
        "diagnosis": "Normal" if 60 <= info['heart_rate'] <= 100 else "Posible arritmia",
        "intervals": {"PR": 160, "QRS": 88, "QT": 380}  # Datos simulados
    })

# Chatbot con IA (OpenAI)
@app.route('/ask-chatbot', methods=['POST'])
def ask_chatbot():
    user_message = request.json.get('message')
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_message}]
    )
    return jsonify({"response": response.choices[0].message['content']})

if __name__ == '__main__':
    app.run(debug=True)



from flask import Flask
app = Flask(__name__)  # Primero esto
from flask import Flask

app = Flask(__name__)

# Ruta básica que responde a la URL raíz "/"
@app.route('/')
def home():
    return '¡Hola, mundo!'

if __name__ == '__main__':
    app.run(debug=True)

    from flask import Flask, request, render_template_string

app = Flask(__name__)

# Ruta con formulario
@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    mensaje = ''
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        mensaje = f'¡Hola, {nombre}!'
    return render_template_string('''
        <form method="post">
            Nombre: <input type="text" name="nombre">
            <input type="submit" value="Enviar">
        </form>
        <p>{{ mensaje }}</p>
    ''', mensaje=mensaje)

if __name__ == '__main__':
    app.run(debug=True)
    
    

    


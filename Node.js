// server.js
// Este es el archivo principal de tu aplicación backend.

// 1. Importar módulos necesarios
const express = require('express'); // Framework web para Node.js
const cors = require('cors');     // Middleware para manejar CORS (Cross-Origin Resource Sharing)
const multer = require('multer'); // Middleware para manejar la subida de archivos (multipart/form-data)
const path = require('path');     // Módulo para manejar rutas de archivos y directorios

// 2. Inicializar la aplicación Express
const app = express();

// 3. Configurar el puerto del servidor
// Usa el puerto proporcionado por el entorno (ej. Render, Vercel) o 3000 por defecto para desarrollo local.
const PORT = process.env.PORT || 3000;

// 4. Configuración de CORS
// Es crucial para permitir que tu frontend (servido desde un dominio diferente)
// pueda hacer peticiones a este backend.
const allowedOrigin = process.env.CORS_ORIGIN || 'http://localhost:8080'; // Reemplaza con la URL de tu frontend en producción
// En producción, CORS_ORIGIN debe ser la URL COMPLETA de tu frontend (ej. https://tu-app-frontend.vercel.app)
// En desarrollo, puede ser http://localhost:puerto_de_tu_frontend (ej. 8080, 3000, 5000)

const corsOptions = {
  origin: allowedOrigin,
  methods: 'GET,HEAD,PUT,PATCH,POST,DELETE', // Permite los métodos HTTP que usarás
  credentials: true, // Si tu frontend necesita enviar cookies o credenciales (ej. tokens de autenticación)
  optionsSuccessStatus: 204 // Para algunas peticiones preflight OPTIONS (necesario para CORS)
};

// Aplica el middleware CORS a todas las rutas
app.use(cors(corsOptions));
console.log(`CORS configurado para el origen: ${allowedOrigin}`);

// 5. Configuración de Multer para la subida de archivos
// Define dónde se guardarán temporalmente los archivos subidos.
// En un entorno serverless o con plataformas como Render, no guardarás archivos en disco
// de forma persistente, sino que los procesarás directamente en memoria.
const storage = multer.memoryStorage(); // Guarda el archivo en memoria como un Buffer
const upload = multer({ storage: storage });

// 6. Ruta principal (opcional, para verificar que el servidor está funcionando)
app.get('/', (req, res) => {
  res.send('ECG Vision AI Backend está funcionando. Envía una imagen a /api/analyze-ecg');
});

// 7. Ruta para el análisis de ECG
// 'upload.single('ecgImage')' es el middleware de Multer que procesa un solo archivo
// con el nombre de campo 'ecgImage' (¡debe coincidir con el formData.append en tu frontend!)
app.post('/api/analyze-ecg', upload.single('ecgImage'), async (req, res) => {
  console.log('Petición recibida en /api/analyze-ecg');

  // Verifica si se recibió un archivo
  if (!req.file) {
    console.error('Error: No se proporcionó ningún archivo de imagen.');
    return res.status(400).json({ error: 'No se proporcionó ningún archivo de imagen.' });
  }

  // Accede al archivo subido (está en req.file.buffer si usas memoryStorage)
  const ecgImageBuffer = req.file.buffer;
  const mimeType = req.file.mimetype;
  const originalname = req.file.originalname;

  console.log(`Archivo recibido: ${originalname} (${mimeType}, ${ecgImageBuffer.length} bytes)`);

  // --- SIMULACIÓN DEL ANÁLISIS DE IA ---
  // Aquí es donde normalmente integrarías tu modelo de IA.
  // Por ejemplo, enviarías 'ecgImageBuffer' a una API de Google AI Platform,
  // AWS Rekognition, o un modelo custom desplegado.

  // Para esta simulación, esperaremos un poco y generaremos un resultado ficticio.
  try {
    await new Promise(resolve => setTimeout(resolve, 2000)); // Simula un retardo de 2 segundos para el análisis

    const simulatedInterpretation = `
      --- Informe de Análisis de ECG (Simulado por IA) ---

      **Paciente:** Desconocido
      **Fecha del Análisis:** ${new Date().toLocaleDateString('es-ES')}
      **Hora del Análisis:** ${new Date().toLocaleTimeString('es-ES')}
      **Archivo Procesado:** ${originalname}

      **Resultados Principales:**
      - **Ritmo Cardíaco:** Sinusal regular
      - **Frecuencia Cardíaca:** 75 lpm (latidos por minuto)
      - **Intervalo PR:** 0.16s (Normal)
      - **Duración QRS:** 0.08s (Normal)
      - **Intervalo QT/QTc:** 0.38s / 0.42s (Normal)
      - **Eje QRS:** +60 grados (Normal)

      **Hallazgos Clave (Simulados):**
      - No se detectan arritmias significativas.
      - Ausencia de signos de isquemia aguda.
      - Morfología de ondas P, QRS y T dentro de los límites normales.
      - No hay evidencia de hipertrofia ventricular.

      **Recomendaciones (Simuladas):**
      - Monitoreo de rutina.
      - En caso de síntomas, consultar a un especialista.

      --- Fin del Informe ---
    `;

    // Envía la respuesta JSON al frontend
    res.json({
      message: 'Análisis de ECG completado con éxito (simulado).',
      interpretation: simulatedInterpretation,
      // Puedes enviar más datos si tu IA los generara, como métricas, gráficos, etc.
      // rawData: ecgImageBuffer.toString('base64') // Si quisieras devolver el base64 de la imagen (no recomendado para grandes archivos)
    });

  } catch (error) {
    console.error('Error durante el análisis simulado:', error);
    res.status(500).json({ error: 'Error interno del servidor durante el análisis simulado.' });
  }
});

// 8. Iniciar el servidor
app.listen(PORT, () => {
  console.log(`Servidor backend escuchando en el puerto ${PORT}`);
  console.log(`Accede a http://localhost:${PORT} en desarrollo.`);
});
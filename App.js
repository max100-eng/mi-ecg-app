import React, { useState, useEffect, useRef } from 'react';

// Main App Component
const App = () => {
    // State to manage the current view: 'landing' or 'analysis'
    const [view, setView] = useState('landing');
    // State for the uploaded ECG image
    const [ecgImage, setEcgImage] = useState(null);
    // State for the AI analysis input (textual findings)
    const [aiInput, setAiInput] = useState('');
    // State for the AI generated analysis result
    const [aiResult, setAiResult] = useState('');
    // State for loading status during AI analysis
    const [loading, setLoading] = useState(false);
    // State for error messages
    const [error, setError] = useState('');
    // Ref for the hidden file input
    const fileInputRef = useRef(null);

    // --- File Upload Handlers ---
    const handleFileChange = (event) => {
        const file = event.target.files[0];
        if (file) {
            // Check if the file is an image
            if (!file.type.startsWith('image/')) {
                setError('Por favor, sube solo archivos de imagen (PNG, JPG, JPEG, GIF).');
                setEcgImage(null);
                return;
            }
            const reader = new FileReader();
            reader.onloadend = () => {
                setEcgImage(reader.result); // Set the base64 string of the image
                setError('');
            };
            reader.readAsDataURL(file); // Read the file as a data URL (base64)
        }
    };

    const handleDragOver = (event) => {
        event.preventDefault(); // Prevent default to allow drop
    };

    const handleDrop = (event) => {
        event.preventDefault();
        const file = event.dataTransfer.files[0];
        if (file) {
            if (!file.type.startsWith('image/')) {
                setError('Por favor, sube solo archivos de imagen (PNG, JPG, JPEG, GIF).');
                setEcgImage(null);
                return;
            }
            const reader = new FileReader();
            reader.onloadend = () => {
                setEcgImage(reader.result);
                setError('');
            };
            reader.readAsDataURL(file);
        }
    };

    const handleClickUploadArea = () => {
        fileInputRef.current.click(); // Programmatically click the hidden file input
    };

    // --- AI Analysis Handler ---
    const handleAnalyzeEcg = async () => {
        if (!ecgImage || !aiInput.trim()) {
            setError('Por favor, sube una imagen de ECG e ingresa algunos hallazgos para el análisis.');
            return;
        }

        setLoading(true);
        setAiResult('');
        setError('');

        try {
            // Prepare the prompt for the AI model
            const prompt = `Analiza los siguientes hallazgos de electrocardiograma y proporciona una interpretación concisa y fácil de entender. Incluye posibles implicaciones y sugerencias generales (no médicas) si hay algo inusual. Los hallazgos son: "${aiInput}". IMPORTANTE: ESTO ES UNA SIMULACIÓN. No uses jerga médica compleja, y siempre añade un recordatorio de que esto no sustituye un diagnóstico médico profesional.`;

            let chatHistory = [];
            chatHistory.push({ role: "user", parts: [{ text: prompt }] });

            const payload = {
                contents: chatHistory,
                generationConfig: {
                    temperature: 0.7, // Adjust creativity
                    maxOutputTokens: 500 // Limit output length
                }
            };

            const apiKey = ""; // Canvas will provide this key at runtime
            const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;

            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (result.candidates && result.candidates.length > 0 &&
                result.candidates[0].content && result.candidates[0].content.parts &&
                result.candidates[0].content.parts.length > 0) {
                const text = result.candidates[0].content.parts[0].text;
                setAiResult(text);
            } else {
                setError('Error al obtener la respuesta de la IA. Inténtalo de nuevo.');
                console.error('Unexpected AI response structure:', result);
            }
        } catch (err) {
            setError('Error de conexión o de la IA. Por favor, revisa tu red e inténtalo de nuevo.');
            console.error('Fetch error:', err);
        } finally {
            setLoading(false);
        }
    };

    // --- Render Logic ---
    return (
        <div className="min-h-screen bg-gray-50 font-inter text-gray-800 p-4 flex flex-col items-center">
            {/* Disclaimer for medical use */}
            <div className="w-full max-w-4xl bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded-md shadow-sm mb-6" role="alert">
                <p className="font-bold">Aviso Importante:</p>
                <p className="text-sm">Esta aplicación es una **demostración simulada** y **NO debe utilizarse para diagnósticos médicos reales**. Siempre consulta a un profesional de la salud cualificado para cualquier preocupación médica.</p>
            </div>

            {view === 'landing' ? (
                // Landing Page View
                <div className="w-full max-w-4xl bg-white rounded-xl shadow-lg p-8 space-y-8 animate-fade-in">
                    <h1 className="text-4xl md:text-5xl font-extrabold text-center text-teal-700 leading-tight mb-4">
                        Analiza tus electrocardiogramas en segundos
                    </h1>
                    <p className="text-lg text-center text-gray-600 mb-8">
                        Nuestra plataforma utiliza algoritmos de última generación para procesar tus registros ECG y detectar anomalías cardíacas con precisión médica.
                    </p>

                    {/* File Upload Area */}
                    <div
                        className="w-full h-80 border-4 border-dashed border-gray-300 rounded-2xl flex flex-col items-center justify-center text-gray-500 cursor-pointer hover:border-teal-500 hover:text-teal-600 transition-all duration-300 relative overflow-hidden"
                        onDragOver={handleDragOver}
                        onDrop={handleDrop}
                        onClick={handleClickUploadArea}
                    >
                        {ecgImage ? (
                            <img src={ecgImage} alt="ECG Preview" className="max-w-full max-h-full object-contain rounded-xl shadow-md" />
                        ) : (
                            <>
                                <svg
                                    className="w-20 h-20 mb-4"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                    xmlns="http://www.w3.org/2000/svg"
                                >
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth="1.5"
                                        d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                                    ></path>
                                </svg>
                                <p className="text-xl font-semibold">Arrastra y suelta tu archivo ECG aquí</p>
                                <p className="text-md">o haz clic para seleccionar</p>
                            </>
                        )}
                        <input
                            type="file"
                            ref={fileInputRef}
                            onChange={handleFileChange}
                            className="hidden"
                            accept="image/*"
                        />
                    </div>
                    {error && <p className="text-red-500 text-center mt-2">{error}</p>}

                    {/* Button to proceed to analysis */}
                    <button
                        onClick={() => {
                            if (ecgImage) {
                                setView('analysis');
                                setError('');
                            } else {
                                setError('Por favor, sube una imagen de ECG primero para abrir la aplicación completa.');
                            }
                        }}
                        className="w-full py-4 px-6 bg-teal-600 text-white text-xl font-bold rounded-xl shadow-lg hover:bg-teal-700 transition-colors duration-300 focus:outline-none focus:ring-4 focus:ring-teal-300 disabled:opacity-50 disabled:cursor-not-allowed"
                        disabled={!ecgImage} // Disable if no image is uploaded
                    >
                        Abrir Aplicación Completa
                    </button>

                    {/* Feature Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
                        <div className="bg-gradient-to-br from-teal-50 to-teal-100 p-6 rounded-xl shadow-md text-center flex flex-col items-center transform hover:scale-105 transition-transform duration-300">
                            <span className="mb-4 text-teal-600 text-5xl">🫀</span> {/* Heart emoji as icon */}
                            <h3 className="text-xl font-semibold text-teal-800 mb-2">Diagnóstico Automático</h3>
                            <p className="text-gray-700">Identificación automática de taquicardias, bradicardias y arritmias comunes.</p>
                        </div>
                        <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-xl shadow-md text-center flex flex-col items-center transform hover:scale-105 transition-transform duration-300">
                            <span className="mb-4 text-blue-600 text-5xl">📊</span> {/* Chart emoji as icon */}
                            <h3 className="text-xl font-semibold text-blue-800 mb-2">Visualización Profesional</h3>
                            <p className="text-gray-700">Gráficos interactivos que muestran todos los componentes de tu ECG (onda P, complejo QRS, onda T).</p>
                        </div>
                        <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-xl shadow-md text-center flex flex-col items-center transform hover:scale-105 transition-transform duration-300">
                            <span className="mb-4 text-purple-600 text-5xl">🔬</span> {/* Microscope emoji as icon */}
                            <h3 className="text-xl font-semibold text-purple-800 mb-2">Análisis Detallado</h3>
                            <p className="text-gray-700">Métricas precisas de frecuencia cardíaca, intervalos RR y variabilidad del ritmo.</p>
                        </div>
                    </div>

                    {/* Bottom Call to Action */}
                    <div className="bg-teal-50 p-8 rounded-xl shadow-inner mt-12 text-center">
                        <h2 className="text-3xl font-bold text-teal-800 mb-4">¿Listo para analizar tus ECG?</h2>
                        <p className="text-lg text-gray-700 mb-6">
                            Sube tu archivo y obtén resultados instantáneos sin necesidad de instalación.
                        </p>
                        <button
                            onClick={() => {
                                if (ecgImage) {
                                    setView('analysis');
                                    setError('');
                                } else {
                                    setError('Por favor, sube una imagen de ECG primero para comenzar el análisis.');
                                }
                            }}
                            className="py-3 px-8 bg-teal-600 text-white text-lg font-bold rounded-full shadow-lg hover:bg-teal-700 transition-colors duration-300 focus:outline-none focus:ring-4 focus:ring-teal-300 disabled:opacity-50 disabled:cursor-not-allowed"
                            disabled={!ecgImage} // Disable if no image is uploaded
                        >
                            Comenzar Análisis
                        </button>
                    </div>
                </div>
            ) : (
                // Analysis Page View
                <div className="w-full max-w-5xl bg-white rounded-xl shadow-lg p-8 space-y-8 animate-fade-in">
                    <h2 className="text-4xl font-extrabold text-center text-teal-700 mb-6">Resultados del Análisis de ECG (Simulado)</h2>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        {/* ECG Image Display Section */}
                        <div className="flex flex-col items-center bg-gray-50 p-6 rounded-xl shadow-inner">
                            <h3 className="text-2xl font-semibold text-gray-700 mb-4">Imagen de ECG Subida</h3>
                            {ecgImage ? (
                                <img src={ecgImage} alt="ECG Uploaded" className="w-full max-h-96 object-contain rounded-lg shadow-md border border-gray-200" />
                            ) : (
                                <div className="w-full h-64 bg-gray-200 flex items-center justify-center text-gray-500 rounded-lg">
                                    No se ha subido ninguna imagen de ECG.
                                </div>
                            )}
                            <button
                                onClick={() => setView('landing')}
                                className="mt-6 py-2 px-6 bg-gray-200 text-gray-700 rounded-full hover:bg-gray-300 transition-colors duration-200"
                            >
                                Cambiar Imagen / Volver
                            </button>
                        </div>

                        {/* AI Analysis Section */}
                        <div className="flex flex-col bg-gray-50 p-6 rounded-xl shadow-inner">
                            <h3 className="text-2xl font-semibold text-gray-700 mb-4">Introducir Hallazgos para Análisis de IA</h3>
                            <textarea
                                className="w-full h-32 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-all duration-200 text-gray-700"
                                placeholder="Ej: Ritmo irregular, latidos rápidos ocasionales, sensación de palpitaciones."
                                value={aiInput}
                                onChange={(e) => setAiInput(e.target.value)}
                            ></textarea>

                            <button
                                onClick={handleAnalyzeEcg}
                                className="mt-4 py-3 px-6 bg-teal-600 text-white text-lg font-bold rounded-xl shadow-lg hover:bg-teal-700 transition-colors duration-300 focus:outline-none focus:ring-4 focus:ring-teal-300 disabled:opacity-50 disabled:cursor-not-allowed"
                                disabled={loading || !aiInput.trim()}
                            >
                                {loading ? (
                                    <span className="flex items-center justify-center">
                                        <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                        </svg>
                                        Analizando...
                                    </span>
                                ) : (
                                    'Obtener Análisis de IA'
                                )}
                            </button>
                            {error && <p className="text-red-500 text-center mt-2">{error}</p>}

                            {aiResult && (
                                <div className="mt-6 bg-white p-6 rounded-xl shadow-md border border-gray-200">
                                    <h4 className="text-xl font-semibold text-teal-800 mb-3">Interpretación de la IA:</h4>
                                    <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">{aiResult}</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default App;
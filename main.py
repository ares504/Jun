from flask import Flask, request, jsonify
import requests

app = Flask(name)

# --- CONFIGURACIÓN (Pon tus datos aquí) ---
GROQ_API_KEY = "TU_API_KEY_DE_GROQ"
# Si vas a usar Telegram, pon el Token aquí. Si no, déjalo vacío por ahora.
TELEGRAM_TOKEN = "TU_TOKEN_DE_TELEGRAM" 

# Esta variable guardará la última respuesta para que tu Motorola la lea
buzon_voz = {"mensaje": ""}

@app.route('/')
def home():
    return "Servidor de Rebelde Activo"

# RUTA PARA EL MOTOROLA (CLIENTE)
@app.route('/leer', methods=['GET'])
def leer():
    # El celular llama aquí para sacar el texto
    res = buzon_voz["mensaje"]
    buzon_voz["mensaje"] = "" # Limpiamos el buzón tras leer
    return jsonify({"texto": res})

# RUTA PARA ENVIAR MENSAJES (WEBHOOK O PRUEBA)
@app.route('/hablar', methods=['POST'])
def hablar_desde_nube():
    data = request.json
    pregunta = data.get("pregunta", "")
    
    # 1. Consultar a Groq
    url_groq = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "Eres Rebelde, una IA cínica y sarcástica de La Ceiba. Responde corto."},
            {"role": "user", "content": pregunta}
        ]
    }
    
    response = requests.post(url_groq, json=payload, headers=headers).json()
    respuesta_ia = response['choices'][0]['message']['content']
    
    # 2. Guardar en el buzón para el Motorola
    buzon_voz["mensaje"] = respuesta_ia
    
    return jsonify({"status": "sent", "respuesta": respuesta_ia})

if name == "main":
    app.run(host='0.0.0.0', port=5000)
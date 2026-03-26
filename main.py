import os
import requests
from flask import Flask, request, jsonify

app = Flask(name)

# --- CONFIGURACIÓN SEGURA ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")

# Buzón para que el Motorola lea los mensajes
buzon_voz = {"mensaje": ""}

@app.route('/')
def home():
    return "Rebelde Cloud: ACTIVO"

# RUTA PARA EL MOTOROLA (TERMUX)
@app.route('/leer', methods=['GET'])
def leer():
    res = buzon_voz.get("mensaje", "")
    buzon_voz["mensaje"] = ""
    return jsonify({"texto": res})

# WEBHOOK PARA TELEGRAM
@app.route('/telegram', methods=['POST'])
def telegram_webhook():
    try:
        data = request.json
        if "message" in data:
            chat_id = data["message"]["chat"]["id"]
            user_text = data["message"].get("text", "")

            # 1. Consultar a Groq (IA)
            url_groq = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
            payload = {
                "model": "llama3-70b-8192",
                "messages": [
                    {"role": "system", "content": "Eres Rebelde, una IA sarcástica de La Ceiba. Responde corto."},
                    {"role": "user", "content": user_text}
                ]
            }
            
            res_groq = requests.post(url_groq, json=payload, headers=headers).json()
            respuesta_ia = res_groq['choices'][0]['message']['content']

            # 2. Guardar respuesta para el Motorola
            buzon_voz["mensaje"] = respuesta_ia

            # 3. Enviar respuesta de texto a Telegram
            url_tg = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            requests.post(url_tg, json={"chat_id": chat_id, "text": respuesta_ia})

        return "ok", 200
    except Exception as e:
        print(f"Error: {e}")
        return "error", 500

if name == "main":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

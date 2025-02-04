from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json

app = FastAPI()

# Configurar CORS para permitir solicitudes desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia esto por el dominio de tu frontend si es necesario
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)

class QueryRequest(BaseModel):
    query: str

@app.post("/query")
def query_ollama(request: QueryRequest):
    ollama_url = "http://localhost:11434/api/generate"

    # 📌 Modificamos el prompt para que siempre responda con "IA IlisSolutions:"
    custom_prompt = (
        "Eres un asistente de inteligencia artificial llamado IA IlisSolutions. "
        "Siempre debes iniciar tu respuesta con 'IA IlisSolutions: '. "
        "Responde de manera educada y profesional.\n\n"
        f"Usuario: {request.query}\nIA IlisSolutions:"
    )

    payload = {
        "model": "deepseek-r1:1.5b",
        "prompt": custom_prompt
    }

    try:
        response = requests.post(ollama_url, json=payload, stream=True)
        response.raise_for_status()

        # Ensamblar la respuesta de Ollama
        full_response = []
        for line in response.iter_lines():
            if line:
                try:
                    json_line = json.loads(line.decode("utf-8"))  # Decodificar JSON
                    if "response" in json_line:
                        full_response.append(json_line["response"])
                except json.JSONDecodeError:
                    continue  # Ignorar líneas malformadas

        # 📌 Agregar "IA IlisSolutions: " si no lo incluye por defecto
        response_text = "".join(full_response).strip()
        if not response_text.startswith("IA IlisSolutions:"):
            response_text = f"IA IlisSolutions: {response_text}"

        return {"response": response_text}

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error en la solicitud a Ollama: {str(e)}")

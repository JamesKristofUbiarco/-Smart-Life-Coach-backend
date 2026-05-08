from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI,HTTPException, Request
from Esquemas import ChatPayload, CoachResponse
import asyncio
from datetime import datetime, timezone
import uuid
from fastapi.responses import StreamingResponse
import httpx

# 🧪 LAB: Importar módulos de laboratorio
from lab.stream_v6 import generar_respuesta_v6, STREAM_HEADERS
from lab.crud_planes import router as planes_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

async def generar_respuesta(texto: str):
    # 1. En la v5, necesitamos generar un ID único para el mensaje
    msg_id = f"msg_{uuid.uuid4().hex}"
    
    # 2. Evento de inicio (Server-Sent Event format)
    yield f'data: {{"type":"text-start","id":"{msg_id}"}}\n\n'
    
    # 3. Eventos de escritura (delta) letra por letra o palabra por palabra
    palabras = texto.split(" ")
    for palabra in palabras:
        yield f'data: {{"type":"text-delta","id":"{msg_id}","delta":"{palabra} "}}\n\n'
        await asyncio.sleep(0.1)
        
    # 4. Evento de fin
    yield f'data: {{"type":"text-end","id":"{msg_id}"}}\n\n'

@app.post("/Chat")
async def recibir_mensaje(request:Request):
    cuerpo = await request.json()
    print(cuerpo)
    mensajes= cuerpo.get("messages",[])
    print(f"\n{mensajes}")

    # Extraer el último mensaje del usuario
    texto_recibido = "(sin mensaje)"
    if mensajes:
        ultimo_mensaje=mensajes[-1]
        partes= ultimo_mensaje.get("parts",[])
        if partes:
            texto_recibido = partes[0].get("text","")
            print(f"Mensaje recibido: {texto_recibido}")

    # Intentar llamar al AI-component (puerto 8001)
    try:
        url = "http://localhost:8001/chat"
        payload = ChatPayload(
                    id="123",
                    messages=[
                        {
                            "id": str(uuid.uuid4()),
                            "role": "user",
                            "parts": [
                                {
                                    "type": "text",
                                    "text": texto_recibido
                                }
                            ]
                        }
                    ],
                    trigger="chat",
                    user_name="Jose",
                    age=22
                )
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload.model_dump())
        if response.status_code != 200:
            raise Exception(f"AI-component respondió {response.status_code}")
        coach = CoachResponse(**response.json())
        respuesta_texto = coach.summary
    except Exception as e:
        # 🧪 LAB: Si el AI-component no está disponible, devolver echo diagnóstico
        print(f"⚠️ AI-component no disponible ({e}), usando echo diagnóstico")
        roles = [m.get("role", "?") for m in mensajes]
        respuesta_texto = (
            f"✅ **Echo diagnóstico** (AI-component no conectado)\n\n"
            f'Tu mensaje: *"{texto_recibido}"*\n\n'
            f"| Campo | Valor |\n"
            f"|-------|-------|\n"
            f"| Mensajes en historial | {len(mensajes)} |\n"
            f"| Roles | {', '.join(roles)} |\n"
            f"| AI-component | ❌ No disponible |\n"
            f"| Stream | ✅ AI SDK v6 |\n\n"
            f"> Cuando el AI-component esté corriendo en el puerto 8001, "
            f"verás la respuesta real de Gemini aquí."
        )

    # 🧪 LAB: Usar stream v6 en vez del formato antiguo
    return StreamingResponse(
        generar_respuesta_v6(respuesta_texto),
        headers=STREAM_HEADERS,
        media_type="text/event-stream"
    )


# 🧪 LAB: Registrar el router de CRUD con Supabase (reemplaza el mock_db)
app.include_router(planes_router)

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI,HTTPException, Request
from Esquemas import ChatPayload, CoachResponse
import asyncio
from datetime import datetime, timezone
import uuid
from fastapi.responses import StreamingResponse
import httpx
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

from lab.crud_chat import router as chat_router
from lab.supabase_client import get_supabase

@app.post("/Chat")
async def recibir_mensaje(request:Request):
    cuerpo = await request.json()
    mensajes= cuerpo.get("messages",[])
    session_id = cuerpo.get("session_id", str(uuid.uuid4()))
    ai_settings = cuerpo.get("ai_settings", {})
    
    # Extraer token
    auth_header = request.headers.get("Authorization")
    token = None
    user_id = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            supabase = get_supabase()
            user_response = supabase.auth.get_user(token)
            if user_response and user_response.user:
                user_id = user_response.user.id
        except Exception as e:
            print(f"Error verificando token en Chat: {e}")

    # Extraer el último mensaje del usuario
    texto_recibido = "(sin mensaje)"
    if mensajes:
        ultimo_mensaje=mensajes[-1]
        partes= ultimo_mensaje.get("parts",[])
        if partes:
            texto_recibido = partes[0].get("text","")

    # Guardar en base de datos si hay usuario
    if user_id:
        supabase = get_supabase()
        # Verificar si existe la sesión, si no, crearla
        try:
            sesion = supabase.table("chat_sessions").select("id").eq("id", session_id).execute()
            if not sesion.data:
                supabase.table("chat_sessions").insert({
                    "id": session_id,
                    "user_id": user_id,
                    "title": texto_recibido[:30] + "..." if len(texto_recibido) > 30 else texto_recibido
                }).execute()
            
            # Guardar mensaje del usuario
            supabase.table("chat_messages").insert({
                "session_id": session_id,
                "sender": "user",
                "content": texto_recibido
            }).execute()
        except Exception as e:
            print(f"Error guardando mensaje de usuario: {e}")

    # Intentar llamar al AI-component (puerto 8001)
    try:
        url = "http://localhost:8001/chat"
        # ⚠️ Cambiamos el payload para enviar TODOS los mensajes y el token
        payload = ChatPayload(
                    id=session_id,
                    messages=mensajes,
                    trigger="chat",
                    user_name=cuerpo.get("user_name", "Usuario"),
                    age=22,
                    token=token,
                    ai_settings=ai_settings
                )
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload.model_dump())
        if response.status_code != 200:
            raise Exception(f"AI-component respondió {response.status_code}")
        data = response.json()
        coach_dict = data.get("coach_response", {})
        coach = CoachResponse(**coach_dict)
        respuesta_texto = coach.summary
    except Exception as e:
        # 🧪 LAB: Si el AI-component no está disponible, devolver echo diagnóstico
        print(f"⚠️ AI-component no disponible ({e}), usando echo diagnóstico")
        respuesta_texto = f"El Coach no está disponible. Error: {e}"

    # Guardar la respuesta de la IA
    if user_id:
        try:
            supabase.table("chat_messages").insert({
                "session_id": session_id,
                "sender": "ai",
                "content": respuesta_texto
            }).execute()
        except Exception as e:
            print(f"Error guardando mensaje de la IA: {e}")

    # 🧪 LAB: Usar stream v6 en vez del formato antiguo
    return StreamingResponse(
        generar_respuesta_v6(respuesta_texto),
        headers=STREAM_HEADERS,
        media_type="text/event-stream"
    )

app.include_router(planes_router)
app.include_router(chat_router)

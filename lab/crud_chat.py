from fastapi import APIRouter, HTTPException, Request, Depends
from datetime import datetime, timezone
import uuid

from lab.supabase_client import get_supabase
from lab.auth import get_current_user_id

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.get("/sessions")
async def obtener_sesiones(user_id: str = Depends(get_current_user_id)):
    """Obtiene las sesiones de chat del usuario"""
    try:
        supabase = get_supabase()
        response = (
            supabase.table("chat_sessions")
            .select("*")
            .eq("user_id", user_id)
            .order("updated_at", desc=True)
            .execute()
        )
        return response.data
    except Exception as e:
        print(f"❌ Error al obtener sesiones: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}/messages")
async def obtener_mensajes(session_id: str, user_id: str = Depends(get_current_user_id)):
    """Obtiene los mensajes de una sesión (verifica propiedad)"""
    try:
        supabase = get_supabase()
        
        # Verificar que la sesión pertenece al usuario
        session_check = supabase.table("chat_sessions").select("id").eq("id", session_id).eq("user_id", user_id).execute()
        if not session_check.data:
            raise HTTPException(status_code=404, detail="Sesión no encontrada o no autorizada")

        response = (
            supabase.table("chat_messages")
            .select("*")
            .eq("session_id", session_id)
            .order("created_at", desc=False)
            .execute()
        )
        return response.data
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error al obtener mensajes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions")
async def crear_sesion(request: Request, user_id: str = Depends(get_current_user_id)):
    """Crea una nueva sesión de chat"""
    body = await request.json()
    title = body.get("title", "Nueva conversación")
    try:
        supabase = get_supabase()
        response = supabase.table("chat_sessions").insert({
            "user_id": user_id,
            "title": title
        }).execute()
        return response.data[0] if response.data else {"status": "success"}
    except Exception as e:
        print(f"❌ Error al crear sesión: {e}")
        raise HTTPException(status_code=500, detail=str(e))


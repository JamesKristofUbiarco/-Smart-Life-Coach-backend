# backend/lab/crud_planes.py
# Router de FastAPI para CRUD de planes y tareas usando Supabase.
# Reemplaza el mock_db en memoria de main.py.

from fastapi import APIRouter, HTTPException, Request, Depends
from datetime import datetime, timezone

from lab.supabase_client import get_supabase
from lab.auth import get_current_user_id

router = APIRouter(prefix="/api/planes", tags=["planes"])


@router.get("")
async def obtener_planes(user_id: str = Depends(get_current_user_id)):
    """
    Obtiene todos los planes y tareas del usuario desde Supabase.
    Retorna el mismo formato JSON que el mock_db original.
    """
    try:
        supabase = get_supabase()
        response = (
            supabase.table("goals")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=False)
            .execute()
        )
        return response.data
    except Exception as e:
        print(f"❌ Error obteniendo planes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
async def crear_plan(request: Request, user_id: str = Depends(get_current_user_id)):
    """
    Crea un plan o tarea en Supabase.
    Si parent_id es null → es un Plan.
    Si parent_id tiene un UUID → es una Tarea hija de ese Plan.
    """
    body = await request.json()
    ahora = datetime.now(timezone.utc).isoformat()

    nuevo_item = {
        "user_id": user_id,
        "title": body.get("title", "Sin título"),
        "description": body.get("description", ""),
        "status": body.get("status", "pending"),
        "priority": body.get("priority", "medium"),
        "parent_id": body.get("parent_id", None),
        "due_date": body.get("due_date", ahora),
    }

    try:
        supabase = get_supabase()
        response = supabase.table("goals").insert(nuevo_item).execute()
        print(f"✅ Creado en Supabase: {nuevo_item['title']}")
        return response.data[0] if response.data else {"status": "success"}
    except Exception as e:
        print(f"❌ Error creando plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{item_id}")
async def actualizar_estado(
    item_id: str,
    request: Request,
    user_id: str = Depends(get_current_user_id),
):
    """
    Actualiza el estado de un plan o tarea en Supabase.
    """
    body = await request.json()
    nuevo_estado = body.get("status")

    try:
        supabase = get_supabase()
        response = (
            supabase.table("goals")
            .update({"status": nuevo_estado})
            .eq("id", item_id)
            .eq("user_id", user_id)  # Seguridad: solo el dueño puede modificar
            .execute()
        )

        if response.data:
            print(f"✅ Supabase actualizó item {item_id} a: {nuevo_estado}")
            return {
                "status": "success",
                "item_id": item_id,
                "new_status": nuevo_estado,
            }
        else:
            return {"status": "error", "message": "Item no encontrado"}
    except Exception as e:
        print(f"❌ Error actualizando: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{item_id}")
async def eliminar_plan(
    item_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """
    Elimina un plan o tarea de Supabase.
    Si es un plan padre, CASCADE eliminará sus tareas hijas automáticamente.
    """
    try:
        supabase = get_supabase()
        response = (
            supabase.table("goals")
            .delete()
            .eq("id", item_id)
            .eq("user_id", user_id)
            .execute()
        )

        if response.data:
            print(f"🗑️ Eliminado de Supabase: {item_id}")
            return {"status": "success", "item_id": item_id}
        else:
            return {"status": "error", "message": "Item no encontrado"}
    except Exception as e:
        print(f"❌ Error eliminando: {e}")
        raise HTTPException(status_code=500, detail=str(e))

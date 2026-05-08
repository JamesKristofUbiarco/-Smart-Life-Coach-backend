# backend/lab/auth.py
# Dependency de autenticación para FastAPI.
# Valida el JWT usando el cliente oficial de Supabase.

from fastapi import Request, HTTPException
from lab.supabase_client import get_supabase

async def get_current_user_id(request: Request) -> str:
    """
    Extrae el token del header Authorization y lo valida usando Supabase Auth.
    Retorna el user_id del usuario autenticado.
    """
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Header Authorization inválido o faltante")
        
    token = auth_header.split(" ")[1]
    
    try:
        supabase = get_supabase()
        # get_user con token valida la sesión contra el servidor Auth de Supabase directamente
        response = supabase.auth.get_user(token)
        
        if not response or not response.user:
            raise HTTPException(status_code=401, detail="Token inválido o usuario no encontrado")
            
        return response.user.id
        
    except Exception as e:
        print(f"Error auth Supabase: {str(e)}")
        raise HTTPException(status_code=401, detail=f"No autorizado: {str(e)}")

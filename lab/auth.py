# backend/lab/auth.py
# Dependency de autenticación para FastAPI.
# Valida el JWT de Supabase y extrae el user_id.

import os
import jwt
from fastapi import Request, HTTPException
from dotenv import load_dotenv

load_dotenv()

# El secreto por defecto de Supabase Local si no se provee otro en el .env
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "super-secret-jwt-token-with-at-least-32-characters-long")

async def get_current_user_id(request: Request) -> str:
    """
    Extrae y valida el JWT de Supabase desde el header Authorization.
    Retorna el user_id (sub) del usuario autenticado.
    """
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Header Authorization inválido o faltante")
        
    token = auth_header.split(" ")[1]
    
    try:
        # Supabase usa HS256 y la audiencia "authenticated"
        payload = jwt.decode(
            token, 
            SUPABASE_JWT_SECRET, 
            algorithms=["HS256"], 
            audience="authenticated"
        )
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Token sin subject (sub)")
            
        return user_id
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="El token ha expirado")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Token inválido: {str(e)}")

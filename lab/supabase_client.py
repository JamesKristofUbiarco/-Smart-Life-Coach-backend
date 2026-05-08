# backend/lab/supabase_client.py
# Cliente de Supabase para conectar con la DB real.
# Usa la SERVICE_ROLE_KEY para bypasear RLS (backend tiene acceso completo).

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Cargar variables de .env
load_dotenv()

_supabase_instance: Client | None = None


def get_supabase() -> Client:
    """
    Retorna una instancia singleton del cliente de Supabase.
    Usa SERVICE_ROLE_KEY para tener acceso completo (bypass RLS).
    """
    global _supabase_instance

    if _supabase_instance is None:
        url = os.getenv("SUPABASE_URL", "http://127.0.0.1:54321")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

        if not key:
            raise RuntimeError(
                "❌ SUPABASE_SERVICE_ROLE_KEY no está configurada. "
                "Ejecuta 'npx supabase status' en la carpeta db/ y copia "
                "la Secret Key al archivo backend/.env"
            )

        _supabase_instance = create_client(url, key)
        print(f"✅ Supabase conectado a: {url}")

    return _supabase_instance

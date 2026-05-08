# backend/lab/stream_v6.py
# Generador SSE compatible con AI SDK v6 (UI Message Stream Protocol)
# Ref: frontend/docs/ai-sdk-chat-protocol.md

import json
import uuid
import asyncio


# Headers obligatorios para que el AI SDK v6 reconozca el stream
STREAM_HEADERS = {
    "Content-Type": "text/event-stream",
    "Cache-Control": "no-cache, no-transform",
    "x-vercel-ai-ui-message-stream": "v1",
}


async def generar_respuesta_v6(texto: str):
    """
    Genera un stream SSE en formato UI Message Stream Protocol (AI SDK v6).

    Secuencia obligatoria:
      start → start-step → text-start(id) → text-delta(id,delta) × N
      → text-end(id) → finish-step → finish(finishReason)

    Reglas (validadas por Zod en el frontend):
      - start, start-step, finish-step: NO llevan campos extra
      - text-start, text-delta, text-end: llevan 'id' (mismo para los 3)
      - text-delta: lleva 'id' + 'delta'
      - finish: lleva 'finishReason' pero NO 'usage'
    """
    part_id = f"part_{uuid.uuid4().hex[:8]}"

    def sse(data: dict) -> str:
        return f"data: {json.dumps(data)}\n\n"

    # 1. start
    yield sse({"type": "start"})

    # 2. start-step
    yield sse({"type": "start-step"})

    # 3. text-start (requiere id)
    yield sse({"type": "text-start", "id": part_id})

    # 4. text-delta (requiere id + delta) — palabra por palabra
    palabras = texto.split(" ")
    for palabra in palabras:
        delta = palabra + " "
        yield sse({"type": "text-delta", "id": part_id, "delta": delta})
        await asyncio.sleep(0.03)

    # 5. text-end (requiere id)
    yield sse({"type": "text-end", "id": part_id})

    # 6. finish-step (sin campos extra)
    yield sse({"type": "finish-step"})

    # 7. finish (solo finishReason, sin usage)
    yield sse({"type": "finish", "finishReason": "stop"})

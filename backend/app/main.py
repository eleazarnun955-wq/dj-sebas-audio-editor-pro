import json
import os
from typing import Any
from urllib.parse import quote

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

ACE_STEP_BASE_URL = os.getenv("ACE_STEP_BASE_URL", "").rstrip("/")
ACE_STEP_API_KEY = os.getenv("ACE_STEP_API_KEY", "")
BACKEND_TOKEN = os.getenv("DJ_SEBAS_BACKEND_TOKEN", "")
TIMEOUT = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "45"))

app = FastAPI(
    title="DJ SEBAS PRODUCCIONES API",
    version="0.1.0",
    description="Secure adapter between the Android app and a privately hosted ACE-Step music generation service.",
)


class GenerateRequest(BaseModel):
    prompt: str = Field(default="", max_length=4000)
    lyrics: str = Field(default="", max_length=12000)
    vocal_language: str = Field(default="es", max_length=12)
    instrumental: bool = False
    duration: int = Field(default=120, ge=10, le=600)
    bpm: int | None = Field(default=None, ge=30, le=300)
    key_scale: str = Field(default="", max_length=40)
    genre: str = Field(default="", max_length=120)
    model: str = Field(default="acestep-v15-turbo", max_length=80)
    thinking: bool = True
    use_format: bool = True


def require_app_token(authorization: str | None = Header(default=None)) -> None:
    # Fail closed: an unconfigured adapter must never expose a public generation endpoint.
    if not BACKEND_TOKEN or BACKEND_TOKEN == "change-me-before-deploy":
        raise HTTPException(status_code=503, detail="Backend authentication is not configured")
    if authorization != f"Bearer {BACKEND_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")


def provider_headers() -> dict[str, str]:
    headers = {"Accept": "application/json"}
    if ACE_STEP_API_KEY:
        headers["Authorization"] = f"Bearer {ACE_STEP_API_KEY}"
    return headers


def require_provider() -> None:
    if not ACE_STEP_BASE_URL:
        raise HTTPException(status_code=503, detail="ACE-Step provider is not configured")


def unwrap_provider(payload: dict[str, Any]) -> Any:
    if payload.get("error"):
        raise HTTPException(status_code=502, detail=f"Music provider error: {payload['error']}")
    if payload.get("code", 200) != 200:
        raise HTTPException(status_code=502, detail="Music provider returned an unsuccessful response")
    return payload.get("data", payload)


def parse_result(raw: Any) -> list[dict[str, Any]]:
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            return []
    if isinstance(raw, dict):
        raw = [raw]
    if not isinstance(raw, list):
        return []
    return [item for item in raw if isinstance(item, dict)]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "dj-sebas-producciones-api"}


@app.get("/api/music/models", dependencies=[Depends(require_app_token)])
async def models() -> dict[str, Any]:
    require_provider()
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(f"{ACE_STEP_BASE_URL}/v1/models", headers=provider_headers())
    if response.is_error:
        raise HTTPException(status_code=502, detail="Could not retrieve available music models")
    return unwrap_provider(response.json())


@app.post("/api/music/generate", dependencies=[Depends(require_app_token)])
async def generate(request: GenerateRequest) -> dict[str, Any]:
    if not request.prompt.strip() and not request.lyrics.strip():
        raise HTTPException(status_code=422, detail="Describe the song or provide lyrics")
    require_provider()
    prompt = request.prompt.strip()
    if request.genre.strip():
        prompt = f"{prompt}, genre: {request.genre.strip()}".strip(", ")
    payload: dict[str, Any] = {
        "prompt": prompt,
        "lyrics": request.lyrics,
        "vocal_language": request.vocal_language,
        "instrumental": request.instrumental,
        "audio_duration": request.duration,
        "audio_format": "mp3",
        "model": request.model,
        "thinking": request.thinking,
        "use_format": request.use_format,
        "batch_size": 1,
    }
    if request.bpm is not None:
        payload["bpm"] = request.bpm
    if request.key_scale:
        payload["key_scale"] = request.key_scale
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.post(
            f"{ACE_STEP_BASE_URL}/release_task",
            json=payload,
            headers=provider_headers(),
        )
    if response.is_error:
        raise HTTPException(status_code=502, detail="Music generation request failed at the provider")
    data = unwrap_provider(response.json())
    if not isinstance(data, dict) or not data.get("task_id"):
        raise HTTPException(status_code=502, detail="Provider did not return a generation task ID")
    return {
        "task_id": str(data["task_id"]),
        "status": data.get("status", "queued"),
        "queue_position": data.get("queue_position"),
    }


@app.get("/api/music/tasks/{task_id}", dependencies=[Depends(require_app_token)])
async def task_status(task_id: str) -> dict[str, Any]:
    require_provider()
    if len(task_id) > 100 or any(ch not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for ch in task_id):
        raise HTTPException(status_code=422, detail="Invalid task ID")
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.post(
            f"{ACE_STEP_BASE_URL}/query_result",
            json={"task_id_list": [task_id]},
            headers=provider_headers(),
        )
    if response.is_error:
        raise HTTPException(status_code=502, detail="Could not query generation status")
    data = unwrap_provider(response.json())
    if not isinstance(data, list) or not data:
        raise HTTPException(status_code=404, detail="Generation task was not found")
    item = data[0]
    results = parse_result(item.get("result"))
    result = results[0] if results else {}
    status = item.get("status", result.get("status", 0))
    audio_path = result.get("file") if status == 1 else None
    audio_url = None
    if audio_path:
        # The proxy only forwards a relative path to the fixed ACE-Step origin; never accepts an arbitrary host.
        audio_url = f"/api/music/audio?path={quote(str(audio_path), safe='')}"
    return {
        "task_id": task_id,
        "status": "succeeded" if status == 1 else "failed" if status == 2 else "processing",
        "audio_url": audio_url,
        "metadata": result.get("metas", {}),
        "error": item.get("error") if status == 2 else None,
    }


@app.get("/api/music/audio", dependencies=[Depends(require_app_token)])
async def audio(path: str = Query(min_length=1, max_length=2000)) -> StreamingResponse:
    require_provider()
    # ACE-Step returns /v1/audio?path=... . Restrict to that exact endpoint to avoid SSRF.
    if not path.startswith("/v1/audio?path=") or path.startswith("//") or "://" in path:
        raise HTTPException(status_code=400, detail="Invalid provider audio path")
    upstream_url = f"{ACE_STEP_BASE_URL}{path}"
    client = httpx.AsyncClient(timeout=TIMEOUT)
    try:
        upstream = await client.send(
            client.build_request("GET", upstream_url, headers={"Authorization": f"Bearer {ACE_STEP_API_KEY}"} if ACE_STEP_API_KEY else {}),
            stream=True,
        )
        if upstream.is_error:
            await upstream.aclose()
            await client.aclose()
            raise HTTPException(status_code=502, detail="Could not download generated audio")
    except Exception:
        await client.aclose()
        raise

    async def stream():
        try:
            async for chunk in upstream.aiter_bytes():
                yield chunk
        finally:
            await upstream.aclose()
            await client.aclose()

    return StreamingResponse(stream(), media_type=upstream.headers.get("content-type", "audio/mpeg"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))

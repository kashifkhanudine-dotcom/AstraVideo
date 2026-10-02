from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone
from typing import Literal

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel, Field

from .auth import get_current_user
from .providers import GenerationRequest, get_provider

app = FastAPI(title="AstraVideo API", version="0.2.0")

GenerationStatus = Literal["queued", "processing", "completed", "failed"]


class GenerationCreate(BaseModel):
    prompt: str = Field(min_length=3, max_length=2000)
    mode: Literal["text-to-video", "image-to-video"] = "text-to-video"
    duration_seconds: Literal[5, 10] = 5
    resolution: Literal["720p", "1080p"] = "720p"
    aspect_ratio: Literal["16:9", "9:16", "1:1"] = "9:16"
    image_url: str | None = None


class Generation(BaseModel):
    id: str
    user_id: str
    prompt: str
    mode: str
    duration_seconds: int
    resolution: str
    aspect_ratio: str
    status: GenerationStatus
    progress: int = 0
    credits_used: int
    output_url: str | None = None
    error: str | None = None
    created_at: datetime


_GENERATIONS: dict[str, Generation] = {}


def credit_cost(payload: GenerationCreate) -> int:
    base = 10 if payload.duration_seconds == 5 else 18
    if payload.resolution == "1080p":
        base *= 2
    if payload.mode == "image-to-video":
        base += 2
    return base


async def run_generation(generation_id: str, payload: GenerationCreate) -> None:
    generation = _GENERATIONS[generation_id]
    generation.status = "processing"
    generation.progress = 10
    try:
        provider = get_provider()
        generation.progress = 25
        result = await provider.generate(
            GenerationRequest(
                prompt=payload.prompt,
                mode=payload.mode,
                duration_seconds=payload.duration_seconds,
                resolution=payload.resolution,
                aspect_ratio=payload.aspect_ratio,
                image_url=payload.image_url,
            )
        )
        generation.progress = 100
        generation.status = "completed"
        generation.output_url = result.output_url
    except Exception as exc:
        generation.status = "failed"
        generation.error = str(exc)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "version": "0.2.0"}


@app.get("/v1/me")
async def me(user: dict[str, str] = Depends(get_current_user)) -> dict[str, str]:
    return user


@app.get("/v1/credits")
async def credits(user: dict[str, str] = Depends(get_current_user)) -> dict[str, int]:
    return {"balance": 120}


@app.post("/v1/uploads/image")
async def upload_image(
    file: UploadFile = File(...),
    user: dict[str, str] = Depends(get_current_user),
) -> dict[str, str]:
    # MVP placeholder: validates upload path. R2 persistence is wired next.
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image uploads are allowed")
    return {"filename": file.filename or "image", "status": "accepted"}


@app.post("/v1/generations", response_model=Generation, status_code=202)
async def create_generation(
    payload: GenerationCreate,
    background_tasks: BackgroundTasks,
    user: dict[str, str] = Depends(get_current_user),
) -> Generation:
    if payload.mode == "image-to-video" and not payload.image_url:
        raise HTTPException(status_code=400, detail="image_url is required for image-to-video")

    generation_id = str(uuid.uuid4())
    generation = Generation(
        id=generation_id,
        user_id=user["uid"],
        prompt=payload.prompt,
        mode=payload.mode,
        duration_seconds=payload.duration_seconds,
        resolution=payload.resolution,
        aspect_ratio=payload.aspect_ratio,
        status="queued",
        credits_used=credit_cost(payload),
        created_at=datetime.now(timezone.utc),
    )
    _GENERATIONS[generation_id] = generation
    background_tasks.add_task(run_generation, generation_id, payload)
    return generation


@app.get("/v1/generations", response_model=list[Generation])
async def list_generations(user: dict[str, str] = Depends(get_current_user)) -> list[Generation]:
    return sorted(
        [g for g in _GENERATIONS.values() if g.user_id == user["uid"]],
        key=lambda item: item.created_at,
        reverse=True,
    )


@app.get("/v1/generations/{generation_id}", response_model=Generation)
async def get_generation(
    generation_id: str,
    user: dict[str, str] = Depends(get_current_user),
) -> Generation:
    generation = _GENERATIONS.get(generation_id)
    if generation is None or generation.user_id != user["uid"]:
        raise HTTPException(status_code=404, detail="Generation not found")
    return generation


@app.post("/v1/webhooks/revenuecat")
async def revenuecat_webhook(payload: dict) -> dict[str, bool]:
    # Signature validation will be enabled when the RevenueCat secret is configured.
    return {"received": True}

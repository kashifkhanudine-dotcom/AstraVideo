from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone
from typing import Literal

from fastapi import BackgroundTasks, FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="AstraVideo API", version="0.1.0")

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


async def run_mock_generation(generation_id: str) -> None:
    try:
        generation = _GENERATIONS[generation_id]
        generation.status = "processing"
        for progress in (15, 35, 60, 85):
            await asyncio.sleep(0.8)
            generation.progress = progress
        generation.status = "completed"
        generation.progress = 100
        generation.output_url = "https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"
    except Exception as exc:  # pragma: no cover
        generation = _GENERATIONS[generation_id]
        generation.status = "failed"
        generation.error = str(exc)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/v1/credits")
async def credits() -> dict[str, int]:
    return {"balance": 120}


@app.post("/v1/generations", response_model=Generation, status_code=202)
async def create_generation(payload: GenerationCreate, background_tasks: BackgroundTasks) -> Generation:
    generation_id = str(uuid.uuid4())
    generation = Generation(
        id=generation_id,
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
    background_tasks.add_task(run_mock_generation, generation_id)
    return generation


@app.get("/v1/generations", response_model=list[Generation])
async def list_generations() -> list[Generation]:
    return sorted(_GENERATIONS.values(), key=lambda item: item.created_at, reverse=True)


@app.get("/v1/generations/{generation_id}", response_model=Generation)
async def get_generation(generation_id: str) -> Generation:
    generation = _GENERATIONS.get(generation_id)
    if generation is None:
        raise HTTPException(status_code=404, detail="Generation not found")
    return generation

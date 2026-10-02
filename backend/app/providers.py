from __future__ import annotations

import asyncio
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass

import httpx

from .config import settings


@dataclass(slots=True)
class GenerationRequest:
    prompt: str
    mode: str
    duration_seconds: int
    resolution: str
    aspect_ratio: str
    image_url: str | None = None


@dataclass(slots=True)
class GenerationResult:
    output_url: str


class VideoProvider(ABC):
    @abstractmethod
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        raise NotImplementedError


class MockVideoProvider(VideoProvider):
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        await asyncio.sleep(3)
        return GenerationResult(
            output_url="https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"
        )


class ReplicateVideoProvider(VideoProvider):
    def __init__(self) -> None:
        if not settings.replicate_api_token or not settings.replicate_model_version:
            raise RuntimeError("Replicate is selected but token/model version is missing")

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        headers = {
            "Authorization": f"Token {settings.replicate_api_token}",
            "Content-Type": "application/json",
        }
        input_payload: dict[str, object] = {
            "prompt": request.prompt,
            "duration": request.duration_seconds,
            "aspect_ratio": request.aspect_ratio,
        }
        if request.image_url:
            input_payload["image"] = request.image_url

        async with httpx.AsyncClient(timeout=120) as client:
            create = await client.post(
                "https://api.replicate.com/v1/predictions",
                headers=headers,
                json={
                    "version": settings.replicate_model_version,
                    "input": input_payload,
                },
            )
            create.raise_for_status()
            prediction = create.json()
            prediction_id = prediction["id"]

            for _ in range(180):
                poll = await client.get(
                    f"https://api.replicate.com/v1/predictions/{prediction_id}",
                    headers=headers,
                )
                poll.raise_for_status()
                data = poll.json()
                status = data.get("status")
                if status == "succeeded":
                    output = data.get("output")
                    if isinstance(output, list) and output:
                        output = output[0]
                    if not isinstance(output, str):
                        raise RuntimeError("Replicate returned no video URL")
                    return GenerationResult(output_url=output)
                if status in {"failed", "canceled"}:
                    raise RuntimeError(data.get("error") or f"Replicate generation {status}")
                await asyncio.sleep(2)

        raise RuntimeError("Replicate generation timed out")


def get_provider() -> VideoProvider:
    if settings.ai_provider.lower() == "replicate":
        return ReplicateVideoProvider()
    return MockVideoProvider()

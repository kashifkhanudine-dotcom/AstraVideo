from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from .config import settings


class Base(DeclarativeBase):
    pass


class GenerationRow(Base):
    __tablename__ = "generations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(255), index=True)
    prompt: Mapped[str] = mapped_column(Text)
    mode: Mapped[str] = mapped_column(String(32))
    duration_seconds: Mapped[int] = mapped_column(Integer)
    resolution: Mapped[str] = mapped_column(String(16))
    aspect_ratio: Mapped[str] = mapped_column(String(16))
    status: Mapped[str] = mapped_column(String(32), index=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    credits_used: Mapped[int] = mapped_column(Integer)
    output_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    payload_json: Mapped[str] = mapped_column(Text, default="{}")


_engine = None
_Session = None


def database_enabled() -> bool:
    return bool(settings.database_url)


def init_database() -> None:
    global _engine, _Session
    if not database_enabled() or _engine is not None:
        return
    _engine = create_engine(settings.database_url, pool_pre_ping=True)
    _Session = sessionmaker(bind=_engine, expire_on_commit=False)
    Base.metadata.create_all(_engine)


def save_generation(data: dict[str, Any], payload: dict[str, Any] | None = None) -> None:
    if not database_enabled():
        return
    init_database()
    assert _Session is not None
    with _Session() as session:
        row = session.get(GenerationRow, data["id"])
        if row is None:
            row = GenerationRow(
                id=data["id"], user_id=data["user_id"], prompt=data["prompt"], mode=data["mode"],
                duration_seconds=data["duration_seconds"], resolution=data["resolution"], aspect_ratio=data["aspect_ratio"],
                status=data["status"], progress=data.get("progress", 0), credits_used=data["credits_used"],
                output_url=data.get("output_url"), error=data.get("error"), created_at=data["created_at"],
                payload_json=json.dumps(payload or {}),
            )
            session.add(row)
        else:
            row.status = data["status"]
            row.progress = data.get("progress", 0)
            row.output_url = data.get("output_url")
            row.error = data.get("error")
        session.commit()


def list_generations_for_user(user_id: str) -> list[dict[str, Any]]:
    if not database_enabled():
        return []
    init_database()
    assert _Session is not None
    with _Session() as session:
        rows = session.scalars(
            select(GenerationRow).where(GenerationRow.user_id == user_id).order_by(GenerationRow.created_at.desc())
        ).all()
        return [row_to_dict(row) for row in rows]


def get_generation_for_user(generation_id: str, user_id: str) -> dict[str, Any] | None:
    if not database_enabled():
        return None
    init_database()
    assert _Session is not None
    with _Session() as session:
        row = session.get(GenerationRow, generation_id)
        if row is None or row.user_id != user_id:
            return None
        return row_to_dict(row)


def row_to_dict(row: GenerationRow) -> dict[str, Any]:
    return {
        "id": row.id, "user_id": row.user_id, "prompt": row.prompt, "mode": row.mode,
        "duration_seconds": row.duration_seconds, "resolution": row.resolution, "aspect_ratio": row.aspect_ratio,
        "status": row.status, "progress": row.progress, "credits_used": row.credits_used,
        "output_url": row.output_url, "error": row.error, "created_at": row.created_at,
    }

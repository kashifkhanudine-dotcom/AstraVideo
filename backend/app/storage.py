from __future__ import annotations

import asyncio
import mimetypes
import uuid

import boto3
from fastapi import HTTPException, UploadFile

from .config import settings


def _client():
    if not all([
        settings.r2_account_id,
        settings.r2_access_key_id,
        settings.r2_secret_access_key,
        settings.r2_bucket,
    ]):
        raise RuntimeError("R2 is not configured")

    return boto3.client(
        "s3",
        endpoint_url=f"https://{settings.r2_account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        region_name="auto",
    )


async def upload_image(file: UploadFile, user_id: str) -> str:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image uploads are allowed")

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty image")
    if len(data) > 15 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image is larger than 15 MB")

    extension = mimetypes.guess_extension(file.content_type) or ".jpg"
    key = f"users/{user_id}/inputs/{uuid.uuid4().hex}{extension}"
    client = _client()

    await asyncio.to_thread(
        client.put_object,
        Bucket=settings.r2_bucket,
        Key=key,
        Body=data,
        ContentType=file.content_type,
    )

    if settings.r2_public_base_url:
        return f"{settings.r2_public_base_url.rstrip('/')}/{key}"

    return await asyncio.to_thread(
        client.generate_presigned_url,
        "get_object",
        Params={"Bucket": settings.r2_bucket, "Key": key},
        ExpiresIn=3600,
    )

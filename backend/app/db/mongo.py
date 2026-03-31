from __future__ import annotations

from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings


class MongoRepository:
    def __init__(self) -> None:
        self._client: AsyncIOMotorClient | None = None

    def _get_client(self) -> AsyncIOMotorClient:
        if self._client is None:
            self._client = AsyncIOMotorClient(settings.mongo_uri, serverSelectionTimeoutMS=1500)
        return self._client

    async def save_draft(self, payload: dict[str, Any]) -> str | None:
        try:
            collection = self._get_client()[settings.mongo_db_name]["drafts"]
            result = await collection.insert_one(payload)
            return str(result.inserted_id)
        except Exception:
            return None


mongo_repository = MongoRepository()

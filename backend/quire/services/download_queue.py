import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from threading import Lock


class DownloadStatus(StrEnum):
    QUEUED = "queued"
    DOWNLOADING = "downloading"
    UPLOADING = "uploading"
    COMPLETE = "complete"
    ERROR = "error"
    CANCELLED = "cancelled"


@dataclass
class DownloadItem:
    id: str
    source: str
    url: str
    title: str
    author: str
    status: DownloadStatus = DownloadStatus.QUEUED
    progress: float = 0.0
    error: str | None = None
    verso_book_id: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "source": self.source,
            "url": self.url,
            "title": self.title,
            "author": self.author,
            "status": self.status,
            "progress": self.progress,
            "error": self.error,
            "verso_book_id": self.verso_book_id,
            "created_at": self.created_at,
        }


class DownloadQueue:
    def __init__(self, max_concurrent: int = 3):
        self.max_concurrent = max_concurrent
        self._items: dict[str, DownloadItem] = {}
        self._lock = Lock()

    def add(self, source: str, url: str, title: str, author: str) -> DownloadItem:
        item = DownloadItem(
            id=str(uuid.uuid4()),
            source=source,
            url=url,
            title=title,
            author=author,
        )
        with self._lock:
            self._items[item.id] = item
        return item

    def get(self, item_id: str) -> DownloadItem | None:
        return self._items.get(item_id)

    def list_all(self) -> list[DownloadItem]:
        return list(self._items.values())

    def update_status(
        self,
        item_id: str,
        status: DownloadStatus,
        progress: float | None = None,
        error: str | None = None,
        verso_book_id: str | None = None,
    ) -> None:
        with self._lock:
            item = self._items.get(item_id)
            if not item:
                return
            item.status = status
            if progress is not None:
                item.progress = progress
            if error is not None:
                item.error = error
            if verso_book_id is not None:
                item.verso_book_id = verso_book_id

    def cancel(self, item_id: str) -> None:
        self.update_status(item_id, DownloadStatus.CANCELLED)

    def active_count(self) -> int:
        return sum(
            1 for item in self._items.values() if item.status == DownloadStatus.DOWNLOADING
        )

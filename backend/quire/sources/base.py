from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class SearchResult:
    source: str
    title: str
    author: str
    url: str
    format: str
    size_bytes: int | None = None
    language: str | None = None
    year: int | None = None
    isbn: str | None = None
    cover_url: str | None = None
    extra: dict = field(default_factory=dict)

    @property
    def size_display(self) -> str:
        if not self.size_bytes:
            return "Unknown"
        mb = self.size_bytes / (1024 * 1024)
        return f"{mb:.1f} MB"


class Source(ABC):
    name: str
    display_name: str

    @abstractmethod
    async def search(self, query: str, max_results: int = 25) -> list[SearchResult]:
        ...

    @abstractmethod
    async def download(self, url: str) -> tuple[bytes, str]:
        """Download a book. Returns (file_content, filename)."""
        ...

    @abstractmethod
    async def is_available(self) -> bool:
        ...

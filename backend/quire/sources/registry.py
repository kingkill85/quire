from quire.sources.base import Source


class SourceRegistry:
    def __init__(self):
        self._sources: dict[str, Source] = {}

    def register(self, source: Source) -> None:
        self._sources[source.name] = source

    def get(self, name: str) -> Source | None:
        return self._sources.get(name)

    def list_sources(self) -> list[str]:
        return list(self._sources.keys())

    def all(self) -> list[Source]:
        return list(self._sources.values())

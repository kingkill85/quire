from quire.config import settings
from quire.sources.annas_archive import AnnasArchiveSource
from quire.sources.gutenberg import GutenbergSource
from quire.sources.libgen import LibGenSource
from quire.sources.openlibrary import OpenLibrarySource
from quire.sources.registry import SourceRegistry
from quire.sources.standard_ebooks import StandardEbooksSource
from quire.sources.zlibrary import ZLibrarySource


def create_registry() -> SourceRegistry:
    registry = SourceRegistry()

    registry.register(OpenLibrarySource())
    registry.register(GutenbergSource())
    registry.register(StandardEbooksSource())
    registry.register(LibGenSource())
    registry.register(AnnasArchiveSource(api_key=settings.annas_archive_api_key))

    if settings.zlibrary_email and settings.zlibrary_password:
        registry.register(
            ZLibrarySource(
                email=settings.zlibrary_email,
                password=settings.zlibrary_password,
            )
        )

    return registry

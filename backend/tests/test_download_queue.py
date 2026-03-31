from quire.services.download_queue import DownloadQueue, DownloadStatus


def test_add_and_get_item():
    queue = DownloadQueue(max_concurrent=2)
    item = queue.add(source="libgen", url="https://example.com/book", title="Test Book", author="Author")
    assert item.status == DownloadStatus.QUEUED
    assert item.title == "Test Book"
    retrieved = queue.get(item.id)
    assert retrieved is not None
    assert retrieved.id == item.id


def test_list_items():
    queue = DownloadQueue(max_concurrent=2)
    queue.add(source="libgen", url="https://example.com/1", title="Book 1", author="A")
    queue.add(source="libgen", url="https://example.com/2", title="Book 2", author="B")
    items = queue.list_all()
    assert len(items) == 2


def test_update_status():
    queue = DownloadQueue(max_concurrent=2)
    item = queue.add(source="libgen", url="https://example.com/book", title="Test", author="A")
    queue.update_status(item.id, DownloadStatus.DOWNLOADING, progress=50.0)
    updated = queue.get(item.id)
    assert updated.status == DownloadStatus.DOWNLOADING
    assert updated.progress == 50.0


def test_cancel_item():
    queue = DownloadQueue(max_concurrent=2)
    item = queue.add(source="libgen", url="https://example.com/book", title="Test", author="A")
    queue.cancel(item.id)
    updated = queue.get(item.id)
    assert updated.status == DownloadStatus.CANCELLED

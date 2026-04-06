"""Test that get_image evicts cached files when Scryfall updates a scan."""

import os
from pathlib import Path
from tempfile import gettempdir
from unittest.mock import patch

import pytest


IMAGE_URI = "https://cards.scryfall.io/png/front/7/6/76b6c35a-bb92-4ad3-8f85-88b9bafc6266.png?1774978609"
TIMESTAMP = 1774978609


@pytest.fixture()
def cache_folder(tmp_path, monkeypatch):
    monkeypatch.setattr("mtg_proxies.scryfall.scryfall._cache_folder", tmp_path)
    return tmp_path


def cached_file(cache_folder: Path) -> Path:
    return cache_folder / "png_front_76b6c35a-bb92-4ad3-8f85-88b9bafc6266.png"


def test_stale_file_is_evicted_and_redownloaded(cache_folder):
    from mtg_proxies.scryfall.scryfall import get_image

    # Plant a cached file with mtime older than the URI timestamp
    f = cached_file(cache_folder)
    f.write_bytes(b"old")
    os.utime(f, (TIMESTAMP - 1, TIMESTAMP - 1))

    downloaded = []

    def fake_get_file(file_name, url, *, silent=False):
        downloaded.append(file_name)
        path = cache_folder / file_name
        path.write_bytes(b"new")
        return str(path)

    with patch("mtg_proxies.scryfall.scryfall.get_file", side_effect=fake_get_file):
        get_image(IMAGE_URI, silent=True)

    assert downloaded, "get_file should have been called to re-download the stale image"
    assert not f.exists() or f.read_bytes() == b"new"


def test_fresh_file_is_not_redownloaded(cache_folder):
    from mtg_proxies.scryfall.scryfall import get_image

    # Plant a cached file with mtime newer than the URI timestamp
    f = cached_file(cache_folder)
    f.write_bytes(b"current")
    os.utime(f, (TIMESTAMP + 1, TIMESTAMP + 1))

    downloaded = []

    def fake_get_file(file_name, url, *, silent=False):
        downloaded.append(file_name)
        return str(cache_folder / file_name)

    with patch("mtg_proxies.scryfall.scryfall.get_file", side_effect=fake_get_file):
        get_image(IMAGE_URI, silent=True)

    assert downloaded, "get_file is always called — it handles the already-cached case internally"
    assert f.read_bytes() == b"current", "fresh file should not have been deleted"


def test_uri_without_timestamp_is_not_evicted(cache_folder):
    from mtg_proxies.scryfall.scryfall import get_image

    uri_no_ts = "https://cards.scryfall.io/png/front/7/6/76b6c35a-bb92-4ad3-8f85-88b9bafc6266.png"
    f = cached_file(cache_folder)
    f.write_bytes(b"original")

    deleted = []
    real_unlink = Path.unlink

    def track_unlink(self, *args, **kwargs):
        deleted.append(self)
        real_unlink(self, *args, **kwargs)

    def fake_get_file(file_name, url, *, silent=False):
        return str(cache_folder / file_name)

    with patch("mtg_proxies.scryfall.scryfall.get_file", side_effect=fake_get_file):
        with patch.object(Path, "unlink", track_unlink):
            get_image(uri_no_ts, silent=True)

    assert not deleted, "file without URI timestamp should never be evicted"

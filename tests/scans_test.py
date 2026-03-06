from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from mtg_proxies.decklists import Decklist


@pytest.mark.parametrize(
    ("faces", "expected_images"),
    [
        ("all", 7),
        ("front", 6),
        ("back", 1),
    ],
)
def test_fetch_scans_scryfall(example_decklist: Decklist, faces: str, expected_images: int) -> None:
    from mtg_proxies import fetch_scans_scryfall

    images = fetch_scans_scryfall(example_decklist, faces=faces)

    assert len(images) == expected_images

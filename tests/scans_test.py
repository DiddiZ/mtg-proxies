from pathlib import Path
from typing import Literal

import pytest

from mtgproxies.decklists import Decklist


@pytest.fixture(scope="module")
def example_decklist(cache_dir: Path, example_decklists_dir: Path) -> Decklist:
    from mtgproxies.decklists import parse_decklist

    decklist, _, _ = parse_decklist(example_decklists_dir / "decklist.txt", cache_dir=cache_dir)

    return decklist


@pytest.mark.parametrize(
    "faces,expected_images",
    [
        ("all", 7),
        ("front", 6),
        ("back", 1),
    ],
)
def test_fetch_scans_scryfall(
    example_decklist: Decklist, faces: Literal["all", "front", "back"], expected_images: int, cache_dir: Path
):
    from mtgproxies import fetch_scans_scryfall

    images = fetch_scans_scryfall(example_decklist, faces=faces, cache_dir=cache_dir)

    assert len(images) == expected_images

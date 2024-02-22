from pathlib import Path

import pytest

from mtgproxies.decklists import Decklist


@pytest.fixture(scope="module")
def example_decklist() -> Decklist:
    from mtgproxies.decklists import parse_decklist

    decklist, _, _ = parse_decklist(Path(__file__).parent.parent / "examples/decklist.txt")

    return decklist


@pytest.mark.parametrize(
    "faces,expected_images",
    [
        ("all", 7),
        ("front", 6),
        ("back", 1),
    ],
)
def test_fetch_scans_scryfall(example_decklist: Decklist, faces: str, expected_images: int):
    from mtgproxies import fetch_scans_scryfall

    images = fetch_scans_scryfall(example_decklist, faces=faces)

    assert len(images) == expected_images

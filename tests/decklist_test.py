import os

import pytest


def test_parsing():
    from mtgproxies.decklists import parse_decklist

    decklist, ok, warnings = parse_decklist("examples/decklist.txt")

    assert ok
    assert len(warnings) == 0

    with open("examples/decklist.txt", encoding="utf-8") as f:
        # Ignore differences in linebreaks
        assert (format(decklist, "arena") + os.linesep).replace("\r\n", "\n") == f.read().replace("\r\n", "\n")


@pytest.mark.parametrize(
    "archidekt_id,expected_first_card",
    [
        ("1212142", "Squirrel Nest"),
        ("42", "Merieke Ri Berit"),
    ],
)
def test_archidekt(archidekt_id: str, expected_first_card: str):
    from mtgproxies.decklists.archidekt import parse_decklist

    decklist, ok, _ = parse_decklist(archidekt_id)

    assert ok
    assert decklist.cards[0]["name"] == expected_first_card


def test_reversible_cards():
    """Check that reversible cards are parsed correctly."""
    from io import StringIO

    from mtgproxies import fetch_scans_scryfall
    from mtgproxies.decklists import parse_decklist_stream

    decklist, ok, _ = parse_decklist_stream(StringIO("1 Propaganda // Propaganda (SLD) 381\n"))

    assert ok
    assert decklist.cards[0]["name"] == "Propaganda // Propaganda"

    images = fetch_scans_scryfall(decklist)

    assert len(images) == 2  # Front and back

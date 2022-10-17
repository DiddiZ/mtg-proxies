import os

import pytest


def test_parsing():
    from mtgproxies.decklists import parse_decklist

    decklist, ok, warnings = parse_decklist("examples/decklist.txt")

    assert ok
    assert len(warnings) == 0

    with open("examples/decklist.txt", "r", encoding="utf-8") as f:
        # Ignore differences in linebreaks
        assert (format(decklist, "arena") + os.linesep).replace("\r\n", "\n") == f.read().replace("\r\n", "\n")


@pytest.mark.parametrize(
    "archidekt_id,expected_first_card",
    [
        ("1212142", "Basilisk Collar"),
        ("42", "Merieke Ri Berit"),
    ],
)
def test_archidekt(archidekt_id: str, expected_first_card: str):
    from mtgproxies.decklists.archidekt import parse_decklist

    decklist, ok, _ = parse_decklist(archidekt_id)

    assert ok
    assert decklist.cards[0]["name"] == expected_first_card

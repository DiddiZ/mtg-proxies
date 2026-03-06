import os
from io import StringIO
from pathlib import Path

import pytest


def test_parsing(data_dir: Path) -> None:
    from mtg_proxies.decklists import parse_decklist

    decklist, ok, warnings = parse_decklist(data_dir / "decklist.txt")

    assert ok
    assert len(warnings) == 0

    # Ignore differences in linebreaks
    expected = (data_dir / "decklist.txt").read_text(encoding="utf-8")
    assert (format(decklist, "arena") + os.linesep).replace("\r\n", "\n") == expected.replace("\r\n", "\n")


@pytest.mark.parametrize(
    ("line", "expected_card_name", "expected_warnings"),
    [
        (  # Wrong set
            "1 Liliana, Dreadhorde General (WAR2) 97",
            "1 Liliana, Dreadhorde General (RVR) 80",
            [
                "WARNING: Unable to find scan of 'Liliana, Dreadhorde General (WAR2) 97'. Using 'Liliana, Dreadhorde General (RVR) 80' instead."  # noqa: E501
            ],
        ),
        (  # Only front of double faced card (adventure layout)
            "1 Murderous Rider (ELD) 287",
            "1 Murderous Rider // Swift End (ELD) 287",
            ["WARNING: Misspelled card name 'Murderous Rider'. Assuming you mean 'Murderous Rider // Swift End'."],
        ),
        (  # Only front of double faced card (split layout)
            "1 Wear (DGM) 135",
            "1 Wear // Tear (DGM) 135",
            ["WARNING: Misspelled card name 'Wear'. Assuming you mean 'Wear // Tear'."],
        ),
        (  # Wrong collector number
            "1 Forbidden Friendship (IKO) 120",
            "1 Forbidden Friendship (IKO) 367",
            [
                "WARNING: Unable to find scan of 'Forbidden Friendship (IKO) 120'. Using 'Forbidden Friendship (IKO) 367' instead."  # noqa: E501
            ],
        ),
        (  # Incomplete name (but unique)
            "1 Counterspel (EMA) 43",
            "1 Counterspell (EMA) 43",
            ["WARNING: Misspelled card name 'Counterspel'. Assuming you mean 'Counterspell'."],
        ),
        (  # Incomplete name (ambiguous, few options)
            "1 Counterb",
            None,
            ["ERROR: Unable to find card 'Counterb'. Did you mean 'Counterbalance' or 'Counterbore'?"],
        ),
        (  # Incomplete name (ambiguous, many options)
            "1 Counter",
            None,
            [
                "ERROR: Unable to find card 'Counter'. Did you mean 'Cackling Counterpart', 'Counterspell', 'Counters', 'Countermand', 'Feral Encounter', 'Countervailing Winds', ...?"  # noqa: E501
            ],
        ),
        (  # Non-black border with alternative
            "1 Counterspell (5ED) 77",
            "1 Counterspell (5ED) 77",
            ["COSMETIC: White border for 'Counterspell (5ED) 77'. Maybe you want 'Counterspell (DMR) 45'?"],
        ),
        (  # Non-black border without alternative
            "1 Adorable Kitten (UST) 1",
            "1 Adorable Kitten (UST) 1",
            ["COSMETIC: Silver border for 'Adorable Kitten (UST) 1'."],
        ),
        (  # Wrong card name
            "1 Countersark (5ED) 77",
            None,
            ["ERROR: Unable to find card 'Countersark'."],
        ),
        (  # Token with set and collector number
            "1 Saproling (TC19) 19",
            "1 Saproling (TC19) 19",
            [],  # No error
        ),
        (  # Token without set and collector number
            "1 Saproling",
            "1 Saproling (TC16) 16",
            [
                "WARNING: Tokens are not unique by name. Assuming 'Saproling' is a '1/1 green Token Creature — Saproling'.",  # noqa: E501
            ],
        ),
        (  # Token with same name as the front of a double faced card (with set and collector number)
            "1 Illusion (TXLN) 2",
            "1 Illusion (TXLN) 2",  # Remains the token
            [],  # No error
        ),
        (  # Double faced card with same name as a token (with set and collector number)
            "1 Illusion // Reality (DMR) 213",
            "1 Illusion // Reality (DMR) 213",  # Remains the card
            [],  # No error
        ),
        (  # Double faced card with same name as a token (with set and collector number)
            "1 Illusion (DMR) 213",
            "1 Illusion (TBLC) 13",  # TODO: This turns into the token, should be the card instead
            ["WARNING: Unable to find scan of 'Illusion (DMR) 213'. Using 'Illusion (TBLC) 13' instead."],
        ),
        (  # Token with same name as the front of a double faced card (without set and collector number)
            "1 Illusion",
            "1 Illusion (TBLC) 13",  # Remains the token
            [
                "WARNING: Tokens are not unique by name. Assuming 'Illusion' is a '*/* blue Token Creature — Illusion'.",  # noqa: E501
            ],  # TODO: There should be a warning about the ambiguity
        ),
    ],
)
def test_parse_decklist_warnings(line: str, expected_card_name: str | None, expected_warnings: list[str]) -> None:
    from mtg_proxies.decklists import Card, Comment, parse_decklist_stream

    decklist, ok, warnings = parse_decklist_stream(StringIO(f"{line}\n"))

    assert len(decklist.entries) == 1  # One line input, so one entry
    if expected_card_name is None:  # There was an error, so no valid card
        assert not ok
        assert len(decklist.cards) == 0
        assert type(decklist.entries[0]) is Comment
        assert decklist.entries[0].text == line  # Input is preserved as comment
        assert len(warnings) > 0  # At least one warning for the error
    else:  # No error, so valid card
        assert ok
        assert len(decklist.cards) == 1
        assert type(decklist.entries[0]) is Card
        assert f"{decklist.entries[0]:arena}" == expected_card_name

    assert [str(w) for w in warnings] == expected_warnings


@pytest.mark.parametrize(
    ("archidekt_id", "expected_first_card"),
    [
        ("1212142", "Emerald Medallion"),
        ("42", "Dromar's Cavern"),
    ],
)
def test_archidekt(archidekt_id: str, expected_first_card: str) -> None:
    from mtg_proxies.decklists.archidekt import parse_decklist

    decklist, ok, _ = parse_decklist(archidekt_id)

    assert ok
    assert decklist.cards[0]["name"] == expected_first_card


def test_reversible_cards() -> None:
    """Check that reversible cards are parsed correctly."""
    from mtg_proxies import fetch_scans_scryfall
    from mtg_proxies.decklists import parse_decklist_stream

    decklist, ok, _ = parse_decklist_stream(StringIO("1 Propaganda // Propaganda (SLD) 381\n"))

    assert ok
    assert decklist.cards[0]["name"] == "Propaganda // Propaganda"

    images = fetch_scans_scryfall(decklist)

    assert len(images) == 2  # Front and back

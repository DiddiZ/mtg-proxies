from __future__ import annotations

import os
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import scryfall
from mtgproxies.decklists.sanitizing import validate_card_name, validate_print


@dataclass
class Card:
    """Card in a decklist.

    Composed of a count and a Scryfall object.
    """

    count: int
    card: dict[str | Any]

    def __getitem__(self, key: str):
        return self.card[key]

    def __contains__(self, key: str):
        return key in self.card

    @property
    def image_uris(self):
        """Image uris of all faces on this card.

        For single faced cards, this is just the front.
        """
        return [face["image_uris"] for face in scryfall.get_faces(self.card)]

    def __format__(self, format_spec: str) -> str:
        if format_spec == "text":
            return f"{self.count} {self['name']}"
        if format_spec == "arena":
            return f"{self.count} {self['name']} ({self['set'].upper()}) {self['collector_number']}"
        raise ValueError(f"Unkown format {format_spec}")


@dataclass
class Comment:
    """Comment in a decklist."""

    text: str

    def __format__(self, format_spec: str) -> str:
        return self.text


@dataclass
class Decklist:
    """Container class for a decklist.

    Contains cards and comment lines.
    """

    entries: list[Card | Comment] = field(default_factory=list)
    name: str = None

    def append_card(self, count, card) -> None:
        """Append a card line to this decklist."""
        self.entries.append(Card(count, card))

    def append_comment(self, text) -> None:
        """Append a comment line to this decklist."""
        self.entries.append(Comment(text))

    def extend(self, other: Decklist) -> None:
        """Append another decklist to this."""
        self.entries.extend(other.entries)

    def save(self, file: str | Path, fmt="arena", mode="w") -> None:
        """Write decklist to a file.

        Args:
            fmt: Decklist format, either "arena" or "text".
        """
        with open(file, mode, encoding="utf-8", newline="") as f:
            f.write(format(self, fmt) + os.linesep)

    def __format__(self, format_spec: str) -> str:
        return os.linesep.join([format(e, format_spec) for e in self.entries])

    @property
    def cards(self) -> list[Card]:
        """List of all card objects in this decklist."""
        return [e for e in self.entries if isinstance(e, Card)]

    @property
    def total_count(self) -> int:
        """Total count of cards in this decklist."""
        return sum(c.count for c in self.cards)

    @property
    def total_count_unique(self) -> int:
        """Count of unique cards in this decklist."""
        return len(self.cards)

    @staticmethod
    def from_scryfall_ids(card_ids) -> Decklist:
        """Construct a Decklist from scryfall ids.

        Multiple instances of the same id are counted.

        Args:
            card_ids: List of scryfall ids
        """
        decklist = Decklist()
        for card_id, count in Counter(card_ids).items():
            decklist.append_card(count, scryfall.card_by_id()[card_id])
        return decklist


def parse_decklist(filepath) -> tuple[Decklist, bool, list]:
    """Parse card information from a decklist in text or MtG Arena (or mixed) format.

    E.g.:
    ```
    4 Blood Crypt (RNA) 245
    1 Alela, Artful Provocateur
    ```

    Maintains comments. If decklist is in text format, set and collector_number entries will be `None`.

    Returns:
        decklist: Decklist object
        ok: whether all cards could be found.
        warnings: List of (entry, warning) tuples
    """
    with open(filepath, encoding="utf-8") as f:
        decklist, ok, warnings = parse_decklist_stream(f)

    # Use file name without extension as name
    decklist.name = Path(filepath).stem

    return decklist, ok, warnings


def parse_decklist_stream(stream) -> tuple[Decklist, bool, list]:
    """Parse card information from a decklist in text or MtG Arena (or mixed) format from a stream.

    See:
        parse_decklist
    """
    decklist = Decklist()
    warnings = []
    ok = True
    for line in stream:
        m = re.search(r"([0-9]+)\s+(.+?)(?:\s+\((\S*)\)\s+(\S+))?\s*$", line)
        if m:
            # Extract relevant data
            count = int(m.group(1))
            card_name = m.group(2)
            set_id = m.group(3)  # May be None
            collector_number = m.group(4)  # May be None

            # Validate card name
            card_name, warnings_name = validate_card_name(card_name)
            if card_name is None:
                decklist.append_comment(line.rstrip())
                warnings.extend([(decklist.entries[-1], level, msg) for level, msg in warnings_name])
                ok = False
                continue

            # Validate card print
            card, warnings_print = validate_print(card_name, set_id, collector_number)

            decklist.append_card(count, card)
            warnings.extend([(decklist.entries[-1], level, msg) for level, msg in warnings_name + warnings_print])
        else:
            decklist.append_comment(line.rstrip())
    return decklist, ok, warnings

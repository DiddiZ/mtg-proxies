from __future__ import annotations

from pathlib import Path

import requests

from mtgproxies.decklists import Decklist
from mtgproxies.decklists.sanitizing import validate_card_name, validate_print


def parse_decklist(archidekt_id: str, cache_dir: Path, zones: list[str] = None) -> tuple[Decklist, bool, list]:
    """Parse a decklist from manastack.

    Args:
        archidekt_id: Deck list id as shown in the deckbuilder URL
        cache_dir: Directory to store cached card data
        zones: List of zones to include. Available are: `mainboard`, `commander`, `sideboard` and `maybeboard`
    """
    decklist = Decklist()
    warnings = []
    ok = True

    if zones is not None:
        raise NotImplementedError("Zones are not implemented for Archidekt decklists")

    r = requests.get(f"https://archidekt.com/api/decks/{archidekt_id}/")
    if r.status_code != 200:
        raise (ValueError(f"Archidekt returned statuscode {r.status_code}"))

    data = r.json()

    in_deck = {cat["name"] for cat in data["categories"] if cat["includedInDeck"]}

    for item in data["cards"]:
        # Extract relevant data
        count = item["quantity"]
        card_name = item["card"]["oracleCard"]["name"]
        set_id = item["card"]["edition"]["editioncode"]
        collector_number = item["card"]["collectorNumber"]
        if item["categories"] is not None and len(item["categories"]) > 0 and item["categories"][0] not in in_deck:
            continue

        # Validate card name
        card_name, warnings_name = validate_card_name(card_name, cache_dir=cache_dir)
        if card_name is None:
            decklist.append_comment(card_name)
            warnings.extend([(decklist.entries[-1], level, msg) for level, msg in warnings_name])
            ok = False
            continue

        # Validate card print
        card, warnings_print = validate_print(card_name, set_id, collector_number, cache_dir=cache_dir)

        decklist.append_card(count, card)
        warnings.extend([(decklist.entries[-1], level, msg) for level, msg in warnings_name + warnings_print])

    decklist.name = data["name"]

    return decklist, ok, warnings

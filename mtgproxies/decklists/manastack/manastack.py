from __future__ import annotations

import requests

from mtgproxies.decklists import Decklist
from mtgproxies.decklists.sanitizing import validate_card_name, validate_print


def parse_decklist(manastack_id: str, zones: list[str] = ["commander", "mainboard"]):
    """Parse a decklist from manastack.

    Args:
        manastack_id: Deck list id as shown in the deckbuilder URL
        zones: List of zones to include. Available are: `mainboard`, `commander`, `sideboard` and `maybeboard`
    """
    decklist = Decklist()
    warnings = []
    ok = True

    r = requests.get(f"https://manastack.com/api/decklist?format=json&id={manastack_id}")
    if r.status_code != 200:
        raise (ValueError(f"Manastack returned statuscode {r.status_code}"))

    data = r.json()
    for zone in zones:
        if len(data["list"][zone]) > 0:
            decklist.append_comment(zone.capitalize())
            for item in data["list"][zone]:
                # Extract relevant data
                count = item["count"]
                card_name = item["card"]["name"]
                set_id = item["card"]["set"]["slug"]
                collector_number = item["card"]["num"]

                # Validate card name
                card_name, warnings_name = validate_card_name(card_name)
                if card_name is None:
                    decklist.append_comment(card_name)
                    warnings.extend([(decklist.entries[-1], level, msg) for level, msg in warnings_name])
                    ok = False
                    continue

                # Validate card print
                card, warnings_print = validate_print(card_name, set_id, collector_number)

                decklist.append_card(count, card)
                warnings.extend([(decklist.entries[-1], level, msg) for level, msg in warnings_name + warnings_print])

            if zone != zones[-1]:
                decklist.append_comment("")

    decklist.name = data["info"]["name"]

    return decklist, ok, warnings

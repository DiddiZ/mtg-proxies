from dataclasses import dataclass
from typing import Literal

import mtg_proxies.scryfall as scryfall
from mtg_proxies.format import format_print, format_token, listing


@dataclass(slots=True)
class ParseWarning:
    """Warning during parsing."""

    level: Literal["COSMETIC", "WARNING", "ERROR"]
    message: str

    def __str__(self) -> str:
        return f"{self.level}: {self.message}"


def validate_card_name(card_name: str) -> tuple[str | None, list[ParseWarning]]:
    """Validate card name against the Scryfall database.

    Returns:
        card_name: valid card name.
        warnings: list of (level, message) warnings.
        ok: whether the card could be found.
    """
    # Unique names of all cards
    oracle_ids_by_name = scryfall.oracle_ids_by_name()
    cards_by_oracle_id = scryfall.cards_by_oracle_id()

    validated_name = None
    canonical_name = scryfall.canonic_card_name(card_name)
    warnings: list[ParseWarning] = []

    oracle_ids = oracle_ids_by_name.get(canonical_name, [])

    if len(oracle_ids) > 1:
        


    if len(oracle_ids) == 0:  # No exact match, try partial matching
        oracle_ids = [
            oracle_id
            for name in oracle_ids_by_name
            if all(elem in name for elem in canonical_name.split(" "))
            for oracle_id in oracle_ids_by_name[name]
        ]

    if len(oracle_ids) == 1:  # Unique match
        validated_name = cards_by_oracle_id[oracle_ids[0]][0]["name"]
        if validated_name != card_name:
            warnings.append(
                ParseWarning("WARNING", f"Misspelled card name {card_name!r}. Assuming you mean {validated_name!r}.")
            )
    elif len(oracle_ids) == 0:  # No matching card
        warnings.append(ParseWarning("ERROR", f"Unable to find card {card_name!r}."))
    else:  # Multiple matching cards
        alternatives = listing(
            [repr(cards_by_oracle_id[oracle_id][0]["name"]) for oracle_id in oracle_ids], ", ", " or ", 6
        )
        warnings.append(ParseWarning("ERROR", f"Unable to find card {card_name!r}. Did you mean {alternatives}?"))

    return validated_name, warnings


def get_print_warnings(card: dict) -> list[str]:
    """Return warnings for low-resolution scans."""
    warnings = []
    if not card["highres_image"] or card["digital"]:
        warnings.append("low resolution scan")
    if card["collector_number"][-1] in ["p", "s"]:
        warnings.append("promo")
    if card["lang"] != "en":
        warnings.append("non-english print")
    if card["border_color"] != "black":
        warnings.append(card["border_color"] + " border")
    return warnings


def validate_print(card_name: str, set_id: str, collector_number: str) -> tuple[dict, list[ParseWarning]]:
    """Validate a print against the Scryfall database.

    Assumes card name is valid.

    Returns:
        card: valid Scryfall database object.
        warnings: list of warnings.
    """
    warnings: list[ParseWarning] = []

    if set_id is None:
        card = scryfall.recommend_print(card_name=card_name)
        # Warn for tokens, as they are not unique by name
        if card["layout"] in ["token", "double_faced_token"]:
            warnings.append(
                ParseWarning(
                    "WARNING", f"Tokens are not unique by name. Assuming {card_name!r} is a {format_token(card)!r}."
                )
            )
    else:
        card = scryfall.get_card(card_name, set_id, collector_number)
        if card is None:  # No exact match
            # Find alternative print
            card = scryfall.recommend_print(card_name=card_name)
            warnings.append(
                ParseWarning(
                    "WARNING",
                    f"Unable to find scan of {format_print(card_name, set_id, collector_number)!r}."
                    + f" Using {format_print(card)!r} instead.",
                )
            )

    # Warnings for low-quality scans
    quality_warnings = get_print_warnings(card)
    if len(quality_warnings) > 0:
        # Get recommendation
        recommendation = scryfall.recommend_print(card)

        # Format warnings string
        quality_warnings = listing(quality_warnings, ", ", " and ").capitalize()

        warnings.append(
            ParseWarning(
                "COSMETIC",
                f"{quality_warnings} for {format_print(card)!r}."
                + (f" Maybe you want {format_print(recommendation)!r}?" if recommendation != card else ""),
            )
        )
    return card, warnings

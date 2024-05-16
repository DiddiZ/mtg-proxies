from functools import lru_cache
from pathlib import Path

from mtgproxies import scryfall
from mtgproxies.format import format_print, format_token, listing


@lru_cache(maxsize=None)
def card_names(cache_dir: Path):
    """Sets of valid card names.

    Cached for performance.
    """
    cards_by_name = {
        card["name"].lower(): card["name"] for card in scryfall.get_cards(cache_dir=cache_dir) if card["layout"] not in ["art_series"]
    }
    double_faced_by_front = {
        name.split("//")[0].strip().lower(): name for name in cards_by_name.values() if "//" in name
    }
    return cards_by_name, double_faced_by_front


def validate_card_name(card_name: str, cache_dir: Path):
    """Validate card name against the Scryfall database.

    Returns:
        card_name: valid card name.
        warnings: list of (level, message) warnings.
        ok: whether the card could be found.
    """
    # Unique names of all cards
    cards_by_name, double_faced_by_front = card_names(cache_dir=cache_dir)

    validated_name = None
    sanizized_name = scryfall.canonic_card_name(card_name)
    warnings = []
    if sanizized_name in cards_by_name:  # Exact match
        validated_name = cards_by_name[sanizized_name]
    elif sanizized_name in double_faced_by_front:  # Exact match of front of double faced card
        validated_name = double_faced_by_front[sanizized_name]
        warnings.append(("WARNING", f"Misspelled card name '{card_name}'. Assuming you mean {validated_name}."))
    else:  # No exact match
        # Try partial matching
        candidates = [
            cards_by_name[name] for name in cards_by_name if all(elem in name for elem in sanizized_name.split(" "))
        ]

        if len(candidates) == 1:  # Found unique candidate
            validated_name = candidates[0]
            warnings.append(("WARNING", f"Misspelled card name '{card_name}'. Assuming you mean {validated_name}."))
        elif len(candidates) == 0:  # No matching card
            warnings.append(("ERROR", f"Unable to find card '{card_name}'."))
        else:  # Multiple matching cards
            alternatives = listing(["'" + card + "'" for card in candidates], ", ", " or ", 6)
            warnings.append(("ERROR", f"Unable to find card '{card_name}'. Did you mean {alternatives}?"))

    return validated_name, warnings


def get_print_warnings(card) -> list[str]:
    """Returns warnings for low-resolution scans."""
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


def validate_print(card_name: str, set_id: str, collector_number: str, cache_dir: Path):
    """Validate a print against the Scryfall database.

    Assumes card name is valid.

    Returns:
        card: valid Scryfall database object.
        warnings: list of warnings.
    """
    warnings = []

    if set_id is None:
        card = scryfall.recommend_print(card_name=card_name, cache_dir=cache_dir)
        # Warn for tokens, as they are not unique by name
        if card["layout"] in ["token", "double_faced_token"]:
            warnings.append(
                ("WARNING", f"Tokens are not unique by name. Assuming '{card_name}' is a '{format_token(card)}'.")
            )
    else:
        card = scryfall.get_card(card_name=card_name, cache_dir=cache_dir, set_id=set_id, collector_number=collector_number)
        if card is None:  # No exact match
            # Find alternative print
            card = scryfall.recommend_print(card_name=card_name, cache_dir=cache_dir)
            warnings.append(
                (
                    "WARNING",
                    f"Unable to find scan of {format_print(card_name, set_id, collector_number)}."
                    + f" Using {format_print(card)} instead.",
                )
            )

    # Warnings for low-quality scans
    quality_warnings = get_print_warnings(card)
    if len(quality_warnings) > 0:
        # Get recommendation
        recommendation = scryfall.recommend_print(current=card, cache_dir=cache_dir)

        # Format warnings string
        quality_warnings = listing(quality_warnings, ", ", " and ").capitalize()

        warnings.append(
            (
                "COSMETIC",
                f"{quality_warnings} for {format_print(card)}."
                + (f" Maybe you want {format_print(recommendation)}?" if recommendation != card else ""),
            )
        )
    return card, warnings

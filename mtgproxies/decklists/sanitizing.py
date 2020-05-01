import pandas as pd
import scryfall
from mtgproxies.format import format_print, listing


def merge_duplicates(decklist):
    """Merge duplicates entries in a decklist.

    Cards with same name, set and collector number are considered duplicates.

    Maintains the order of the decklist. Duplicates are merged with the first occurrence.
    """
    return (
        # Create dataframe from decklist
        pd.DataFrame(decklist, columns=["Count", "Name", "Set", "Collector Number"])
        # Group by print identifier
        .reset_index().groupby(["Name", "Set", "Collector Number"]).agg(
            {
                "Count": "sum",
                "index": "first",  # Keep first index for ordering order
            }
        ).reset_index().set_index("index").sort_index()  # Restore card order
        # Restore column order
        [["Count", "Name", "Set", "Collector Number"]].values
    )


def validate_card_names(decklist, silent=False):
    """Validate card names of a decklist against the Scryfall database.

    Returns:
        decklist: Filtered decklist, contains only valid card names.
        ok: Whether all cards could be found.
    """
    # Unique names of all cards
    names = {card["name"].lower(): card["name"] for card in scryfall.scryfall._get_database("scryfall-default-cards")}
    double_faced_names = {name.split("//")[0].strip().lower(): name for name in names.values() if "//" in name}

    validated_decklist = []
    for count, card_name, set_id, collector_number in decklist:
        if card_name.lower() in names:  # Exact match
            validated_decklist.append((count, names[card_name.lower()], set_id, collector_number))
        elif card_name.lower() in double_faced_names:  # Exact match of front of double faced card
            full_name = double_faced_names[card_name.lower()]
            if not silent:
                print(f"WARNING: Misspelled card name '{card_name}'. Assuming you mean {full_name}.")
            validated_decklist.append((count, full_name, set_id, collector_number))
        else:  # No exact match
            # Try partial matching
            candidates = [names[name] for name in names if all(elem in name for elem in card_name.lower().split(" "))]

            if len(candidates) == 1:  # Found unique candidate
                if not silent:
                    print(f"WARNING: Misspelled card name '{card_name}'. Assuming you mean {candidates[0]}.")
                validated_decklist.append((count, candidates[0], set_id, collector_number))
            elif len(candidates) == 0:  # No matching card
                if not silent:
                    print(f"ERROR: Unable to find card '{card_name}'.")
            else:  # Multiple matching cards
                if not silent:
                    alternatives = listing(["'" + card + "'" for card in candidates], ", ", " or ", 6)
                    print(f"ERROR: Unable to find card '{card_name}'. Did you mean {alternatives}?")

    return validated_decklist, len(validated_decklist) == len(decklist)


def validate_prints(decklist):
    """Validate prints of a decklist against the Scryfall database.

    Assumes card names are valid.

    Returns:
        decklist: Validated decklist, contains only valid prints.
    """
    validated_decklist = []
    for count, card_name, set_id, collector_number in decklist:

        card = scryfall.get_card(card_name, set_id, collector_number)

        if card is None:  # No exact match
            # Find alternative print
            card = scryfall.recommend_print(card_name)
            print(
                f"WARNING: Unable to find scan of {format_print(card_name, set_id, collector_number)}." +
                f" Using {format_print(card)} instead."
            )
            set_id = card["set"]
            collector_number = card["collector_number"]

        # Warnings for low-quality scans
        warnings = []
        if not card["highres_image"]:
            warnings.append("low resolution scan")
        elif card["border_color"] != "black":
            warnings.append("non-black border")
        if len(warnings) > 0:
            # Get recommendation
            recommendation = scryfall.recommend_print(card_name, set_id, collector_number)

            # Format warnings string
            warnings = listing(warnings, ", ", " and ").capitalize()

            print(
                f"WARNING: {warnings} for {format_print(card_name, set_id, collector_number)}." +
                (f" Maybe you want {format_print(recommendation)}?" if recommendation is not None else "")
            )

        validated_decklist.append((count, card["name"], card["set"], card["collector_number"]))

    return validated_decklist

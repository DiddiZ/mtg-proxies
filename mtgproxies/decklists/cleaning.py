from mtgproxies.decklists import Decklist, Card


def merge_duplicates(decklist, identifier="oracle_id"):
    """Merge duplicates entries in a decklist.

    Maintains the order of the decklist. Duplicates are merged with the first occurrence.

    Can merge on different identifiers. `"oracle_id"` will merge different prints of the same card,
    while `"id"` will only merge exact duplicates.

    Args:
        decklist: Decklist object
        identifier: Id to merge on.
    """
    cards_by_id = {}

    merged = Decklist()
    for entry in decklist.entries:
        if isinstance(entry, Card):
            card_id = entry[identifier]
            if card_id in cards_by_id:
                # Merge
                cards_by_id[card_id].count += entry.count
            else:
                # Append card
                merged.entries.append(entry)
                cards_by_id[card_id] = merged.entries[-1]
        else:
            # Append comment
            merged.entries.append(entry)

    return merged

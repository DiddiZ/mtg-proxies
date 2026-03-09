from mtg_proxies import scryfall
from mtg_proxies.decklists import Decklist


def get_tokens(decklist: Decklist) -> list[dict]:
    """Find all tokens related to the cards in a decklist."""
    tokens = {}
    for card in decklist.cards:
        if card["layout"] in ["token", "double_faced_token"]:
            continue

        # Iterate over all prints, as not all have token information associated with them
        for card_print in scryfall.get_cards(oracle_id=card["oracle_id"]):
            if "all_parts" in card_print:
                for related_card in card_print["all_parts"]:
                    if related_card["component"] == "token":
                        # Related cards are only provided by their id.
                        # We need the oracle id to weed out duplicates
                        related = scryfall.get_cards(id=related_card["id"])[0]
                        tokens[related["oracle_id"]] = related

    # Resolve oracle ids to actual cards.
    return [scryfall.recommend_print(token) for token in tokens.values()]

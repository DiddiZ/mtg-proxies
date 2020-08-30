import argparse
from pathlib import Path
import scryfall
from mtgproxies.decklists import Decklist, parse_decklist


def get_tokens(decklist):
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Append the tokens created by the cards in a decklist to it.')
    parser.add_argument('decklist', help='a decklist in Arena format')
    parser.add_argument(
        '--format', help='output format (default: %(default)s)', choices=['arena', 'text'], default='arena'
    )
    args = parser.parse_args()

    # Parse decklist
    print("Parsing decklist ...")
    decklist, ok, warnings = parse_decklist(args.decklist)
    for _, warning in warnings:
        print(warning)
    if not ok:
        print("Decklist contains invalid card names. Fix errors above before reattempting.")
        quit()

    print("Found %d cards in total with %d unique cards." % (
        decklist.total_count,
        decklist.total_count_unique,
    ))

    # Find tokens
    tokens = get_tokens(decklist)
    print(f"Found {len(tokens)} created tokens.")

    # Create decklist of tokens
    token_list = Decklist()
    token_list.append_comment("")
    token_list.append_comment("Tokens")
    for token in tokens:
        token_list.append_card(1, token)

    # Write decklist
    token_list.save(args.decklist, fmt=args.format, mode='a')

    print(f"Successfully appended to {Path(args.decklist).resolve()}.")

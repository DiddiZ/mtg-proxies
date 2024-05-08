import argparse
from pathlib import Path

from mtgproxies import scryfall
from mtgproxies.cli import parse_decklist_spec
from mtgproxies.decklists import Decklist


def get_tokens(decklist: Decklist, cache_dir: Path):
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
                        related = scryfall.get_cards(cache_dir=cache_dir, id=related_card["id"])[0]
                        tokens[related["oracle_id"]] = related

    # Resolve oracle ids to actual cards.
    return [scryfall.recommend_print(cache_dir=cache_dir, current=token) for token in tokens.values()]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Append the tokens created by the cards in a decklist to it.")
    parser.add_argument(
        "decklist",
        metavar="decklist_spec",
        help="path to a decklist in text/arena format, or manastack:{manastack_id}, or archidekt:{archidekt_id}",
    )
    parser.add_argument(
        "--format", help="output format (default: %(default)s)", choices=["arena", "text"], default="arena"
    )
    args = parser.parse_args()

    # Parse decklist
    decklist_ = parse_decklist_spec(args.decklist, warn_levels=["ERROR", "WARNING"])

    # Find tokens
    tokens_ = get_tokens(decklist_)
    print(f"Found {len(tokens_)} created tokens.")

    # Append tokens
    decklist_.append_comment("")
    decklist_.append_comment("Tokens")
    for t in tokens_:
        decklist_.append_card(1, t)

    # Write decklist
    out_file = args.decklist if Path(args.decklist).is_file() else f"{args.decklist.split(':')[-1]}.txt"
    decklist_.save(out_file, fmt=args.format)

    print(f"Successfully appended to {Path(out_file).resolve()}.")

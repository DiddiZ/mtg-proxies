import argparse
import codecs
from pathlib import Path
import scryfall
from mtgproxies.decklists import parse_decklist_arena, validate_card_names


def get_tokens(decklist):
    tokens = set()
    for _, card_name, _, _ in decklist:
        # Iterate over all prints, as not all have token information associated with them
        for card in scryfall.get_cards(name=card_name):
            if "all_parts" in card and card["layout"] not in ["token", "double_faced_token"]:
                for related_card in card["all_parts"]:
                    if related_card["component"] == "token":
                        # Related card only provided by their id.
                        # We need the oracle id to weed out doublicates
                        related = scryfall.get_cards(id=related_card["id"])[0]
                        tokens.add(related["oracle_id"])

    # Resolve oracle ids to actual cards.
    return [scryfall.recommend_print(card_name=None, oracle_id=token) for token in tokens]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Append the tokens created by the cards in a decklist to it.')
    parser.add_argument('decklist', help='a decklist in Arena format')
    args = parser.parse_args()

    # Parse decklist
    print("Parsing decklist ...")
    decklist = parse_decklist_arena(args.decklist)
    print(
        "Found %d cards in total with %d unique cards." % (
            sum([count for count, _, _, _ in decklist]),
            len(decklist),
        )
    )

    # Sanitizing decklist
    decklist, ok = validate_card_names(decklist)
    if not ok:
        print("Decklist contains invalid card names. Fix errors above before reattempting.")
        quit()

    # Find tokens
    tokens = get_tokens(decklist)
    print(f"Found {len(tokens)} created tokens.")

    # Append to decklist file
    with codecs.open(args.decklist, 'a', 'utf-8') as f_out:
        f_out.write("\nTokens\n")

        for token in tokens:
            f_out.write(f'1 {token["name"]} ({token["set"].upper()}) {token["collector_number"]}\n')

    print(f"Successfully appended to {Path(args.decklist).resolve()}.")

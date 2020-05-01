import argparse
import codecs
from pathlib import Path
import re
import scryfall
from mtgproxies.decklists import parse_decklist_text, validate_card_names

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert a decklist from text format to arena format.')
    parser.add_argument('decklist', help='a decklist in text format')
    parser.add_argument('outfile', help='output file')
    args = parser.parse_args()

    # Parse decklist
    print("Parsing decklist ...")
    decklist = parse_decklist_text(args.decklist)
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

    # Write to target. Re-read file to preserve comments.
    with codecs.open(args.decklist, 'r', 'utf-8') as f_in, codecs.open(args.outfile, 'w', 'utf-8') as f_out:
        for line in f_in:
            m = re.search(r'([0-9]+) (.+)', line.strip())
            if m:
                # Extract relevant data
                count = int(m.group(1))
                card_name = m.group(2)

                # Fetch name changes again
                card_name = validate_card_names([(count, card_name, None, None)], silent=True)[0][0][1]

                card = scryfall.recommend_print(card_name)
                f_out.write(f'{count} {card["name"]} ({card["set"].upper()}) {card["collector_number"]}\n')
            else:
                f_out.write(line)

    print(f"Successfully wrote decklist to {Path(args.outfile).resolve()}.")

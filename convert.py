import argparse
from pathlib import Path
from mtgproxies.decklists import parse_decklist

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert a decklist from text format to arena format or vice-versa.')
    parser.add_argument('decklist', help='a decklist in text or arena format')
    parser.add_argument('outfile', help='output file')
    parser.add_argument(
        '--format', help='output format (default: %(default)s)', choices=['arena', 'text'], default='arena'
    )
    parser.add_argument('--clean', action='store_true', help='remove all non-card lines')
    args = parser.parse_args()

    # Parse decklist
    print("Parsing decklist ...")
    decklist, ok = parse_decklist(args.decklist)
    if not ok:
        print("Decklist contains invalid card names. Fix errors above before reattempting.")
        quit()

    print("Found %d cards in total with %d unique cards." % (
        decklist.total_count,
        decklist.total_count_unique,
    ))

    # Write decklist
    decklist.save(args.outfile, fmt=args.format)

    print(f"Successfully wrote decklist to {Path(args.outfile).resolve()}.")

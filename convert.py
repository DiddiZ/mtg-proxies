import argparse
from pathlib import Path
from mtgproxies.cli import parse_decklist_spec

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert a decklist from text format to arena format or vice-versa.')
    parser.add_argument(
        'decklist',
        metavar='decklist_spec',
        help='path to a decklist in text/arena format, or manastack:{manastack_id}, or archidekt:{archidekt_id}'
    )
    parser.add_argument('outfile', help='output file')
    parser.add_argument(
        '--format', help='output format (default: %(default)s)', choices=['arena', 'text'], default='arena'
    )
    parser.add_argument('--clean', action='store_true', help='remove all non-card lines')
    args = parser.parse_args()

    # Parse decklist
    decklist = parse_decklist_spec(args.decklist, warn_levels=["ERROR", "WARNING"])

    # Write decklist
    decklist.save(args.outfile, fmt=args.format)

    print(f"Successfully wrote decklist to {Path(args.outfile).resolve()}.")

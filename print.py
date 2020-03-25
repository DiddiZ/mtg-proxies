import numpy as np
import argparse
from mtgproxies import print_cards, fetch_scans_scryfall
from mtgproxies.decklists import parse_decklist_arena


def papersize(string):
    spec = string.lower()
    if spec == "a4":
        return np.array([21, 29.7]) / 2.54
    if 'x' in spec:
        split = spec.split("x")
        return np.array([float(split[0]), float(split[1])])
    raise argparse.ArgumentTypeError()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Prepare a decklist for printing.')
    parser.add_argument('decklist', help='a decklist in MtG Arena format')
    parser.add_argument('outfile', help='output file. Supports pdf, png and jpg.')
    parser.add_argument('--dpi', help='dpi of output file', type=int, default=300)
    parser.add_argument('--paper', help='paper size of output', type=papersize, default="a4")
    args = parser.parse_args()

    decklist = parse_decklist_arena(args.decklist)
    images = fetch_scans_scryfall(decklist)
    print_cards(
        images,
        args.outfile,
        papersize=args.paper,
        dpi=args.dpi,
    )

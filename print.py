import numpy as np
import argparse
from mtgproxies import print_cards, fetch_scans_scryfall
from mtgproxies.cli import parse_decklist_spec


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
    parser.add_argument('decklist', help='a decklist in MtG Arena format, or Manastack id')
    parser.add_argument('outfile', help='output file. Supports pdf, png and jpg.')
    parser.add_argument('--dpi', help='dpi of output file (default: %(default)d)', type=int, default=300)
    parser.add_argument(
        '--paper',
        help='paper size in inches or preconfigured format (default: %(default)s)',
        type=papersize,
        default="a4",
        metavar="WIDTHxHEIGHT"
    )
    parser.add_argument(
        '--scale',
        help='scaling factor for printed cards (default: %(default)s)',
        type=float,
        default=1.0,
        metavar="FLOAT"
    )
    parser.add_argument(
        '--border_crop',
        help='how much to crop inner borders of printed cards (default: %(default)s)',
        type=int,
        default=14,
        metavar="PIXELS"
    )
    parser.add_argument(
        '--background',
        help='background color, either by name or by hex code (e.g. black or "#ff0000", default: %(default)s)',
        type=str,
        default=None,
        metavar="COLOR"
    )
    args = parser.parse_args()

    # Parse decklist
    decklist = parse_decklist_spec(args.decklist)

    # Fetch scans
    images = fetch_scans_scryfall(decklist)

    # Plot cards
    print_cards(
        images,
        args.outfile,
        papersize=args.paper,
        cardsize=np.array([2.5, 3.5]) * args.scale,
        dpi=args.dpi,
        border_crop=args.border_crop,
        background_color=args.background,
    )

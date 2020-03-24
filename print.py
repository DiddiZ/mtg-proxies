import argparse
from mtgproxies import print_cards, fetch_scans_scryfall
from mtgproxies.decklists import parse_decklist_arena

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Prepare a decklist for printing.')
    parser.add_argument('decklist', help='a decklist in MtG Arena format')
    parser.add_argument('outfile', help='output file. Supports pdf, png and jpg.')
    parser.add_argument('--dpi', help='dpi of output file', type=int, default=300)
    args = parser.parse_args()

    decklist = parse_decklist_arena(args.decklist)
    images = fetch_scans_scryfall(decklist)
    print_cards(images, args.outfile, dpi=args.dpi)

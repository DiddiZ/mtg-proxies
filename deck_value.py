import argparse
import matplotlib.pyplot as plt
from mtgproxies.cli import parse_decklist_spec
import scryfall

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Show deck value decomposition.')
    parser.add_argument(
        'decklist',
        metavar='decklist_spec',
        help='path to a decklist in text/arena format, or manastack:{manastack_id}, or archidekt:{archidekt_id}'
    )
    parser.add_argument(
        '--lump-threshold',
        help='lump together cards with lesser proportional value',
        type=float,
        default=0.03,
        metavar='FLOAT'
    )

    args = parser.parse_args()

    # Parse decklist
    decklist = parse_decklist_spec(args.decklist, warn_levels=["ERROR", "WARNING"])

    # Fetch prices
    card_prices = []
    for card in decklist.cards:
        price = scryfall.get_price(card['oracle_id'])
        if price is not None:
            card_prices.append((card['name'], card.count * price))
        else:
            print(f"WARNING: Unable to find price for {card['name']}")

    card_prices.sort(key=lambda x: x[1], reverse=True)
    price_total = sum(p for _, p in card_prices)

    # Partition cards in named and bulk
    cards_named = [(card, price) for card, price in card_prices if price >= args.lump_threshold * price_total]
    cards_lump = [(card, price) for card, price in card_prices if price < args.lump_threshold * price_total]

    # Plot
    plt.pie(
        [price for _, price in cards_named] + [sum(p for _, p in cards_lump)],
        labels=[name for name, _ in cards_named] + ["other"],
        autopct=lambda pct: f"{pct / 100. * price_total:0.2f}€",
        shadow=True,
        startangle=90,
    )
    plt.title(f"{decklist.name} ({price_total:0.2f}€)")
    plt.show()

from operator import itemgetter

import matplotlib.pyplot as plt

from mtg_proxies import scryfall
from mtg_proxies.decklists.decklist import Decklist


def show_deck_value(decklist: Decklist, lump_threshold: float = 0.03) -> None:
    """Show deck value decomposition."""
    # Fetch prices
    card_prices = []
    for card in decklist.cards:
        price = scryfall.get_price(card["oracle_id"])
        if price is not None:
            card_prices.append((card["name"], card.count * price))
        else:
            print(f"WARNING: Unable to find price for {card['name']}")

    card_prices.sort(key=itemgetter(1), reverse=True)
    price_total = sum(p for _, p in card_prices)

    # Partition cards in named and bulk
    cards_named = [(card, price) for card, price in card_prices if price >= lump_threshold * price_total]
    cards_lump = [(card, price) for card, price in card_prices if price < lump_threshold * price_total]

    # Plot
    plt.pie(
        [price for _, price in cards_named] + [sum(p for _, p in cards_lump)],
        labels=[name for name, _ in cards_named] + ["other"],
        autopct=lambda pct: f"{pct / 100.0 * price_total:0.2f}€",
        shadow=True,
        startangle=90,
    )
    plt.title(f"{decklist.name} ({price_total:0.2f}€)")
    plt.tight_layout()
    plt.show()

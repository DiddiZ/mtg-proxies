from __future__ import annotations

from tqdm import tqdm

import scryfall
from mtgproxies.decklists.decklist import Decklist


def fetch_scans_scryfall(decklist: Decklist) -> list[str]:
    """Search Scryfall for scans of a decklist.

    Args:
        decklist: List of (count, name, set_id, collectors_number)-tuples

    Returns:
        List: List of image files
    """
    return [
        scan for card in tqdm(decklist.cards, desc="Fetching artwork") for image_uri in card.image_uris
        for scan in [scryfall.get_image(image_uri["png"], silent=True)] * card.count
    ]

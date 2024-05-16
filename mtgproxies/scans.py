from __future__ import annotations

from pathlib import Path
from typing import Literal

from tqdm import tqdm

from mtgproxies import scryfall
from mtgproxies.decklists.decklist import Decklist


def fetch_scans_scryfall(decklist: Decklist, cache_dir: Path,
                         faces: Literal["all", "front", "back"] = "all") -> list[Path]:
    """Search Scryfall for scans of a decklist.

    Args:
        decklist: The decklist to fetch scans for
        faces: Which faces to fetch ("all", "front", "back")
        cache_dir: Directory to cache the images

    Returns:
        List: List of image files
    """
    return [
        scan
        for card in tqdm(decklist.cards, desc="Fetching artwork")
        for i, image_uri in enumerate(card.image_uris)
        for scan in [scryfall.get_image(image_uri["png"], silent=True, cache_dir=cache_dir)] * card.count
        if faces == "all" or (faces == "front" and i == 0) or (faces == "back" and i > 0)
    ]

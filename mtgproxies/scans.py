import scryfall
from mtgproxies.format import format_print
from tqdm import tqdm


def fetch_scans_scryfall(decklist):
    """Search Scryfall for scans of a decklist.

    Args:
        decklist: List of (count, name, set_id, collectors_number)-tuples

    Returns:
        List: List of image files
    """
    images = []
    for card in tqdm(decklist.cards, desc="Fetching artwork"):
        if "image_uris" in card:
            image_uris = [card["image_uris"]["png"]]
        elif "card_faces" in card and "image_uris" in card["card_faces"][0]:
            image_uris = [face["image_uris"]["png"] for face in card["card_faces"]]
        else:
            raise ValueError(f"Unknown layout {card['layout']}")

        for image_uri in image_uris:
            image_file = scryfall.get_image(image_uri, silent=True)
            images.extend([image_file for _ in range(card.count)])
    return images

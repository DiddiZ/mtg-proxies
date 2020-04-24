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
    for count, card_name, set_id, collector_number in tqdm(decklist, desc="Fetching artwork"):
        card = scryfall.get_card(card_name, set_id, collector_number)
        if card is None:  # name/set/cn combination not found
            raise ValueError(f"Unable to find card {format_print(card_name, set_id, collector_number)}")

        if card["layout"] == "normal" or card["layout"] == "split" or card["layout"] == "adventure":
            image_uri = card["image_uris"]["png"]
        elif card["layout"] == "transform":
            image_uri = card["card_faces"][0]["image_uris"]["png"]
        else:
            assert False, f"Unknown layout {card['layout']}"

        image_file = scryfall.get_image(image_uri, silent=True)
        images.extend([image_file for _ in range(count)])
    return images

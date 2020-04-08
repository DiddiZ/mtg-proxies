import scryfall
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
            if scryfall.get_card(card_name) is None:  # name not found
                # Change card name

                # Search Scryfall for matches
                candidates = scryfall.search(f'{card_name} order=name', unique="cards")
                if len(candidates) != 1:  # Choice is ambiguous
                    tqdm.write(f"ERROR: Unable to find card '{card_name}'." + _recommend_card_msg(candidates))
                    continue  # Can't decide, thus skipping this card

                # Found exactly one match
                tqdm.write(f"WARNING: Misspelled card name '{card_name}'. Assuming you mean {candidates[0]['name']}.")
                card = scryfall.get_card(candidates[0]["name"], set_id, collector_number)
                card_name = candidates[0]["name"]

            if card is None:  # set/cn not found
                # Change set/cn
                card = scryfall.recommend_print(card_name, set_id, collector_number)
                tqdm.write(
                    f"WARNING: Unable to find scan of '{card_name} ({set_id.upper()}) {collector_number}'. Using '{card_name} ({card['set'].upper()}) {card['collector_number']}' instead."
                )

                set_id = card["set"]
                collector_number = card["collector_number"]

        # Warnings for low-quality scans
        if not card["highres_image"]:
            tqdm.write(
                f"WARNING: Low resolution scan of '{card_name} ({set_id.upper()}) {collector_number}'." +
                _recommend_print_msg(scryfall.recommend_print(card_name, set_id, collector_number))
            )
        if card["border_color"] != "black":
            tqdm.write(
                f"WARNING: Non-black border on '{card_name} ({set_id.upper()}) {collector_number}''." +
                _recommend_print_msg(scryfall.recommend_print(card_name, set_id, collector_number))
            )

        if card["layout"] == "normal" or card["layout"] == "split" or card["layout"] == "adventure":
            image_uri = card["image_uris"]["png"]
        elif card["layout"] == "transform":
            image_uri = card["card_faces"][0]["image_uris"]["png"]
        else:
            assert False, f"Unknown layout {card['layout']}"

        image_file = scryfall.get_image(image_uri, silent=True)
        images.extend([image_file for _ in range(count)])
    return images


def _recommend_print_msg(recommendation):
    if recommendation is not None:
        return f" Maybe you want '{recommendation['name']} ({recommendation['set'].upper()}) {recommendation['collector_number']}'?"
    return ""


def _recommend_card_msg(cards):
    if len(cards) > 0:
        card_names = ["'" + card["name"] + "'" for card in cards]
        if len(card_names) <= 10:
            card_names = ", ".join(card_names[:-1]) + " or " + card_names[-1]
        else:
            card_names = ", ".join(card_names[:10] + ["..."])

        return f" Do you mean {card_names}?"
    return ""

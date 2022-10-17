import re

import scryfall
from mtgproxies.format import color_names, format_token, listing


def find_token(type_line, power, toughness, colors, oracle_text):
    print("Searching:", type_line, power, toughness, colors, oracle_text)
    cards = scryfall.get_cards(type_line=type_line, power=power, toughness=toughness, oracle_text=oracle_text)

    # Filter colors
    cards = [card for card in cards if sorted(card["colors"]) == colors]

    if len(cards) == 0:
        print("Token not found")
        return None

    # Check for ambiguity
    oracle_ids = {card["oracle_id"]: card for card in cards}
    if len(oracle_ids) > 1:
        print("Ambiguous token: " + listing(format_token(card) for card in oracle_ids.values()))
        return None

    return scryfall.recommend_print(oracle_id=cards[0]["oracle_id"])


def parse_colors(s):
    colors = set()

    reverse_color_names = {value: key for key, value in color_names.items()}

    for word in s.lower().split(" "):
        if word in reverse_color_names:
            colors.add(reverse_color_names[word])

    return sorted(list(colors))


def parse_oracle(s):
    if s is None:
        return ""

    return s.replace(" and ", ", ")


if __name__ == "__main__":

    # token = find_token("Token Creature — Insect", "1", "1", None, None)
    # quit()

    card = scryfall.get_card("Myr Matrix")

    print(card["oracle_text"])

    for m in re.finditer(
        r"(\d+)/(\d+) ((?:white|blue|black|red|green|colorless)(?: and (?:white|blue|black|red|green))*) (.+?) (?:(artifact|enchantment) )?creature tokens?(?: with (.+?)(?:\.|,| at | for ))?",
        card["oracle_text"],
    ):
        token = find_token(
            "Token " + (m.group(5).capitalize() + " " if m.group(5) else "") + "Creature — " + m.group(4),
            m.group(1),
            m.group(2),
            parse_colors(m.group(3)),
            parse_oracle(m.group(6)),
        )

        if token:
            print("Found:", format_token(token))

    # find_token("Token Creature — Dragon", "1", "1", "Flying, devour 2")
    # find_token("Token Creature — Dragon", "1", "1", None)

    #     # if "Treasure token" in card["oracle_text"]:
    #     #     print("Treasure")

    #     print(card)

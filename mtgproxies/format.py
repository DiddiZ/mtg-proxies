"""String formatting utils."""


def format_print(card_name, set_id=None, collector_number=None):
    if "name" in card_name:
        card_name, set_id, collector_number = card_name["name"], card_name["set"], card_name["collector_number"]

    return f"'{card_name} ({set_id.upper()}) {collector_number}'"


color_names = {
    "W": "white",
    "U": "blue",
    "B": "black",
    "R": "red",
    "G": "green",
}


def format_colors(colors):
    if len(colors) == 0:
        return "colorless"
    return listing([color_names[c] for c in colors], ", ", " and ")


def listing(items, sep, final_sep, max_items=None):
    if len(items) == 0:
        return ""
    if len(items) == 1:
        return items[0]
    if max_items is None or len(items) <= max_items:
        return sep.join(items[:-1]) + final_sep + items[-1]
    else:
        return sep.join(items[:max_items] + ["..."])


def format_token(card):
    # Double faced cards
    if "colors" not in card:
        return format_token(card["card_faces"][0]) + " // " + format_token(card["card_faces"][1])

    s = ""

    # P/T
    if "power" in card:
        s += f"{card['power']}/{card['toughness']} "

    # Colors
    s += format_colors(card["colors"]) + " "

    # Type line
    s += card["type_line"]

    # Oracle text
    if card["oracle_text"] != "":
        s += f" with '{card['oracle_text']}'"

    return s

"""String formatting utils."""
from __future__ import annotations


def format_print(card_name: str | dict, set_id: str = None, collector_number: str = None) -> str:
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


def format_colors(colors: list[str]) -> str:
    if len(colors) == 0:
        return "colorless"
    return listing([color_names[c] for c in colors], ", ", " and ")


def listing(items: list[str], sep: str, final_sep: str, max_items: int = None) -> str:
    if len(items) == 0:
        return ""
    if len(items) == 1:
        return items[0]
    if max_items is None or len(items) <= max_items:
        return sep.join(items[:-1]) + final_sep + items[-1]
    else:
        return sep.join(items[:max_items] + ["..."])


def format_token(card: dict) -> str:
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

"""String formatting utils."""


def format_print(card_name, set_id=None, collector_number=None):
    if "name" in card_name:
        card_name, set_id, collector_number = card_name["name"], card_name["set"], card_name["collector_number"]

    return f"'{card_name} ({set_id.upper()}) {collector_number}'"


color_names = {
    'W': 'white',
    'U': 'blue',
    'B': 'black',
    'R': 'red',
    'G': 'green',
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

"""Simple interface to the Scryfall API.

See:
    https://scryfall.com/docs/api
"""

import json
import logging
import threading
from collections import defaultdict
from functools import cache
from pathlib import Path

import numpy as np
import requests
from tqdm import tqdm

from mtgproxies.scryfall.rate_limit import RateLimiter


logger = logging.getLogger(__name__)

DEFAULT_CACHE_DIR = Path(__file__).parent / ".cache" / "mtgproxies" / "scryfall"
# cache.mkdir(parents=True, exist_ok=True)  # Create cache folder
scryfall_rate_limiter = RateLimiter(delay=0.1)
_download_lock = threading.Lock()


def get_image(image_uri: str, cache_dir: Path, silent: bool = False) -> Path:
    """Download card artwork and return the path to a local copy.

    Uses cache and Scryfall API call rate limit.

    Returns:
        string: Path to local file.
    """
    split = image_uri.split("/")
    file_name = split[-5] + "_" + split[-4] + "_" + split[-1].split("?")[0]
    logger.debug(f"Downloading {file_name} from {image_uri}")
    return get_file(file_name, image_uri, cache_dir=cache_dir, silent=silent)


def get_file(file_name: str, url: str, cache_dir: Path, silent: bool = False) -> Path:
    """Download a file and return the path to a local copy.

    Uses cache and Scryfall API call rate limit.

    Returns:
        string: Path to local file.
    """
    file_path = cache_dir / file_name
    with _download_lock:
        if not file_path.is_file():
            if "api.scryfall.com" in url:  # Apply rate limit
                with scryfall_rate_limiter:
                    download(url, file_path, silent=silent)
            else:
                download(url, file_path, silent=silent)

    return file_path


def download(url: str, dst, chunk_size: int = 1024 * 4, silent: bool = False):
    """Download a file with a tqdm progress bar."""
    with requests.get(url, stream=True) as req:
        req.raise_for_status()
        file_size = int(req.headers["Content-Length"]) if "Content-Length" in req.headers else None
        with open(dst, "xb") as f, tqdm(
            total=file_size,
            unit="B",
            unit_scale=True,
            desc=url.split("/")[-1],
            disable=silent,
        ) as pbar:
            for chunk in req.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    pbar.update(chunk_size)


def depaginate(url: str) -> list[dict]:
    """Recursively unpack Scryfall search results from multiple pages into a single list.

    Uses Scryfall API call rate limit to avoid excessive requests.

    Returns:
        list: Concatenation of all `data` entries.
    """
    with scryfall_rate_limiter:
        response = requests.get(url).json()
    assert response["object"]

    if "data" not in response:
        return []
    data = response["data"]
    if response["has_more"]:
        data = data + depaginate(response["next_page"])

    return data


def search(q: str) -> list[dict]:
    """Perform Scryfall search.

    Returns:
        list: All matching cards.

    See:
        https://scryfall.com/docs/api/cards/search
    """
    return depaginate(f"https://api.scryfall.com/cards/search?q={q}&format=json")


@cache
def _get_database(cache_dir: Path, database_name: str = "default_cards"):
    databases = depaginate("https://api.scryfall.com/bulk-data")
    bulk_data = [database for database in databases if database["type"] == database_name]
    if len(bulk_data) != 1:
        raise ValueError(f"Unknown database {database_name}")

    bulk_file = get_file(bulk_data[0]["download_uri"].split("/")[-1], bulk_data[0]["download_uri"], cache_dir=cache_dir)
    with open(bulk_file, encoding="utf-8") as json_file:
        return json.load(json_file)


def canonic_card_name(card_name: str) -> str:
    """Get canonic card name representation."""
    card_name = card_name.lower()

    # Replace special chars
    card_name = card_name.replace("æ", "ae")  # Sometimes used, e.g. in "Vedalken Aethermage"

    return card_name


def get_card(
    card_name: str, cache_dir: Path, set_id: str | None = None, collector_number: str | None = None
) -> dict | None:
    """Find a card by its name and possibly set and collector number.

    In case, the Scryfall database contains multiple cards, the first is returned.

    Args:
        card_name: Exact English card name
        cache_dir: Path to cache directory
        set_id: Shorthand set name
        collector_number: Collector number, may be a string for e.g. promo suffixes

    Returns:
        card: Dictionary of card, or `None` if not found.
    """
    cards = get_cards(name=card_name, set=set_id, collector_number=collector_number, cache_dir=cache_dir)

    return cards[0] if len(cards) > 0 else None


def get_cards(cache_dir: Path, database: str = "default_cards", **kwargs):
    """Get all cards matching certain attributes.

    Matching is case-insensitive.

    Args:
        cache_dir: Path to cache directory
        database: Name of the database to use
        kwargs: (key, value) pairs, e.g. `name="Tendershoot Dryad", set="RIX"`.
                keys with a `None` value are ignored

    Returns:
        List of all matching cards
    """
    cards = _get_database(cache_dir=cache_dir, database_name=database)

    for key, value in kwargs.items():
        if value is not None:
            value = value.lower()
            if key == "name":  # Normalize card name
                value = canonic_card_name(value)
            cards = [card for card in cards if key in card and card[key].lower() == value]

    return cards


def get_faces(card):
    """All faces on this card.

    For single faced cards, this is just the card.

    Args:
        card: Scryfall card object
    """
    if "image_uris" in card:
        return [card]
    elif "card_faces" in card and "image_uris" in card["card_faces"][0]:
        return card["card_faces"]
    else:
        raise ValueError(f"Unknown layout {card['layout']}")


def recommend_print(
    cache_dir: Path, current=None, card_name: str | None = None, oracle_id: str | None = None, mode="best"
):
    if current is not None and oracle_id is None:  # Use oracle id of current
        if current.get("layout") == "reversible_card":
            # Reversible cards have the same oracle id for both faces
            oracle_id = current["card_faces"][0]["oracle_id"]
        else:
            oracle_id = current["oracle_id"]

    if oracle_id is not None:
        alternatives = get_cards_by_oracle_id(cache_dir=cache_dir)[oracle_id]
    else:
        alternatives = get_cards(name=card_name, cache_dir=cache_dir)

    def score(card: dict):
        points = 0
        if card["set"] != "mb1" and card["border_color"] != "gold":
            points += 1
        if card["frame"] == "2015":
            points += 2
        if not card["digital"]:
            points += 4
        if card["border_color"] == "black" and (
            mode != "best" or "frame_effects" not in card or "extendedart" not in card["frame_effects"]
        ):
            points += 8
        if card["collector_number"][-1] not in ["p", "s"] and card["nonfoil"]:
            points += 16
        if card["highres_image"]:
            points += 32
        if card["lang"] == "en":
            points += 64

        return points

    scores = [score(card) for card in alternatives]

    if mode == "best":
        if current is not None and scores[alternatives.index(current)] == np.max(scores):
            return current  # No better recommendation

        # Return print with highest score
        recommendation = alternatives[np.argmax(scores)]
        return recommendation
    elif mode == "all":
        recommendations = list(np.array(alternatives)[np.argsort(scores)][::-1])

        # Bring current print to front
        if current is not None:
            if current in recommendations:
                recommendations.remove(current)
            recommendations = [current, *recommendations]

        # Return all card in descending order
        return recommendations
    elif mode == "choices":
        artworks = np.array(
            [
                get_faces(card)[0]["illustration_id"] if "illustration_id" in get_faces(card)[0] else card["id"]
                for card in alternatives
            ]  # Not all cards have illustrations, use id instead
        )
        choices = []
        for artwork in set(artworks):
            artwork_alternatives = np.array(alternatives)[artworks == artwork]
            artwork_scores = np.array(scores)[artworks == artwork]

            recommendations = artwork_alternatives[artwork_scores == np.max(artwork_scores)]
            # TODO Sort again
            choices.extend(recommendations)

        # Bring current print to front
        if current is not None:
            choices = [current] + [c for c in choices if c["id"] != current["id"]]

        return choices
    else:
        raise ValueError(f"Unknown mode '{mode}'")


@cache
def card_by_id(cache_dir: Path):
    """Create dictionary to look up cards by their id.

    Faster than repeated lookup via get_cards().

    Returns:
        dict {id: card}
    """
    return {c["id"]: c for c in get_cards(cache_dir=cache_dir)}


@cache
def get_cards_by_oracle_id(cache_dir: Path):
    """Create dictionary to look up cards by their oracle id.

    Faster than repeated lookup via get_cards().

    Returns:
        dict {id: [cards]}
    """
    cards_by_oracle_id = defaultdict(list)
    for c in get_cards(cache_dir=cache_dir):
        if "oracle_id" in c:  # Not all cards have a oracle id, *sigh*
            cards_by_oracle_id[c["oracle_id"]].append(c)
        elif "card_faces" in c and "oracle_id" in c["card_faces"][0]:
            cards_by_oracle_id[c["card_faces"][0]["oracle_id"]].append(c)
    return cards_by_oracle_id


@cache
def get_oracle_ids_by_name(cache_dir: Path) -> dict[str, list[dict]]:
    """Create dictionary to look up oracle ids by their name.

    Faster than repeated lookup via `get_cards(oracle_id=oracle_id)`.
    Also matches the front side of double faced cards.
    Names are lower case.

    Returns:
        dict {name: [oracle_ids]}
    """
    oracle_ids_by_name = defaultdict(set)
    for oracle_id, cards in get_cards_by_oracle_id(cache_dir=cache_dir).items():
        card = cards[0]
        if card["layout"] in ["art_series"]:  # Skip art series, as they have double faced names
            continue
        name = card["name"].lower()
        # Use name and also front face only for double faced cards
        oracle_ids_by_name[name].add(oracle_id)
        if "//" in name:
            oracle_ids_by_name[name.split(" // ")[0]].add(oracle_id)

    # Converts sets to lists
    oracle_ids_by_name = {k: list(v) for k, v in oracle_ids_by_name.items()}
    return oracle_ids_by_name


def get_price(cache_dir: Path, oracle_id: str, currency: str = "eur", foil: bool | None = None) -> float | None:
    """Find the lowest price for oracle id.

    Args:
        cache_dir: Path to cache directory
        oracle_id: oracle_id of card
        currency: `usd`, `eur` or `tix`
        foil: `False`, `True`, or `None` for any
    """
    cards = get_cards_by_oracle_id(cache_dir=cache_dir)[oracle_id]

    slots = []
    if not foil:
        slots += [currency]
    if (foil or foil is None) and currency != "tix":  # "TIX has no foil"
        slots += [currency + "_foil"]

    prices = [float(c["prices"][slot]) for c in cards for slot in slots if c["prices"][slot] is not None]

    if len(prices) == 0 and currency == "eur":  # Try dollar and apply conversion
        usd = get_price(cache_dir=cache_dir, oracle_id=oracle_id, currency="usd")
        return 0.83 * usd if usd is not None else None

    return min(prices) if len(prices) > 0 else None

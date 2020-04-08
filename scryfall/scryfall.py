"""Simple interface to the Scryfall API.

See:
    https://scryfall.com/docs/api
"""
import io
import json
import time
import requests
import threading
from pathlib import Path
from tempfile import gettempdir
from tqdm import tqdm

cache = Path(gettempdir()) / 'scryfall_cache'
cache.mkdir(parents=True, exist_ok=True)  # Create cach folder
last_scryfall_api_call = 0
scryfall_api_call_delay = 0.1
_lock = threading.Lock()
_databases = {}


def rate_limit():
    """Sleep to ensure 100ms delay between Scryfall API calls, as requested by Scryfall."""
    with _lock:
        global last_scryfall_api_call
        if time.time() < last_scryfall_api_call + scryfall_api_call_delay:
            time.sleep(last_scryfall_api_call + scryfall_api_call_delay - time.time())
        last_scryfall_api_call = time.time()
    return


def get_image(image_uri, silent=False):
    """Download card artwork and return the path to a local copy.

    Uses cache and Scryfall API call rate limit.

    Returns:
        string: Path to local file.
    """
    split = image_uri.split('/')
    file_name = split[-5] + '_' + split[-4] + '_' + split[-1].split('?')[0]
    return get_file(file_name, image_uri, silent=silent)


def get_file(file_name, url, silent=False):
    """Download a file and return the path to a local copy.

    Uses cache and Scryfall API call rate limit.

    Returns:
        string: Path to local file.
    """
    file_path = cache / file_name
    if not file_path.is_file():
        rate_limit()
        download(url, file_path, silent=silent)

    return str(file_path)


def download(url, dst, chunk_size=1024 * 4, silent=False):
    """Download a file with a tqdm progress bar."""
    with requests.get(url, stream=True) as req:
        req.raise_for_status()
        file_size = int(req.headers["Content-Length"])
        with open(dst, 'xb') as f, tqdm(
            total=file_size,
            unit='B',
            unit_scale=True,
            desc=url.split('/')[-1],
            disable=silent,
        ) as pbar:
            for chunk in req.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    pbar.update(chunk_size)


def depaginate(url):
    """Depaginates Scryfall search results.

    Uses cache and Scryfall API call rate limit.

    Returns:
        list: Concatenation of all `data` entries.
    """
    rate_limit()
    response = requests.get(url).json()
    assert response["object"]

    if "data" not in response:
        return []
    data = response["data"]
    if response["has_more"]:
        data = data + depaginate(response["next_page"])

    return data


def search(q, include_extras="false", include_multilingual="false", unique="cards"):
    """Perform Scryfall search.

    Returns:
        list: All matching cards.

    See:
        https://scryfall.com/docs/api/cards/search
    """
    return depaginate(
        f"https://api.scryfall.com/cards/search?q={q}&format=json&include_extras={include_extras}" +
        f"&include_multilingual={include_multilingual}&unique={unique}"
    )


def _get_database(database_name="scryfall-default-cards"):
    global _databases

    if database_name not in _databases:
        bulk_file = get_file(database_name + ".json", "https://archive.scryfall.com/" + database_name + ".json")
        with io.open(bulk_file, mode="r", encoding="utf-8") as json_file:
            data = json.load(json_file)
        _databases[database_name] = data
    return _databases[database_name]


def get_card(card_name, set_id=None, collector_number=None):
    """Find a card by it's name and possibly set and collector number.

    In case, the Scryfall database contains multiple cards, the first is returned.

    Args:
        card_name: Exact English card name
        set_id: Shorthand set name
        collector_number: Collector number, may be a string for e.g. promo suffixes

    Returns:
        card: Dictionary of card, or `None` if non found.
    """
    cards = [card for card in _get_database("scryfall-default-cards") if card["name"].lower() == card_name.lower()]
    if set_id is not None:  # Filter for set
        cards = [card for card in cards if card["set"].lower() == set_id.lower()]
    if collector_number is not None:  # Filter for cn
        cards = [card for card in cards if card["collector_number"].lower() == collector_number.lower()]

    return cards[0] if len(cards) > 0 else None


def recommend_print(card_name, set_id=None, collector_number=None):
    for query in [
        "is:hires border=black"  # High-res and black border preferred
        "is:hires",  # Only high-res
        "border=black",  # Only black border
        "",  # Anything goes
    ]:
        cards = search(f'!"{card_name}" ' + query, unique="art")
        if len(cards) > 0:
            card = cards[0]
            if card["set"].lower() == set_id.lower() and card["collector_number"].lower() == collector_number.lower():
                return None  # No better recommendation
            return card

    return None

"""Simple interface to the Scryfall API.

See:
    https://scryfall.com/docs/api
"""
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


def rate_limit():
    """Sleep to ensure 100ms delay between Scryfall API calls, as requested by Scryfall."""
    with _lock:
        global last_scryfall_api_call
        if time.time() < last_scryfall_api_call + scryfall_api_call_delay:
            time.sleep(last_scryfall_api_call + scryfall_api_call_delay - time.time())
        last_scryfall_api_call = time.time()
    return


def get_image(image_uri):
    """Download card artwork and return the path to a local copy.

    Uses cache and Scryfall API call rate limit.

    Returns:
        string: Path to local file.
    """
    split = image_uri.split('/')
    file_name = split[-5] + '_' + split[-4] + '_' + split[-1].split('?')[0]
    return get_file(file_name, image_uri)


def get_file(file_name, url):
    """Download a file and return the path to a local copy.

    Uses cache and Scryfall API call rate limit.

    Returns:
        string: Path to local file.
    """
    file_path = cache / file_name
    if not file_path.is_file():
        rate_limit()
        download(url, file_path)

    return str(file_path)


def download(url, dst, chunk_size=1024 * 4):
    """Download a file with a tqdm progress bar."""
    file_size = int(requests.head(url).headers["Content-Length"])
    req = requests.get(url, stream=True)
    with open(dst, 'xb') as f, tqdm(total=file_size, unit='B', unit_scale=True, desc=url.split('/')[-1]) as pbar:
        for chunk in req.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
            pbar.update(chunk_size)
        pbar.close()


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
        print(url)
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

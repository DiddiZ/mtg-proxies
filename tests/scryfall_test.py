import os

import pytest

# Vedalken Aethermage — stable old card, timestamp won't change
_IMAGE_URI = "https://cards.scryfall.io/png/front/4/9/49999b95-5e62-414c-b975-4191b9c1ab39.png?1562402358"
_TIMESTAMP = 1562402358


def test_get_image_evicts_stale_cache() -> None:
    from mtg_proxies.scryfall.scryfall import get_image

    # Populate cache then make the file appear stale
    path = get_image(_IMAGE_URI, silent=True)
    os.utime(path, (_TIMESTAMP - 1, _TIMESTAMP - 1))

    get_image(_IMAGE_URI, silent=True)

    assert os.path.getmtime(path) > _TIMESTAMP - 1, "stale cached file should have been re-downloaded"


def test_get_image_keeps_fresh_cache() -> None:
    from mtg_proxies.scryfall.scryfall import get_image

    # Populate cache then mark the file as newer than the URI timestamp
    path = get_image(_IMAGE_URI, silent=True)
    os.utime(path, (_TIMESTAMP + 1, _TIMESTAMP + 1))

    get_image(_IMAGE_URI, silent=True)

    assert os.path.getmtime(path) == _TIMESTAMP + 1, "fresh cached file should not be re-downloaded"


@pytest.mark.parametrize(
    ("id", "n_faces"),
    [
        ("76ac5b70-47db-4cdb-91e7-e5c18c42e516", 1),
        ("c470539a-9cc7-4175-8f7c-c982b6072b6d", 2),  # Modal double-faced
        ("c1f53d7a-9dad-46e8-b686-cd1362867445", 2),  # Transforming double-faced
        ("6ee6cd34-c117-4d7e-97d1-8f8464bfaac8", 1),  # Flip
    ],
)
def test_get_faces(id: str, n_faces: int) -> None:
    from mtg_proxies import scryfall

    card = scryfall.card_by_id()[id]
    faces = scryfall.get_faces(card)

    assert type(faces) is list
    assert len(faces) == n_faces
    for face in faces:
        assert "illustration_id" in face


@pytest.mark.parametrize(
    ("name", "expected_id"),
    [
        ("Vedalken Aethermage", "496eb37d-5c8f-4dd7-a0a7-3ed1bd2210d6"),
        ("vedalken aethermage", "496eb37d-5c8f-4dd7-a0a7-3ed1bd2210d6"),
        ("vedalken Æthermage", "496eb37d-5c8f-4dd7-a0a7-3ed1bd2210d6"),
        ("vedalken æthermage", "496eb37d-5c8f-4dd7-a0a7-3ed1bd2210d6"),
    ],
)
def test_canonic_card_name(name: str, expected_id: str) -> None:
    from mtg_proxies import scryfall

    card = scryfall.get_card(name)

    assert card["id"] == expected_id

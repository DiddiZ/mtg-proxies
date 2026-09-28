import pytest


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
    ("name", "oracle_id"),
    [
        ("Vedalken Aethermage", "271b37b6-b60b-4687-bd82-ecacf3b66cb3"),
        ("vedalken aethermage", "271b37b6-b60b-4687-bd82-ecacf3b66cb3"),
        ("Vedalken Æthermage", "271b37b6-b60b-4687-bd82-ecacf3b66cb3"),
        ("vedalken æthermage", "271b37b6-b60b-4687-bd82-ecacf3b66cb3"),
        # ("Demon's Disciple", "d5a33091-a348-4b13-8dbd-79ab0ad99afe"),
        # ("Demons Disciple", "d5a33091-a348-4b13-8dbd-79ab0ad99afe"),
    ],
)
def test_canonic_card_name(name: str, oracle_id: str) -> None:
    from mtg_proxies import scryfall

    card = scryfall.get_card(name)

    assert card is not None
    assert card["oracle_id"] == oracle_id


def test_get_cards() -> None:
    from mtg_proxies import scryfall

    cards = scryfall.get_cards(highres_image=True)
    for card in cards:
        assert card["highres_image"] is True

    cards = scryfall.get_cards(highres_image=False)
    for card in cards:
        assert card["highres_image"] is False

    cards = scryfall.get_cards(edhrec_rank=1)
    for card in cards:
        assert card["edhrec_rank"] == 1

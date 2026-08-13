from pathlib import Path
from unittest import mock

import pytest


def test_get_database_supports_scryfall_jsonl_bulk_data(tmp_path: Path) -> None:
    from mtg_proxies.scryfall import scryfall

    download_url = "https://data.scryfall.io/default-cards/default-cards.jsonl.gz"
    bulk_file = tmp_path / "default-cards.jsonl.gz"
    bulk_file.write_bytes(b"")

    with (
        mock.patch.object(
            scryfall,
            "depaginate",
            return_value=[{"type": "default_cards", "jsonl_download_uri": download_url}],
        ),
        mock.patch.object(scryfall, "get_file", return_value=str(bulk_file)),
        mock.patch("gzip.open", mock.mock_open(read_data='{"name": "Lightning Bolt"}\n')),
    ):
        scryfall._get_database.cache_clear()
        assert scryfall._get_database() == [{"name": "Lightning Bolt"}]
        scryfall._get_database.cache_clear()


def test_download_keeps_partial_file_after_failure_for_resume(tmp_path: Path) -> None:
    from mtg_proxies.scryfall import scryfall

    destination = tmp_path / "default-cards.jsonl.gz"
    response = mock.MagicMock()
    response.headers = {}
    response.iter_content.side_effect = OSError("connection interrupted")
    request = mock.MagicMock()
    request.__enter__.return_value = response

    with mock.patch.object(scryfall.requests, "get", return_value=request):
        with pytest.raises(OSError, match="connection interrupted"):
            scryfall.download("https://data.scryfall.io/default-cards/default-cards.jsonl.gz", destination)

    assert not destination.exists()
    assert destination.with_suffix(".gz.partial").exists()



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

import pytest


@pytest.mark.parametrize(
    "id,n_faces",
    [
        ("76ac5b70-47db-4cdb-91e7-e5c18c42e516", 1),
        ("c470539a-9cc7-4175-8f7c-c982b6072b6d", 2),  # Modal double-faced
        ("c1f53d7a-9dad-46e8-b686-cd1362867445", 2),  # Transforming double-faced
        ("6ee6cd34-c117-4d7e-97d1-8f8464bfaac8", 1),  # Flip
    ],
)
def test_get_faces(id: str, n_faces: int):
    import scryfall

    card = scryfall.card_by_id()[id]
    faces = scryfall.get_faces(card)

    assert type(faces) == list
    assert len(faces) == n_faces
    for face in faces:
        assert "illustration_id" in face

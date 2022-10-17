import os


def test_parsing():
    from mtgproxies.decklists import parse_decklist

    decklist, ok, warnings = parse_decklist("examples/decklist.txt")

    assert ok
    assert len(warnings) == 0

    with open("examples/decklist.txt", "r", encoding="utf-8") as f:
        # Ignore differences in linebreaks
        assert (format(decklist, "arena") + os.linesep).replace("\r\n", "\n") == f.read().replace("\r\n", "\n")

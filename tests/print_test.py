from pathlib import Path
from tempfile import TemporaryDirectory


def test_print_pdf():
    from mtgproxies import fetch_scans_scryfall, print_cards_fpdf
    from mtgproxies.decklists import parse_decklist

    decklist, _, _ = parse_decklist("examples/decklist.txt")
    images = fetch_scans_scryfall(decklist)

    with TemporaryDirectory() as dir:
        out_file = Path(dir) / "decklist.pdf"

        print_cards_fpdf(images, out_file)

        assert out_file.is_file()


def test_print_png():
    from mtgproxies import fetch_scans_scryfall, print_cards_matplotlib
    from mtgproxies.decklists import parse_decklist

    decklist, _, _ = parse_decklist("examples/decklist.txt")
    images = fetch_scans_scryfall(decklist)

    with TemporaryDirectory() as dir:
        out_file = Path(dir) / "decklist.png"

        print_cards_matplotlib(images, str(out_file))

        assert (Path(dir) / "decklist_000.png").is_file()

import math
from pathlib import Path

import pytest

from mtgproxies import dimensions
from mtgproxies.print_cards import MatplotlibCardAssembler, FPDF2CardAssembler


# @pytest.fixture(scope="module")
# def example_images(cache_dir) -> list[Path]:
#     from mtgproxies import fetch_scans_scryfall
#     from mtgproxies.decklists import parse_decklist
#
#     decklist, _, _ = parse_decklist(Path(__file__).parent.parent / "examples/decklist.txt", cache_dir=cache_dir)
#     images = fetch_scans_scryfall(decklist)
#
#     return images


def test_example_images(example_images_7: list[str], example_images_24: list[Path]):
    assert len(example_images_7) == 7
    assert len(example_images_24) == 24


# def test_print_cards_fpdf(example_images: list[str], tmp_path: Path):
#     from mtgproxies import print_cards_fpdf
#
#     out_file = tmp_path / "decklist.pdf"
#     print_cards_fpdf(example_images, out_file)
#
#     assert out_file.is_file()


# def test_print_cards_matplotlib_pdf(example_images: list[str], tmp_path: Path):
#     from mtgproxies import print_cards_matplotlib
#
#     out_file = tmp_path / "decklist.pdf"
#     print_cards_matplotlib(example_images, out_file)
#
#     assert out_file.is_file()


def test_print_cards_matplotlib(example_images_24: list[Path]):
    assembler = MatplotlibCardAssembler(
        dpi=600,
        paper_size=dimensions.PAPER_SIZE['A4']['in'],
        card_size=dimensions.MTG_CARD_SIZE['in'],
        border_crop=0,
        crop_marks_thickness=0.01,
        cut_spacing_thickness=0.2,
        fill_corners=False,
        background_color=None,
        page_safe_margin=0,
        units="in",
    )

    out_file = Path("test_proxies.png")
    assembler.assemble(example_images_24, out_file)
    print(out_file.absolute().as_posix())


def test_print_cards_fpdf(example_images_24: list[Path]):
    assembler = FPDF2CardAssembler(
        paper_size=dimensions.PAPER_SIZE['A4']['mm'],
        card_size=dimensions.MTG_CARD_SIZE['mm'],
        border_crop=0,
        crop_marks_thickness=0.5,
        cut_spacing_thickness=0.1,
        fill_corners=False,
        background_color=None,
        page_safe_margin=0,
        units="mm",
    )

    out_file = Path("test_proxies.pdf")
    assembler.assemble(example_images_24, out_file)
    print(out_file.absolute().as_posix())


def test_dimension_units_coverage():
    from mtgproxies.dimensions import Units, PAPER_SIZE

    for unit in Units.__args__:
        for spec in PAPER_SIZE:
            assert unit in PAPER_SIZE[spec]


@pytest.mark.parametrize(
    "unit,amount,expected_mm",
    [
        ("in", 6, 152.4),
        ("cm", 6, 60),
        ("mm", 6, 6),
    ],
)
def test_units_to_mm(unit: str, amount: float, expected_mm: float):
    from mtgproxies.dimensions import UNITS_TO_MM
    assert math.isclose(amount * UNITS_TO_MM[unit], expected_mm, rel_tol=1e-3)
    assert math.isclose(expected_mm / UNITS_TO_MM[unit], amount, rel_tol=1e-3)

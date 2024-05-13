import math
from pathlib import Path

import pytest

from mtgproxies import dimensions
from mtgproxies.print_cards import FPDF2CardAssembler, MatplotlibCardAssembler


def test_example_images(example_images_7: list[str], example_images_24: list[Path]):
    assert len(example_images_7) == 7
    assert len(example_images_24) == 24


def test_print_cards_matplotlib(example_images_24: list[Path], test_outputs_dir: Path):
    assembler = MatplotlibCardAssembler(
        dpi=600,
        paper_size=dimensions.PAPER_SIZE["A4"]["in"],
        card_size=dimensions.MTG_CARD_SIZE["in"],
        border_crop=0,
        crop_marks_thickness=0.01,
        cut_spacing_thickness=0.2,
        filled_corners=True,
        background_color=None,
        page_safe_margin=0,
        units="in",
    )

    out_file = test_outputs_dir / "test_proxies.png"
    assembler.assemble(example_images_24, out_file)
    glob_pattern = out_file.stem + "*" + out_file.suffix
    result_files = list(out_file.parent.glob(glob_pattern))
    assert len(result_files) == 3, f"Expected 3 files, the glob pattern {glob_pattern} got {result_files}"


def test_print_cards_fpdf(example_images_24: list[Path], test_outputs_dir: Path):
    assembler = FPDF2CardAssembler(
        paper_size=dimensions.PAPER_SIZE["A4"]["mm"],
        card_size=dimensions.MTG_CARD_SIZE["mm"],
        border_crop=0,
        crop_marks_thickness=0.5,
        cut_spacing_thickness=0.1,
        filled_corners=True,
        background_color=None,
        page_safe_margin=0,
        units="mm",
    )

    out_file = test_outputs_dir / "test_proxies.pdf"
    assembler.assemble(example_images_24, out_file)
    assert out_file.exists()


def test_dimension_units_coverage():
    from mtgproxies.dimensions import PAPER_SIZE, Units

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

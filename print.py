from pathlib import Path
from typing import Literal

import click
import numpy as np
from nptyping import Float32, NDArray, Shape
from webcolors import IntegerRGB, name_to_rgb

from mtgproxies import fetch_scans_scryfall
from mtgproxies.cli import parse_decklist_spec
from mtgproxies.decklists import Decklist
from mtgproxies.dimensions import MTG_CARD_SIZE, PAPER_SIZE, UNITS_TO_MM, Units
from mtgproxies.print_cards import FPDF2CardAssembler, MatplotlibCardAssembler
from mtgproxies.scryfall.scryfall import DEFAULT_CACHE_DIR


# def papersize(string: str) -> np.ndarray:
#     spec = string.lower()
#     if spec == "a4":
#         return np.array([21, 29.7]) / 2.54
#     if "x" in spec:
#         split = spec.split("x")
#         return np.array([float(split[0]), float(split[1])])
#     raise argparse.ArgumentTypeError()


def click_callback_cardsize(
    ctx: click.Context, param: click.Parameter, value: str
) -> NDArray[Shape["2"], Float32] | None:
    if value is None:
        return None
    spec = value.lower()
    if "x" in spec:
        split = spec.split("x")
        return np.asarray([float(split[0]), float(split[1])]).astype(float)
    raise click.BadParameter("Card size must be in the format WIDTHxHEIGHT", param=param, ctx=ctx)


def click_callback_papersize(
    ctx: click.Context, param: click.Parameter, value: str
) -> str | NDArray[Shape["2"], Float32]:
    spec = value.upper()
    if spec in PAPER_SIZE:
        return spec
    elif "x" in spec:
        split = spec.split("x")
        if len(split) == 2:
            return np.asarray([float(split[0]), float(split[1])], dtype=float)
        else:
            raise click.BadParameter("Paper size must be in the format WIDTHxHEIGHT", param=param, ctx=ctx)

    else:
        raise click.BadParameter(
            f"Paper size not supported: {spec}. Try one of: {', '.join(PAPER_SIZE.keys())}, "
            f"or define the dimensions in a WIDTHxHEIGHT format",
            param=param,
            ctx=ctx,
        )


def click_callback_cache_dir(ctx: click.Context, param: click.Parameter, value: Path) -> Path:
    assert isinstance(value, Path)
    if not value.exists():
        value.mkdir(parents=True)
    return value


@click.group(name="print")
@click.pass_context
def command_group_print(ctx):
    ctx.ensure_object(dict)


def common_cli_arguments(func):
    func = click.argument("output_file", type=click.Path(path_type=Path, exists=False, writable=True), required=True)(
        func
    )
    func = click.argument("deck_list", type=str, nargs=-1)(func)
    func = click.option(
        "--crop-mark-thickness",
        "-cm",
        type=float,
        default=0.0,
        help="Thickness of crop marks in the specified units. Use 0 to disable crop marks.",
    )(func)
    func = click.option(
        "--cut-spacing-thickness",
        "-cl",
        type=float,
        default=0.0,
        help="Thickness of cut lines in the specified units. Use 0 to disable cut lines.",
    )(func)
    func = click.option(
        "--crop-border",
        "-cb",
        type=float,
        default=0.0,
        help="How much to crop the borders of the cards in the specified units.",
    )(func)
    func = click.option(
        "--background-color",
        "-bg",
        type=name_to_rgb,
        default=None,
        help="Background color of the cards, either by name or by hex code.",
    )(func)
    func = click.option(
        "--paper-size",
        "-ps",
        type=str,
        default="a4",
        callback=click_callback_papersize,
        help="Paper size keyword (A0 - A10) or dimensions in the format WIDTHxHEIGHT.",
    )(func)
    func = click.option(
        "--page-safe-margin",
        "-m",
        type=float,
        default=0.0,
        help="Margin around the area where no cards will be printed. Useful for printers that can't print to the edge.",
    )(func)
    func = click.option(
        "--faces", "-f", type=click.Choice(["all", "front", "back"]), default="all", help="Which faces to print."
    )(func)
    func = click.option(
        "--units",
        "-u",
        type=click.Choice(Units.__args__),
        default="mm",
        help="Units of the specified dimensions. Default is mm.",
    )(func)
    func = click.option(
        "--filled-corners",
        "-fc",
        is_flag=True,
        help="Fill the corners of the cards with the colors from the edge of the card. "
        "Works well for cards with uniformly colored borders (any color). May look fine even on borderless cards.",
    )(func)
    func = click.option(
        "--cache-dir",
        "-cd",
        type=click.Path(path_type=Path, file_okay=False, dir_okay=True, writable=True),
        default=DEFAULT_CACHE_DIR,
        callback=click_callback_cache_dir,
        help="Directory to store cached card images.",
    )(func)
    func = click.option(
        "--card-size",
        "-cs",
        default=None,
        help="Size of the cards in the format WIDTHxHEIGHT in the units specified by user. "
        "Default is 2.5x3.5 inches (or 63.1x88 mm).",
        callback=click_callback_cardsize,
    )(func)
    return func


@command_group_print.command(name="pdf")
@common_cli_arguments
def command_pdf(
    deck_list: list[str],
    output_file: Path,
    faces: Literal["all", "front", "back"],
    crop_mark_thickness: float,
    cut_spacing_thickness: float,
    crop_border: float,
    background_color: IntegerRGB,
    paper_size: str | NDArray[Shape["2"], Float32],
    units: Units,
    filled_corners: bool,
    page_safe_margin: float,
    cache_dir: Path,
    card_size: NDArray[Shape["2"], Float32] | None,
):
    """This command generates a PDF document at OUTPUT_FILE with the cards from the files in DECK_LIST.

    DECK_LIST is a list of files containing filepaths to decklist files in text/arena format
    or entries in a manastack:{manastack_id} or archidekt:{archidekt_id} format.

    OUTPUT_FILE is the path to the output PDF file.

    """
    images, resolved_card_size, resolved_paper_size = process_dimensions_and_decklist(
        cache_dir, card_size, deck_list, faces, paper_size, units
    )

    # Plot cards
    printer = FPDF2CardAssembler(
        units=units,
        paper_size=resolved_paper_size,
        card_size=resolved_card_size,
        crop_marks_thickness=crop_mark_thickness,
        cut_spacing_thickness=cut_spacing_thickness,
        border_crop=crop_border,
        background_color=background_color,
        filled_corners=filled_corners,
        page_safe_margin=page_safe_margin,
    )

    printer.assemble(card_image_filepaths=images, output_filepath=output_file)


@command_group_print.command(name="image")
@common_cli_arguments
@click.option("--dpi", "-d", type=int, default=300, help="DPI of the output image.")
def command_image(
    deck_list: list[str],
    output_file: Path,
    faces: Literal["all", "front", "back"],
    crop_mark_thickness: float,
    cut_spacing_thickness: float,
    crop_border: float,
    background_color: IntegerRGB,
    paper_size: str | NDArray[Shape["2"], Float32],
    units: Units,
    filled_corners: bool,
    page_safe_margin: float,
    cache_dir: Path,
    card_size: NDArray[Shape["2"], Float32] | None,
    dpi: int,
):
    """This command generates an image file at OUTPUT_FILE with the cards from the files in DECK_LIST.

    DECK_LIST is a list of files containing filepaths to decklist files in text/arena format
    or entries in a manastack:{manastack_id} or archidekt:{archidekt_id} format.

    OUTPUT_FILE is the path to the output image file. The extension of the file determines the format. Only formats
    supported by matplotlib are allowed.

    """
    images, resolved_card_size, resolved_paper_size = process_dimensions_and_decklist(
        cache_dir, card_size, deck_list, faces, paper_size, units
    )

    # Plot cards
    printer = MatplotlibCardAssembler(
        units=units,
        paper_size=resolved_paper_size,
        card_size=resolved_card_size,
        crop_marks_thickness=crop_mark_thickness,
        cut_spacing_thickness=cut_spacing_thickness,
        border_crop=crop_border,
        background_color=background_color,
        filled_corners=filled_corners,
        page_safe_margin=page_safe_margin,
        dpi=dpi,
    )

    printer.assemble(card_image_filepaths=images, output_filepath=output_file)


def process_dimensions_and_decklist(cache_dir, card_size, deck_list, faces, paper_size, units):
    parsed_deck_list = Decklist()
    for deck in deck_list:
        parsed_deck_list.extend(parse_decklist_spec(deck, cache_dir=cache_dir))
    # Fetch scans
    images = fetch_scans_scryfall(decklist=parsed_deck_list, cache_dir=cache_dir, faces=faces)

    # resolve paper size
    if isinstance(paper_size, str):
        if units in PAPER_SIZE[paper_size]:
            resolved_paper_size = PAPER_SIZE[paper_size][units]
        else:
            resolved_paper_size = PAPER_SIZE[paper_size]["mm"] / UNITS_TO_MM[units]
    else:
        resolved_paper_size = paper_size
    resolved_card_size = MTG_CARD_SIZE[units] if card_size is None else card_size
    return images, resolved_card_size, resolved_paper_size


if __name__ == "__main__":
    command_group_print(obj={})

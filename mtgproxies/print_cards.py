from __future__ import annotations

import abc
import math
from logging import getLogger
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np
import PIL
from fpdf import FPDF
from PIL import ImageChops, ImageFilter
from PIL.Image import Image, Transpose
from tqdm import tqdm

from mtgproxies.dimensions import UNITS_TO_IN, Units, get_pixels_from_size_and_ppsu, get_ppsu_from_size_and_pixels


if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path
    from typing import Literal

    from nptyping import Float, NDArray


logger = getLogger(__name__)

Bbox = tuple[float, float, float, float]  # (x, y, width, height)
Lcoords = tuple[float, float, float, float]  # (x0, y0, x1, y1)


def blend_patch_into_image(bbox: tuple[int, int, int, int], image: PIL.Image, patch: PIL.Image) -> PIL.Image:
    """Blends an image patch into another image at the defined bounding box using an alpha mask.

    The patch is inserted over the image based on the values in the alpha channel of the image.
    The pixels are pasted only to fill in the transparent regions in the image (as described by the alpha channel)

    The edges of the original card are eroded away slightly to remove any black lining that would disturb the blend.
    Then, the edge is blurred a little to improve the blending of the pixels that are filled in.

    Args:
        bbox (tuple[int, int, int, int]): The bounding box that further limits the area where pixels are being written
        image (PIL.Image): The image to be written over.
        patch (PIL.Image): The image patch to be pasted over the base image.

    Returns:
        A PIL image with the result
    """
    size = min(image.size)
    alpha = image.split()[3]
    alpha = ImageChops.invert(alpha)
    dill_size = size // 10 + 1 - (size // 10 % 2)  # values identified manually
    blur_size = size // 30  # values identified manually
    print(dill_size, blur_size)
    alpha = alpha.filter(ImageFilter.MaxFilter(dill_size))
    alpha = alpha.filter(ImageFilter.GaussianBlur(blur_size))
    # paste the blurred image where the alpha is 255
    image.paste(patch, mask=alpha.crop(bbox), box=bbox)
    return image


def blend_flipped_stripe(
    square_image: Image,
    stripe_width_fraction: float,
    flip_how: Literal["horizontal", "vertical"],
    stripe_location: Literal["top", "bottom", "left", "right"],
) -> Image:
    """Takes a leftmost stripe of a square image, flips it, and blends it back into the image.

    The stripe is blended using the alpha channel of the image to fill in the transparent regions
    with the non-transparent regions of the flipped stripe.

    Args:
        square_image: Image to process.
        stripe_width_fraction: Fraction of the width/height of the square image to use as the stripe.
        flip_how: How to flip the stripe. Either "horizontal" or "vertical".
        stripe_location: Where to take the stripe from. Either "top", "bottom", "left", or "right" of the square
                         image. The stripe is adjacent to the edge.

    Returns:
        The image with the flipped stripe blended in.
    """
    corner_copy = square_image.copy()
    width, height = corner_copy.size
    if stripe_location in ["top", "bottom"]:
        transpose_method = Transpose.FLIP_LEFT_RIGHT
    elif stripe_location in ["left", "right"]:
        transpose_method = Transpose.FLIP_TOP_BOTTOM
    else:
        raise ValueError(f"Invalid stripe_location: {stripe_location}")

    if flip_how == "horizontal":
        if stripe_location == "top":
            stripe_width = int(height * stripe_width_fraction)
            bbox = (0, 0, width, stripe_width)
        elif stripe_location == "bottom":
            stripe_width = int(height * (1 - stripe_width_fraction))
            bbox = (0, stripe_width, width, height)
        else:
            raise ValueError(f"Invalid stripe_location: {stripe_location} for flip_how: {flip_how}")
    elif flip_how == "vertical":
        if stripe_location == "left":
            stripe_width = int(width * stripe_width_fraction)
            bbox = (0, 0, stripe_width, height)
        elif stripe_location == "right":
            stripe_width = int(width * (1 - stripe_width_fraction))
            bbox = (stripe_width, 0, width, height)
        else:
            raise ValueError(f"Invalid stripe_location: {stripe_location} for flip_how: {flip_how}")
    else:
        raise ValueError(f"Invalid flip_how: {flip_how}")

    patch_inverted = corner_copy.crop(bbox).transpose(method=transpose_method)
    return blend_patch_into_image(bbox, corner_copy, patch_inverted)


def fill_corners(card_image: Image) -> Image:
    """Fill the corners of the card with the closest pixels around the corners to match the border color."""
    corner_size = card_image.width // 10

    # top corners, vertical stripes
    box_left = (0, 0, corner_size, corner_size)
    card_image.paste(
        blend_flipped_stripe(
            square_image=card_image.crop(box=box_left),
            stripe_width_fraction=1 / 6,
            flip_how="vertical",
            stripe_location="left",
        ),
        box=box_left,
    )
    box_right = (card_image.width - corner_size, 0, card_image.width, corner_size)
    card_image.paste(
        blend_flipped_stripe(
            square_image=card_image.crop(box=box_right),
            stripe_width_fraction=1 / 6,
            flip_how="vertical",
            stripe_location="right",
        ),
        box=box_right,
    )

    # bottom corners, vertical stripes
    box_left = (0, card_image.height - corner_size, corner_size, card_image.height)
    card_image.paste(
        blend_flipped_stripe(
            square_image=card_image.crop(box=box_left),
            stripe_width_fraction=1 / 6,
            flip_how="vertical",
            stripe_location="left",
        ),
        box=box_left,
    )
    box_right = (card_image.width - corner_size, card_image.height - corner_size, card_image.width, card_image.height)
    card_image.paste(
        blend_flipped_stripe(
            square_image=card_image.crop(box=box_right),
            stripe_width_fraction=1 / 6,
            flip_how="vertical",
            stripe_location="right",
        ),
        box=box_right,
    )

    # top corners, horizontal stripes
    box_top = (0, 0, corner_size, corner_size)
    card_image.paste(
        blend_flipped_stripe(
            square_image=card_image.crop(box=box_top),
            stripe_width_fraction=1 / 6,
            flip_how="horizontal",
            stripe_location="top",
        ),
        box=box_top,
    )
    box_bottom = (card_image.width - corner_size, 0, card_image.width, corner_size)
    card_image.paste(
        blend_flipped_stripe(
            square_image=card_image.crop(box=box_bottom),
            stripe_width_fraction=1 / 6,
            flip_how="horizontal",
            stripe_location="top",
        ),
        box=box_bottom,
    )

    # bottom corners, horizontal stripes
    box_top = (0, card_image.height - corner_size, corner_size, card_image.height)
    card_image.paste(
        blend_flipped_stripe(
            square_image=card_image.crop(box=box_top),
            stripe_width_fraction=1 / 6,
            flip_how="horizontal",
            stripe_location="bottom",
        ),
        box=box_top,
    )
    box_bottom = (card_image.width - corner_size, card_image.height - corner_size, card_image.width, card_image.height)
    card_image.paste(
        blend_flipped_stripe(
            square_image=card_image.crop(box=box_bottom),
            stripe_width_fraction=1 / 6,
            flip_how="horizontal",
            stripe_location="bottom",
        ),
        box=box_bottom,
    )

    return card_image


class CardAssembler(abc.ABC):
    """Base class for assembling cards into sheets."""

    def __init__(
        self,
        paper_size: NDArray[2, Float],
        card_size: NDArray[2, Float],
        border_crop: float = 0,
        crop_marks_thickness: float = 0,
        cut_spacing_thickness: float = 0,
        filled_corners: bool = False,
        background_color: tuple[int, int, int] | None = None,
        page_safe_margin: float = 0,
        units: Units = "mm",
    ):
        """Initialize the CardAssembler.

        Args:
            paper_size: Size of the paper in the specified units.
            card_size: Size of a card in the specified units.
            border_crop: How many units to crop from the border of each card.
            crop_marks_thickness: Thickness of crop marks in the specified units. Use 0 to disable crop marks.
            cut_spacing_thickness: Thickness of cut lines in the specified units. Use 0 to disable cut lines.
            filled_corners: Whether to fill in the corners of the cards.
            background_color: Background color of the paper.
            page_safe_margin: How much to leave as a margin on the paper.
            units: Units to use for the sizes.
        """
        # self.mm_coeff = UNITS_TO_MM[units]
        self.units = units
        self.paper_size = paper_size
        self.paper_safe_margin = page_safe_margin
        self.card_size = card_size
        self.border_crop = border_crop
        self.crop_marks_thickness = crop_marks_thickness
        self.cut_spacing_thickness = cut_spacing_thickness
        self.background_color = background_color
        self.filled_corners = filled_corners

        # precompute some values
        self.card_bbox_size = self.card_size - (self.border_crop * 2)
        self.safe_printable_area = self.paper_size - (self.paper_safe_margin * 2)
        self.grid_dims = (
            (self.safe_printable_area + self.cut_spacing_thickness)
            // (self.card_bbox_size + self.cut_spacing_thickness)
        ).astype(np.int32)
        self.rows, self.cols = self.grid_dims
        self.grid_bbox_size = self.card_bbox_size * self.grid_dims + self.cut_spacing_thickness * (self.grid_dims - 1)
        self.offset = (self.safe_printable_area - self.grid_bbox_size) / 2

    @abc.abstractmethod
    def assemble(self, card_image_filepaths: list[Path], output_filepath: Path):
        ...

    def process_card_image(self, card_image_filepath: Path) -> Image:
        """Process an image for assembly.

        Loads the image, fills in corners, crops the borders, etc.

        Args:
            card_image_filepath: Image file to process.
        """
        img = PIL.Image.open(card_image_filepath).copy()
        # fill corners
        if self.filled_corners:
            img = fill_corners(img)
        # crop the cards
        ppsu = get_ppsu_from_size_and_pixels(pixel_values=img.size, size=self.card_size)
        crop_px = int(get_pixels_from_size_and_ppsu(ppsu=ppsu, size=self.border_crop))

        img = img.crop(box=(crop_px, crop_px, img.width - crop_px, img.height - crop_px))
        return img

    def get_page_generators(
        self,
        card_image_filepaths: list[str | Path],
    ) -> Generator[Generator[tuple[Bbox, NDArray]]]:
        """This method is a generator of generators of bounding boxes for each card on a page and the page indices.

        The method can be iterated over to get the bbox iterators for each page and its index.

        Yields:
            tuple[Generator[Bbox], int]: Generator of bounding boxes and page index.
        """
        per_sheet = self.rows * self.cols
        remaining = card_image_filepaths
        while remaining:
            if len(remaining) >= per_sheet:
                for_sheet = remaining[:per_sheet]
                remaining = remaining[per_sheet:]
            else:
                for_sheet = remaining
                remaining = []

            yield self.get_bbox_generator(for_sheet)

    def get_bbox_generator(self, cards_on_page: list[Path]) -> Generator[tuple[Bbox, Image]]:
        """This method is a generator of bounding boxes for each card on a page.

        The method takes a list of card image filepaths and yields the bounding boxes for each of those cards.
        The bounding boxes are tiling a precalculated grid on the page.

        Args:
            cards_on_page: Number of cards on the page.

        Yields:
            Bbox: Bounding box for each card. The format is (x, y, width, height).
        """
        for i, card_image_filepath in enumerate(cards_on_page):
            card_pos = np.array([i % self.cols, i // self.cols])

            cut_spacing_offset = self.cut_spacing_thickness * card_pos
            preceding_cards_offset = self.card_bbox_size * card_pos
            card_offset = cut_spacing_offset + preceding_cards_offset + self.paper_safe_margin + self.offset

            image = self.process_card_image(card_image_filepath)

            yield (*card_offset, *self.card_bbox_size), image

    def get_line_generator(self) -> Generator[Lcoords]:
        """This method is a generator of line coordinates for crop marks.

        The crop marks are lining the edges of each card to help with aligning both printed sides together.

        Yields:
            Bbox: Coordinate points for each cut line. The format is (x0, y0, x1, y1).
        """
        # Horizontal lines
        for i in range(self.rows):
            y_top = self.paper_safe_margin + self.offset[1] + i * (self.card_bbox_size[1] + self.cut_spacing_thickness)
            y_bottom = y_top + self.card_bbox_size[1]
            yield 0, y_top, self.paper_size[0], y_top
            yield 0, y_bottom, self.paper_size[0], y_bottom

        # Vertical lines
        for i in range(self.cols):
            x_left = self.paper_safe_margin + self.offset[0] + i * (self.card_bbox_size[0] + self.cut_spacing_thickness)
            x_right = x_left + self.card_bbox_size[0]
            yield x_left, self.paper_size[1], x_left, 0
            yield x_right, self.paper_size[1], x_right, 0

    def prepare_routine(self, card_image_filepaths, output_filepath):
        total_cards = len(card_image_filepaths)
        pages = np.ceil(total_cards / (self.rows * self.cols)).astype(int)
        tqdm_ = tqdm(total=total_cards, desc="Plotting cards")
        logger.info(f"Will print {total_cards} cards in {pages} pages in a {self.rows}x{self.cols} grid.")
        # Ensure parent directory exists for the output file
        output_filepath.parent.mkdir(parents=True, exist_ok=True)
        return pages, tqdm_


class FPDF2CardAssembler(CardAssembler):
    """Class for assembling cards into sheets using FPDF."""

    def assemble(self, card_image_filepaths: list[Path], output_filepath: Path):
        pages, tqdm_ = self.prepare_routine(card_image_filepaths, output_filepath)

        # Initialize PDF
        pdf = FPDF(orientation="P", unit=self.units, format=self.paper_size)

        for page_idx, bbox_gen in enumerate(self.get_page_generators(card_image_filepaths)):
            tqdm_.set_description(f"Plotting cards (page {page_idx + 1}/{pages})")
            pdf.add_page()
            if self.background_color is not None:
                pdf.set_fill_color(*self.background_color)
                pdf.rect(0, 0, float(self.paper_size[0]), float(self.paper_size[1]), "F")

            # print crop marks
            if self.crop_marks_thickness is not None and self.crop_marks_thickness > 0.0:
                tqdm_.set_description(f"Plotting crop marks (page {page_idx + 1}/{pages})")
                pdf.set_line_width(self.crop_marks_thickness)
                for line_coordinates in self.get_line_generator():
                    pdf.line(*line_coordinates)

            # print cards
            tqdm_.set_description(f"Plotting cards (page {page_idx + 1}/{pages})")
            for bbox, image in bbox_gen:
                pdf.image(name=image, x=bbox[0], y=bbox[1], w=bbox[2], h=bbox[3])
                tqdm_.update(1)

        tqdm.write(f"Writing to {output_filepath}")
        pdf.output(str(output_filepath))


class MatplotlibCardAssembler(CardAssembler):
    """Class for assembling cards into sheets using Matplotlib."""

    def __init__(self, dpi: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dpi = dpi

        self.paper_size = self.paper_size * UNITS_TO_IN[self.units]
        self.card_size = self.card_size * UNITS_TO_IN[self.units]
        self.card_bbox_size = self.card_bbox_size * UNITS_TO_IN[self.units]
        self.border_crop = self.border_crop * UNITS_TO_IN[self.units]
        self.crop_marks_thickness = self.crop_marks_thickness * UNITS_TO_IN[self.units]
        self.cut_spacing_thickness = self.cut_spacing_thickness * UNITS_TO_IN[self.units]
        self.paper_safe_margin = self.paper_safe_margin * UNITS_TO_IN[self.units]
        self.offset = self.offset * UNITS_TO_IN[self.units]
        self.safe_printable_area = self.safe_printable_area * UNITS_TO_IN[self.units]
        self.grid_bbox_size = self.grid_bbox_size * UNITS_TO_IN[self.units]

    def assemble(self, card_image_filepaths: list[Path], output_filepath: Path):
        pages, tqdm_ = self.prepare_routine(card_image_filepaths, output_filepath)
        digits = int(np.ceil(math.log10(pages)))

        with tqdm(total=len(card_image_filepaths), desc="Plotting cards") as pbar:
            for page_idx, bbox_gen in enumerate(self.get_page_generators(card_image_filepaths)):
                tqdm_.set_description(f"Plotting cards (page {page_idx + 1}/{pages})")
                fig = plt.figure(figsize=self.paper_size)
                ax = fig.add_axes(rect=(0, 0, 1, 1))
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.invert_yaxis()

                if self.crop_marks_thickness > 0.0:
                    pbar.set_description("plotting crop marks...")
                    crop_marks_thickness_in_pt = self.crop_marks_thickness * 72
                    for line_coordinates in self.get_line_generator():
                        x0, y0, x1, y1 = line_coordinates
                        x_rel = np.asarray([x0, x1]) / self.paper_size[0]
                        y_rel = np.asarray([y0, y1]) / self.paper_size[1]

                        # convert cropmarks thickness to point units
                        ax.plot(x_rel, y_rel, color="black", linewidth=crop_marks_thickness_in_pt)

                for bbox, image in bbox_gen:
                    left, top, width, height = bbox

                    x0 = left / self.paper_size[0]
                    y0 = top / self.paper_size[1]

                    width_scaled = width / self.paper_size[0]
                    height_scaled = height / self.paper_size[1]

                    x1 = x0 + width_scaled
                    y1 = y0 + height_scaled

                    # extent = (left, right, bottom, top)
                    extent = (x0, x1, y0, y1)

                    _ = ax.imshow(image, extent=extent, interpolation="lanczos", aspect="auto", origin="lower")
                    pbar.update(1)

                # save the page and skip the rest
                out_file_name = (
                    output_filepath.parent / f"{output_filepath.stem}_{page_idx:0{digits}d}{output_filepath.suffix}"
                )
                fig.savefig(fname=out_file_name, dpi=self.dpi)
                plt.close()

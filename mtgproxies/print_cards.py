import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from mtgproxies.plotting import SplitPages
from tqdm import tqdm


def _occupied_space(cardsize, pos, border_crop, image_size, closed=False):
    return cardsize * (pos * image_size - np.clip(2 * pos - 1 - closed, 0, None) * border_crop) / image_size


def print_cards(
    images,
    filepath,
    papersize=np.array([8.27, 11.69]),
    cardsize=np.array([2.5, 3.5]),
    border_crop=14,
    interpolation="lanczos",
    dpi=600,
):
    """Print a list of cards to a pdf file.

    Args:
        images: List of image files
        filepath: Name of the pdf file
        papersize: Size of the paper in inches. Defaults to A4.
        cardsize: Size of a card in inches.
        border_crop: How many pixel to crop from the border of each card.
    """
    # Cards per figure
    N = np.floor(papersize / cardsize).astype(int)
    if N[0] == 0 or N[1] == 0:
        raise ValueError(f"Paper size too small: {papersize}")

    if filepath[-4:] == ".pdf":
        saver = PdfPages
    else:
        saver = SplitPages

    with saver(filepath) as saver, tqdm(total=len(images), desc="Plotting cards") as pbar:
        while len(images) > 0:
            fig = plt.figure(figsize=papersize)
            ax = fig.add_axes([0, 0, 1, 1])  # ax covers the whole figure

            offset = (papersize - _occupied_space(cardsize, N, border_crop, [745, 1040], closed=True)) / 2

            for y in range(N[1]):
                for x in range(N[0]):
                    if len(images) > 0:
                        img = plt.imread(images.pop(0))

                        # Crop left and top if not on border of sheet
                        left = border_crop if x > 0 else 0
                        top = border_crop if y > 0 else 0
                        img = img[top:, left:]

                        # Compute extent
                        lower = (
                            offset + _occupied_space(cardsize, np.array([x, y]), border_crop, [745, 1040])
                        ) / papersize
                        upper = (
                            offset + _occupied_space(cardsize, np.array([x, y]), border_crop, [745, 1040]) +
                            cardsize * [
                                (745 - left) / 745,
                                (1040 - top) / 1040,
                            ]
                        ) / papersize
                        extent = [lower[0], upper[0], 1 - upper[1], 1 - lower[1]]  # flip y-axis

                        plt.imshow(
                            img,
                            extent=extent,
                            aspect=papersize[1] / papersize[0],
                            interpolation=interpolation,
                        )
                        pbar.update(1)

            plt.xlim(0, 1)
            plt.ylim(0, 1)

            # Hide all axis ticks and labels
            ax.axis('off')

            saver.savefig(dpi=dpi)
            plt.close()

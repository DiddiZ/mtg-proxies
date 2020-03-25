import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from mtgproxies.plotting import SplitPages


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
    if border_crop > 0:
        cardsize[0] *= (745 - 2 * border_crop) / 745
        cardsize[1] *= (1040 - 2 * border_crop) / 1040

    # Cards per figure
    N = np.floor(papersize / cardsize).astype(int)
    if N[0] == 0 or N[1] == 0:
        raise ValueError(f"Paper size too small: {papersize}")

    if filepath[-4:] == ".pdf":
        saver = PdfPages
    else:
        saver = SplitPages

    with saver(filepath) as saver:
        while len(images) > 0:
            fig = plt.figure(figsize=papersize)
            ax = fig.add_axes([0, 0, 1, 1])  # ax covers the whole figure

            offset = (papersize - cardsize * N) / 2

            for y in range(N[1]):
                for x in range(N[0]):
                    if len(images) > 0:
                        img = plt.imread(images.pop(0))

                        if border_crop > 0:
                            img = img[border_crop:-border_crop, border_crop:-border_crop]

                        plt.imshow(
                            img,
                            extent=((offset + np.array([[x, N[1] - y - 1], [x + 1, N[1] - y]]) * cardsize) /
                                    papersize).T.flatten(),
                            aspect=papersize[1] / papersize[0],
                            interpolation=interpolation,
                        )

            plt.xlim(0, 1)
            plt.ylim(0, 1)

            # Hide all axis ticks and labels
            ax.axis('off')

            saver.savefig(dpi=dpi)
            plt.close()

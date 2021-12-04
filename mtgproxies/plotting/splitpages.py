import matplotlib.pyplot as plt


class SplitPages:
    """Wrapper around `plt.savefig` which rembers a page number.

    This mirrors the functionality of the `PdfPages` wrapper from matplotlib.
    """
    def __init__(self, filename):
        self.file_basename = filename[:filename.rindex(".")]
        self.file_extension = filename[filename.rindex("."):]
        self.pagecount = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def savefig(self, figure=None, **kwargs):
        """Save figure to a new file.

        The file name is suffixed with the current page number.
        """
        if figure is None:
            figure = plt.gcf()

        filename = self.file_basename + f"_{self.pagecount:03}" + self.file_extension
        plt.savefig(filename, **kwargs)
        self.pagecount += 1

    def get_pagecount(self) -> int:
        """
        Returns the current number of pages in the multipage png.
        """
        return self.pagecount

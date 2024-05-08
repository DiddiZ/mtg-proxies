from __future__ import annotations

from pathlib import Path
from types import TracebackType

import matplotlib
import matplotlib.pyplot as plt


class SplitPages:
    """Wrapper around `plt.savefig` which rembers a page number.

    This mirrors the functionality of the `PdfPages` wrapper from matplotlib.
    """

    def __init__(self, filename: Path | str) -> None:
        """Create a new SplitPages object."""
        self.filename = Path(filename)
        self.pagecount = 0
        self.prev_mpl_backend = None

    def __enter__(self) -> SplitPages:
        self.prev_mpl_backend = matplotlib.get_backend()
        matplotlib.use('Agg')
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        matplotlib.use(self.prev_mpl_backend)
        pass

    def savefig(self, figure=None, **kwargs):
        """Save figure to a new file.

        The file name is suffixed with the current page number.
        """
        if figure is None:
            figure = plt.gcf()

        filename = self.filename.parent / f"{self.filename.stem}_{self.pagecount:03}{self.filename.suffix}"
        figure.savefig(filename, **kwargs)
        print(f"Saved to: {filename}")
        self.pagecount += 1

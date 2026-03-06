from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from mtg_proxies.decklists import Decklist


@pytest.fixture(scope="session")
def data_dir() -> Path:
    """Return the path to the data directory."""
    data_dir = Path(__file__).parent / "data"
    assert data_dir.is_dir()
    return data_dir


@pytest.fixture(scope="session")
def example_decklist(data_dir: Path) -> Decklist:
    from mtg_proxies.decklists import parse_decklist

    decklist, _, _ = parse_decklist(data_dir / "decklist.txt")
    return decklist

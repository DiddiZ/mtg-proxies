import itertools

import pytest
from pathlib import Path


TEST_ROOT_DIR = Path(__file__).parent


@pytest.fixture(scope="session")
def cache_dir():
    test_cache = TEST_ROOT_DIR / ".test_cache"
    test_cache.mkdir(exist_ok=True)
    return test_cache


@pytest.fixture(scope="session")
def example_images_dir() -> Path:
    return TEST_ROOT_DIR / "resources" / "images"


@pytest.fixture(scope="session")
def example_decklists_dir() -> Path:
    return TEST_ROOT_DIR / "resources" / "decklists"


def take_n_images(n: int, directory: Path) -> list[Path]:
    """Return n image files from a directory cycling through the directory iterator."""
    available_image_files = []
    dir_iterator = directory.iterdir()
    card_iter = itertools.cycle(dir_iterator)
    while len(available_image_files) < n:
        image = next(card_iter)
        if image.is_file() and image.suffix in [".jpg", ".png"]:
            available_image_files.append(image)
    return available_image_files


@pytest.fixture(scope="session")
def example_images_7(example_images_dir) -> list[Path]:
    return take_n_images(7, directory=example_images_dir)


@pytest.fixture(scope="session")
def example_images_24(example_images_dir) -> list[Path]:
    return take_n_images(24, directory=example_images_dir)


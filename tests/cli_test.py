from unittest.mock import patch

import pytest


def test_main(capsys: pytest.CaptureFixture) -> None:
    """Test the main function.

    Ensure that ther a are no import errors and that the help message is printed correctly.
    """
    from mtg_proxies.cli import main

    # Mock argv
    with patch("sys.argv", ["mtg-proxies", "--help"]), pytest.raises(SystemExit):
        main()

    # Check output
    captured = capsys.readouterr()
    assert (
        captured.out
        == """usage: mtg-proxies [-h] {print,convert,tokens,deck_value} ...

Create high quality MtG proxies from your decklist.

positional arguments:
  {print,convert,tokens,deck_value}
    print               Prepare a decklist for printing
    convert             Convert a decklist to text or arena format
    tokens              Append the created tokens to a decklist
    deck_value          Show deck value decomposition

options:
  -h, --help            show this help message and exit
"""
    )

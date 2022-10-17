import os
import unittest


class Test_Decklist(unittest.TestCase):
    def test_parsing(self):
        from mtgproxies.decklists import parse_decklist

        decklist, ok, warnings = parse_decklist("examples/decklist.txt")

        self.assertTrue(ok)
        self.assertEqual(len(warnings), 0)

        with open("examples/decklist.txt", "r", encoding="utf-8") as f:
            # Ignore differences in linebreaks
            self.assertEqual(
                (format(decklist, "arena") + os.linesep).replace("\r\n", "\n"),
                f.read().replace("\r\n", "\n"),
            )

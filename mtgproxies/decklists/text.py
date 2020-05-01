import codecs
import re


def parse_decklist_text(filepath):
    """Parse card information from a decklist in text format.

    E.g.:
    ```
    Mainboard

    4 Burst of Strength
    1 Finale of Devastation
    4 Beast Whisperer
    [...]
    ```
    Ignores all non-card rows and does not discern between main deck and sideboard.

    Returns:
        [(int, str)]: List of (count, name)-tuples.
    """
    decklist = []
    with codecs.open(filepath, 'r', 'utf-8') as fp:
        for line in fp:
            m = re.search(r'([0-9]+) (.+)', line.strip())
            if m:
                # Extract relevant data
                count = int(m.group(1))
                name = m.group(2)
                decklist.append((
                    count,
                    name,
                ))
    return decklist

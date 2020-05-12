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
        [(int, str, None, None)]: List of (count, name, None, None)-tuples.
    """
    decklist = []
    with codecs.open(filepath, 'r', 'utf-8') as fp:
        for line in fp:
            m = re.search(r'([0-9]+)\s(.+?)\s*$', line)
            if m:
                # Extract relevant data
                count = int(m.group(1))
                name = m.group(2)
                decklist.append((
                    count,
                    name,
                    None,
                    None,
                ))
    return decklist

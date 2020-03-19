import re


def parse_decklist_arena(filepath):
    """Parse card information from a decklist in MtG Arena format.

    E.g.:
    ```
    4 Blood Crypt (RNA) 245
    ```

    Ignores all non-card rows and does not discern betwenn main deck and sideboard.

    Returns:
        [(int, str, str, str)]: List of (count, name, set_id, collectors_number)-tuples.
    """
    decklist = []
    with open(filepath) as fp:
        for line in fp:
            m = re.search(r'([0-9]+) (.+) \((.*)\) ([0-9a-z]+)', line)
            if m:
                # Extract relevant data
                count = int(m.group(1))
                name = m.group(2)
                set_id = m.group(3)
                collector_number = m.group(4)
                decklist.append((
                    count,
                    name,
                    set_id,
                    collector_number,
                ))
    return decklist

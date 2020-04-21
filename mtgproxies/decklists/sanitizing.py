import pandas as pd


def merge_duplicates(decklist):
    """Merge duplicates entries in a decklist.

    Cards with same name, set and collector number are considered duplicates.

    Maintains the order of the decklist. Duplicates are merged with the first occurrence.
    """
    return (
        # Create dataframe from decklist
        pd.DataFrame(decklist, columns=["Count", "Name", "Set", "Collector Number"])
        # Group by print identifier
        .reset_index().groupby(["Name", "Set", "Collector Number"]).agg(
            {
                "Count": "sum",
                "index": "first",  # Keep first index for ordering order
            }
        ).reset_index().set_index("index").sort_index()  # Restore card order
        # Restore column order
        [["Count", "Name", "Set", "Collector Number"]].values
    )

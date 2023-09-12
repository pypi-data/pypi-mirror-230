import os
from typing import Union

import pandas as pd

from ez_pdf_tables.tables import df_columns_to_text


def make_multiindex(
    df: pd.DataFrame,
    indices: list,
) -> pd.DataFrame:
    """Updates index on a dataframe to multiple."""
    if not isinstance(indices, list) or len(indices) == 0:
        raise ValueError('Indices must be a non-empty list.')
    df.set_index(indices, inplace=True)
    df.sort_index(inplace=True)
    return df


def multiindex_as_is(
    source: Union[str, pd.DataFrame],
    make_multiindex_with_indices: list,
) -> pd.DataFrame:
    """
    Set a multiindex df to be printable exactly as it looks,
    with empty values below top value such that the console printable
    multiindex is exportable to file.
    """
    if isinstance(source, pd.DataFrame):
        df = source
        if isinstance(df.index, pd.MultiIndex):
            msg = (
                'The given dataframe already contains a multiindex, this would'
                ' truncate additional indices. Pass the dataframe with a single'
                ' index and supply the multiindex values to'
                ' "make_multiindex_with_indices".'
            )
            raise ValueError(msg)
    elif os.path.isfile(os.path.abspath(source)):
        df = pd.read_csv(source)
    else:
        raise ValueError('Source must be a dataframe object or csv file path.')
    df_dict = df.to_dict('list')
    # Headers.
    header = list(df_dict.keys())
    # Column values.
    column_values = list(df_dict.values())
    # Starting position is 0 for column lengths.
    column_lengths = [0,]
    # Insert header into beginning of each column list
    for i, column_list in enumerate(column_values):
        column_list.insert(0, header[i])
    # Loop through the list of columns.
    for column_index, column in enumerate(column_values):
        # Set initial length for each list to 0.
        length = 0
        for cell in column:
            # If the length of the current item in the list is
            # longer, update the max length.
            if len(str(cell)) > length:
                length = len(str(cell))
        # Set the pad to account for spaces in df str.
        pad = 0 if i == 0 else 1
        length += column_lengths[-1] + pad
        column_lengths.append(length)
    # Increase the final column length by an additional 1
    column_lengths[-1] = column_lengths[-1] + 1
    # Convert the df to multiindex
    df = make_multiindex(df, make_multiindex_with_indices)
    # Convert all columns to text to prevent spacing issues
    df = df_columns_to_text(df, df.columns.tolist())
    text_rows = str(df).split('\n')
    # Delete non-indexed header and indexed header
    text_rows.pop(1)
    text_rows.pop(0)
    # Cut each row into cells based on the 2 bounds it is within
    for i, row in enumerate(text_rows):
        text_rows[i] = [
            row[left_bound:right_bound]
            for left_bound, right_bound
            in zip(column_lengths, column_lengths[1:])
        ]
    # Pass the header to df
    return pd.DataFrame(text_rows, columns=header)

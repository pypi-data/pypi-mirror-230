from typing import Any, List

import pandas as pd


def as_text(value: Any, remove_decimal: bool = False) -> str:
    """Convert a value to text."""
    if value is None:
        return ""
    if remove_decimal:
        value = str(value).split('.')[0]
    return str(value)


def columns_to_text(data: List[list], column_list: list) -> None:
    """Convert a column's data to text in-place."""
    for i in data:
        for v in column_list:
            i[v] = as_text(i[v], remove_decimal=True)


def df_columns_to_text(
    df: pd.DataFrame,
    column_list: list,
    remove_decimal: bool = False,
) -> pd.DataFrame:
    """Convert specified df columns to text."""
    for column_name in column_list:
        # Fill NaN values with a space to prevent NaN being made into text.
        df[column_name].fillna(' ', inplace=True)
        df[column_name] = df.apply(
            lambda row: as_text(
                row[column_name],
                remove_decimal=remove_decimal
            ),
            axis=1
        )
    return df

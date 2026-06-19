"""
Stock Quant Strategy Framework
---------------------------------------------------
Author:    PiggyLa
Contact:   Veritas428 (WeChat)
Copyright: (c) 2026 PiggyLa. All rights reserved.

Proprietary & Confidential. Do not distribute.
---------------------------------------------------
"""
import pandas as pd

fin_cols = []
extra_data = {'dividend-delivery': ['连续分红年份']}


def add_factor(df: pd.DataFrame, param=None, **kwargs) -> pd.DataFrame:
    """
    Calculate and add new factor columns to stock market data, returning the DataFrame with calculated factors and their aggregation method.

    Workflow:
    1. Calculate factor values for the stock based on provided parameters.
    2. Append factor values to the original market data DataFrame.

    :param df: pd.DataFrame, containing K-line data for a single stock, must include market data (e.g., Close price).
    :param param: Parameters required for factor calculation; format and meaning vary by factor type.
    :param kwargs: Additional keyword arguments, including:
        - col_name: Name of the new factor column.
        - fin_data: Financial data dictionary, format {'Financial Data': fin_df, 'Raw Financial Data': raw_fin_df}, where fin_df is processed financial data and raw_fin_df is raw data, the latter can be used for custom calculations of certain factors.
        - Other parameters: Other factor parameters passed as needed.
    :return:
        - pd.DataFrame: DataFrame containing the new factor column, with the same index as the input df.

    Notes:
    - If factor calculation involves financial data, relevant data can be provided via the `fin_data` parameter.

    Consecutive Dividend Years Factor (z_ConsecutiveDividendYears)
    ---------------------------------------------------
    Meaning: Passthrough of the consecutive dividend years computed by data_bridge.
         Counts the number of uninterrupted years with dividend payments,
         going backwards from the most recent record date.
         Values are integers (1, 2, 3, 5, 10 ...), typically used as a filter, not for ranking.

    param: None (pass empty string)
    Sorting: Not applicable (filter factor)

    Selection Case: None
    Filter Case:    ('z_ConsecutiveDividendYears_en', '', 'val:>=3', False)
    """
    col_name = kwargs['col_name']

    factor_df = pd.DataFrame(
        {col_name: df['连续分红年份']},
        index=df.index,
    )

    return factor_df

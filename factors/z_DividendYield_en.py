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
extra_data = {'dividend-delivery': ['分红率_最近日']}


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

    Current Dividend Yield Factor (z_DividendYield)
    ---------------------------------------------------
    Meaning: Real-time dividend yield based on the current closing price.
    Principle: Computed by data_bridge as TTM dividends per share / daily closing price.
         Unlike the record-date snapshot (分红率_登记日 which is ffilled between dates),
         this factor updates its denominator with every trading day's close,
         reflecting the actual yield an investor would lock in by buying today.
         Larger values indicate a higher dividend return at the current price.

    Formula: TTM Dividends per Share / Daily Close (= 分红率_最近日, passthrough)

    param: None (pass empty string)
    Sorting: False (Larger is better)

    Selection Case: ('z_DividendYield_en', False, '', 1)
    Filter Case:    ('z_DividendYield_en', '', 'pct:<=0.5', False)
    """
    col_name = kwargs['col_name']

    factor_df = pd.DataFrame(
        {col_name: df['分红率_最近日']},
        index=df.index,
    )

    return factor_df

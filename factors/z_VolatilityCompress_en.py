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
import numpy as np

fin_cols = []


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

    Volatility Compression Factor (z_VolatilityCompress)
    ---------------------------------------------------
    Meaning: Measures the change in short-term volatility relative to long-term volatility.
    Principle:
         - Ratio > 1: Short-term volatility expands, implying the stock is entering an active phase, possibly with new capital entry.
         - Ratio < 1: Short-term volatility contracts, implying the stock is in consolidation.
    Goal: (When sorting False) To find "Launch-type" stocks where volatility is expanding, breaking silence, and becoming active.

    Formula: std(Return, short) / std(Return, long)

    param: (short, long) e.g., (10, 60)
    Sorting: False (Larger is better = Volatility Expansion = High Activity)

    Selection Case: ('z_VolatilityCompress_en', False, (10, 60), 1)
    """
    col_name = kwargs['col_name']
    short, long = param[0], param[1]

    short_vol = df['涨跌幅'].rolling(short, min_periods=short).std()
    long_vol = df['涨跌幅'].rolling(long, min_periods=long).std()

    factor_col = np.where(long_vol > 1e-10, short_vol / long_vol, np.nan)

    factor_df = pd.DataFrame({col_name: factor_col}, index=df.index)

    return factor_df

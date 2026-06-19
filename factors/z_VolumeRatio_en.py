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

    Volume Ratio Factor (z_VolumeRatio)
    ---------------------------------------------------
    Meaning: Measures the multiple of recent transaction amount relative to the long-term average.
    Principle: Volume precedes price. An increase in volume is often a direct signal of capital entry.
         - Ratio > 1: Recent volume expansion, increased capital attention.
         - Ratio < 1: Recent volume contraction, light trading.
    Goal: (When sorting False) To find stocks with significant recent volume expansion and clear signs of capital intervention.

    Formula: mean(Amount, short) / mean(Amount, long)

    param: (short, long) e.g., (5, 60)
    Sorting: False (Larger is better = Volume Expansion = High Activity)

    Selection Case: ('z_VolumeRatio_en', False, (5, 60), 1)
    """
    col_name = kwargs['col_name']
    short, long = param[0], param[1]

    short_avg = df['成交额'].rolling(short, min_periods=short).mean()
    long_avg = df['成交额'].rolling(long, min_periods=long).mean()

    ratio = short_avg / long_avg.replace(0, float('nan'))

    factor_df = pd.DataFrame({col_name: ratio}, index=df.index)

    return factor_df

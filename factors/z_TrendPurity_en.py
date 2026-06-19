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

    Trend Purity Factor (z_TrendPurity)
    ---------------------------------------------------
    Meaning: Measures the "efficiency" of price movement, i.e., how straight it goes.
    Principle: Also known as Kaufman Efficiency Ratio.
         - If price rises in a straight line, purity approaches 1.
         - If price rises slightly after repeated oscillations, path is long but displacement is small, purity approaches 0.
    Goal: To find smooth trend stocks with clean movement, less noise, and less resistance.

    Formula: (close_t / close_{t-N} - 1) / Σ|daily_return_i|
    Range: [-1, +1]

    param: N (Lookback window, e.g., 20)
    Sorting: False (Larger is better)

    Selection Case: ('z_TrendPurity_en', False, 20, 1)
    """
    col_name = kwargs['col_name']
    n = param

    price = df['收盘价_复权']
    daily_ret = price.pct_change()
    net_return = price / price.shift(n) - 1
    total_path = daily_ret.abs().rolling(n, min_periods=n).sum()

    factor_col = np.where(total_path > 1e-10, net_return / total_path, np.nan)

    factor_df = pd.DataFrame({col_name: factor_col}, index=df.index)

    return factor_df

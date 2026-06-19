"""
Stock Quant Strategy Framework
---------------------------------------------------
Author:    Xinhao Zheng
Contact:   Veritas428 (WeChat)
Copyright: (c) 2026 Xinhao Zheng. Licensed under the MIT License.
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

    Momentum Volatility Factor
    ---------------------------------------------------
    Meaning: Finds stocks with "clear direction" and "strong intensity".
    Principle: Combines Mean (Direction) and Standard Deviation (Volatility/Intensity).
         - Mean > 0 indicates uptrend.
         - High Standard Deviation indicates intense volatility (active capital).
         - Product: Factor value is maximized only when "Rising" AND "Active".
    Goal: To find aggressive stocks that have both an uptrend and capital attention (high volatility).

    Formula: mean(Return, N) × std(Return, N)

    param: N (Lookback window, e.g., 20)
    Sorting: False (Larger is better)

    Selection Case: ('z_MomentumVolatility_en', False, 20, 1)
    """
    col_name = kwargs['col_name']
    n = param

    mtm_mean = df['涨跌幅'].rolling(n, min_periods=n).mean()
    mtm_std = df['涨跌幅'].rolling(n, min_periods=n).std()

    factor_df = pd.DataFrame({col_name: mtm_mean * mtm_std}, index=df.index)

    return factor_df

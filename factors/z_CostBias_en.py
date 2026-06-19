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

    VWAP Bias Factor
    ---------------------------------------------------
    Meaning: Measures the deviation of the current price from the recent market average holding cost (VWAP).
    Principle: VWAP represents the average cost of market participants.
         - When Bias > 0: Price is above cost, the market is in profit, selling pressure may be light (uptrend confirmation).
         - When Bias < 0: Price is below cost, the market is in loss, there is selling pressure from locked-in positions above.
    Goal: To find stocks standing above the average cost line, with strengthening trends and less locked-in selling pressure.

    Formula: (Close - VWAP_N) / VWAP_N
      VWAP_N = sum(Amount, N) / sum(Volume, N)

    param: N (Lookback window, e.g., 20)
    Sorting: False (Larger is better)

    Selection Case: ('z_CostBias_en', False, 20, 1)
    """
    col_name = kwargs['col_name']
    n = param

    amount_sum = df['成交额'].rolling(n, min_periods=n).sum()
    volume_sum = df['成交量'].rolling(n, min_periods=n).sum()
    vwap = amount_sum / volume_sum.replace(0, float('nan'))

    factor_df = pd.DataFrame({col_name: (df['收盘价'] - vwap) / vwap}, index=df.index)

    return factor_df

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

    Momentum Strength Factor
    ---------------------------------------------------
    Meaning: Measures the "quality" and "consistency" of the price uptrend.
    Principle: Pure return can be deceptive if contributed by just one or two days of sharp rise.
         This factor combines "Cumulative Return" and "Up Days Ratio".
         - Higher return with more up days yields a higher score.
         - High return but few up days (volatile rise) gets a discounted score.
    Goal: To find strong momentum stocks with steady ascent where bulls consistently dominate.

    Formula: pct_change(N) × (2 × up_ratio - 1)
      up_ratio = Ratio of up days in N days

    param: N (Lookback window, e.g., 20)
    Sorting: False (Larger is better)

    Selection Case: ('z_MomentumStrength_en', False, 20, 1)
    """
    col_name = kwargs['col_name']
    n = param

    total_return = df['收盘价_复权'].pct_change(n)
    daily_ret = df['涨跌幅']
    up_ratio = daily_ret.gt(0).astype(float).rolling(n, min_periods=n).mean()
    weight = 2 * up_ratio - 1

    factor_df = pd.DataFrame({col_name: total_return * weight}, index=df.index)

    return factor_df

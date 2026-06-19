"""
Stock Quant Strategy Framework
---------------------------------------------------
Author:    Xinhao Zheng
Contact:   Veritas428 (WeChat)
Copyright: (c) 2026 Xinhao Zheng. Licensed under the MIT License.
---------------------------------------------------
"""
import pandas as pd
import numpy as np

fin_cols = ['C_ncf_from_oa@xbx_ttm', 'C_cash_paid_for_assets@xbx_ttm']
extra_data = {'dividend-delivery': ['分红率_最近日', '近一年分红']}


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

    Dividend Safety Margin Factor
    ---------------------------------------------------
    Meaning: Combines current dividend yield and dividend sustainability into a single
         metric; only dividends that are both high and sustainable count.
    Principle: High dividend yield underpins shareholder return, but payouts must be
         supported by internally generated cash, not debt or balance-sheet drawdown.
         This factor multiplies current dividend yield by a truncated FCF coverage coefficient:
         - Current Dividend Yield (DivYield_Latest): real-time cash return at the day's close;
           higher = more generous;
         - FCF Coverage = FCF TTM / Total Dividend TTM: sustainability verification;
           Coverage < 0 (negative FCF, debt-funded payout) → truncated to 0, effective
           dividend yield zeroed;
           Coverage > cap (far exceeds payout requirement) → truncated to cap, preventing
           extreme values from dominating.
         Larger values indicate high current dividend yield backed by real cash flow.

    Formula: DivYield_Latest × clip(FCF Coverage, 0, cap)
      FCF Coverage = (Operating Cash Flow TTM − CapEx TTM) / Total Dividend TTM
      Total Dividend TTM = Dividend Per Share (TTM) × Total Shares
      Total Shares = Market Cap / Close Price

    param: cap (FCF coverage upper-bound multiplier, default 3.0; larger = more lenient;
           1.0 = full score when coverage exactly equals payout)
    Sorting: False (Larger is better)

    Selection Case: ('z_DividendSafetyMargin_en', False, 3, 1)
    Filter Case:    ('z_DividendSafetyMargin_en', 3, 'pct:<=0.5', False)
    """
    col_name = kwargs['col_name']
    cap = float(param) if param not in (None, '') else 3.0

    # Current dividend yield: TTM dividend / daily close (updated daily by data_bridge)
    div_yield = df['分红率_最近日'].to_numpy(dtype='float64', na_value=np.nan)

    # FCF TTM = Operating Cash Flow TTM − CapEx TTM
    oa = df['C_ncf_from_oa@xbx_ttm'].to_numpy(dtype='float64', na_value=np.nan)
    capex = df['C_cash_paid_for_assets@xbx_ttm'].to_numpy(dtype='float64', na_value=np.nan)
    fcf_ttm = oa - capex

    # Total Dividend TTM = Dividend Per Share (TTM) × Total Shares; Total Shares = Market Cap / Close Price
    close = df['收盘价'].to_numpy(dtype='float64', na_value=np.nan)
    close = np.where(close == 0, np.nan, close)
    total_shares = df['总市值'].to_numpy(dtype='float64', na_value=np.nan) / close
    total_dividend = df['近一年分红'].to_numpy(dtype='float64', na_value=np.nan) * total_shares
    total_dividend = np.where(total_dividend == 0, np.nan, total_dividend)

    # FCF coverage clipped to [0, cap]: negative (debt-funded payout) → 0; excess → cap
    fcf_cover = np.clip(fcf_ttm / total_dividend, 0.0, cap)

    factor_df = pd.DataFrame({col_name: div_yield * fcf_cover}, index=df.index)

    return factor_df

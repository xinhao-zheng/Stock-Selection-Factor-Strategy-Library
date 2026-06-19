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
extra_data = {'dividend-delivery': ['近一年分红']}


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

    FCF Dividend Coverage Factor
    ---------------------------------------------------
    Meaning: How many times the company's TTM Free Cash Flow covers its
         TTM total dividends paid.
         > 1: FCF comfortably covers dividends (sustainable).
         < 1: Dividends exceed FCF (potentially borrowing to pay).
         <= 0: Negative FCF; dividends funded entirely by reserves/debt.

    Formula: FCF_TTM / Total_Dividend_TTM
      FCF_TTM = Operating Cash Flow TTM - CapEx TTM
      Total_Dividend_TTM = Dividend Per Share (TTM) x Total Shares
      Total Shares = Market Cap / Close Price

    param: None (pass empty string)
    Sorting: Not applicable (filter factor)

    Selection Case: None
    Filter Case:    ('z_FCFDividendCoverage_en', '', 'val:>=1', False)
    """
    col_name = kwargs['col_name']

    oa = df['C_ncf_from_oa@xbx_ttm'].to_numpy(dtype='float64', na_value=np.nan)
    capex = df['C_cash_paid_for_assets@xbx_ttm'].to_numpy(dtype='float64', na_value=np.nan)
    fcf_ttm = oa - capex

    close = df['收盘价'].to_numpy(dtype='float64', na_value=np.nan)
    close[close == 0] = np.nan
    total_shares = df['总市值'].to_numpy(dtype='float64', na_value=np.nan) / close
    total_dividend = df['近一年分红'].to_numpy(dtype='float64', na_value=np.nan) * total_shares
    total_dividend[total_dividend == 0] = np.nan

    factor_df = pd.DataFrame(
        {col_name: fcf_ttm / total_dividend},
        index=df.index,
    )

    return factor_df

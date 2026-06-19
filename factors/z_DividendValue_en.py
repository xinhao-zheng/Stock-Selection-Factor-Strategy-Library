"""
Stock Quant Strategy Framework
---------------------------------------------------
Author:    Xinhao Zheng
Contact:   Veritas428 (WeChat)
Copyright: (c) 2026 Xinhao Zheng. Licensed under the MIT License.
---------------------------------------------------
"""
import pandas as pd

fin_cols = [
    'B_st_borrow@xbx', 'B_lt_loan@xbx', 'B_bond_payable@xbx',
    'B_lease_libilities@xbx', 'B_minority_equity@xbx',
    'B_preferred_shares@xbx', 'B_currency_fund@xbx',
]
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

    Dividend Value Factor
    ---------------------------------------------------
    Meaning: The dividend analog of FCFFEV. Measures dividend yield per unit of
         Enterprise Value, adjusted for capital structure.
    Principle: Current Dividend Yield x (Market Cap / EV).
         - Current Dividend Yield: How much dividend relative to today's price.
         - Market Cap / EV: Leverage adjustment (< 1 for leveraged firms, penalizing them).
         Larger values indicate generous dividends at a cheap whole-firm price.
         Dividend stability is ensured by filters (z_ConsecutiveDividendYears_en or
         z_DividendQuality_en), not by discounting the factor value.

    Formula: DivYield_Latest x (MarketCap / EV)
      DivYield_Latest = TTM Dividend / Daily Close (updated daily by data_bridge)
      EV = Market Cap + Short-Term Borrowings + Long-Term Loans
           + Bonds Payable + Lease Liabilities
           + Minority Interest + Preferred Stock - Cash

    param: None (pass empty string)
    Sorting: False (Larger is better)

    Selection Case: ('z_DividendValue_en', False, '', 1)
    Filter Case:    ('z_DividendValue_en', '', 'pct:<=0.5', False)
    """
    col_name = kwargs['col_name']

    div_yield = df['分红率_最近日']

    ev = (df['总市值'].fillna(0)
          + df['B_st_borrow@xbx'].fillna(0)
          + df['B_lt_loan@xbx'].fillna(0)
          + df['B_bond_payable@xbx'].fillna(0)
          + df['B_lease_libilities@xbx'].fillna(0)
          + df['B_minority_equity@xbx'].fillna(0)
          + df['B_preferred_shares@xbx'].fillna(0)
          - df['B_currency_fund@xbx'].fillna(0))

    mv_ev_ratio = df['总市值'] / ev.replace(0, float('nan'))

    factor_df = pd.DataFrame(
        {col_name: div_yield * mv_ev_ratio},
        index=df.index,
    )

    return factor_df

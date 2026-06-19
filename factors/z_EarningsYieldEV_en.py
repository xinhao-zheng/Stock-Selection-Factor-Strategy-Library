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

fin_cols = [
    'R_np@xbx_ttm', 'R_np@xbx_单季',
    'B_st_borrow@xbx', 'B_lt_loan@xbx', 'B_bond_payable@xbx',
    'B_lease_libilities@xbx', 'B_minority_equity@xbx',
    'B_preferred_shares@xbx', 'B_currency_fund@xbx',
]


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

    Earnings Yield EV Factor (z_EarningsYieldEV)
    ---------------------------------------------------
    Meaning: An enterprise-value-based variant of EP. Net profit is divided by EV rather
         than market cap, removing capital-structure (leverage) distortion from valuation
         ranking.
    Principle: EP = Net Profit / Market Cap reflects the equity-holder perspective only;
         this factor replaces the denominator with EV (Market Cap + interest-bearing debt
         + minority interest + preferred stock − cash),
         so heavily leveraged firms are not spuriously ranked as cheap due to a small
         market cap.
         Larger values indicate higher earnings return at whole-firm price, i.e. lower
         valuation (cheaper).

    Formula: Net Profit / EV
      EV = Market Cap + Short-Term Borrowings + Long-Term Loans
           + Bonds Payable + Lease Liabilities
           + Minority Interest + Preferred Stock − Cash

    param: '全年' (TTM net profit) or '单季' (latest single-quarter net profit)
    Sorting: False (Larger is better)

    Selection Case: ('z_EarningsYieldEV_en', False, '全年', 1)
    Filter Case:    ('z_EarningsYieldEV_en', '全年', 'pct:<=0.8', False)
    """
    col_name = kwargs['col_name']

    profit_cols = {
        '全年': 'R_np@xbx_ttm',
        '单季': 'R_np@xbx_单季',
    }
    if param not in profit_cols:
        raise ValueError(f"z_EarningsYieldEV_en supports only '全年' or '单季', got: {param}")
    profit_col = profit_cols[param]

    ev = (df['总市值'].fillna(0)
          + df['B_st_borrow@xbx'].fillna(0)
          + df['B_lt_loan@xbx'].fillna(0)
          + df['B_bond_payable@xbx'].fillna(0)
          + df['B_lease_libilities@xbx'].fillna(0)
          + df['B_minority_equity@xbx'].fillna(0)
          + df['B_preferred_shares@xbx'].fillna(0)
          - df['B_currency_fund@xbx'].fillna(0))

    factor_df = pd.DataFrame(
        {col_name: df[profit_col] / ev.replace(0, float('nan'))},
        index=df.index,
    )

    return factor_df

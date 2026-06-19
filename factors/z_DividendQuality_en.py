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
extra_data = {'dividend-delivery': ['分红率_登记日_近年均值', '分红率_登记日_近年标准差']}


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

    Dividend Quality Factor
    ---------------------------------------------------
    Meaning: Measures whether 3-year trailing dividend yield is both high and stable.
    Principle: Starts from the 3-year mean dividend yield, then applies a bounded
         discount driven by standard deviation.
         High mean + low volatility = high score; high mean + high volatility = discounted;
         low mean scores poorly regardless of stability.
         Discount = Mean / (Mean + k * Std), always between 0 and 1.
         Larger k = stricter penalty on volatility; k=0 degrades to pure mean ranking.

    Formula: Mean * Mean / (Mean + k * Std)
      Mean = 3-year trailing dividend yield mean (computed by data_bridge)
      Std  = 3-year trailing dividend yield std  (computed by data_bridge)

    param: k (stability penalty coefficient, default 1; 0.5=lenient, 2=strict)
    Sorting: False (Larger is better)

    Selection Case: ('z_DividendQuality_en', False, 1, 1)
    Filter Case:    ('z_DividendQuality_en', 1, 'pct:<=0.5', False)
    """
    col_name = kwargs['col_name']
    k = param if param is not None else 1

    mean = df['分红率_登记日_近年均值']
    std = df['分红率_登记日_近年标准差'].fillna(0)

    factor_df = pd.DataFrame(
        {col_name: mean * mean / (mean + k * std).replace(0, float('nan'))},
        index=df.index,
    )

    return factor_df

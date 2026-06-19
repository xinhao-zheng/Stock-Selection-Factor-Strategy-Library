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
    计算并将新的因子列添加到股票行情数据中，并返回包含计算因子的DataFrame及其聚合方式。

    工作流程：
    1. 根据提供的参数计算股票的因子值。
    2. 将因子值添加到原始行情数据DataFrame中。

    :param df: pd.DataFrame，包含单只股票的K线数据，必须包括市场数据（如收盘价等）。
    :param param: 因子计算所需的参数，格式和含义根据因子类型的不同而有所不同。
    :param kwargs: 其他关键字参数，包括：
        - col_name: 新计算的因子列名。
        - fin_data: 财务数据字典，格式为 {'财务数据': fin_df, '原始财务数据': raw_fin_df}，其中fin_df为处理后的财务数据，raw_fin_df为原始数据，后者可用于某些因子的自定义计算。
        - 其他参数：根据具体需求传入的其他因子参数。
    :return:
        - pd.DataFrame: 包含新计算的因子列，与输入的df具有相同的索引。

    注意事项：
    - 如果因子的计算涉及财务数据，可以通过`fin_data`参数提供相关数据。

    趋势纯度因子
    ---------------------------------------------------
    含义：衡量价格运动的"效率"，即走得有多直。
    原理：也就是考夫曼效率系数 (Kaufman Efficiency Ratio)。
         - 如果股价直线拉升，纯度接近 1。
         - 如果股价反复震荡后才微涨，路径长但位移小，纯度接近 0。
    目标：寻找走势干净利落、杂波少、阻力小的顺畅趋势标的。

    公式: (close_t / close_{t-N} - 1) / Σ|daily_return_i|
    范围: [-1, +1]

    param: N (回看窗口, 如 20)
    排序: False (值越大越好)

    选股因子案例: ('z_趋势纯度_zh', False, 20, 1)
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

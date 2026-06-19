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

    波动压缩因子
    ---------------------------------------------------
    含义：衡量近期波动率相对于长期波动率的变化。
    原理：
         - 当 比值 > 1 时：近期波动放大，意味着股票进入活跃期，可能有新资金介入。
         - 当 比值 < 1 时：近期波动收敛，意味着股票处于盘整期。
    目标：(排序False时) 寻找波动率正在放大、打破沉寂、开始活跃的启动型标的。

    公式: std(涨跌幅, short) / std(涨跌幅, long)

    param: (short, long) 如 (10, 60)
    排序: False (值越大 = 近期波动放大 = 活跃度高 = 越好)

    选股因子案例: ('z_波动压缩_zh', False, (10, 60), 1)
    """
    col_name = kwargs['col_name']
    short, long = param[0], param[1]

    short_vol = df['涨跌幅'].rolling(short, min_periods=short).std()
    long_vol = df['涨跌幅'].rolling(long, min_periods=long).std()

    factor_col = np.where(long_vol > 1e-10, short_vol / long_vol, np.nan)

    factor_df = pd.DataFrame({col_name: factor_col}, index=df.index)

    return factor_df

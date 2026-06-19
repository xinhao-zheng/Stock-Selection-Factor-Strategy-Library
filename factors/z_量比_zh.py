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

    量比因子
    ---------------------------------------------------
    含义：衡量近期成交金额相对于长期均值的放大倍数。
    原理：量在价先。成交量的放大通常是资金进场的直接信号。
         - 比值 > 1：近期放量，资金关注度提升。
         - 比值 < 1：近期缩量，交投清淡。
    目标：(排序False时) 寻找近期明显放量、资金介入迹象明显的标的。

    公式: mean(成交额, short) / mean(成交额, long)

    param: (short, long) 如 (5, 60)
    排序: False (值越大 = 近期放量 = 活跃度高 = 越好)

    选股因子案例: ('z_量比_zh', False, (5, 60), 1)
    """
    col_name = kwargs['col_name']
    short, long = param[0], param[1]

    short_avg = df['成交额'].rolling(short, min_periods=short).mean()
    long_avg = df['成交额'].rolling(long, min_periods=long).mean()

    ratio = short_avg / long_avg.replace(0, float('nan'))

    factor_df = pd.DataFrame({col_name: ratio}, index=df.index)

    return factor_df

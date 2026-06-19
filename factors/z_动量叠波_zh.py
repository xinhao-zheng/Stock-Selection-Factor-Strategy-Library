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

    动量叠波因子
    ---------------------------------------------------
    含义：寻找"方向明确"且"力度强劲"的上涨股票。
    原理：结合了均值（方向）和标准差（波动率/力度）。
         - 均值 > 0 表示上涨。
         - 标准差大 表示波动剧烈（资金活跃）。
         - 两者相乘：只有当"上涨"且"活跃"时，因子值才会极大。
    目标：寻找既有上涨趋势，又有资金关注（高波动）的进攻型标的。

    公式: mean(涨跌幅, N) × std(涨跌幅, N)

    param: N (回看窗口, 如 20)
    排序: False (值越大越好)

    选股因子案例: ('z_动量叠波_zh', False, 20, 1)
    """
    col_name = kwargs['col_name']
    n = param

    mtm_mean = df['涨跌幅'].rolling(n, min_periods=n).mean()
    mtm_std = df['涨跌幅'].rolling(n, min_periods=n).std()

    factor_df = pd.DataFrame({col_name: mtm_mean * mtm_std}, index=df.index)

    return factor_df

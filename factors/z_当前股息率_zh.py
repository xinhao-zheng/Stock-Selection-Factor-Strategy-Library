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

fin_cols = []
extra_data = {'dividend-delivery': ['分红率_最近日']}


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

    当前股息率因子
    ---------------------------------------------------
    含义：以当日收盘价衡量的实时股息率。
    原理：分红率_最近日 = 近一年分红(TTM) / 当日收盘价，由框架 data_bridge 每日更新。
         与 分红率_登记日（仅在登记日快照后 ffill）不同，本因子分母随股价实时变动，
         能反映「今天买入的真实股息回报率」。
         因子值越大，说明以当前价格买入可获得的股息收益率越高。

    公式: 近一年分红 / 当日收盘价 (= 分红率_最近日，直接透传)

    param: 无 (传空字符串即可)
    排序: False (值越大越好)

    选股因子案例: ('z_当前股息率_zh', False, '', 1)
    过滤因子案例: ('z_当前股息率_zh', '', 'pct:<=0.5', False)
    """
    col_name = kwargs['col_name']

    factor_df = pd.DataFrame(
        {col_name: df['分红率_最近日']},
        index=df.index,
    )

    return factor_df

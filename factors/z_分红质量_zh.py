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
extra_data = {'dividend-delivery': ['分红率_登记日_近年均值', '分红率_登记日_近年标准差']}


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

    分红质量因子
    ---------------------------------------------------
    含义：衡量近 3 年分红率是否「既高又稳」。
    原理：以近 3 年分红率均值为基础，乘以一个由标准差决定的折扣系数。
         均值高且波动小 → 得分高；均值高但波动大 → 被折扣；均值低即使极稳也排不上去。
         折扣系数 = 均值 / (均值 + k × 标准差)，取值恒在 0~1 之间，
         k 越大越严格（更怕波动），k=0 退化为纯均值排序。

    公式: 均值 × 均值 / (均值 + k × 标准差)
      均值 = 分红率_登记日_近年均值（框架 data_bridge 已计算，近 3 年报告期）
      标准差 = 分红率_登记日_近年标准差（同上）

    param: k (稳定性惩罚系数, 默认 1; 0.5=温和, 2=严格)
    排序: False (值越大越好)

    选股因子案例: ('z_分红质量_zh', False, 1, 1)
    过滤因子案例: ('z_分红质量_zh', 1, 'pct:<=0.5', False)
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

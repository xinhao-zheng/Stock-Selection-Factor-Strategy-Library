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
extra_data = {'dividend-delivery': ['连续分红年份']}


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

    连续分红年份因子
    ---------------------------------------------------
    含义：透传 data_bridge 计算的「连续分红年份」，用于过滤门槛。
         连续分红年份 = 从最近一次登记日往回数，不间断有分红记录的年数。
         因子值为整数（1, 2, 3, 5, 10 ...），一般不用于排序打分，仅作过滤。

    param: 无 (传空字符串即可)
    排序: 不适用（过滤因子）

    选股因子案例: 无
    过滤因子案例: ('z_连续分红年份_zh', '', 'val:>=3', False)
    """
    col_name = kwargs['col_name']

    factor_df = pd.DataFrame(
        {col_name: df['连续分红年份']},
        index=df.index,
    )

    return factor_df

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

    持仓成本偏离因子
    ---------------------------------------------------
    含义：衡量当前股价相对于近期市场平均持仓成本（VWAP）的偏离程度。
    原理：VWAP 代表了市场参与者的平均成本。
         - 当 Bias > 0 时，股价高于成本，市场处于获利状态，抛压可能较轻（上涨趋势确认）。
         - 当 Bias < 0 时，股价低于成本，市场处于套牢状态，上方存在解套抛压。
    目标：寻找股价站上平均成本线、趋势转强且套牢盘较少的标的。

    公式: (收盘价 - VWAP_N) / VWAP_N
      VWAP_N = sum(成交额, N) / sum(成交量, N)

    param: N (回看窗口, 如 20)
    排序: False (值越大越好)

    选股因子案例: ('z_持仓成本偏离_zh', False, 20, 1)
    """
    col_name = kwargs['col_name']
    n = param

    amount_sum = df['成交额'].rolling(n, min_periods=n).sum()
    volume_sum = df['成交量'].rolling(n, min_periods=n).sum()
    vwap = amount_sum / volume_sum.replace(0, float('nan'))

    factor_df = pd.DataFrame({col_name: (df['收盘价'] - vwap) / vwap}, index=df.index)

    return factor_df

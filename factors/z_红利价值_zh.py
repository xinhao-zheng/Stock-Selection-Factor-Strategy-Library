"""
Stock Quant Strategy Framework
---------------------------------------------------
Author:    Xinhao Zheng
Contact:   Veritas428 (WeChat)
Copyright: (c) 2026 Xinhao Zheng. Licensed under the MIT License.
---------------------------------------------------
"""
import pandas as pd

fin_cols = [
    'B_st_borrow@xbx', 'B_lt_loan@xbx', 'B_bond_payable@xbx',
    'B_lease_libilities@xbx', 'B_minority_equity@xbx',
    'B_preferred_shares@xbx', 'B_currency_fund@xbx',
]
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

    红利价值因子
    ---------------------------------------------------
    含义：红利版的 FCFFEV。衡量「每单位企业价值对应多少分红回报」。
    原理：当前股息率 × (总市值/EV)，与 FCFFEV = 自由现金流 / EV 结构对齐。
         - 当前股息率（分红率_最近日）：分红多不多、当前价格贵不贵
         - 总市值/EV：资本结构调整（高杠杆公司该比值 < 1，被打折）
         因子值越大，说明公司分红慷慨且整体标价便宜。
         分红稳定性由过滤条件（z_连续分红年份_zh 或 z_分红质量_zh）保障，不在因子内做折扣。

    公式: 分红率_最近日 × (总市值 / EV)
      分红率_最近日 = 近一年分红(TTM) / 当日收盘价（data_bridge 每日更新）
      EV = 总市值 + 短期借款 + 长期借款 + 应付债券 + 租赁负债
           + 少数股东权益 + 优先股 − 货币资金

    param: 无（传空字符串即可）
    排序: False (值越大越好)

    选股因子案例: ('z_红利价值_zh', False, '', 1)
    过滤因子案例: ('z_红利价值_zh', '', 'pct:<=0.5', False)
    """
    col_name = kwargs['col_name']

    div_yield = df['分红率_最近日']

    ev = (df['总市值'].fillna(0)
          + df['B_st_borrow@xbx'].fillna(0)
          + df['B_lt_loan@xbx'].fillna(0)
          + df['B_bond_payable@xbx'].fillna(0)
          + df['B_lease_libilities@xbx'].fillna(0)
          + df['B_minority_equity@xbx'].fillna(0)
          + df['B_preferred_shares@xbx'].fillna(0)
          - df['B_currency_fund@xbx'].fillna(0))

    mv_ev_ratio = df['总市值'] / ev.replace(0, float('nan'))

    factor_df = pd.DataFrame(
        {col_name: div_yield * mv_ev_ratio},
        index=df.index,
    )

    return factor_df

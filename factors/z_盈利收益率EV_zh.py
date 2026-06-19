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

fin_cols = [
    'R_np@xbx_ttm', 'R_np@xbx_单季',
    'B_st_borrow@xbx', 'B_lt_loan@xbx', 'B_bond_payable@xbx',
    'B_lease_libilities@xbx', 'B_minority_equity@xbx',
    'B_preferred_shares@xbx', 'B_currency_fund@xbx',
]


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

    盈利收益率EV因子
    ---------------------------------------------------
    含义：EP 的企业价值版本。用净利润除以 EV 而非总市值，
         消除不同资本结构（杠杆高低）对估值排序的扭曲。
    原理：EP = 净利润 / 总市值，只站在股东视角；
         本因子将分母替换为 EV（总市值 + 带息负债 + 少数股东权益 + 优先股 − 货币资金），
         使高杠杆公司不会因「市值小」而虚假地显得便宜。
         因子值越大，说明整家公司标价下的盈利回报率越高，估值越低（更便宜）。

    公式: 净利润 / EV
      EV = 总市值 + 短期借款 + 长期借款 + 应付债券 + 租赁负债
           + 少数股东权益 + 优先股 − 货币资金

    param: '全年' (TTM净利润) 或 '单季' (最近单季净利润)
    排序: False (值越大越好)

    选股因子案例: ('z_盈利收益率EV_zh', False, '全年', 1)
    过滤因子案例: ('z_盈利收益率EV_zh', '全年', 'pct:<=0.8', False)
    """
    col_name = kwargs['col_name']

    profit_cols = {
        '全年': 'R_np@xbx_ttm',
        '单季': 'R_np@xbx_单季',
    }
    if param not in profit_cols:
        raise ValueError(f"z_盈利收益率EV_zh 仅支持参数 '全年' 或 '单季'，收到：{param}")
    profit_col = profit_cols[param]

    ev = (df['总市值'].fillna(0)
          + df['B_st_borrow@xbx'].fillna(0)
          + df['B_lt_loan@xbx'].fillna(0)
          + df['B_bond_payable@xbx'].fillna(0)
          + df['B_lease_libilities@xbx'].fillna(0)
          + df['B_minority_equity@xbx'].fillna(0)
          + df['B_preferred_shares@xbx'].fillna(0)
          - df['B_currency_fund@xbx'].fillna(0))

    factor_df = pd.DataFrame(
        {col_name: df[profit_col] / ev.replace(0, float('nan'))},
        index=df.index,
    )

    return factor_df

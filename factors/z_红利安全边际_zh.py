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

fin_cols = ['C_ncf_from_oa@xbx_ttm', 'C_cash_paid_for_assets@xbx_ttm']
extra_data = {'dividend-delivery': ['分红率_最近日', '近一年分红']}


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

    红利安全边际因子
    ---------------------------------------------------
    含义：把「当前股息率」和「分红可持续性」合成一个数，只有既高、又撑得住的分红才算数。
    原理：高股息是回报的底气，但分红必须靠公司自己赚的现金撑住，而不是借钱或掏存量硬分。
         本因子在当前股息率的基础上，乘以一个由 FCF 覆盖度决定的截断系数：
         - 当前股息率（分红率_最近日）：以当日收盘价衡量的实时现金回报率，越高越慷慨；
         - FCF覆盖度 = 自由现金流TTM / 近一年分红总额：分红撑不撑得住的验证项；
           覆盖度<0（自由现金流为负、靠举债分红）→ 截断为 0，有效股息率直接归零；
           覆盖度>cap（远超分红所需）→ 截断为 cap，避免极端值喧宾夺主。
         因子值越大，说明当前股息既高、又有真实现金流撑住。

    公式: 分红率_最近日 × clip(FCF覆盖度, 0, cap)
      FCF覆盖度 = (经营现金流净额TTM − 购建固定资产等支付的现金TTM) / 近一年分红总额
      近一年分红总额 = 近一年分红(每股) × 总股本；  总股本 = 总市值 / 收盘价

    param: cap (FCF覆盖度上限倍数，默认 3.0；越大越宽松，1.0=要求分红恰好被现金流覆盖即满分)
    排序: False (值越大越好)

    选股因子案例: ('z_红利安全边际_zh', False, 3, 1)
    过滤因子案例: ('z_红利安全边际_zh', 3, 'pct:<=0.5', False)
    """
    col_name = kwargs['col_name']
    cap = float(param) if param not in (None, '') else 3.0

    # 当前股息率：近一年分红(TTM) / 当日收盘价（框架 data_bridge 每日更新）
    div_yield = df['分红率_最近日'].to_numpy(dtype='float64', na_value=np.nan)

    # 自由现金流TTM = 经营现金流净额TTM − 购建固定资产等支付的现金TTM
    oa = df['C_ncf_from_oa@xbx_ttm'].to_numpy(dtype='float64', na_value=np.nan)
    capex = df['C_cash_paid_for_assets@xbx_ttm'].to_numpy(dtype='float64', na_value=np.nan)
    fcf_ttm = oa - capex

    # 近一年分红总额 = 近一年分红(每股) × 总股本；总股本 = 总市值 / 收盘价
    close = df['收盘价'].to_numpy(dtype='float64', na_value=np.nan)
    close = np.where(close == 0, np.nan, close)
    total_shares = df['总市值'].to_numpy(dtype='float64', na_value=np.nan) / close
    total_dividend = df['近一年分红'].to_numpy(dtype='float64', na_value=np.nan) * total_shares
    total_dividend = np.where(total_dividend == 0, np.nan, total_dividend)

    # FCF覆盖度截断到 [0, cap]：负值（靠借钱分红）记 0 分，超高值封顶
    fcf_cover = np.clip(fcf_ttm / total_dividend, 0.0, cap)

    factor_df = pd.DataFrame({col_name: div_yield * fcf_cover}, index=df.index)

    return factor_df

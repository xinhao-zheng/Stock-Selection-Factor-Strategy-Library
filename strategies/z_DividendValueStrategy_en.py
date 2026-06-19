"""
Stock Quant Strategy Framework
---------------------------------------------------
Author:    Xinhao Zheng
Contact:   Veritas428 (WeChat)
Copyright: (c) 2026 Xinhao Zheng. Licensed under the MIT License.
---------------------------------------------------
"""
import pandas as pd
from core.model.strategy_config import StrategyConfig
import numpy as np
from core.market_essentials import factor_neutralization

STG_INTRO = {
    'Strategy Livestream': [],
    'Forum Posts': [],
    'Related Fleets': [],
    'Strategy Description': """
    The dividend analog of the FCFFEV strategy, following the universal value
    template: Factor A (X/Price) + Factor B (Verify X).
    - Factor A (z_DividendValue_en): Dividend/EV — is the dividend cheap?
    - Factor B (z_FCFDividendCoverage_en): FCF/Dividends — is the dividend sustainable?
    Both factors are equally weighted; one measures value, the other quality.

    In factor_list:
        - z_DividendValue_en and Primary Industry: Mandatory
        - z_FCFDividendCoverage_en: Recommended (quality factor, replaces profit growth used in legacy dividend strategy)
        - Other factors: Auxiliary ranking factors, where args = weight (1 = equal weight, 0.5 = half weight)
        - Composite Factor = Core Rank * 1 + Σ(Auxiliary Factor Rank * Weight), smaller rank = better

    The weight parameter for [z_DividendValue_en] defines the industry over-weighting rule (Quota), which can be a list or tuple of custom length, for example:
        Sort industry average values to get Industry Average Rank, then sort stock factor values within industries to get Intra-Industry Rank,
        [1,1,1,1,1]: Select 1 stock from each of the top 5 industries
        [2,2,2]: Select 2 stocks from each of the top 3 industries
        [3,2,1]: Select 3 stocks from the 1st industry, 2 from the 2nd, and 1 from the 3rd.
    If the weight parameter for [z_DividendValue_en] is not a list or tuple, the industry over-weighting function is disabled.

    The weight parameter for [Primary Industry] determines whether to apply industry neutralization to the core factor, options:
        original: Do not apply industry neutralization
        neutralized: Apply industry neutralization

    Recommended filter_list:
        ('z_ConsecutiveDividendYears_en', '', 'val:>=3', False)  — At least 3 consecutive years of dividends (hard threshold)
        ('z_DividendQuality_en', 1, 'pct:<=0.5', False)  — Dividend quality (high and stable) in the top 50% of the market
        ('一级行业过滤', ['银行', '非银金融', '房地产'], 'val:==0', False)  — Exclude high-leverage industries
    """,
    'Use Case-1 (Recommended: Dual-Factor Ranking)':
        {
            'name': 'z_DividendValueStrategy_en',
            'hold_period': 'W',
            'offset_list': [0, 1, 2, 3, 4],
            'select_num': 5,
            'cap_weight': 1,
            'rebalance_time': 'open',
            'factor_list': [('z_DividendValue_en', False, '', 1),
                            ('一级行业', False, '', 'original'),
                            ('z_FCFDividendCoverage_en', False, '', 1),
                            ],
            'filter_list': [('z_ConsecutiveDividendYears_en', '', 'val:>=3', False),
                            ('z_DividendQuality_en', 1, 'pct:<=0.5', False),
                            ('一级行业过滤', ['银行', '非银金融', '房地产'], 'val:==0', False),
                            ],
        },
    'Use Case-2 (Industry Quota)':
        {
            'name': 'z_DividendValueStrategy_en',
            'hold_period': 'W',
            'offset_list': [0, 1, 2, 3, 4],
            'select_num': 5,
            'cap_weight': 1,
            'rebalance_time': 'open',
            'factor_list': [('z_DividendValue_en', False, '', [3, 2, 1]),
                            ('一级行业', False, '', 'original'),
                            ('z_FCFDividendCoverage_en', False, '', 1),
                            ],
            'filter_list': [('z_ConsecutiveDividendYears_en', '', 'val:>=3', False),
                            ('z_DividendQuality_en', 1, 'pct:<=0.5', False),
                            ('一级行业过滤', ['银行', '非银金融', '房地产'], 'val:==0', False),
                            ],
        },
}


def calc_select_factor(df, strategy: StrategyConfig) -> pd.DataFrame:
    """
    Calculate composite selection factor
    :param df: Processed data containing factor information and period conversion
    :param strategy: Strategy configuration
    :return: Filtered data

    ### df Column Description
    Includes base columns: ['交易日期', '股票代码', '股票名称', '周频起始日', '月频起始日', '上市至今交易天数', '复权因子', '开盘价', '最高价',
                '最低价', '收盘价', '成交额', '是否交易', '流通市值', '总市值', '下日_开盘涨停', '下日_是否ST', '下日_是否交易',
                '下日_是否退市']
    And result columns calculated from factors configured in config.

    ### strategy Data Description
    - strategy.name: Strategy name
    - strategy.hold_period: Holding period
    - strategy.select_num: Number of stocks to select
    - strategy.factor_name: Composite factor name
    - strategy.factor_list: List of selection factors
    - strategy.filter_list: List of filter factors
    - strategy.factor_columns: Column names of selection + filter factors
    """

    # Extract data for all factors
    core = None
    ind = None
    aux_factors = []
    for f in strategy.factor_list:
        if f.name == '一级行业':
            ind = f
        elif core is None:
            core = f
        else:
            aux_factors.append(f)

    # Parse parameters
    neutral_type = ind.args if ind.args in ['original', 'neutralized'] else 'original'  # Whether to apply industry neutralization to the core factor
    quota = core.args  # Industry quota list

    # Apply industry neutralization if configured
    if neutral_type == 'neutralized':
        # Apply industry neutralization to the core factor
        df = factor_neutralization(df, factor=core.col_name, neutralize_list=[], industry=ind.col_name)
        # Calculate Core Rank
        df['核心排名'] = df.groupby('交易日期')[f'{core.col_name}_中性'].rank(ascending=False, method='min')
    else:
        # Calculate Core Rank
        df['核心排名'] = df.groupby('交易日期')[core.col_name].rank(ascending=False, method='min')

    df['复合因子'] = df['核心排名']

    # Weighted ranking of auxiliary factors
    for af in aux_factors:
        af_rank = df.groupby('交易日期')[af.col_name].rank(ascending=af.is_sort_asc, method='min')
        weight = float(af.args) if isinstance(af.args, (int, float)) else 1.0
        df['复合因子'] = df['复合因子'] + af_rank * weight

    # Check if quota is a list or tuple
    if isinstance(quota, (list, tuple)):
        strategy.select_num = sum(quota)

        # Calculate Industry Average Rank
        rank_col = f'{core.col_name}_中性' if neutral_type == 'neutralized' else core.col_name
        industry_stats = df.groupby(['交易日期', ind.col_name])[rank_col].agg(['mean']).reset_index()
        industry_stats.columns = ['交易日期', ind.col_name, '行业平均值']
        industry_stats['行业平均排名'] = industry_stats.groupby('交易日期')['行业平均值'].rank(ascending=False, method='min')

        # Add Industry Average Rank
        df = pd.merge(df, industry_stats[['交易日期', ind.col_name, '行业平均排名']],
                      on=['交易日期', ind.col_name], how='left')

        # Calculate Intra-Industry Rank based on Composite Factor
        df['行业内排名'] = df.groupby(['交易日期', ind.col_name])['复合因子'].rank(ascending=True, method='min')
        df['是否保留'] = np.nan
        for i in range(len(quota)):
            ind_rank = i + 1
            ind_count = quota[i]

            con1 = df['行业平均排名'] == ind_rank
            con2 = df['行业内排名'] <= ind_count
            df.loc[con1 & con2, '是否保留'] = 1

        df = df[df['是否保留'] == 1]

    return df

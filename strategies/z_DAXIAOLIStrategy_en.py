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
    Li Daxiao Strategy (academic research simulation based on public corpora and local RAG;
    not endorsed by Li Daxiao; not investment advice).
    Refined from the z_DividendValueStrategy_en template, operationalizing Li Daxiao's
    "do good, buy good stocks, reap good returns" thesis into a multi-factor value strategy of
    [FCF-validated high dividend + cheapness + large-cap blue chips], following the universal
    value template skeleton: Core Factor A: X/Price + Verification Factor B: Verify X.
    Provenance for each design choice: see 《李大霄选股逻辑_量化因子分析.md》(RAG / book / public reports).

    Li Daxiao source logic → factor / filter mapping:
    - Good stock = tangible cash return to shareholders; high dividends sustainable only at
      quality companies
      → Core factor z_DividendSafetyMargin_en (Current Dividend Yield × FCF Coverage);
        spurious high yield / debt-funded dividends zero out automatically
    - Exceptional value, lowest-valued quality blue chips
      → Auxiliary z_EarningsYieldEV_en (Net Profit / EV; EV not PE)
    - Large-cap blue chips / core assets / banks as king
      → Auxiliary 市值 (larger is better, half weight); banks NOT excluded
    - Avoid five overvalued categories (small / new / bad / thematic / pseudo-growth)
      → All enforced as hard boundaries in filter_list
    - Low turnover / ride the lift → hold_period monthly 'M'
    (Bond-equity relative value is a timing dimension with no cross-sectional discriminatory
     power; stock selection only, no timing overlay, hence no such factor)

    In factor_list:
        - Core factor (1st non-"一级行业" factor) and 一级行业: Mandatory
        - Recommended core factor: z_DividendSafetyMargin_en (FCF-validated effective dividend
          yield); z_DividendValue_en may be substituted
        - Other factors: Auxiliary ranking factors, args = weight (1 = equal to core, 0.5 = half)
        - Composite Factor = Core Rank × 1 + Σ(Auxiliary Rank × Weight), smaller rank = better

    The weight parameter for [Core Factor] defines the industry over-weighting rule (Quota),
    which can be a list or tuple of custom length, for example:
        Sort industry average values to get Industry Average Rank, then sort stock factor values
        within industries to get Intra-Industry Rank,
        [1,1,1,1,1]: Select 1 stock from each of the top 5 industries
        [3,3,2,2]: Select 3 from the 1st industry, 3 from the 2nd, 2 from the 3rd and 4th (10 total)
    If the weight parameter for [Core Factor] is not a list or tuple, industry over-weighting is disabled.

    The weight parameter for [一级行业] controls industry neutralization of the core factor:
        original: No industry neutralization
        neutralized: Apply industry neutralization (avoid dividend concentration in a single
                     industry, e.g. all banks)

    Recommended filter_list (avoid five overvalued categories + investable-quality threshold,
    ordered small → new → bad → pseudo-growth → thematic):
        ('市值', '', 'pct:>=0.3', True)                  — ① Avoid "small": exclude bottom 30% by market cap (micro-cap / delisting risk)
        ('上市至今交易天数', '', 'val:>=750', False)      — ② Avoid "new": listed ≥ ~3 years (IPO price decay)
        ('z_ConsecutiveDividendYears_en', '', 'val:>=3', False)  — ③ Avoid "bad": consecutive dividend ≥ 3 years (non-payers excluded)
        ('EP', '全年', 'val:>0', False)                  — ④ Avoid "pseudo-growth": TTM net profit > 0 (loss-makers excluded)
        ('换手率', 20, 'pct:<=0.8', True)                — ⑤ Avoid "thematic": exclude top 20% turnover (speculation / concept stocks)
        ('z_DividendQuality_en', 1, 'pct:<=0.5', False)  — ⑥ High and stable dividends (top half of market by dividend quality)
        # ('一级行业过滤', ['银行', '非银金融', '房地产'], 'val:==0', False)  — Optional: exclude high-leverage industries; Li Daxiao version disabled by default (banks as king)
    """,
    'Use Case-1 (Recommended: FCF-validated high dividend, monthly ride-the-lift)':
        {
            'name': 'z_DAXIAOLIStrategy_en',
            'hold_period': 'M',
            'offset_list': [0],
            'select_num': 10,
            'cap_weight': 1,
            'rebalance_time': 'open',
            'factor_list': [('z_DividendSafetyMargin_en', False, 3, 1),
                            ('一级行业', False, '', 'original'),
                            ('z_EarningsYieldEV_en', False, '全年', 1),
                            ('市值', False, '', 0.5),
                            ],
            'filter_list': [('市值', '', 'pct:>=0.3', True),
                            ('上市至今交易天数', '', 'val:>=750', False),
                            ('z_ConsecutiveDividendYears_en', '', 'val:>=3', False),
                            ('EP', '全年', 'val:>0', False),
                            ('换手率', 20, 'pct:<=0.8', True),
                            ('z_DividendQuality_en', 1, 'pct:<=0.5', False),
                            # ('一级行业过滤', ['银行', '非银金融', '房地产'], 'val:==0', False),  # Optional: align with classic template; disabled by default
                            ],
        },
    'Use Case-2 (Industry Quota + Industry Neutralization, forced cross-industry diversification)':
        {
            'name': 'z_DAXIAOLIStrategy_en',
            'hold_period': 'M',
            'offset_list': [0],
            'select_num': 10,
            'cap_weight': 1,
            'rebalance_time': 'open',
            'factor_list': [('z_DividendSafetyMargin_en', False, 3, [3, 3, 2, 2]),
                            ('一级行业', False, '', 'neutralized'),
                            ('z_EarningsYieldEV_en', False, '全年', 1),
                            ('市值', False, '', 0.5),
                            ],
            'filter_list': [('市值', '', 'pct:>=0.3', True),
                            ('上市至今交易天数', '', 'val:>=750', False),
                            ('z_ConsecutiveDividendYears_en', '', 'val:>=3', False),
                            ('EP', '全年', 'val:>0', False),
                            ('换手率', 20, 'pct:<=0.8', True),
                            ('z_DividendQuality_en', 1, 'pct:<=0.5', False),
                            # ('一级行业过滤', ['银行', '非银金融', '房地产'], 'val:==0', False),  # Optional: align with classic template; disabled by default
                            ],
        },
    'Use Case-3 (Classic Dividend Value, aligned with original template core factors)':
        {
            'name': 'z_DAXIAOLIStrategy_en',
            'hold_period': 'M',
            'offset_list': [0],
            'select_num': 10,
            'cap_weight': 1,
            'rebalance_time': 'open',
            'factor_list': [('z_DividendValue_en', False, '', 1),
                            ('一级行业', False, '', 'original'),
                            ('z_FCFDividendCoverage_en', False, '', 1),
                            ('市值', False, '', 0.5),
                            ],
            'filter_list': [('市值', '', 'pct:>=0.3', True),
                            ('上市至今交易天数', '', 'val:>=750', False),
                            ('z_ConsecutiveDividendYears_en', '', 'val:>=3', False),
                            ('EP', '全年', 'val:>0', False),
                            ('换手率', 20, 'pct:<=0.8', True),
                            ('z_DividendQuality_en', 1, 'pct:<=0.5', False),
                            # ('一级行业过滤', ['银行', '非银金融', '房地产'], 'val:==0', False),  # Optional: align with classic template; disabled by default
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

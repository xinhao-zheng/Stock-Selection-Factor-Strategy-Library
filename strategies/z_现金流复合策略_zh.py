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
    '策略直播': [],
    '论坛帖子': [],
    '相关船队': [],
    '策略说明': """
    基于现金流选股策略的多因子扩展版。
    保留原版FCFFEV+一级行业+行业配额的全部功能，新增支持任意辅助因子的排名加权。

    factor_list 中:
        - FCFFEV 和 一级行业: 必选，功能与原版完全一致
        - 其余因子: 辅助排名因子，args 为权重（1=与FCFFEV等权, 0.5=半权）
        - 复合因子 = FCFFEV排名×1 + Σ(辅助因子排名×权重)，排名越小=越优

    行业配额规则与原版完全一致，唯一区别是行业内排名使用复合因子而非纯FCFFEV。
    当 factor_list 中只有 FCFFEV 和 一级行业 时，行为与原版现金流选股策略完全相同。

    【FCFFEV】的权重参数是行业超配规则，可以设置为一个列表或元组，长度可自定义，例如：
        对行业平均值进行排序后得到行业平均排名，再对行业内股票因子值排序得到行业内排名，
        [1,1,1,1,1]: 表示前5的行业，每个选1个股票
        [2,2,2]：表示前3的行业，每个选2个股票
        [3,2,1]：表示第1的行业选3个，第2的行业选2个，第3的行业选1个
    当【FCFFEV】的权重参数不为列表或元组，则不使用行业超配功能。

    【一级行业】的权重参数控制是否要对核心因子做行业中性化，可以设置：
        original：不做行业中性化
        neutralized：做行业中性化
    """,
    '使用案例-1（基础：纯FCFFEV选股）':
        {
            'name': 'z_现金流复合策略_zh',
            'hold_period': 'W',
            'offset_list': [0, 1, 2, 3, 4],
            'select_num': 5,
            'cap_weight': 1,
            'rebalance_time': 'open',
            'factor_list': [('FCFFEV', False, 'ttm', 1),
                            ('一级行业', False, '', 'original'),
                            ],
            'filter_list': [('FCFF_TTM大于0', 3 * 250, 'val:==1', False),
                            ('一级行业过滤', ['银行', '非银金融', '房地产'], 'val:==0', False),
                            ],
        },
    '使用案例-2（多因子+行业配额）':
        {
            'name': 'z_现金流复合策略_zh',
            'hold_period': '3D',
            'offset_list': [0, 1, 2],
            'select_num': 5,
            'cap_weight': 1,
            'rebalance_time': '0950-0950',
            'factor_list': [('FCFFEV', False, 'ttm', [3, 2, 1]),
                            ('一级行业', False, '', 'original'),
                            ('z_动量叠波_zh', False, 20, 1),
                            ('z_趋势纯度_zh', False, 20, 1),
                            ],
            'filter_list': [('FCFF_TTM大于0', 3 * 250, 'val:==1', False),
                            ('一级行业过滤', ['银行', '非银金融', '房地产'], 'val:==0', False),
                            ],
        },
}


def calc_select_factor(df, strategy: StrategyConfig) -> pd.DataFrame:
    """
    计算复合选股因子
    :param df: 整理好的数据，包含因子信息，并做过周期转换
    :param strategy: 策略配置
    :return: 返回过滤后的数据

    ### df 列说明
    包含基础列：  ['交易日期', '股票代码', '股票名称', '周频起始日', '月频起始日', '上市至今交易天数', '复权因子', '开盘价', '最高价',
                '最低价', '收盘价', '成交额', '是否交易', '流通市值', '总市值', '下日_开盘涨停', '下日_是否ST', '下日_是否交易',
                '下日_是否退市']
    以及config中配置好的，因子计算的结果列。

    ### strategy 数据说明
    - strategy.name: 策略名称
    - strategy.hold_period: 持仓周期
    - strategy.select_num: 选股数量
    - strategy.factor_name: 复合因子名称
    - strategy.factor_list: 选股因子列表
    - strategy.filter_list: 过滤因子列表
    - strategy.factor_columns: 选股+过滤因子的列名
    """

    # 拿出所有因子的数据
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

    # 解析参数
    neutral_type = ind.args if ind.args in ['original', 'neutralized'] else 'original'  # 是否对核心因子做行业中性化
    quota = core.args  # 行业超配列表

    # 是否进行行业中性化
    if neutral_type == 'neutralized':
        # 对核心因子进行行业中性化
        df = factor_neutralization(df, factor=core.col_name, neutralize_list=[], industry=ind.col_name)
        # 计算核心排名
        df['核心排名'] = df.groupby('交易日期')[f'{core.col_name}_中性'].rank(ascending=False, method='min')
    else:
        # 计算核心排名
        df['核心排名'] = df.groupby('交易日期')[core.col_name].rank(ascending=False, method='min')

    df['复合因子'] = df['核心排名']

    # 计算辅助因子排名并加权
    for af in aux_factors:
        af_rank = df.groupby('交易日期')[af.col_name].rank(ascending=af.is_sort_asc, method='min')
        weight = float(af.args) if isinstance(af.args, (int, float)) else 1.0
        df['复合因子'] = df['复合因子'] + af_rank * weight

    # 检查quota是否是一个列表或者元组
    if isinstance(quota, (list, tuple)):
        strategy.select_num = sum(quota)

        # 计算行业平均值排名
        rank_col = f'{core.col_name}_中性' if neutral_type == 'neutralized' else core.col_name
        industry_stats = df.groupby(['交易日期', ind.col_name])[rank_col].agg(['mean']).reset_index()
        industry_stats.columns = ['交易日期', ind.col_name, '行业平均值']
        industry_stats['行业平均排名'] = industry_stats.groupby('交易日期')['行业平均值'].rank(ascending=False, method='min')

        # 添加行业平均排名
        df = pd.merge(df, industry_stats[['交易日期', ind.col_name, '行业平均排名']],
                      on=['交易日期', ind.col_name], how='left')

        # 计算复合因子行业内排名
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

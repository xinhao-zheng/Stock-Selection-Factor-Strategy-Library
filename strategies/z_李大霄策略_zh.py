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
    李大霄策略（基于公开语料 + 本地 RAG 的学术研究模拟，非李大霄本人、非投资建议）。
    在 z_红利价值策略_zh 模板之上精修，把李大霄"做好人买好股得好报"的理念，操作化为
    【经现金流验证的高股息 + 便宜 + 大蓝筹】多因子价值策略，遵循通用价值模板
    「核心因子A: X/价格 + 验证因子B: 验证X」的骨架。每条设计的出处见
    《李大霄选股逻辑_量化因子分析.md》（RAG/书/公开报道）。

    李大霄本源逻辑 → 因子/过滤映射：
    - 好股=给股东真金白银的现金回报，且高分红只有好股票才撑得住
      → 核心因子 z_红利安全边际_zh（当前股息率 × FCF覆盖度），假高息/借钱分红自动归零
    - 物超所值、最低估优质蓝筹 → 辅助因子 z_盈利收益率EV_zh（净利润/EV，用 EV 而非 PE）
    - 大蓝筹/核心资产/银行为王 → 辅助因子 市值（越大越优，半权倾斜），且【不】排除银行
    - 远离高估的五类（小/新/差/题材/伪成长）→ 全部进 filter_list 做硬边界
    - 少交易/坐轿子 → hold_period 用月频 'M'
    （股债性价比是择时维度，对横截面选股无区分度，本策略只做选股不做择时，故不设该因子）

    factor_list 中:
        - 核心因子（第1个非"一级行业"的因子）和 一级行业: 必选
        - 推荐核心因子: z_红利安全边际_zh（经现金流验证的有效股息率）; 也可换回 z_红利价值_zh
        - 其余因子: 辅助排名因子，args 为权重（1=与核心因子等权, 0.5=半权）
        - 复合因子 = 核心因子排名×1 + Σ(辅助因子排名×权重)，排名越小=越优

    【核心因子】的权重参数是行业超配规则，可以设置为一个列表或元组，长度可自定义，例如：
        对行业平均值排序得到行业平均排名，再对行业内股票因子值排序得到行业内排名，
        [1,1,1,1,1]: 表示前5的行业，每个选1个股票
        [3,3,2,2]: 表示第1、2行业各选3个，第3、4行业各选2个（共10个）
    当【核心因子】的权重参数不为列表或元组，则不使用行业超配功能。

    【一级行业】的权重参数控制是否要对核心因子做行业中性化，可以设置：
        original：不做行业中性化
        neutralized：做行业中性化（避免红利扎堆单一行业，如全是银行）

    建议搭配的 filter_list（远离高估的五类 + 余钱好股门槛，按 小→新→差→伪成长→题材 顺序）：
        ('市值', '', 'pct:>=0.3', True)                 — ①远离「小」：剔除最小30%市值（微盘/退市风险）
        ('上市至今交易天数', '', 'val:>=750', False)     — ②远离「新」：上市满约3年（次新股价格折损）
        ('z_连续分红年份_zh', '', 'val:>=3', False)      — ③远离「差」：连续分红≥3年（铁公鸡出局）
        ('EP', '全年', 'val:>0', False)                 — ④远离「伪成长」：TTM净利润>0（亏损出局）
        ('换手率', 20, 'pct:<=0.8', True)               — ⑤远离「题材」：剔除换手最高20%（投机/概念炒作）
        ('z_分红质量_zh', 1, 'pct:<=0.5', False)        — ⑥分红高且稳（处于全市场较好的一半）
        # ('一级行业过滤', ['银行', '非银金融', '房地产'], 'val:==0', False)  — 可选：排除高杠杆行业；李大霄版默认关闭（银行为王）
    """,
    '使用案例-1（推荐：经现金流验证的高股息，月频坐轿子）':
        {
            'name': 'z_李大霄策略_zh',
            'hold_period': 'M',
            'offset_list': [0],
            'select_num': 10,
            'cap_weight': 1,
            'rebalance_time': 'open',
            'factor_list': [('z_红利安全边际_zh', False, 3, 1),
                            ('一级行业', False, '', 'original'),
                            ('z_盈利收益率EV_zh', False, '全年', 1),
                            ('市值', False, '', 0.5),
                            ],
            'filter_list': [('市值', '', 'pct:>=0.3', True),
                            ('上市至今交易天数', '', 'val:>=750', False),
                            ('z_连续分红年份_zh', '', 'val:>=3', False),
                            ('EP', '全年', 'val:>0', False),
                            ('换手率', 20, 'pct:<=0.8', True),
                            ('z_分红质量_zh', 1, 'pct:<=0.5', False),
                            # ('一级行业过滤', ['银行', '非银金融', '房地产'], 'val:==0', False),  # 可选：对齐经典模板；默认关闭
                            ],
        },
    '使用案例-2（行业配额 + 行业中性化，强制跨行业分散）':
        {
            'name': 'z_李大霄策略_zh',
            'hold_period': 'M',
            'offset_list': [0],
            'select_num': 10,
            'cap_weight': 1,
            'rebalance_time': 'open',
            'factor_list': [('z_红利安全边际_zh', False, 3, [3, 3, 2, 2]),
                            ('一级行业', False, '', 'neutralized'),
                            ('z_盈利收益率EV_zh', False, '全年', 1),
                            ('市值', False, '', 0.5),
                            ],
            'filter_list': [('市值', '', 'pct:>=0.3', True),
                            ('上市至今交易天数', '', 'val:>=750', False),
                            ('z_连续分红年份_zh', '', 'val:>=3', False),
                            ('EP', '全年', 'val:>0', False),
                            ('换手率', 20, 'pct:<=0.8', True),
                            ('z_分红质量_zh', 1, 'pct:<=0.5', False),
                            # ('一级行业过滤', ['银行', '非银金融', '房地产'], 'val:==0', False),  # 可选：对齐经典模板；默认关闭
                            ],
        },
    '使用案例-3（经典红利价值，对齐原模板核心因子）':
        {
            'name': 'z_李大霄策略_zh',
            'hold_period': 'M',
            'offset_list': [0],
            'select_num': 10,
            'cap_weight': 1,
            'rebalance_time': 'open',
            'factor_list': [('z_红利价值_zh', False, '', 1),
                            ('一级行业', False, '', 'original'),
                            ('z_FCF覆盖度_zh', False, '', 1),
                            ('市值', False, '', 0.5),
                            ],
            'filter_list': [('市值', '', 'pct:>=0.3', True),
                            ('上市至今交易天数', '', 'val:>=750', False),
                            ('z_连续分红年份_zh', '', 'val:>=3', False),
                            ('EP', '全年', 'val:>0', False),
                            ('换手率', 20, 'pct:<=0.8', True),
                            ('z_分红质量_zh', 1, 'pct:<=0.5', False),
                            # ('一级行业过滤', ['银行', '非银金融', '房地产'], 'val:==0', False),  # 可选：对齐经典模板；默认关闭
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

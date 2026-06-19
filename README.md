# Stock-Selection Factor & Strategy Library · 量化选股因子与策略库

A library of plug-in factors and strategies for a stock-selection framework. Factors measure a stock; strategies compose those measurements into a portfolio. Each is a self-contained module the framework loads by filename — add a file to extend the library, take any file to reuse it.

面向选股框架的即插即用因子与策略库。因子度量个股，策略把度量组合成持仓。每个都是框架按文件名加载的自包含模块——加一个文件即扩展，取任一文件即复用。

## Layout · 结构

```text
.
├── factors/        # add_factor(df, param, **kwargs) → 一列因子值
├── strategies/     # calc_select_factor(df, strategy) + STG_INTRO → 持仓
├── requirements.txt
└── LICENSE
```

Every module ships in two editions of identical logic: a Chinese edition `z_中文名_zh.py` and an English edition `z_EnglishName_en.py`. The host resolves a module by its filename — the file is the identifier.

每个模块提供逻辑相同的两个版本：中文版 `z_中文名_zh.py` 与英文版 `z_EnglishName_en.py`。宿主按文件名解析模块——文件名即标识。

Dependencies: `pandas`, `numpy`.

依赖：`pandas`、`numpy`。

---
*MIT*

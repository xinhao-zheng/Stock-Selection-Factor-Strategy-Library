# Factor Library · 因子库

A factor is a self-contained module that maps one stock's history to a single column — the score that downstream ranking and filtering consume. Modules are independent: add a file and the framework discovers it by filename, with no registry to update and no base class to inherit.

因子是一个自包含模块，把单只股票的历史映射为一列——供下游排序与过滤使用的分值。模块彼此独立：新增一个文件，框架即按文件名发现它，无需更新注册表，也无需继承基类。

Each factor ships in two editions of identical computation: the English edition `z_EnglishName_en.py` and the Chinese edition `z_中文名_zh.py` — the same logic documented twice, not two implementations.

每个因子提供计算完全相同的两个版本：英文版 `z_EnglishName_en.py` 与中文版 `z_中文名_zh.py`——同一逻辑的双语文档，而非两套实现。

## Interface · 接口约定

```python
import pandas as pd

fin_cols = []        # financial columns the factor needs; the framework joins them in
extra_data = {}      # other declared inputs, e.g. dividend fields

def add_factor(df: pd.DataFrame, param=None, **kwargs) -> pd.DataFrame:
    col_name = kwargs['col_name']
    factor = df['收盘价'].pct_change(param)
    return pd.DataFrame({col_name: factor}, index=df.index)
```

- **Input** — `df`: one stock's K-line plus any columns named in `fin_cols` / `extra_data`. `param`: the factor's single setting — a window, a tuple, or a mode string. `col_name`: the output name, passed through `kwargs`.
- **Output** — a one-column DataFrame on `df`'s index; the module writes nothing else and keeps no state.
- **Missing data** — read only what is declared; when an input is absent, return `NaN` rather than a substitute.

- **输入** —— `df`：单只股票的K线，加上 `fin_cols` / `extra_data` 中声明的列。`param`：因子唯一参数——窗口、元组或模式字符串。`col_name`：输出列名，经 `kwargs` 传入。
- **输出** —— 与 `df` 同索引的单列 DataFrame；模块不写其他内容、不保留状态。
- **缺失数据** —— 只读声明的列；输入缺失时返回 `NaN`，不以替代值填充。

## Conventions · 约定

- One parameter per factor; pack compound settings into a tuple, e.g. `(short, long)`.
- Vectorize over `df` — avoid per-row loops, so the factor applies across the universe at scale.
- Sort direction, and whether a factor ranks or filters, are decided by the calling strategy, not the factor.

- 每个因子一个参数；复合设置打包成元组，如 `(short, long)`。
- 对 `df` 向量化——避免逐行循环，使因子可在全市场规模应用。
- 排序方向、以及作排序还是过滤，由调用的策略决定，而非因子自身。

A file's docstring is its specification: meaning, formula, parameter, and direction.

文件的 docstring 即其规格：含义、公式、参数、方向。

---
*MIT*

# data-cognition-2026-1140

学号：2515311140  
姓名：廖乙霖

## 实验目录

- [exp1-git](./exp1-git/)：Git 练习与收获文档
- [exp2-data-collection](./exp2-data-collection/)：数据采集与清洗
- [exp3-visualization](./exp3-visualization/)：交互式数据可视化
- [exp4-agent](./exp4-agent/)：智能体资料

实验1 完成于 2026 年 10 月。

## 实验2和实验3项目

主题：九地区生物图鉴数据采集与属性能力可视化分析

数据来源：PokeAPI API v2

### 项目结构

```text
exp2-data-collection/
├─ collect.py
├─ validate_data.py
├─ data/
└─ docs/

exp3-visualization/
├─ app.py
├─ run_app.bat
├─ .streamlit/config.toml
└─ docs/report_notes.md
```

### 环境安装

在仓库根目录执行：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 实验二：数据采集

```powershell
cd exp2-data-collection
..\.venv\Scripts\python.exe .\collect.py
..\.venv\Scripts\python.exe .\validate_data.py
```

数据结果：

- 基础物种记录 1025 条
- 地区形态记录 58 条
- 覆盖九个地区
- 采集失败 0 条
- 自动质量校验通过

### 实验三：交互式可视化

```powershell
cd exp3-visualization
..\.venv\Scripts\python.exe -m streamlit run .\app.py
```

也可以双击 `exp3-visualization/run_app.bat` 启动。

页面包含地区总览、属性结构、图鉴明细和数据质量四个视图。演示阶段不需要联网，
采集后的 CSV 已保存在本地仓库中。

### 文档

- `exp2-data-collection/docs/data_dictionary.md`
- `exp2-data-collection/docs/data_quality.md`
- `exp2-data-collection/docs/experiment2_report.md`
- `exp3-visualization/docs/report_notes.md`

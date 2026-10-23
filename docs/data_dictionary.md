# 数据字典

## 数据文件

| 文件 | 内容 |
|---|---|
| `data/pokemon_clean.csv` | 基础物种数据，每行代表一个物种 |
| `data/forms_clean.csv` | 地区形态数据，每行代表一个地区形态 |
| `data/region_summary.csv` | 九个地区的物种数量与平均能力值 |
| `data/type_region_long.csv` | 地区与属性的长表统计 |
| `data/type_region_matrix.csv` | 地区与属性的交叉矩阵 |
| `data/data_quality.json` | 采集数量、缺失字段和失败记录 |
| `data/validation_report.json` | 自动质量校验结果 |

## `pokemon_clean.csv` 主要字段

| 字段 | 含义 |
|---|---|
| `species_id` | 物种唯一编号 |
| `dex_number` | 图鉴编号 |
| `name_en` | 英文名称 |
| `name_zh` | 简体中文名称 |
| `generation` | PokeAPI 世代标识 |
| `generation_cn` | 中文世代名称 |
| `generation_order` | 世代排序值，从 1 到 9 |
| `region_en` | 地区英文名称 |
| `region_cn` | 地区中文名称 |
| `type1_en` / `type1_zh` | 第一属性 |
| `type2_en` / `type2_zh` | 第二属性，单属性物种为空 |
| `hp` | HP 基础值 |
| `attack` | 攻击基础值 |
| `defense` | 防御基础值 |
| `special_attack` | 特攻基础值 |
| `special_defense` | 特防基础值 |
| `speed` | 速度基础值 |
| `total_stats` | 六项基础值总和 |
| `is_legendary` | 是否为传说物种 |
| `is_mythical` | 是否为幻之物种 |
| `height_m` | 身高，单位米 |
| `weight_kg` | 体重，单位千克 |
| `abilities` | 常规特性，多个特性用分号分隔 |
| `hidden_ability` | 隐藏特性 |
| `capture_rate` | 捕获率 |
| `base_happiness` | 基础亲密度 |
| `pokemon_id` | 默认形态对应的 API 编号 |

## `forms_clean.csv` 主要字段

| 字段 | 含义 |
|---|---|
| `species_id` | 所属物种编号 |
| `species_name_zh` | 所属物种中文名 |
| `form_id` | 地区形态编号 |
| `form_name_en` | 地区形态英文名 |
| `form_name_zh` | 地区形态中文名 |
| `form_region_en` | 形态地区英文标识 |
| `form_region_cn` | 形态地区中文名 |
| `is_regional_form` | 是否为地区形态 |
| `type1_zh` / `type2_zh` | 地区形态的属性 |
| `total_stats` | 地区形态的总种族值 |

## 地区与世代映射

| 世代 | 地区 |
|---|---|
| 第一世代 | 关都 |
| 第二世代 | 城都 |
| 第三世代 | 丰缘 |
| 第四世代 | 神奥 |
| 第五世代 | 合众 |
| 第六世代 | 卡洛斯 |
| 第七世代 | 阿罗拉 |
| 第八世代 | 伽勒尔 |
| 第九世代 | 帕底亚 |

## 数据口径

- 基础物种按照首次出现的世代归入对应地区。
- 地区形态独立存储，不重复计入新增物种数。
- 洗翠形态保留为独立形态地区。洗翠属于古代神奥，不与现代神奥合并。
- 数据中不使用演员、训练家或用户个人字段。

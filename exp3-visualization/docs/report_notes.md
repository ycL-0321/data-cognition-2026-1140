# 九地区生物图鉴数据采集与可视化分析

## Experiment 2: Data collection

- Data source: PokeAPI API v2.
- Collection method: species index, species detail, default form detail, and regional form detail.
- Raw JSON responses are cached in `raw/`.
- The final collection contains 1,025 base species records and 58 regional form records.
- Duplicate species IDs: 0.
- Failed species: 0.
- All nine main regions are represented.

## Experiment 3: Visual analysis

The interactive page contains four views:

1. Region overview: species counts, average stat radar chart, and total-stat distribution.
2. Type structure: region-type heatmap, type frequency, and attack-speed scatter plot.
3. Catalog detail: name, type, region, abilities, stats, and regional forms.
4. Data quality: source, collection metadata, missing values, and regional form counts.

## Key findings

- Unova has the largest number of newly introduced species at 156.
- Kanto follows with 151, Hoenn with 135, and Paldea with 120.
- Kalos has the smallest number at 72.
- Paldea has the highest average total base stat at 457.39.
- Johto has the lowest average total base stat at 407.18.
- Water is the most frequent type occurrence at 154, followed by Normal at 131 and Grass at 127.
- Alola, Galar, and Paldea each contain 11 legendary records.
- Regional forms are distributed as follows: Alola 18, Galar 20, Hisui 16, and Paldea 4.
- Primary type leaders vary by region. Kanto, Johto, Hoenn, and Galar lean toward Water; Unova toward Bug; Kalos toward Fairy; Paldea and Alola toward Grass.

## Presentation flow

1. Explain the data source and the difference between base species and regional forms.
2. Show the data-quality view and state the final row counts.
3. Move to the region overview and compare species counts and average stats.
4. Use the type heatmap to show regional type preferences.
5. Demonstrate filters and open one catalog entry.
6. Close with three findings and one limitation.

## Saved screenshots

- `docs/images/overview.png`
- `docs/images/type_structure.png`
- `docs/images/catalog_detail.png`
- `docs/images/data_quality.png`

## Limitation

Region is assigned by the generation in which a base species first appeared.
Regional forms are stored separately and do not increase the count of newly
introduced species.

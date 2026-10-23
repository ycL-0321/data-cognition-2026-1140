from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "exp2-data-collection" / "data"

REGION_ORDER = ["关都", "城都", "丰缘", "神奥", "合众", "卡洛斯", "阿罗拉", "伽勒尔", "帕底亚"]
TYPE_ORDER = [
    "一般",
    "火",
    "水",
    "电",
    "草",
    "冰",
    "格斗",
    "毒",
    "地面",
    "飞行",
    "超能力",
    "虫",
    "岩石",
    "幽灵",
    "龙",
    "恶",
    "钢",
    "妖精",
]

TYPE_COLORS = {
    "一般": "#A8A77A",
    "火": "#EE8130",
    "水": "#6390F0",
    "电": "#F7D02C",
    "草": "#7AC74C",
    "冰": "#96D9D6",
    "格斗": "#C22E28",
    "毒": "#A33EA1",
    "地面": "#E2BF65",
    "飞行": "#A98FF3",
    "超能力": "#F95587",
    "虫": "#A6B91A",
    "岩石": "#B6A136",
    "幽灵": "#735797",
    "龙": "#6F35FC",
    "恶": "#705746",
    "钢": "#B7B7CE",
    "妖精": "#D685AD",
}

LIGHT_TYPE_COLORS = {
    "一般",
    "电",
    "冰",
    "地面",
    "飞行",
    "虫",
    "岩石",
    "钢",
    "妖精",
}

REGION_COLORS = {
    "关都": "#4E79A7",
    "城都": "#F28E2B",
    "丰缘": "#59A14F",
    "神奥": "#B07AA1",
    "合众": "#E15759",
    "卡洛斯": "#76B7B2",
    "阿罗拉": "#EDC948",
    "伽勒尔": "#9C755F",
    "帕底亚": "#7B61A8",
}

STAT_LABELS = {
    "hp": "HP",
    "attack": "攻击",
    "defense": "防御",
    "special_attack": "特攻",
    "special_defense": "特防",
    "speed": "速度",
}

STAT_COLUMNS = list(STAT_LABELS)

FORM_REGION_ORDER = ["阿罗拉", "伽勒尔", "洗翠", "帕底亚"]


st.set_page_config(
    page_title="宝可梦图鉴数据分析",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp {
        background: #f5f6f8;
    }
    .block-container {
        max-width: 1500px;
        padding-top: 4rem;
        padding-bottom: 2.5rem;
    }
    h1, h2, h3 {
        letter-spacing: 0;
    }
    .app-title {
        font-size: 30px;
        line-height: 1.2;
        font-weight: 760;
        color: #17212b;
        margin-bottom: 4px;
    }
    .app-subtitle {
        font-size: 14px;
        color: #63707d;
        margin-bottom: 18px;
    }
    .kpi {
        min-height: 100px;
        padding: 16px 18px;
        border: 1px solid #e1e5e9;
        border-radius: 8px;
        background: #ffffff;
    }
    .kpi-label {
        font-size: 13px;
        color: #68737f;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-size: 28px;
        line-height: 1;
        font-weight: 760;
        color: #17212b;
    }
    .kpi-note {
        margin-top: 8px;
        font-size: 12px;
        color: #7c8792;
    }
    .type-badge {
        display: inline-block;
        min-width: 54px;
        text-align: center;
        padding: 5px 10px;
        margin-right: 6px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 650;
    }
    .detail-card {
        border: 1px solid #e1e5e9;
        border-radius: 8px;
        background: #ffffff;
        padding: 20px;
        min-height: 100%;
    }
    .detail-eyebrow {
        font-size: 12px;
        color: #75808b;
        letter-spacing: 0;
        margin-bottom: 6px;
    }
    .detail-title {
        font-size: 27px;
        font-weight: 760;
        color: #17212b;
        margin-bottom: 10px;
    }
    .detail-meta {
        font-size: 13px;
        color: #5e6b77;
        margin-top: 12px;
        line-height: 1.8;
    }
    .stat-row {
        display: grid;
        grid-template-columns: 46px 1fr 40px;
        gap: 10px;
        align-items: center;
        margin: 9px 0;
        font-size: 13px;
        color: #34414d;
    }
    .stat-track {
        height: 8px;
        border-radius: 999px;
        background: #e9edf0;
        overflow: hidden;
    }
    .stat-fill {
        height: 100%;
        border-radius: 999px;
        background: #4e79a7;
    }
    .section-note {
        color: #66727e;
        font-size: 13px;
        margin: 2px 0 10px 0;
    }
    div[data-testid="stDataFrame"] {
        border: 1px solid #e1e5e9;
        border-radius: 8px;
        overflow: hidden;
    }
    @media (max-width: 700px) {
        .app-title {
            font-size: 26px;
        }
        .kpi {
            min-height: 88px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    species = pd.read_csv(DATA_DIR / "pokemon_clean.csv")
    forms = pd.read_csv(DATA_DIR / "forms_clean.csv")
    quality = json.loads((DATA_DIR / "data_quality.json").read_text(encoding="utf-8"))

    for column in ("is_legendary", "is_mythical"):
        species[column] = species[column].astype(str).str.lower().eq("true")

    numeric_columns = STAT_COLUMNS + [
        "total_stats",
        "height_m",
        "weight_kg",
        "capture_rate",
        "base_happiness",
        "dex_number",
        "generation_order",
    ]
    for column in numeric_columns:
        if column in species:
            species[column] = pd.to_numeric(species[column], errors="coerce")

    species["type2_zh"] = species["type2_zh"].fillna("")
    forms["type2_zh"] = forms["type2_zh"].fillna("")
    species["region_cn"] = pd.Categorical(
        species["region_cn"], categories=REGION_ORDER, ordered=True
    )
    forms["form_region_cn"] = pd.Categorical(
        forms["form_region_cn"], categories=FORM_REGION_ORDER, ordered=True
    )
    return species, forms, quality


def style_figure(fig: go.Figure, height: int = 420) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Microsoft YaHei, Noto Sans CJK SC, sans-serif",
            size=13,
            color="#24313b",
        ),
        legend_title_text="",
        hoverlabel=dict(
            bgcolor="#ffffff",
            font=dict(
                family="Microsoft YaHei, Noto Sans CJK SC, sans-serif",
                size=12,
            ),
        ),
    )
    fig.update_xaxes(gridcolor="#e8ecef", zerolinecolor="#e8ecef")
    fig.update_yaxes(gridcolor="#e8ecef", zerolinecolor="#e8ecef")
    return fig


def type_badge(type_name: str) -> str:
    if not type_name:
        return ""
    color = TYPE_COLORS.get(type_name, "#788491")
    text_color = "#17212b" if type_name in LIGHT_TYPE_COLORS else "#ffffff"
    return (
        f'<span class="type-badge" style="background:{color};color:{text_color}">'
        f"{type_name}</span>"
    )


def kpi_row(items: list[tuple[str, str, str]]) -> None:
    columns = st.columns(len(items))
    for column, (label, value, note) in zip(columns, items):
        column.markdown(
            f"""
            <div class="kpi">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-note">{note}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def stat_bar(label: str, value: int) -> str:
    width = min(max(float(value) / 180 * 100, 2), 100)
    return (
        '<div class="stat-row">'
        f"<span>{label}</span>"
        '<div class="stat-track">'
        f'<div class="stat-fill" style="width:{width:.1f}%"></div>'
        "</div>"
        f"<strong>{value}</strong>"
        "</div>"
    )


def check_required_files() -> None:
    required = [
        DATA_DIR / "pokemon_clean.csv",
        DATA_DIR / "forms_clean.csv",
        DATA_DIR / "data_quality.json",
    ]
    missing = [path.name for path in required if not path.exists()]
    if missing:
        st.error(f"缺少数据文件：{', '.join(missing)}")
        st.stop()


check_required_files()
species_df, forms_df, quality = load_data()

st.markdown('<div class="app-title">宝可梦图鉴数据分析</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-subtitle">基于公开图鉴 API 的物种结构、属性分布与能力差异</div>',
    unsafe_allow_html=True,
)

st.sidebar.markdown("### 筛选条件")
selected_regions = st.sidebar.multiselect(
    "地区",
    REGION_ORDER,
    default=REGION_ORDER,
)
selected_types = st.sidebar.multiselect(
    "属性",
    TYPE_ORDER,
    default=TYPE_ORDER,
)
legend_mode = st.sidebar.radio(
    "传说状态",
    ["全部", "仅传说与幻之", "排除传说与幻之"],
    horizontal=False,
)
min_total = int(species_df["total_stats"].min())
max_total = int(species_df["total_stats"].max())
total_range = st.sidebar.slider(
    "总种族值范围",
    min_value=min_total,
    max_value=max_total,
    value=(min_total, max_total),
    step=10,
)
keyword = st.sidebar.text_input("名称搜索", placeholder="例如：皮卡丘")

if not selected_regions:
    st.warning("请至少选择一个地区。")
    st.stop()
if not selected_types:
    st.warning("请至少选择一种属性。")
    st.stop()

mask = species_df["region_cn"].isin(selected_regions)
mask &= species_df["total_stats"].between(total_range[0], total_range[1])
mask &= (
    species_df["type1_zh"].isin(selected_types)
    | species_df["type2_zh"].isin(selected_types)
)

if legend_mode == "仅传说与幻之":
    mask &= species_df["is_legendary"] | species_df["is_mythical"]
elif legend_mode == "排除传说与幻之":
    mask &= ~(species_df["is_legendary"] | species_df["is_mythical"])

if keyword.strip():
    term = keyword.strip()
    mask &= species_df["name_zh"].str.contains(term, case=False, na=False) | species_df[
        "name_en"
    ].str.contains(term, case=False, na=False)

filtered = species_df.loc[mask].sort_values(["generation_order", "species_id"])
if filtered.empty:
    st.warning("当前筛选条件下没有匹配数据。")
    st.stop()

region_in_view = [region for region in REGION_ORDER if region in set(filtered["region_cn"])]
legendary_count = int((filtered["is_legendary"] | filtered["is_mythical"]).sum())
form_region_scope = set(selected_regions)
if "神奥" in form_region_scope:
    form_region_scope.add("洗翠")
forms_in_view = forms_df[forms_df["form_region_cn"].isin(form_region_scope)]

st.caption(
    f"数据来源：PokeAPI API v2　|　物种记录 {quality['species_rows']:,} 条　|　"
    f"地区形态 {quality['regional_form_rows']} 条"
)

kpi_row(
    [
        ("当前物种", f"{len(filtered):,}", f"覆盖 {len(region_in_view)} 个地区"),
        ("平均总种族值", f"{filtered['total_stats'].mean():.0f}", "当前筛选结果"),
        ("传说与幻之", f"{legendary_count:,}", "包含传说和幻之记录"),
        ("地区形态", f"{len(forms_in_view):,}", "当前地区范围内"),
    ]
)

download_csv = filtered.to_csv(index=False).encode("utf-8-sig")
st.sidebar.download_button(
    "下载当前筛选结果",
    data=download_csv,
    file_name="filtered_pokedex.csv",
    mime="text/csv",
    use_container_width=True,
)

tab_region, tab_types, tab_detail, tab_data = st.tabs(
    ["地区总览", "属性结构", "图鉴明细", "数据质量"]
)

with tab_region:
    left, right = st.columns([1.12, 1])

    region_counts = (
        filtered.groupby("region_cn", observed=True)
        .size()
        .reindex(region_in_view)
        .reset_index(name="物种数")
    )
    count_fig = px.bar(
        region_counts,
        x="region_cn",
        y="物种数",
        color="region_cn",
        color_discrete_map=REGION_COLORS,
        text="物种数",
        labels={"region_cn": "地区", "物种数": "新增物种数"},
        title="各地区新增物种数量",
    )
    count_fig.update_traces(textposition="outside", cliponaxis=False)
    count_fig.update_layout(showlegend=False)
    left.plotly_chart(
        style_figure(count_fig, 430),
        use_container_width=True,
        config={"displayModeBar": False},
    )

    region_means = (
        filtered.groupby("region_cn", observed=True)[STAT_COLUMNS]
        .mean()
        .reindex(region_in_view)
        .reset_index()
    )
    radar_fig = go.Figure()
    radar_labels = [STAT_LABELS[column] for column in STAT_COLUMNS]
    for index, row in region_means.iterrows():
        values = [float(row[column]) for column in STAT_COLUMNS]
        radar_fig.add_trace(
            go.Scatterpolar(
                r=values + [values[0]],
                theta=radar_labels + [radar_labels[0]],
                fill="toself",
                name=str(row["region_cn"]),
                line=dict(
                    color=REGION_COLORS.get(str(row["region_cn"]), "#4e79a7"),
                    width=2,
                ),
                opacity=0.72,
            )
        )
    radar_fig.update_layout(
        title="各地区平均能力结构",
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 130], gridcolor="#e6eaee"),
            angularaxis=dict(gridcolor="#e6eaee"),
        ),
    )
    right.plotly_chart(
        style_figure(radar_fig, 430),
        use_container_width=True,
        config={"displayModeBar": False},
    )

    box_fig = px.box(
        filtered,
        x="region_cn",
        y="total_stats",
        color="region_cn",
        color_discrete_map=REGION_COLORS,
        points="outliers",
        labels={"region_cn": "地区", "total_stats": "总种族值"},
        title="各地区总种族值分布",
    )
    box_fig.update_layout(showlegend=False)
    st.plotly_chart(
        style_figure(box_fig, 420),
        use_container_width=True,
        config={"displayModeBar": False},
    )

    top_region = (
        filtered.groupby("region_cn", observed=True)["total_stats"]
        .mean()
        .idxmax()
    )
    top_value = filtered.groupby("region_cn", observed=True)["total_stats"].mean().max()
    st.info(
        f"当前筛选下，{top_region}的平均总种族值最高，为 {top_value:.1f}。"
        "该指标会受到传说、幻之及地区形态筛选的影响。"
    )

with tab_types:
    type_rows = pd.concat(
        [
            filtered[["region_cn", "type1_zh"]].rename(columns={"type1_zh": "type_cn"}),
            filtered[["region_cn", "type2_zh"]].rename(columns={"type2_zh": "type_cn"}),
        ],
        ignore_index=True,
    )
    type_rows["region_cn"] = type_rows["region_cn"].astype(str)
    type_rows = type_rows[type_rows["type_cn"].isin(TYPE_ORDER)]

    matrix = (
        type_rows.groupby(["region_cn", "type_cn"])
        .size()
        .unstack(fill_value=0)
        .reindex(region_in_view, fill_value=0)
        .reindex(columns=selected_types, fill_value=0)
    )
    heatmap_fig = px.imshow(
        matrix,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="YlGnBu",
        labels={"x": "属性", "y": "地区", "color": "数量"},
        title="地区与属性分布矩阵",
    )
    st.plotly_chart(
        style_figure(heatmap_fig, 440),
        use_container_width=True,
        config={"displayModeBar": False},
    )

    left, right = st.columns([0.9, 1.25])
    type_counts = (
        type_rows["type_cn"]
        .value_counts()
        .reindex(TYPE_ORDER)
        .dropna()
        .reset_index()
    )
    type_counts.columns = ["type_cn", "count"]
    type_counts = type_counts.sort_values("count")
    type_fig = go.Figure(
        go.Bar(
            x=type_counts["count"],
            y=type_counts["type_cn"],
            orientation="h",
            marker_color=[TYPE_COLORS.get(value, "#788491") for value in type_counts["type_cn"]],
            text=type_counts["count"],
            textposition="outside",
        )
    )
    type_fig.update_layout(
        title="属性出现频次",
        xaxis_title="数量",
        yaxis_title="",
        showlegend=False,
    )
    left.plotly_chart(
        style_figure(type_fig, 460),
        use_container_width=True,
        config={"displayModeBar": False},
    )

    scatter_fig = px.scatter(
        filtered,
        x="attack",
        y="speed",
        color="region_cn",
        size="total_stats",
        size_max=20,
        color_discrete_map=REGION_COLORS,
        hover_name="name_zh",
        hover_data={
            "type1_zh": True,
            "type2_zh": True,
            "total_stats": True,
            "attack": False,
            "speed": False,
        },
        labels={
            "attack": "攻击",
            "speed": "速度",
            "region_cn": "地区",
            "type1_zh": "属性一",
            "type2_zh": "属性二",
            "total_stats": "总种族值",
        },
        title="攻击与速度关系",
    )
    scatter_fig.update_traces(
        marker=dict(line=dict(width=0.5, color="white"), opacity=0.72)
    )
    right.plotly_chart(
        style_figure(scatter_fig, 460),
        use_container_width=True,
        config={"displayModeBar": False},
    )

with tab_detail:
    name_options = filtered.sort_values(["generation_order", "species_id"])[
        "name_zh"
    ].tolist()
    selected_name = st.selectbox("选择图鉴条目", name_options)
    selected_rows = filtered[filtered["name_zh"] == selected_name]
    row = selected_rows.iloc[0]

    detail_left, detail_right = st.columns([1.05, 1])
    badges = type_badge(str(row["type1_zh"])) + type_badge(str(row["type2_zh"]))
    detail_left.markdown(
        f"""
        <div class="detail-card">
            <div class="detail-eyebrow">
                No.{int(row["dex_number"]):04d} · {row["generation_cn"]} · {row["region_cn"]}
            </div>
            <div class="detail-title">{row["name_zh"]}</div>
            <div>{badges}</div>
            <div class="detail-meta">
                总种族值：<strong>{int(row["total_stats"])}</strong><br>
                身高：{row["height_m"]:.1f} m　体重：{row["weight_kg"]:.1f} kg<br>
                特性：{row["abilities"] or "暂无"}<br>
                隐藏特性：{row["hidden_ability"] or "暂无"}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    stat_html = "".join(
        stat_bar(STAT_LABELS[column], int(row[column])) for column in STAT_COLUMNS
    )
    detail_right.markdown(
        f"""
        <div class="detail-card">
            <div class="detail-eyebrow">能力值结构</div>
            <div style="height:10px"></div>
            {stat_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

    related_forms = forms_df[forms_df["species_id"] == row["species_id"]]
    if not related_forms.empty:
        st.markdown("#### 地区形态")
        form_columns = st.columns(min(len(related_forms), 4))
        for index, (_, form) in enumerate(related_forms.iterrows()):
            column = form_columns[index % len(form_columns)]
            form_badges = type_badge(str(form["type1_zh"])) + type_badge(
                str(form["type2_zh"])
            )
            column.markdown(
                f"""
                <div class="detail-card">
                    <div class="detail-eyebrow">{form["form_region_cn"]}形态</div>
                    <div style="font-size:19px;font-weight:720;color:#17212b;margin-bottom:8px">
                        {form["form_name_zh"]}
                    </div>
                    <div>{form_badges}</div>
                    <div class="detail-meta">
                        总种族值：<strong>{int(form["total_stats"])}</strong>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    table = filtered[
        [
            "dex_number",
            "name_zh",
            "region_cn",
            "type1_zh",
            "type2_zh",
            "total_stats",
            "hp",
            "attack",
            "defense",
            "special_attack",
            "special_defense",
            "speed",
            "is_legendary",
            "is_mythical",
        ]
    ].copy()
    table["dex_number"] = table["dex_number"].map(lambda value: f"#{int(value):04d}")
    table["region_cn"] = table["region_cn"].astype(str)
    table = table.rename(
        columns={
            "dex_number": "图鉴编号",
            "name_zh": "名称",
            "region_cn": "地区",
            "type1_zh": "属性一",
            "type2_zh": "属性二",
            "total_stats": "总种族值",
            "hp": "HP",
            "attack": "攻击",
            "defense": "防御",
            "special_attack": "特攻",
            "special_defense": "特防",
            "speed": "速度",
            "is_legendary": "传说",
            "is_mythical": "幻之",
        }
    )
    st.dataframe(table, hide_index=True, use_container_width=True, height=420)

with tab_data:
    kpi_row(
        [
            ("物种记录", f"{quality['species_rows']:,}", "基础物种"),
            ("地区形态", f"{quality['regional_form_rows']:,}", "独立记录"),
            ("重复编号", f"{quality['duplicate_species_ids']:,}", "物种 ID"),
            ("采集失败", f"{quality['failed_species_count']:,}", "本次完整采集"),
        ]
    )

    data_left, data_right = st.columns([1, 1])
    with data_left:
        st.markdown("#### 数据来源与采集")
        collected_at = quality.get("collected_at_utc", "").replace("T", " ")[:19]
        st.markdown(
            f"""
            - 数据源：`{quality.get("api_root", "PokeAPI")}`
            - 采集时间：{collected_at} UTC
            - 网络请求：{quality.get("net_api_requests_this_run", 0):,} 次
            - 缓存目录：`raw/`
            - 地区覆盖：{len(quality.get("regions", {}))} 个
            """
        )
        missing_table = pd.DataFrame(
            list(quality.get("missing_counts", {}).items()),
            columns=["字段", "缺失数量"],
        )
        st.dataframe(missing_table, hide_index=True, use_container_width=True, height=260)

    with data_right:
        st.markdown("#### 地区形态数量")
        forms_count = (
            forms_df.groupby("form_region_cn", observed=True)
            .size()
            .reindex(FORM_REGION_ORDER, fill_value=0)
            .reset_index(name="数量")
        )
        forms_fig = px.bar(
            forms_count,
            x="form_region_cn",
            y="数量",
            text="数量",
            color="form_region_cn",
            color_discrete_map={
                "阿罗拉": "#EDC948",
                "伽勒尔": "#9C755F",
                "洗翠": "#7B61A8",
                "帕底亚": "#D685AD",
            },
            labels={"form_region_cn": "形态地区", "数量": "记录数"},
        )
        forms_fig.update_layout(showlegend=False)
        st.plotly_chart(
            style_figure(forms_fig, 320),
            use_container_width=True,
            config={"displayModeBar": False},
        )

    st.markdown("#### 数据样例")
    sample = species_df[
        [
            "dex_number",
            "name_zh",
            "region_cn",
            "type1_zh",
            "type2_zh",
            "total_stats",
            "is_legendary",
            "is_mythical",
        ]
    ].head(20).copy()
    sample["region_cn"] = sample["region_cn"].astype(str)
    sample = sample.rename(
        columns={
            "dex_number": "图鉴编号",
            "name_zh": "名称",
            "region_cn": "地区",
            "type1_zh": "属性一",
            "type2_zh": "属性二",
            "total_stats": "总种族值",
            "is_legendary": "传说",
            "is_mythical": "幻之",
        }
    )
    st.dataframe(sample, hide_index=True, use_container_width=True)

st.divider()
st.caption(
    "数据来源：PokeAPI API v2。本项目仅用于课程学习与数据分析展示，"
    "不使用官方图片、图标或游戏素材。相关名称与数据权利归原权利人所有。"
)

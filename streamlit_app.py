# -*- coding: utf-8 -*-
"""
Olist 电商多模态智能分析（OMMA）—— Streamlit 可视化看板
==========================================================
模式一：🖥️ 科技大屏（默认）—— ECharts 深蓝科技风数据大屏
    - 8 项核心 KPI、月度销售趋势、热销品类、巴西州级地图（指标切换）、
      支付方式、RFM 分群、评分分布、订单状态、配送时效
模式二：详细分析（原 6 大模块）
    1. 总览     —— 核心 KPI 与月度销售趋势
    2. 地理分析 —— 州级客户/订单/销售额/评分/时效 choropleth
    3. 商品分析 —— 热销品类、价格与运费
    4. 支付分析 —— 支付方式、分期与金额
    5. 评分评论 —— 评分分布、评分与配送时效
    6. 客户价值 —— RFM 用户分群与价值分层

运行方式：
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    streamlit run streamlit_app.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit.components.v1 import html as st_html

from config import RAW_DATA_DIR, GEOJSON_PATH
from scripts.dashboard_html import render_dashboard_html

# ---------------- 页面配置 ----------------
st.set_page_config(
    page_title="Olist 电商多模态智能分析",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------- 品牌与配色 ----------------
# 巴西电商主题色（青蓝 → 翠绿 → 靛蓝）
PRIMARY = "#0f172a"
ACCENT = "#0ea5e9"
COLORS = ["#0ea5e9", "#10b981", "#6366f1", "#f59e0b", "#ef4444", "#8b5cf6", "#14b8a6", "#f97316"]
COLOR_SCALES = {
    "map": "Viridis",
    "sales": "Blues",
    "score": "RdYlGn",
    "value": "Plasma",
}

# 各模块 Hero 文案
HERO = {
    "🖥️ 科技大屏": ("🖥️ Olist 电商数据大屏", "ECharts 科技风大屏 · 订单 / 地理 / 支付 / 客户价值一站式总览"),
    "📊 总览": ("📊 全局业务总览", "订单、客户、销售额与物流时效核心指标一览"),
    "🗺️ 地理分析": ("🗺️ 巴西地理洞察", "州级客户分布、销售额、评分与配送时效"),
    "📦 商品分析": ("📦 商品与品类洞察", "热销品类、价格与运费分布"),
    "💳 支付分析": ("💳 支付行为分析", "支付方式、分期与金额结构"),
    "⭐ 评分与评论": ("⭐ 评分与评论洞察", "评分分布、评分与配送时效关系"),
    "👤 客户价值": ("👤 客户价值分层", "RFM 用户分群与价值贡献"),
}


# ---------------- 全局 CSS 注入 ----------------
def inject_css():
    st.markdown(
        """
        <style>
        /* ===== 全局背景与布局 ===== */
        .stApp {
            background: linear-gradient(160deg, #f8fafc 0%, #eef2ff 55%, #f0fdf4 100%);
        }
        .block-container {
            padding-top: 1.8rem;
            padding-bottom: 3rem;
            max-width: 1400px;
        }
        #MainMenu, footer { visibility: hidden; }

        /* ===== 侧边栏（深色渐变）===== */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f172a 0%, #1e3a8a 100%);
            border-right: none;
        }
        section[data-testid="stSidebar"] * { color: #e2e8f0; }
        section[data-testid="stSidebar"] .stRadio label {
            padding: .55rem .85rem;
            border-radius: 10px;
            transition: background .18s ease;
        }
        section[data-testid="stSidebar"] .stRadio label:hover {
            background: rgba(255, 255, 255, .08);
        }
        section[data-testid="stSidebar"] .stRadio label:has(input:checked) {
            background: rgba(255, 255, 255, .14);
            border-left: 3px solid #38bdf8;
            font-weight: 600;
        }

        /* ===== Hero 页头 ===== */
        .hero {
            padding: 1.7rem 2rem;
            border-radius: 20px;
            margin-bottom: 1.6rem;
            background: linear-gradient(120deg, #0f172a 0%, #1e40af 55%, #0e7490 100%);
            box-shadow: 0 10px 30px rgba(15, 23, 42, .25);
            color: #fff;
        }
        .hero-badge {
            display: inline-block;
            font-size: .78rem;
            letter-spacing: .08em;
            padding: .22rem .85rem;
            border: 1px solid rgba(186, 230, 253, .45);
            border-radius: 999px;
            margin-bottom: .65rem;
            color: #bae6fd;
        }
        .hero-title { font-size: 1.85rem; font-weight: 700; margin: 0 0 .35rem; }
        .hero-sub { font-size: .95rem; color: #cbd5e1; margin: 0; }

        /* ===== KPI 卡片 ===== */
        .kpi-card {
            border-radius: 16px;
            padding: 1.05rem 1.25rem;
            color: #fff;
            box-shadow: 0 6px 18px rgba(15, 23, 42, .14);
            position: relative;
            overflow: hidden;
            min-height: 118px;
        }
        .kpi-card::after {
            content: "";
            position: absolute;
            right: -24px;
            top: -24px;
            width: 90px;
            height: 90px;
            border-radius: 50%;
            background: rgba(255, 255, 255, .12);
        }
        .kpi-icon { font-size: 1.55rem; opacity: .95; }
        .kpi-value { font-size: 1.5rem; font-weight: 700; margin: .25rem 0 .1rem; line-height: 1.1; }
        .kpi-label { font-size: .8rem; opacity: .92; }

        /* ===== 模块标题 ===== */
        .section-title {
            font-size: 1.22rem;
            font-weight: 700;
            color: #0f172a;
            margin: 1.1rem 0 .8rem;
            padding-left: .75rem;
            border-left: 4px solid #0ea5e9;
        }

        /* ===== 图表容器 ===== */
        div[data-testid="stPlotlyChart"] { border-radius: 14px; }
        .stPlotlyChart { background: #fff; border-radius: 14px;
            box-shadow: 0 2px 12px rgba(15, 23, 42, .06); padding: .4rem; }

        /* ===== 数据表 ===== */
        div[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }

        /* ===== 下载/按钮 ===== */
        .stDownloadButton button, .stButton button {
            border-radius: 10px;
            border: none;
            background: linear-gradient(135deg, #0ea5e9, #6366f1);
            color: #fff;
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------- 通用 UI 组件 ----------------
def hero(title, subtitle):
    """渐变 Hero 页头。"""
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-badge">🛒 OMMA · Olist Multi-Modal E-Commerce Analytics</div>
            <div class="hero-title">{title}</div>
            <div class="hero-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_row(items):
    """渲染一行 KPI 卡片。items: [(label, value, icon, gradient), ...]"""
    cols = st.columns(len(items))
    for col, (label, value, icon, grad) in zip(cols, items):
        col.markdown(
            f"""
            <div class="kpi-card" style="background: linear-gradient(135deg, {grad[0]}, {grad[1]});">
                <div class="kpi-icon">{icon}</div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-label">{label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def section_title(text):
    st.markdown(f'<div class="section-title">{text}</div>', unsafe_allow_html=True)


def apply_layout(fig, height=420, **kwargs):
    """统一 Plotly 图表风格。调用方可覆盖默认 margin 等参数。"""
    margin = kwargs.pop("margin", dict(l=50, r=30, t=62, b=42))
    fig.update_layout(
        template="plotly_white",
        font=dict(family="Segoe UI, Microsoft YaHei, sans-serif", size=13, color="#334155"),
        title=dict(font=dict(size=16, color="#0f172a"), x=0.02, xanchor="left"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=margin,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=1, xanchor="right"),
        height=height,
        **kwargs,
    )
    fig.update_xaxes(gridcolor="rgba(148,163,184,.18)", zeroline=False)
    fig.update_yaxes(gridcolor="rgba(148,163,184,.18)", zeroline=False)
    return fig


def show_chart(fig, height=420, **kwargs):
    """统一渲染图表。"""
    fig = apply_layout(fig, height=height, **kwargs)
    st.plotly_chart(
        fig, use_container_width=True, config={"displayModeBar": False, "responsive": True}
    )


# ---------------- 工具函数 ----------------
def _read_csv(name: str, **kwargs) -> pd.DataFrame:
    """从标准原始数据目录读取 CSV，缺失时给出明确提示。"""
    path = RAW_DATA_DIR / name
    if not path.exists():
        raise FileNotFoundError(
            f"缺少数据文件：{path}\n请将 Olist 公开数据集放入 {RAW_DATA_DIR}/"
        )
    return pd.read_csv(path, **kwargs)


# ---------------- 数据加载（缓存） ----------------
@st.cache_data(show_spinner="正在加载 Olist 数据（首次约 20~40 秒）...")
def load_data() -> dict:
    orders = _read_csv(
        "olist_orders_dataset.csv",
        parse_dates=[
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ],
    )
    customers = _read_csv("olist_customers_dataset.csv")
    items = _read_csv("olist_order_items_dataset.csv")
    payments = _read_csv("olist_order_payments_dataset.csv")
    reviews = _read_csv("olist_order_reviews_dataset.csv")
    products = _read_csv("olist_products_dataset.csv")
    cat_trans = _read_csv("product_category_name_translation.csv")

    # ---- 订单级宽表：合并客户(州/城市/唯一客户)、销售额、运费、评分、配送天数 ----
    df = orders.merge(
        customers[
            ["customer_id", "customer_unique_id", "customer_state", "customer_city"]
        ],
        on="customer_id",
        how="left",
    )

    order_value = items.groupby("order_id", as_index=False)["price"].sum()
    df = df.merge(order_value, on="order_id", how="left")
    df["order_value"] = df["price"].fillna(0.0)

    order_freight = items.groupby("order_id", as_index=False)["freight_value"].sum()
    df = df.merge(order_freight, on="order_id", how="left")
    df["freight_value"] = df["freight_value"].fillna(0.0)

    order_score = reviews.groupby("order_id", as_index=False)["review_score"].mean()
    df = df.merge(order_score, on="order_id", how="left")

    df["delivery_days"] = (
        df["order_delivered_customer_date"] - df["order_purchase_timestamp"]
    ).dt.days

    # ---- 订单项级：商品品类（葡语 -> 英语翻译） ----
    item_cat = items.merge(
        products[["product_id", "product_category_name"]], on="product_id", how="left"
    )
    item_cat = item_cat.merge(cat_trans, on="product_category_name", how="left")
    item_cat["category"] = item_cat["product_category_name_english"].fillna(
        item_cat["product_category_name"]
    )

    return {
        "orders": orders,
        "customers": customers,
        "items": items,
        "payments": payments,
        "reviews": reviews,
        "products": products,
        "cat_trans": cat_trans,
        "df": df,
        "item_cat": item_cat,
    }


@st.cache_data(show_spinner=False)
def load_geojson() -> dict:
    with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(show_spinner=False)
def simplify_geojson(geojson: dict) -> dict:
    """精简 GeoJSON：仅保留州名/缩写，坐标降低精度，供大屏前端注册地图。"""
    out = {"type": geojson["type"], "features": []}
    for f in geojson["features"]:
        props = f["properties"]

        def _round_coords(obj):
            if isinstance(obj, list):
                return [_round_coords(x) for x in obj]
            return round(obj, 3)

        out["features"].append(
            {
                "type": f["type"],
                "properties": {"name": props["name"], "sigla": props["sigla"]},
                "geometry": {
                    "type": f["geometry"]["type"],
                    "coordinates": _round_coords(f["geometry"]["coordinates"]),
                },
            }
        )
    return out


@st.cache_data(show_spinner=False)
def compute_rfm(df: pd.DataFrame) -> pd.DataFrame:
    """基于订单数据计算 RFM 并分群（中位数二分法）。"""
    rfm = df.groupby("customer_id").agg(
        last_purchase=("order_purchase_timestamp", "max"),
        frequency=("order_id", "nunique"),
        monetary=("order_value", "sum"),
    )
    last_date = df["order_purchase_timestamp"].max()
    rfm["recency"] = (last_date - rfm["last_purchase"]).dt.days
    rfm = rfm.drop(columns=["last_purchase"])

    r_med = rfm["recency"].median()
    f_med = rfm["frequency"].median()
    m_med = rfm["monetary"].median()

    def _classify(row):
        r = row["recency"] <= r_med
        f = row["frequency"] > f_med
        m = row["monetary"] > m_med
        if r and f and m:
            return "重要价值用户"
        if r and m:
            return "重要保持用户"
        if r and f:
            return "重要发展用户"
        if r:
            return "重要挽留用户"
        if m:
            return "一般价值用户"
        if f:
            return "一般发展用户"
        if not (r or f or m):
            return "一般挽留用户"
        return "一般保持用户"

    rfm["segment"] = rfm.apply(_classify, axis=1)
    return rfm


@st.cache_data(show_spinner="正在聚合大屏数据...")
def build_dashboard_payload(d: dict) -> dict:
    """一次性聚合科技大屏所需全部数据（供前端 JSON 渲染）。"""
    df = d["df"]
    payments = d["payments"]
    reviews = d["reviews"]
    products = d["products"]
    item_cat = d["item_cat"]

    delivered = df[df["order_status"] == "delivered"]
    total_orders = int(df["order_id"].nunique())
    total_sales = float(df["order_value"].sum())
    avg_score = float(delivered["review_score"].mean())
    avg_delivery = float(delivered["delivery_days"].mean())

    orders_per_user = (
        df.groupby("customer_unique_id")["order_id"].nunique().reset_index()
    )
    repeat_rate = float((orders_per_user["order_id"] >= 2).mean())

    kpi = [
        {"label": "总订单数", "value": total_orders, "unit": "单", "icon": "🛒", "color": "#00e5ff", "decimals": 0},
        {"label": "唯一客户数", "value": int(df["customer_unique_id"].nunique()), "unit": "人", "icon": "👥", "color": "#3d7eff", "decimals": 0},
        {"label": "总销售额", "value": total_sales, "unit": "R$", "icon": "💰", "color": "#00ffa3", "decimals": 0},
        {"label": "平均客单价", "value": total_sales / total_orders, "unit": "R$", "icon": "🧾", "color": "#ffb020", "decimals": 2},
        {"label": "平均评分", "value": avg_score, "unit": "分", "icon": "⭐", "color": "#ff4d8f", "decimals": 2},
        {"label": "平均配送", "value": avg_delivery, "unit": "天", "icon": "🚚", "color": "#8b5cf6", "decimals": 1},
        {"label": "复购率", "value": repeat_rate * 100, "unit": "%", "icon": "🔁", "color": "#5eead4", "decimals": 1},
        {"label": "商品品类", "value": int(products["product_category_name"].nunique()), "unit": "类", "icon": "🏷️", "color": "#ff7a3d", "decimals": 0},
    ]

    # 月度趋势
    monthly = (
        df.set_index("order_purchase_timestamp")
        .resample("ME")
        .agg(orders=("order_id", "nunique"), sales=("order_value", "sum"))
        .reset_index()
    )
    monthly["month"] = monthly["order_purchase_timestamp"].dt.strftime("%Y-%m")

    # 品类 Top 10（按销量）
    cat_cnt = (
        item_cat.groupby("category")
        .agg(count=("order_item_id", "count"), sales=("price", "sum"))
        .reset_index()
    )
    cat_top = cat_cnt.nlargest(10, "count").sort_values("count")

    # 州级指标
    state = (
        df.groupby("customer_state")
        .agg(
            customers=("customer_unique_id", "nunique"),
            orders=("order_id", "nunique"),
            sales=("order_value", "sum"),
            score=("review_score", "mean"),
            delivery=("delivery_days", "mean"),
        )
        .reset_index()
        .rename(columns={"customer_state": "sigla"})
    )

    # 支付方式
    pay = (
        payments.groupby("payment_type")
        .agg(amount=("payment_value", "sum"), orders=("order_id", "nunique"))
        .reset_index()
        .sort_values("amount", ascending=False)
    )

    # RFM 分群（唯一客户口径）
    rfm = (
        df.groupby("customer_unique_id")
        .agg(
            last_purchase=("order_purchase_timestamp", "max"),
            frequency=("order_id", "nunique"),
            monetary=("order_value", "sum"),
        )
    )
    last_date = df["order_purchase_timestamp"].max()
    rfm["recency"] = (last_date - rfm["last_purchase"]).dt.days
    r_med, f_med, m_med = (
        rfm["recency"].median(),
        rfm["frequency"].median(),
        rfm["monetary"].median(),
    )

    def _seg(row):
        r = row["recency"] <= r_med
        f = row["frequency"] > f_med
        m = row["monetary"] > m_med
        if r and f and m:
            return "重要价值用户"
        if r and m:
            return "重要保持用户"
        if r and f:
            return "重要发展用户"
        if r:
            return "重要挽留用户"
        if m:
            return "一般价值用户"
        if f:
            return "一般发展用户"
        if not (r or f or m):
            return "一般挽留用户"
        return "一般保持用户"

    rfm["segment"] = rfm.apply(_seg, axis=1)
    seg_summary = (
        rfm.groupby("segment")
        .agg(count=("segment", "size"), money=("monetary", "mean"))
        .reset_index()
        .sort_values("count", ascending=False)
    )

    # 评分分布
    score_dist = (
        reviews["review_score"].value_counts().reindex([1, 2, 3, 4, 5], fill_value=0)
    )

    # 订单状态
    status = df["order_status"].value_counts().reset_index()
    status.columns = ["name", "count"]

    # 配送时效分组 + 平均评分
    dl = delivered[["delivery_days", "review_score"]].dropna()
    bins = [0, 5, 10, 15, 20, 30, 10_000]
    labels = ["0-5天", "6-10天", "11-15天", "16-20天", "21-30天", "30天+"]
    dl["range"] = pd.cut(dl["delivery_days"], bins=bins, labels=labels, right=True)
    dl_group = (
        dl.groupby("range", observed=True)
        .agg(count=("review_score", "size"), score=("review_score", "mean"))
        .reset_index()
    )
    dl_total = dl_group["count"].sum()
    delivery = [
        {"range": r, "ratio": round(c / dl_total * 100, 2), "score": round(s, 2)}
        for r, c, s in zip(dl_group["range"], dl_group["count"], dl_group["score"])
    ]

    return {
        "kpi": kpi,
        "monthly": {
            "months": monthly["month"].tolist(),
            "orders": monthly["orders"].astype(int).tolist(),
            "sales": monthly["sales"].round(0).tolist(),
        },
        "categories": [
            {"name": r["category"], "count": int(r["count"]), "sales": float(r["sales"])}
            for _, r in cat_top.iterrows()
        ],
        "states": [
            {
                "sigla": r["sigla"],
                "name": r["sigla"],
                "customers": int(r["customers"]),
                "orders": int(r["orders"]),
                "sales": float(r["sales"]),
                "score": float(r["score"]) if pd.notna(r["score"]) else None,
                "delivery": float(r["delivery"]) if pd.notna(r["delivery"]) else None,
            }
            for _, r in state.iterrows()
        ],
        "payments": [
            {"name": r["payment_type"], "amount": float(r["amount"]), "orders": int(r["orders"])}
            for _, r in pay.iterrows()
        ],
        "rfm": [
            {"name": r["segment"], "count": int(r["count"]), "money": float(r["money"])}
            for _, r in seg_summary.iterrows()
        ],
        "score": [
            {"name": str(i), "count": int(score_dist.loc[i])} for i in [1, 2, 3, 4, 5]
        ],
        "status": [{"name": r["name"], "count": int(r["count"])} for _, r in status.iterrows()],
        "delivery": delivery,
    }


# ============================================================
# 大屏：科技风 ECharts 数据大屏
# ============================================================
def render_dashboard(d):
    payload = build_dashboard_payload(d)
    geojson = simplify_geojson(load_geojson())
    html = render_dashboard_html(payload, geojson)
    st_html(html, height=1050, scrolling=True)


# ============================================================
# 模块 1：总览
# ============================================================
def render_overview(d):
    df = d["df"]
    delivered = df[df["order_status"] == "delivered"]

    kpi_row([
        ("总订单数", f"{len(df):,}", "📦", ("#0ea5e9", "#2563eb")),
        ("唯一客户数", f"{df['customer_id'].nunique():,}", "👥", ("#6366f1", "#8b5cf6")),
        ("总销售额 (R$)", f"{df['order_value'].sum():,.0f}", "💰", ("#10b981", "#059669")),
        ("平均客单价 (R$)", f"{df['order_value'].mean():.2f}", "🧾", ("#f59e0b", "#f97316")),
        ("平均评分", f"{delivered['review_score'].mean():.2f}", "⭐", ("#f43f5e", "#ef4444")),
        ("平均配送天数", f"{delivered['delivery_days'].mean():.1f}", "🚚", ("#14b8a6", "#0d9488")),
    ])

    section_title("趋势与结构")

    left, right = st.columns([2, 1])
    # 月度趋势：订单数与销售额
    trend = (
        df.set_index("order_purchase_timestamp")
        .resample("ME")
        .agg(orders=("order_id", "nunique"), sales=("order_value", "sum"))
        .reset_index()
    )
    trend["月份"] = trend["order_purchase_timestamp"].dt.strftime("%Y-%m")

    fig = go.Figure()
    fig.add_bar(x=trend["月份"], y=trend["orders"], name="订单数", marker_color=COLORS[0])
    fig.add_scatter(
        x=trend["月份"], y=trend["sales"], name="销售额 (R$)", yaxis="y2",
        line=dict(color=COLORS[1], width=3), mode="lines+markers",
    )
    fig.update_layout(
        title="月度订单数与销售额趋势",
        xaxis=dict(title="月份"),
        yaxis=dict(title="订单数"),
        yaxis2=dict(title="销售额 (R$)", overlaying="y", side="right"),
        hovermode="x unified",
    )
    show_chart(fig, height=430)

    # 订单状态分布
    status_counts = df["order_status"].value_counts().reset_index()
    status_counts.columns = ["订单状态", "数量"]
    fig2 = px.bar(
        status_counts, x="订单状态", y="数量", color="订单状态",
        color_discrete_sequence=COLORS, title="订单状态分布",
    )
    with right:
        show_chart(fig2, height=430)


# ============================================================
# 模块 2：地理分析
# ============================================================
def render_geo(d, geojson):
    df = d["df"]
    state = (
        df.groupby("customer_state")
        .agg(
            客户数=("customer_id", "nunique"),
            订单数=("order_id", "nunique"),
            销售额=("order_value", "sum"),
            平均评分=("review_score", "mean"),
            平均配送天数=("delivery_days", "mean"),
        )
        .reset_index()
        .rename(columns={"customer_state": "state"})
    )

    sigla2name = {
        f["properties"]["sigla"]: f["properties"]["name"] for f in geojson["features"]
    }
    state["州名"] = state["state"].map(sigla2name)

    section_title("州级指标分布")
    metric = st.selectbox(
        "选择地图指标",
        ["客户数", "订单数", "销售额", "平均评分", "平均配送天数"],
        index=0,
    )

    c1, c2 = st.columns([3, 2])
    fig = px.choropleth(
        state,
        geojson=geojson,
        locations="state",
        featureidkey="properties.sigla",
        color=metric,
        hover_name="州名",
        hover_data={"state": True, metric: ":.2f"},
        color_continuous_scale=COLOR_SCALES["map"],
        title=f"巴西各州{metric}分布",
    )
    fig.update_geos(fitbounds="locations", visible=False)
    with c1:
        show_chart(fig, height=560, margin=dict(l=10, r=10, t=60, b=10))

    top = state.nlargest(12, "销售额")[
        ["州名", "state", "客户数", "订单数", "销售额", "平均评分", "平均配送天数"]
    ]
    fig2 = px.bar(
        top.sort_values("销售额"),
        x="销售额", y="州名", orientation="h",
        color="销售额", color_continuous_scale=COLOR_SCALES["sales"],
        title="销售额 Top 12 州（R$）",
    )
    with c2:
        show_chart(fig2, height=560)

    with st.expander("查看各州明细数据", expanded=False):
        styled = state.sort_values("销售额", ascending=False).style.format(
            {"销售额": "{:,.0f}", "平均评分": "{:.2f}", "平均配送天数": "{:.1f}"}
        )
        st.dataframe(styled, use_container_width=True, hide_index=True)
        st.download_button(
            "⬇️ 下载州级明细 CSV",
            state.sort_values("销售额", ascending=False).to_csv(index=False).encode("utf-8-sig"),
            file_name="olist_state_summary.csv",
        )


# ============================================================
# 模块 3：商品分析
# ============================================================
def render_products(d):
    item_cat = d["item_cat"]

    section_title("品类结构与价格分布")
    top_n = st.slider("展示品类数量", 5, 20, 10)

    c1, c2 = st.columns(2)
    cat_cnt = (
        item_cat.groupby("category")
        .agg(销量=("order_item_id", "count"), 销售额=("price", "sum"))
        .reset_index()
    )
    fig = px.bar(
        cat_cnt.nlargest(top_n, "销量").sort_values("销量"),
        x="销量", y="category", orientation="h", color="销售额",
        color_continuous_scale=COLOR_SCALES["sales"], title=f"热销品类 Top {top_n}（按销量）",
    )
    with c1:
        show_chart(fig, height=520)

    fig2 = px.pie(
        cat_cnt.nlargest(top_n, "销售额"),
        names="category", values="销售额", title=f"品类销售额占比 Top {top_n}",
        hole=0.4, color_discrete_sequence=COLORS,
    )
    with c2:
        show_chart(fig2, height=520)

    price_cap = float(item_cat["price"].quantile(0.99))
    freight_cap = float(item_cat["freight_value"].quantile(0.99))
    p1, p2 = st.columns(2)
    fig3 = px.histogram(
        item_cat[item_cat["price"] <= price_cap],
        x="price", nbins=50, color_discrete_sequence=[COLORS[2]],
        title=f"商品价格分布（截断至 99 分位 {price_cap:.0f} R$）",
    )
    with p1:
        show_chart(fig3, height=380)

    fig4 = px.histogram(
        item_cat[item_cat["freight_value"] <= freight_cap],
        x="freight_value", nbins=50, color_discrete_sequence=[COLORS[3]],
        title=f"运费分布（截断至 99 分位 {freight_cap:.0f} R$）",
    )
    with p2:
        show_chart(fig4, height=380)


# ============================================================
# 模块 4：支付分析
# ============================================================
def render_payments(d):
    payments = d["payments"]

    section_title("支付方式与金额结构")
    c1, c2 = st.columns([3, 2])

    pay_type = (
        payments.groupby("payment_type")
        .agg(订单数=("order_id", "nunique"), 金额=("payment_value", "sum"))
        .reset_index()
        .sort_values("金额", ascending=False)
    )
    fig = px.pie(
        pay_type, names="payment_type", values="金额", hole=0.4,
        title="支付方式金额占比", color_discrete_sequence=COLORS,
    )
    with c1:
        show_chart(fig, height=440)

    with c2:
        styled = pay_type.copy()
        styled["占比"] = styled["金额"] / styled["金额"].sum() * 100
        styled = styled.style.format(
            {"金额": "{:,.0f}", "占比": "{:.1f}%"}
        )
        st.dataframe(styled, use_container_width=True, hide_index=True)

    credit = payments[payments["payment_type"] == "credit_card"]
    inst_cap = int(credit["payment_installments"].quantile(0.99))
    fig2 = px.histogram(
        credit[credit["payment_installments"] <= inst_cap],
        x="payment_installments", nbins=inst_cap, color_discrete_sequence=[COLORS[4]],
        title=f"信用卡分期数分布（截断至 99 分位 {inst_cap} 期）",
    )
    show_chart(fig2, height=380)


# ============================================================
# 模块 5：评分与评论
# ============================================================
def render_reviews(d):
    reviews = d["reviews"]
    df = d["df"]

    section_title("评分分布与影响因素")
    c1, c2 = st.columns(2)

    score_counts = reviews["review_score"].value_counts().sort_index().reset_index()
    score_counts.columns = ["评分", "数量"]
    fig = px.bar(
        score_counts, x="评分", y="数量", color="评分",
        color_continuous_scale=COLOR_SCALES["score"], text="数量", title="评分分布（1-5 分）",
    )
    with c1:
        show_chart(fig, height=420, showlegend=False)

    scored = df[["delivery_days", "review_score"]].dropna()
    day_cap = int(scored["delivery_days"].quantile(0.99))
    scored = scored[scored["delivery_days"] <= day_cap]
    scored["配送天数分组"] = pd.cut(scored["delivery_days"], bins=30).astype(str)
    group = (
        scored.groupby("配送天数分组", observed=True)
        .agg(平均评分=("review_score", "mean"), 订单数=("review_score", "size"))
        .reset_index()
    )
    fig2 = px.line(
        group, x="配送天数分组", y="平均评分", markers=True,
        title="平均评分随配送天数变化", color_discrete_sequence=[COLORS[1]],
    )
    with c2:
        show_chart(fig2, height=420)

    state_score = (
        df.groupby("customer_state")["review_score"].mean().sort_values(ascending=False)
    ).reset_index()
    state_score.columns = ["州", "平均评分"]
    fig3 = px.bar(
        state_score, x="州", y="平均评分", color="平均评分",
        color_continuous_scale=COLOR_SCALES["score"], title="各州平均评分",
    )
    show_chart(fig3, height=420)


# ============================================================
# 模块 6：客户价值（RFM）
# ============================================================
def render_rfm(d):
    df = d["df"]
    rfm = compute_rfm(df)

    kpi_row([
        ("客户总数", f"{len(rfm):,}", "👥", ("#6366f1", "#8b5cf6")),
        ("人均消费金额 (R$)", f"{rfm['monetary'].mean():.2f}", "💰", ("#10b981", "#059669")),
        ("人均下单次数", f"{rfm['frequency'].mean():.2f}", "🛍️", ("#f59e0b", "#f97316")),
    ])

    section_title("RFM 用户分群")
    seg_summary = (
        rfm.groupby("segment")
        .agg(客户数=("segment", "size"), 人均金额=("monetary", "mean"))
        .reset_index()
        .sort_values("客户数", ascending=False)
    )

    left, right = st.columns(2)
    fig = px.pie(
        seg_summary, names="segment", values="客户数", hole=0.4,
        title="用户分群占比", color_discrete_sequence=COLORS,
    )
    with left:
        show_chart(fig, height=460)

    fig2 = px.bar(
        seg_summary.sort_values("人均金额", ascending=False),
        x="客户数", y="segment", orientation="h", color="人均金额",
        color_continuous_scale=COLOR_SCALES["value"], title="分群客户数与人均金额",
    )
    with right:
        show_chart(fig2, height=460)

    with st.expander("查看 RFM 分群明细", expanded=False):
        st.dataframe(
            seg_summary.style.format({"人均金额": "{:,.2f}"}),
            use_container_width=True, hide_index=True,
        )
        st.download_button(
            "⬇️ 下载 RFM 分群 CSV",
            seg_summary.to_csv(index=False).encode("utf-8-sig"),
            file_name="olist_rfm_segments.csv",
        )


# ============================================================
# 主入口
# ============================================================
def main():
    inject_css()

    with st.sidebar:
        st.markdown(
            """
            <div style="text-align:center; padding:.6rem 0 1.1rem;">
                <div style="font-size:2.3rem;">🛒</div>
                <div style="font-size:1.12rem; font-weight:700; color:#fff;">Olist 多模态分析</div>
                <div style="font-size:.74rem; color:#94a3b8;">OMMA · Brazilian E-Commerce</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        menu = st.radio(
            "选择视图",
            ["🖥️ 科技大屏", "📊 总览", "🗺️ 地理分析", "📦 商品分析", "💳 支付分析", "⭐ 评分与评论", "👤 客户价值"],
        )
        if menu != "🖥️ 科技大屏":
            st.markdown("---")
            st.caption("提示：大屏为 ECharts 科技风视图，首次加载需联网获取 CDN。")
        st.markdown("---")
        st.caption("数据：Kaggle · Olist Brazilian E-Commerce")
        st.caption("分析仅供学习研究用途。")

    # Hero 页头（随模块切换）
    title, subtitle = HERO.get(menu, ("", ""))
    hero(title, subtitle)

    try:
        with st.spinner("加载数据中..."):
            d = load_data()
    except FileNotFoundError as e:
        st.error(str(e))
        st.stop()

    if menu == "🖥️ 科技大屏":
        try:
            render_dashboard(d)
        except FileNotFoundError as e:
            st.error(str(e))
        except Exception as e:
            st.warning(f"大屏渲染失败：{e}。可切换到下方详细分析模块。")
        return

    geojson = None
    if menu == "🗺️ 地理分析":
        try:
            geojson = load_geojson()
        except Exception:
            st.warning("未能加载巴西州界 GeoJSON，地理地图不可用。")

    if menu == "📊 总览":
        render_overview(d)
    elif menu == "🗺️ 地理分析":
        if geojson is None:
            st.info("缺少地理数据，请检查 data/brazi_gdp/brazil-states.geojson。")
        else:
            render_geo(d, geojson)
    elif menu == "📦 商品分析":
        render_products(d)
    elif menu == "💳 支付分析":
        render_payments(d)
    elif menu == "⭐ 评分与评论":
        render_reviews(d)
    elif menu == "👤 客户价值":
        render_rfm(d)


if __name__ == "__main__":
    main()

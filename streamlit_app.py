# -*- coding: utf-8 -*-
"""
Olist 电商多模态智能分析（OMMA）—— Streamlit 可视化看板
==========================================================
覆盖模块：
    1. 总览     —— 核心 KPI 与月度销售趋势
    2. 地理分析 —— 州级客户/订单/销售额/评分/时效 choropleth
    3. 商品分析 —— 热销品类、价格与运费
    4. 支付分析 —— 支付方式、分期与金额
    5. 评分评论 —— 评分分布、评分与配送时效
    6. 客户价值 —— RFM 用户分群与价值分层

运行方式：
    pip install -r requirements.txt
    streamlit run streamlit_app.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from config import RAW_DATA_DIR, GEOJSON_PATH

# ---------------- 页面配置 ----------------
st.set_page_config(
    page_title="Olist 电商多模态智能分析",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 统一品牌色板
COLORS = px.colors.qualitative.Plotly


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

    # ---- 订单级宽表：合并客户(州/城市)、销售额、运费、评分、配送天数 ----
    df = orders.merge(
        customers[["customer_id", "customer_state", "customer_city"]],
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
    item_cat = item_cat.merge(
        cat_trans, on="product_category_name", how="left"
    )
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


# ============================================================
# 模块 1：总览
# ============================================================
def render_overview(d):
    df = d["df"]
    delivered = df[df["order_status"] == "delivered"]

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("总订单数", f"{len(df):,}")
    c2.metric("唯一客户数", f"{df['customer_id'].nunique():,}")
    c3.metric("总销售额 (R$)", f"{df['order_value'].sum():,.0f}")
    c4.metric("平均客单价 (R$)", f"{df['order_value'].mean():.2f}")
    c5.metric("平均评分", f"{delivered['review_score'].mean():.2f}")
    c6.metric("平均配送天数", f"{delivered['delivery_days'].mean():.1f}")

    st.markdown("---")

    left, right = st.columns([2, 1])
    # 月度趋势：订单数与销售额
    trend = (
        df.set_index("order_purchase_timestamp")
        .resample("M")
        .agg(orders=("order_id", "nunique"), sales=("order_value", "sum"))
        .reset_index()
    )
    trend["月份"] = trend["order_purchase_timestamp"].dt.strftime("%Y-%m")

    fig = go.Figure()
    fig.add_bar(x=trend["月份"], y=trend["orders"], name="订单数", marker_color=COLORS[0])
    fig.add_scatter(
        x=trend["月份"], y=trend["sales"], name="销售额 (R$)", yaxis="y2",
        marker_color=COLORS[1], line=dict(width=3),
    )
    fig.update_layout(
        title="月度订单数与销售额趋势",
        xaxis=dict(title="月份"),
        yaxis=dict(title="订单数"),
        yaxis2=dict(title="销售额 (R$)", overlaying="y", side="right"),
        height=420, hovermode="x unified",
    )
    left.plotly_chart(fig, use_container_width=True)

    # 订单状态分布
    status_counts = df["order_status"].value_counts().reset_index()
    status_counts.columns = ["订单状态", "数量"]
    fig2 = px.bar(
        status_counts, x="订单状态", y="数量", color="订单状态",
        color_discrete_sequence=COLORS, title="订单状态分布",
    )
    fig2.update_layout(height=420)
    right.plotly_chart(fig2, use_container_width=True)


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
        color_continuous_scale="Viridis",
        title=f"巴西各州{metric}分布",
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(height=560, margin=dict(l=10, r=10, t=50, b=10))
    c1.plotly_chart(fig, use_container_width=True)

    top = state.nlargest(12, "销售额")[["州名", "state", "客户数", "订单数", "销售额", "平均评分", "平均配送天数"]]
    fig2 = px.bar(
        top.sort_values("销售额"),
        x="销售额", y="州名", orientation="h",
        color="销售额", color_continuous_scale="Viridis",
        title="销售额 Top 12 州（R$）",
    )
    fig2.update_layout(height=560)
    c2.plotly_chart(fig2, use_container_width=True)

    with st.expander("查看各州明细数据"):
        st.dataframe(
            state.sort_values("销售额", ascending=False).style.format(
                {"销售额": "{:,.0f}", "平均评分": "{:.2f}", "平均配送天数": "{:.1f}"}
            ),
            use_container_width=True,
        )


# ============================================================
# 模块 3：商品分析
# ============================================================
def render_products(d):
    item_cat = d["item_cat"]
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
        color_continuous_scale="Blues", title=f"热销品类 Top {top_n}（按销量）",
    )
    fig.update_layout(height=520)
    c1.plotly_chart(fig, use_container_width=True)

    # 品类销售额占比
    fig2 = px.pie(
        cat_cnt.nlargest(top_n, "销售额"),
        names="category", values="销售额", title=f"品类销售额占比 Top {top_n}",
        hole=0.4, color_discrete_sequence=COLORS,
    )
    fig2.update_layout(height=520)
    c2.plotly_chart(fig2, use_container_width=True)

    # 价格 / 运费分布
    st.markdown("---")
    price_cap = float(item_cat["price"].quantile(0.99))
    freight_cap = float(item_cat["freight_value"].quantile(0.99))
    p1, p2 = st.columns(2)
    fig3 = px.histogram(
        item_cat[item_cat["price"] <= price_cap],
        x="price", nbins=50, color_discrete_sequence=[COLORS[2]],
        title=f"商品价格分布（截断至 99 分位 {price_cap:.0f} R$）",
    )
    fig3.update_layout(height=380)
    p1.plotly_chart(fig3, use_container_width=True)

    fig4 = px.histogram(
        item_cat[item_cat["freight_value"] <= freight_cap],
        x="freight_value", nbins=50, color_discrete_sequence=[COLORS[3]],
        title=f"运费分布（截断至 99 分位 {freight_cap:.0f} R$）",
    )
    fig4.update_layout(height=380)
    p2.plotly_chart(fig4, use_container_width=True)


# ============================================================
# 模块 4：支付分析
# ============================================================
def render_payments(d):
    payments = d["payments"]
    c1, c2 = st.columns(2)

    # 支付方式金额占比
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
    fig.update_layout(height=440)
    c1.plotly_chart(fig, use_container_width=True)

    # 各支付方式汇总表
    c2.subheader("各支付方式汇总")
    c2.dataframe(
        pay_type.style.format({"金额": "{:,.0f}"}),
        use_container_width=True, hide_index=True,
    )

    # 分期数分布（信用卡）
    st.markdown("---")
    credit = payments[payments["payment_type"] == "credit_card"]
    inst_cap = int(credit["payment_installments"].quantile(0.99))
    fig2 = px.histogram(
        credit[credit["payment_installments"] <= inst_cap],
        x="payment_installments", nbins=inst_cap, color_discrete_sequence=[COLORS[4]],
        title=f"信用卡分期数分布（截断至 99 分位 {inst_cap} 期）",
    )
    fig2.update_layout(height=380)
    st.plotly_chart(fig2, use_container_width=True)


# ============================================================
# 模块 5：评分与评论
# ============================================================
def render_reviews(d):
    reviews = d["reviews"]
    df = d["df"]

    c1, c2 = st.columns(2)
    # 评分分布
    score_counts = reviews["review_score"].value_counts().sort_index().reset_index()
    score_counts.columns = ["评分", "数量"]
    fig = px.bar(
        score_counts, x="评分", y="数量", color="评分",
        color_continuous_scale="RdYlGn", text="数量", title="评分分布（1-5 分）",
    )
    fig.update_layout(height=420, showlegend=False)
    c1.plotly_chart(fig, use_container_width=True)

    # 评分 vs 配送天数
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
    fig2.update_layout(height=420, xaxis_title="配送天数分组")
    c2.plotly_chart(fig2, use_container_width=True)

    # 各州平均评分
    st.markdown("---")
    state_score = (
        df.groupby("customer_state")["review_score"].mean().sort_values(ascending=False)
    ).reset_index()
    state_score.columns = ["州", "平均评分"]
    fig3 = px.bar(
        state_score, x="州", y="平均评分", color="平均评分",
        color_continuous_scale="RdYlGn", title="各州平均评分",
    )
    fig3.update_layout(height=420)
    st.plotly_chart(fig3, use_container_width=True)


# ============================================================
# 模块 6：客户价值（RFM）
# ============================================================
def render_rfm(d):
    df = d["df"]
    rfm = compute_rfm(df)

    c1, c2, c3 = st.columns(3)
    c1.metric("客户总数", f"{len(rfm):,}")
    c2.metric("人均消费金额 (R$)", f"{rfm['monetary'].mean():.2f}")
    c3.metric("人均下单次数", f"{rfm['frequency'].mean():.2f}")

    st.markdown("---")

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
    fig.update_layout(height=460)
    left.plotly_chart(fig, use_container_width=True)

    fig2 = px.bar(
        seg_summary.sort_values("人均金额", ascending=False),
        x="客户数", y="segment", orientation="h", color="人均金额",
        color_continuous_scale="Plasma", title="分群客户数与人均金额",
    )
    fig2.update_layout(height=460)
    right.plotly_chart(fig2, use_container_width=True)

    with st.expander("查看 RFM 分群明细"):
        st.dataframe(
            seg_summary.style.format({"人均金额": "{:,.2f}"}),
            use_container_width=True, hide_index=True,
        )


# ============================================================
# 主入口
# ============================================================
def main():
    st.sidebar.title("🛒 Olist 电商多模态智能分析")
    st.sidebar.caption("OMMA · Brazilian E-Commerce Analytics")
    menu = st.sidebar.radio(
        "选择分析模块",
        ["📊 总览", "🗺️ 地理分析", "📦 商品分析", "💳 支付分析", "⭐ 评分与评论", "👤 客户价值"],
    )

    try:
        with st.spinner("加载数据中..."):
            d = load_data()
    except FileNotFoundError as e:
        st.error(str(e))
        st.stop()

    # 地理模块需要 GeoJSON
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

    st.sidebar.markdown("---")
    st.sidebar.caption(
        "数据来源：Kaggle — Brazilian E-Commerce Public Dataset by Olist\n"
        "分析仅供学习研究用途。"
    )


if __name__ == "__main__":
    main()

# 🛒 Olist 电商多模态智能分析（OMMA）

> **Olist Multi-Modal E-Commerce Analytics** · 基于巴西电商平台 Olist 公开数据集的多模态数据分析与建模项目
>
> 覆盖 **数据探索 · 地理空间 · 文本情感 · 评分预测 · 客户价值细分 · 生命周期价值预测 · 客户流失** 七大分析维度，融合统计挖掘、机器学习、深度学习与客户分析模型（RFM / K-Means / BTYD），是一套完整的跨境电商用户与运营分析。

---

## 📌 项目名说明

| 项目 | 命名 |
|------|------|
| 中文名（推荐） | **Olist 电商多模态智能分析** |
| 英文名 | **Olist Multi-Modal E-Commerce Analytics** |
| 缩写 | **OMMA** |
| 原工作目录名 | 9.跨境电商巴西Olist多模动态分析 |

> “多模态”体现在项目同时处理 **表格数据（订单/支付/商品）**、**文本数据（评论）**、**地理空间数据（邮编/经纬度）** 与 **时间序列（订单趋势）** 四类异构数据，并采用多种模型分别建模，最终统一服务于“用户价值与运营优化”这一业务目标。

---

## 🎯 项目简介

Olist 是巴西的一家新兴电子商务平台（创立于 2015 年），为巴西各地中小商家提供在线销售、客户支持与售后管理服务，已进驻 Walmart、Amazon、MercadoLivre、Americanas 等大型电商平台。

本项目以 Kaggle 上 Olist 发布的 **2016–2018 年约 10 万笔订单** 的公共数据集为分析对象，结合巴西 GDP 区域经济数据与州级 GeoJSON 地理数据，围绕**用户消费行为、客户价值与运营优化**展开全链路分析：

- 探索电商用户的基础画像与消费行为规律；
- 从地理维度洞察订单分布、物流时效、运费与区域经济差异；
- 基于文本评论与用户评分，构建情感分析与评分预测模型；
- 通过 RFM 与聚类进行客户价值细分；
- 基于 BTYD 模型预测客户生命周期价值（CLV）与存活概率；
- 分析客户流失并给出精细化运营建议。

---

## 🗂️ 数据说明

| 数据 | 来源 | 说明 |
|------|------|------|
| Olist 巴西电商公开数据集 | [Kaggle - Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) | 2016–2018 年约 10 万笔订单，含客户、卖家、商品、订单、支付、评论、地理定位 8 张关联表 |
| 巴西 GDP 数据 | IBGE / 公开统计 | 全国与各州 GDP，用于区域经济水平与消费能力关联分析 |
| 巴西州界 GeoJSON | 公开地理数据 | 用于 choropleth 分级统计地图与地理空间可视化 |

主要数据表（见 [`data/olist_public_dataset/`](data/olist_public_dataset/)）：

- `olist_customers_dataset.csv` — 客户信息（含邮编前缀、城市、州）
- `olist_geolocation_dataset.csv` — 邮编前缀对应的经纬度坐标
- `olist_order_items_dataset.csv` — 订单明细（商品、价格、运费、时效）
- `olist_order_payments_dataset.csv` — 支付方式与支付金额
- `olist_order_reviews_dataset.csv` — 评论评分与评论文本（葡语）
- `olist_orders_dataset.csv` — 订单主表（下单/批准/送达时间、状态）
- `olist_products_dataset.csv` — 商品信息（类别、尺寸、重量等）
- `olist_sellers_dataset.csv` — 卖家信息

> 各表通过 `order_id`、`customer_id`、`product_id`、`seller_id` 等唯一标识关联，整体 ER 关系见 [`export/exploration/Olist数据集关系图.png`](export/exploration/Olist数据集关系图.png)。

---

## 📊 分析模块总览

| # | 模块 | 文件 | 核心内容 | 关键方法 / 模型 |
|---|------|------|----------|-----------------|
| 1 | 基础数据探索 | [`2.基础数据探索.ipynb`](2.基础数据探索.ipynb) | 数据集概览、各州/城市客户分布、关系图、choropleth 地图 | MySQL 查询、Plotly、GeoJSON |
| 2 | 地理空间分析 | [`1.地理空间分析.ipynb`](1.地理空间分析.ipynb) | CEP 邮编体系、订单/收入/运费/配送时效/延迟的地域分布 | Holoviews、Datashader、folium、墨卡托投影 |
| 3 | 反馈评分预测 | [`3.反馈评分预测.ipynb`](3.反馈评分预测.ipynb) | 基于评论文本预测评分（好评/差评），多模型对比 | TF-IDF、朴素贝叶斯、SVM、LR、RF、XGBoost、**LSTM** |
| 4 | 客户价值细分 | [`4.客户价值细分.ipynb`](4.客户价值细分.ipynb) | RFM 分群、客户留存、新客比率、价值矩阵 | **RFM**、**K-Means** 聚类、RFM 分箱 |
| 5 | 客生价值预测 | [`5.客生价值预测.ipynb`](5.客生价值预测.ipynb) | 客户生命周期价值预测、存活概率、未来交易预测 | **BTYD：MBG/NBD + Gamma-Gamma**（lifetimes） |
| 6 | 评论情感分析 | [`6.评论情感分析.ipynb`](6.评论情感分析.ipynb) | 葡语评论情感分析、词云、正负面分布、时空热力图 | NLTK、WordCloud、分类模型、folium |
| 7 | 客户流失率 | [`data/客户流失率.ipynb`](data/客户流失率.ipynb) | 客户分层流失率、资源分配失衡、预算优化建议 | 分层分析、双轴可视化 |

> 另含一份完整消费行为分析报告：[`export/Olist/OlistReport.ipynb`](export/Olist/OlistReport.ipynb)（含 [PDF 版](export/Olist/OlistReport.pdf)），从消费趋势、用户画像、消费行为、复购回购、评分与时效关系到 RFM 用户分群，系统总结了 Olist 用户消费行为特点并给出运营建议。

---

## 🧰 技术栈

| 类别 | 技术 |
|------|------|
| 语言 / 环境 | Python 3.9 · Jupyter Notebook |
| 数据处理 | pandas · numpy · scipy |
| 数据可视化 | matplotlib · seaborn · plotly · folium · holoviews · datashader · bokeh |
| 机器学习 | scikit-learn · XGBoost · LightGBM |
| 深度学习 | TensorFlow 2.18 / Keras（LSTM） |
| 客户分析 | lifetimes（MBG/NBD、Gamma-Gamma） |
| 自然语言处理 | NLTK · WordCloud |
| 数据库 | MySQL（PyMySQL）· SQLAlchemy |
| 外部工具 | Tableau（消费行为报告可视化） |

完整依赖清单见 [`requirements.txt`](requirements.txt)。

---

## 📁 目录结构

```text
.
├── 1.地理空间分析.ipynb          # 地理空间分析
├── 2.基础数据探索.ipynb          # 基础数据探索
├── 3.反馈评分预测.ipynb          # 反馈评分预测（含 LSTM）
├── 4.客户价值细分.ipynb          # 客户价值细分（RFM + K-Means）
├── 5.客生价值预测.ipynb          # 客生价值（CLV）预测（BTYD）
├── 6.评论情感分析.ipynb          # 评论情感分析
├── streamlit_app.py              # Streamlit 可视化看板
├── config.py                     # 全局配置（数据路径 / 数据库连接）
├── .env.example                  # 环境变量模板（数据库凭据等）
├── requirements.txt              # Python 依赖清单
├── data/                         # 原始数据与中间数据
│   ├── 客户流失率.ipynb          # 客户流失率分析
│   ├── processed_orders.csv      # 处理后的订单数据
│   ├── basic_data/               # 基础数据（含 GeoJSON / GDP）
│   ├── olist_public_dataset/     # Olist 原始 8 张数据表
│   ├── Real GDP for Brazil/      # 巴西 GDP 数据
│   └── ...
├── export/                       # 全部输出成果（图表 / HTML / 报告）
│   ├── exploration/              # 探索分析图
│   ├── geospatial/               # 地理空间分析图
│   ├── feedback_rating/          # 评分预测成果
│   ├── lifetime_value/           # CLV 预测成果
│   ├── sentiment/                # 情感分析成果
│   ├── Olist/                    # 完整消费行为分析报告（ipynb/md/pdf）
│   └── Visual Dashboard/         # 可视化仪表板截图
└── scripts/                      # 可复用工具模块
    ├── ml_utils/                 # 机器学习工具（分类器分析、聚类等）
    ├── text_utils/               # 文本处理工具
    ├── viz_utils/                # 可视化工具
    ├── custom_transformers/      # 自定义 Transformer
    └── unittest.py               # 单元测试
```

---

## 🚀 快速开始

```bash
# 1. 创建虚拟环境（建议 Python 3.9）
python -m venv .venv

# Windows
.venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动 Jupyter
jupyter notebook

# 4. 启动 Streamlit 可视化看板（可选）
streamlit run streamlit_app.py
```

**Streamlit 可视化看板（[`streamlit_app.py`](streamlit_app.py)）**：一键式数据看板，含 6 个模块：

| 模块 | 功能 |
|------|------|
| 📊 总览 | 核心 KPI 与月度订单/销售趋势、订单状态分布 |
| 🗺️ 地理分析 | 巴西各州客户/订单/销售额/评分/时效 choropleth 地图 |
| 📦 商品分析 | 热销品类、品类销售额占比、价格与运费分布 |
| 💳 支付分析 | 支付方式占比、各支付方式金额、信用卡分期分布 |
| ⭐ 评分与评论 | 评分分布、评分随配送时效变化、各州平均评分 |
| 👤 客户价值 | RFM 用户分群（重要/一般价值等 8 类）与人均金额 |

> 首次运行约需 20~40 秒加载数据，之后自动缓存，切换页面即时响应。

**运行说明与注意事项：**

- **数据库配置（[`2.基础数据探索.ipynb`](2.基础数据探索.ipynb)）**：该 Notebook 从 MySQL `basic_data` 库读取数据，连接参数统一由 [`config.py`](config.py) 管理，通过项目根目录 `.env` 文件配置（模板见 [`.env.example`](.env.example)），代码中不再硬编码口令。
- **数据路径**：各 Notebook 统一通过 [`config.py`](config.py) 提供的数据路径常量（如 `GEOJSON_PATH`）引用，不再硬编码绝对路径；数据目录规范见 [`data/README.md`](data/README.md)。
- **[`6.评论情感分析.ipynb`](6.评论情感分析.ipynb)** 使用葡语停用词，需先执行 `nltk.download('stopwords')` 等资源下载。
- **[`3.反馈评分预测.ipynb`](3.反馈评分预测.ipynb)** 训练 LSTM 需要 TensorFlow，请按机器配置确认 GPU/CPU 版本。

---

## 📈 核心发现

1. **地域高度集中**：消费用户主要分布在东南部沿海人口密集、经济发达州，圣保罗州占比约 42%；北部/东北部运费更高、配送更慢、评分更低。
2. **二八法则显著**：约 17% 的头部大额用户贡献了 50% 的消费金额。
3. **低频小额消费**：97% 的用户仅消费一次，2017 年度复购率仅约 2.78%，用户忠诚度低、生命周期短。
4. **订单金额右长尾**：90% 的订单消费金额低于 300 雷亚尔，90% 的订单仅购买 1 件商品。
5. **评分两极分化**：约 58.86% 的用户评 5 分，但评分 ≤ 3 分占比达 21.44%，需结合文本情感进一步洞察。
6. **物流是瓶颈**：平均收货用时约 12.5 天，北部/东北部地区时效与运费问题突出，是运营优化重点。

---

## 💡 项目建议

### ✅ 已完成的工程化改进

- **清理硬编码路径与凭据**：[`2.基础数据探索.ipynb`](2.基础数据探索.ipynb) 的 MySQL 连接与 GeoJSON 绝对路径已迁移至 [`config.py`](config.py) + `.env`（模板见 [`.env.example`](.env.example)），代码中不再出现数据库口令与 `F:/...` 绝对路径。
- **标注随机示例代码**：[`4.客户价值细分.ipynb`](4.客户价值细分.ipynb) 中的 3D 曲面与等高线示意图已添加「方法示例」标注，明确其使用数学函数 + 随机噪声模拟，非真实订单数据。
- **补齐依赖清单**：[`requirements.txt`](requirements.txt) 已固定 `shap==0.46.0`、`tabulate==0.9.0`，移除“需补装”标注。
- **统一数据目录**：清理无关的 `data/data/MNIST/` 与冗余副本 `export/exploration/brazilian_ecommerce_dataset.csv`；新增 [`data/README.md`](data/README.md) 明确数据目录规范。

### 2. 分析增强（优先级：中）

- **统一指标体系**：将各 Notebook 的结论收敛为北极星指标 + 漏斗（曝光→下单→复购→留存），并把 RFM 分群映射到具体运营动作，形成可执行策略。
- **补充时间序列预测**：目前仅做趋势描述，可引入 Prophet / ARIMA / LSTM 对销售额与订单量做滚动预测与季节效应分解（黑五、年末大促）。
- **情感分析升级**：当前为二分类（正/负），可升级为 1–5 分多分类，或与评分预测模块统一建模；对葡语可用预训练模型（如 BERTimbau）提升效果。
- **地理分析深化**：结合时效与运费数据输出仓储选址 / 物流网络优化建议，量化北部地区改进后的收益预期。

### 3. 工程化交付（优先级：低）

- **建立评估与版本基准**：将 `scripts/unittest.py` 扩展为统一模型评估脚本，配合 MLflow 管理模型版本与指标。
- **流水线化**：把“数据 → 分析 → 可视化 → 报告”固化为可定时重跑的流水线（如 Airflow / cron），使 `export/` 输出可持续更新。
- **目录清理**：`data/data/MNIST/` 与电商分析无关，建议移出项目，减小仓库体积。

### 4. 合规与安全

- 数据库口令、API Key 一律不入库，改用环境变量注入。
- 数据仅用于学习与研究，请遵守 Olist 数据集与 Kaggle 的使用条款。

---

## 📚 参考

- [Kaggle：Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
- [Correios（巴西邮政）— CEP 邮编体系说明](https://www.correios.com.br/a-a-z/cep-codigo-de-enderecamento-postal)
- Olist 完整消费行为分析报告：[`export/Olist/OlistReport.md`](export/Olist/OlistReport.md)

---

> ⚠️ 本项目数据与分析结果仅用于学习研究用途，不代表任何商业平台的真实运营数据。

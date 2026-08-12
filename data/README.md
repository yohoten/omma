# 数据目录规范（Data Directory Guide）

本目录集中存放 Olist 电商多模态智能分析项目的全部数据，统一遵循以下规范，避免多份重复数据集造成版本混乱。

## 目录约定

| 目录 / 文件 | 定位 | 说明 |
|-------------|------|------|
| `olist_public_dataset/` | **Olist 原始公开数据集（标准来源）** | Kaggle 原始 8 张关联表 + 元数据，供各 Notebook 直接读取 |
| `basic_data/` | **处理后的基础数据** | 巴西州界 GeoJSON、GDP 数据、MySQL 导入用表等 |
| `Real GDP for Brazil/` | 巴西 GDP 原始数据 | 全国 / 州级 GDP CSV 与 JSON |
| `brazilian_ecommerce_dataset.csv` | 汇总导出 | 由 `2.基础数据探索.ipynb` 导出 |
| `processed_orders.csv` | 中间处理结果 | 订单预处理后的中间数据 |

## 使用规范

1. **数据只读**：`data/` 下为原始 / 中间数据，修改前请先备份。
2. **路径统一**：代码中禁止硬编码绝对路径，统一通过根目录 [`config.py`](../config.py) 提供的数据路径常量（`RAW_DATA_DIR` / `BASIC_DATA_DIR` / `GEOJSON_PATH` 等）引用。
3. **MySQL 导入**：[`2.基础数据探索.ipynb`](../2.基础数据探索.ipynb) 从 MySQL `basic_data` 库读取数据；连接参数通过 `.env` 配置（见根目录 [`.env.example`](../.env.example)），不再硬编码在代码中。
4. **避免重复**：新增数据请优先放入对应语义目录，避免在 `export/` 等位置产生冗余副本。

> 原始数据集来源：[Kaggle — Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

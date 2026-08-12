"""
Olist 电商多模态智能分析（OMMA）—— 全局配置模块
=================================================
集中管理数据库连接参数与常用数据路径，避免在各 Notebook 中硬编码。

敏感信息（数据库口令等）通过环境变量或 .env 文件提供：
    1. 复制 .env.example 为 .env，按需修改（config.py 会自动加载）
    2. 或在系统环境变量中设置 OLIST_DB_* 系列变量
未设置任何配置时使用下方默认值（与项目原始本地配置一致，便于快速复跑）。

依赖：仅使用标准库（pathlib / os），无需额外安装 python-dotenv。
"""
import os
from pathlib import Path

# ---- 项目根目录 ----
BASE_DIR = Path(__file__).resolve().parent

# ---- 简易 .env 解析（避免引入额外依赖 python-dotenv） ----
def _load_dotenv(path=None):
    dotenv_path = Path(path) if path else BASE_DIR / ".env"
    if not dotenv_path.exists():
        return
    with open(dotenv_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


_load_dotenv()

# ---- 数据目录 ----
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "olist_public_dataset"  # Olist 原始公开数据集（标准来源）
BASIC_DATA_DIR = DATA_DIR / "basic_data"          # 处理后的基础数据（GeoJSON / GDP 等）
GEOJSON_PATH = BASIC_DATA_DIR / "brazil-states.geojson"  # 巴西州界 GeoJSON

# ---- MySQL 连接参数（优先环境变量 / .env，其次默认值） ----
DB_HOST = os.getenv("OLIST_DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("OLIST_DB_PORT", "3306"))
DB_USER = os.getenv("OLIST_DB_USER", "root")
DB_PASSWORD = os.getenv("OLIST_DB_PASSWORD", "123456")
DB_NAME = os.getenv("OLIST_DB_NAME", "basic_data")


def get_mysql_connection():
    """创建 MySQL 连接（需要 pip install pymysql）。

    连接参数来自 config.py 统一管理（.env / 环境变量 / 默认值）。
    """
    import pymysql

    return pymysql.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        charset="utf8mb4",
    )

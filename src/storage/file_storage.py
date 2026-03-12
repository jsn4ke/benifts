"""文件存储实现"""

import csv
import json
import sqlite3
from pathlib import Path
from typing import List, Optional
import logging

from ..models.product import Product

logger = logging.getLogger(__name__)


class FileStorage:
    """文件存储类

    支持 CSV 和 SQLite 格式存储。
    """

    def __init__(self, data_dir: str = "data"):
        """初始化存储

        Args:
            data_dir: 数据目录路径
        """
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"

        # 创建目录
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def save_csv(self, products: List[Product], filename: str = "products.csv") -> Path:
        """保存产品到 CSV 文件

        Args:
            products: 产品列表
            filename: 输出文件名

        Returns:
            CSV 文件路径
        """
        filepath = self.processed_dir / filename

        if not products:
            logger.warning("No products to save")
            return filepath

        # 获取字段名
        fieldnames = list(products[0].to_dict().keys())

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows([p.to_dict() for p in products])

        logger.info(f"Saved {len(products)} products to {filepath}")
        return filepath

    def save_json(self, products: List[Product], filename: str = "products.json") -> Path:
        """保存产品到 JSON 文件

        Args:
            products: 产品列表
            filename: 输出文件名

        Returns:
            JSON 文件路径
        """
        filepath = self.processed_dir / filename

        data = [p.to_dict() for p in products]

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"Saved {len(products)} products to {filepath}")
        return filepath

    def save_sqlite(self, products: List[Product], db_file: str = "products.db") -> Path:
        """保存产品到 SQLite 数据库

        Args:
            products: 产品列表
            db_file: 数据库文件名

        Returns:
            数据库文件路径
        """
        filepath = self.data_dir / db_file

        conn = sqlite3.connect(filepath)
        cursor = conn.cursor()

        # 创建表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                code TEXT NOT NULL,
                bank TEXT NOT NULL,
                product_type TEXT,
                sale_type TEXT,
                fund_type TEXT,
                issuer TEXT,
                risk_level TEXT,
                status TEXT,
                net_value REAL,
                currency TEXT,
                min_amount REAL,
                investor_scope TEXT,
                fee_standard TEXT,
                fee_method TEXT,
                notice_url TEXT,
                filing_number TEXT,
                fetch_time TEXT,
                source TEXT
            )
        """)

        # 插入数据
        for product in products:
            data = product.to_dict()
            cursor.execute("""
                INSERT INTO products (
                    name, code, bank, product_type, sale_type, fund_type,
                    issuer, risk_level, status,
                    net_value, currency, min_amount, investor_scope,
                    fee_standard, fee_method, notice_url, filing_number,
                    fetch_time, source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data["name"],
                data["code"],
                data["bank"],
                data["product_type"],
                data["sale_type"],
                data["fund_type"],
                data["issuer"],
                data["risk_level"],
                data["status"],
                data["net_value"],
                data["currency"],
                data["min_amount"],
                data["investor_scope"],
                data["fee_standard"],
                data["fee_method"],
                data["notice_url"],
                data["filing_number"],
                data["fetch_time"],
                data["source"],
            ))

        conn.commit()
        conn.close()

        logger.info(f"Saved {len(products)} products to {filepath}")
        return filepath

    def load_sqlite(self, db_file: str = "products.db") -> List[dict]:
        """从 SQLite 数据库加载产品

        Args:
            db_file: 数据库文件名

        Returns:
            产品字典列表
        """
        filepath = self.data_dir / db_file

        if not filepath.exists():
            logger.warning(f"Database file not found: {filepath}")
            return []

        conn = sqlite3.connect(filepath)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM products ORDER BY fetch_time DESC")
        rows = cursor.fetchall()

        conn.close()

        products = [dict(row) for row in rows]
        logger.info(f"Loaded {len(products)} products from {filepath}")
        return products

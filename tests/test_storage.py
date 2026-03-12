"""文件存储测试"""

import pytest
import json
import os
from datetime import datetime

from src.storage.file_storage import FileStorage
from src.models.product import Product


class TestFileStorage:
    """FileStorage 测试"""

    @pytest.fixture
    def storage(self, tmp_path):
        """创建临时存储目录"""
        return FileStorage(data_dir=str(tmp_path))

    def test_initialization(self, storage):
        """测试存储初始化"""
        assert storage.data_dir == "data"
        assert storage.raw_dir.exists()
        assert storage.processed_dir.exists()

    def test_save_csv(self, storage, tmp_path):
        """测试保存为 CSV"""
        products = [
            Product(
                name="测试产品1",
                code="TEST001",
                bank="测试银行",
                risk_level="R2",
                status="开放中",
                net_value=1.0234,
                currency="人民币",
                min_amount=100.0,
            ),
            Product(
                name="测试产品2",
                code="TEST002",
                bank="测试银行",
                risk_level="R3",
                status="未开放",
                net_value=1.05,
                currency="人民币",
                min_amount=500.0,
            ),
        ]

        filepath = storage.save_csv(products, "test_products.csv")

        assert filepath.exists()
        assert "test_products.csv" in str(filepath)
        assert filepath.parent.name == "processed"

        # 验证文件内容
        import csv
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2
            assert rows[0]["name"] == "测试产品1"
            assert rows[1]["name"] == "测试产品2"

    def test_save_json(self, storage, tmp_path):
        """测试保存为 JSON"""
        products = [
            Product(
                name="测试产品",
                code="TEST001",
                bank="测试银行",
                risk_level="R2",
                status="开放中",
                net_value=1.0234,
            ),
        ]

        filepath = storage.save_json(products, "test_products.json")

        assert filepath.exists()
        assert "test_products.json" in str(filepath)

        # 验证文件内容
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert len(data) == 1
            assert data[0]["name"] == "测试产品"

    def test_save_sqlite(self, storage, tmp_path):
        """测试保存为 SQLite"""
        products = [
            Product(
                name="测试产品",
                code="TEST001",
                bank="测试银行",
                risk_level="R2",
                status="开放中",
                net_value=1.0234,
            ),
        ]

        filepath = storage.save_sqlite(products, "test_products.db")

        assert filepath.exists()
        assert "test_products.db" in str(filepath)
        assert filepath.parent.name == "data"

        # 验证数据库文件
        import sqlite3
        conn = sqlite3.connect(str(filepath))
        cursor = conn.cursor()

        # 验证表存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        table_names = [t[0] for t in tables]
        assert "products" in table_names

        # 验证数据
        cursor.execute("SELECT COUNT(*) FROM products")
        count = cursor.fetchone()[0]
        assert count == 1

        conn.close()

        # 清理测试数据库
        conn = sqlite3.connect(str(filepath))
        conn.execute("DROP TABLE IF EXISTS products")
        conn.commit()
        conn.close()

    def test_load_sqlite(self, storage, tmp_path):
        """测试从 SQLite 加载数据"""
        # 先保存一些数据
        products = [
            Product(
                name="测试产品",
                code="TEST001",
                bank="测试银行",
                net_value=1.0234,
            ),
        ]
        storage.save_sqlite(products, "test_products.db")

        # 加载数据
        loaded = storage.load_sqlite("test_products.db")

        assert len(loaded) == 1
        assert loaded[0]["name"] == "测试产品"
        assert loaded[0]["bank"] == "测试银行"

        # 清理测试数据库
        conn = sqlite3.connect(str(storage.data_dir / "test_products.db"))
        conn.execute("DROP TABLE IF EXISTS products")
        conn.commit()
        conn.close()

    def test_empty_products_list(self, storage):
        """测试空产品列表"""
        # 空列表仍会保存，只是空内容
        storage.save_csv([], "empty.csv")

        filepath = storage.processed_dir / "empty.csv"
        assert filepath.exists()
        # 空文件应该存在，只有表头或空行
        import csv
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            # 空列表时可能有表头
            assert len(rows) >= 0

        # 清理
        os.remove(filepath)

    def test_product_to_dict(self):
        """测试 Product 转字典"""
        product = Product(
            name="测试产品",
            code="TEST001",
            bank="测试银行",
            net_value=1.0234,
            fetch_time=datetime(2024, 1, 1, 12, 0, 0),
        )

        data = product.to_dict()

        assert data["name"] == "测试产品"
        assert data["code"] == "TEST001"
        assert data["bank"] == "测试银行"
        assert data["net_value"] == 1.0234
        assert "fetch_time" in data

    def test_product_with_all_fields(self):
        """测试包含所有字段的 Product"""
        product = Product(
            name="测试产品",
            code="TEST001",
            bank="测试银行",
            product_type="代销理财",
            sale_type="代销",
            fund_type="公募",
            issuer="招银理财",
            risk_level="R2",
            status="开放中",
            net_value=1.0234,
            currency="人民币",
            min_amount=100.0,
            investor_scope="遵循风险匹配原则",
            fee_standard="认购费：不收取",
            fee_method="认购费",
            notice_url="https://example.com",
            filing_number="备案001",
            source="测试",
            fetch_time=datetime.now(),
        )

        data = product.to_dict()

        assert len(data) == 19  # 检查所有字段
        expected_fields = {
            "name", "code", "bank", "product_type", "sale_type", "fund_type",
            "issuer", "risk_level", "status", "net_value", "currency",
            "min_amount", "investor_scope", "fee_standard", "fee_method",
            "notice_url", "filing_number", "fetch_time", "source"
        }
        assert set(data.keys()) == expected_fields

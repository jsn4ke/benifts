"""产品模型测试"""

import pytest
from datetime import datetime

from src.models.product import Product


class TestProduct:
    """Product 模型测试"""

    def test_product_creation(self):
        """测试产品创建"""
        product = Product(
            name="测试产品",
            code="TEST001",
            bank="测试银行",
        )

        assert product.name == "测试产品"
        assert product.code == "TEST001"
        assert product.bank == "测试银行"
        assert product.currency == "人民币"
        assert isinstance(product.fetch_time, datetime)

    def test_product_to_dict(self):
        """测试产品转换为字典"""
        product = Product(
            name="测试产品",
            code="TEST001",
            bank="测试银行",
            risk_level="R2",
            status="开放中",
            net_value=1.0234,
        )

        data = product.to_dict()

        assert data["name"] == "测试产品"
        assert data["code"] == "TEST001"
        assert data["bank"] == "测试银行"
        assert data["risk_level"] == "R2"
        assert data["status"] == "开放中"
        assert data["net_value"] == 1.0234
        assert "fetch_time" in data
        assert "source" in data

    def test_product_with_optional_fields(self):
        """测试包含可选字段的产品"""
        product = Product(
            name="测试产品",
            code="TEST001",
            bank="测试银行",
            product_type="代销理财",
            risk_level="R2",
            status="未开放",
            net_value=1.0,
            currency="人民币",
            min_amount=100.0,
            investor_scope="遵循风险匹配原则",
            fee_standard="固定管理费：0.15%",
            fee_method="认购费",
            notice_url="https://example.com",
            filing_number="备案001",
            source="API",
        )

        assert product.product_type == "代销理财"
        assert product.investor_scope == "遵循风险匹配原则"
        assert product.fee_standard == "固定管理费：0.15%"
        assert product.notice_url == "https://example.com"

    def test_product_default_values(self):
        """测试产品默认值"""
        product = Product(
            name="测试产品",
            code="TEST001",
            bank="测试银行",
        )

        assert product.currency == "人民币"
        assert product.product_type is None
        assert product.risk_level is None
        assert product.status is None

"""净值分析功能简化测试"""

import pytest
from datetime import datetime, timedelta

from src.models.product import Product
from src.analytics.product_filter import ProductFilter


class TestNetValueAnalysis:
    """净值分析功能测试"""

    @pytest.fixture
    def sample_products(self):
        """创建测试产品列表"""
        now = datetime.now()

        # A21107: 稳健增长
        a21107 = []
        for i in range(10):
            a21107.append(Product(
                name="招银理财-季季盈",
                code="A21107",
                bank="招商银行",
                net_value=1.0000 + i * 0.002,
                fetch_time=now - timedelta(days=10-i),
            ))

        # A21106: 波动较大
        a21106 = []
        for i in range(8):
            a21106.append(Product(
                name="招银理财-月月享",
                code="A21106",
                bank="招商银行",
                net_value=1.0500 + (i % 5) * 0.01 * (-1 if i % 5 == 4 else 1),
                fetch_time=now - timedelta(days=8-i),
            ))

        # A21108: 新产品
        a21108 = []
        for i in range(5):
            a21108.append(Product(
                name="招银理财-周周盈",
                code="A21108",
                bank="招商银行",
                net_value=1.0000 + i * 0.01,
                fetch_time=now - timedelta(days=5-i),
            ))

        return a21107 + a21106 + a21108

    def test_calculate_net_value_growth(self, sample_products):
        """测试净值增长率计算"""
        # 提取 A21107
        a21107 = [p for p in sample_products if p.code == "A21107"]

        # 计算增长率
        growth_rates = ProductFilter.calculate_net_value_growth(a21107)

        # 验证 A21107: 稳健增长
        assert "A21107" in growth_rates
        assert growth_rates["A21107"]["data_points"] == 10
        assert growth_rates["A21107"]["avg_growth_30d"] == pytest.approx(0.2, abs=0.01)
        assert growth_rates["A21107"]["total_growth"] == pytest.approx(20.0, abs=0.1)

        print("✅ 净值增长率计算测试通过")

    def test_identify_bonus_period_default(self, sample_products):
        """测试红利期识别（默认参数）"""
        now = datetime.now()

        # 创建红利期产品
        bonus_products = [
            Product(
                name="红利期产品A",
                code="BONUS01",
                bank="测试银行",
                net_value=1.05,
                fetch_time=now - timedelta(days=5),
            ),
            Product(
                name="红利期产品B",
                code="BONUS02",
                bank="测试银行",
                net_value=1.08,
                fetch_time=now - timedelta(days=3),
            ),
            Product(
                name="正常产品",
                code="NORMAL01",
                bank="测试银行",
                net_value=1.01,
                fetch_time=now - timedelta(days=10),
            ),
        ]

        growth_rates = ProductFilter.calculate_net_value_growth(bonus_products)
        bonus = ProductFilter.identify_bonus_period(growth_rates)

        assert len(bonus) == 2
        assert all(p["status"] == "红利期" for p in bonus)

        print("✅ 红利期识别测试通过")

    def test_identify_bonus_period_custom_threshold(self):
        """测试自定义阈值"""
        now = datetime.now()

        # 创建测试数据
        products = [
            Product(
                name="高增长产品",
                code="HIGH01",
                bank="测试银行",
                net_value=1.00,
                fetch_time=now - timedelta(days=1),
            ),
        ]

        growth_rates = ProductFilter.calculate_net_value_growth(products)

        # 使用高阈值
        bonus = ProductFilter.identify_bonus_period(
            growth_rates,
            days_threshold=30,
            growth_threshold=0.8
        )

        assert len(bonus) == 1
        assert bonus[0]["code"] == "HIGH01"
        assert bonus[0]["status"] == "红利期"

        print("✅ 自定义阈值测试通过")

    def test_generate_trend_report(self, sample_products):
        """测试趋势报告生成"""
        growth_rates = ProductFilter.generate_trend_report(self.sample_products())

        assert "summary" in growth_rates
        assert growth_rates["summary"]["total_products"] == 3

        print("✅ 趋势报告生成测试通过")

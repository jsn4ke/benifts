"""产品筛选功能测试"""

import pytest
from datetime import datetime, timedelta

from src.models.product import Product
from src.analytics.product_filter import ProductFilter


class TestProductFilter:
    """ProductFilter 测试"""

    @pytest.fixture
    def sample_products(self):
        """创建测试产品列表"""
        return [
            Product(
                name="测试产品1",
                code="TEST001",
                bank="招商银行",
                risk_level="R2",
                status="开放中",
                net_value=1.0234,
                fetch_time=datetime.now(),
            ),
            Product(
                name="测试产品2",
                code="TEST002",
                bank="招商银行",
                risk_level="R3",
                status="未开放",
                net_value=1.05,
                fetch_time=datetime.now() - timedelta(hours=1),
            ),
            Product(
                name="测试产品3",
                code="TEST003",
                bank="上海银行",
                risk_level="R2",
                status="开放中",
                net_value=1.01,
                fetch_time=datetime.now() - timedelta(hours=2),
            ),
            Product(
                name="测试产品4",
                code="TEST004",
                bank="招商银行",
                risk_level="R1",
                status="开放中",
                net_value=None,
                fetch_time=datetime.now(),
            ),
        ]

    def test_filter_by_status(self, sample_products):
        """测试按状态筛选"""
        open_products = ProductFilter.filter_by_status(sample_products, "开放中")
        assert len(open_products) == 3

        closed_products = ProductFilter.filter_by_status(sample_products, "未开放")
        assert len(closed_products) == 1

        none_products = ProductFilter.filter_by_status(sample_products, "不存在")
        assert len(none_products) == 0

    def test_filter_by_bank(self, sample_products):
        """测试按银行筛选"""
        cmb_products = ProductFilter.filter_by_bank(sample_products, "招商银行")
        assert len(cmb_products) == 3

        shb_products = ProductFilter.filter_by_bank(sample_products, "上海银行")
        assert len(shb_products) == 1

    def test_filter_by_risk_level(self, sample_products):
        """测试按风险等级筛选"""
        r2_products = ProductFilter.filter_by_risk_level(sample_products, "R2")
        assert len(r2_products) == 2

        r3_products = ProductFilter.filter_by_risk_level(sample_products, "R3")
        assert len(r3_products) == 1

        r1_products = ProductFilter.filter_by_risk_level(sample_products, "R1")
        assert len(r1_products) == 1

    def test_filter_by_net_value_range(self, sample_products):
        """测试按净值范围筛选"""
        # 全部范围
        all_products = ProductFilter.filter_by_net_value_range(sample_products)
        assert len(all_products) == 3  # 排除净值 None 的

        # 最小值
        min_products = ProductFilter.filter_by_net_value_range(sample_products, min_value=1.02)
        assert len(min_products) == 2

        # 最大值
        max_products = ProductFilter.filter_by_net_value_range(sample_products, max_value=1.02)
        assert len(max_products) == 1

        # 范围内
        range_products = ProductFilter.filter_by_net_value_range(
            sample_products, min_value=1.01, max_value=1.03
        )
        assert len(range_products) == 2

    def test_filter_by_fetch_time(self, sample_products):
        """测试按获取时间筛选"""
        recent_products = ProductFilter.filter_by_fetch_time(sample_products, hours=1)
        assert len(recent_products) == 2

        recent_2h = ProductFilter.filter_by_fetch_time(sample_products, hours=2)
        assert len(recent_2h) == 3

    def test_get_statistics(self, sample_products):
        """测试获取统计信息"""
        stats = ProductFilter.get_statistics(sample_products)

        assert stats["total"] == 4
        assert stats["by_bank"]["招商银行"] == 3
        assert stats["by_bank"]["上海银行"] == 1
        assert stats["by_status"]["开放中"] == 3
        assert stats["by_status"]["未开放"] == 1
        assert stats["by_risk_level"]["R2"] == 2
        assert stats["avg_net_value"] == pytest.approx(1.0278, rel=1e-3)
        assert stats["min_net_value"] == 1.01
        assert stats["max_net_value"] == 1.05

    def test_find_new_products(self, sample_products):
        """测试查找新增产品"""
        previous = [sample_products[0], sample_products[1]]
        current = sample_products

        new_products = ProductFilter.find_new_products(previous, current)
        assert len(new_products) == 2
        assert new_products[0].code == "TEST003"
        assert new_products[1].code == "TEST004"

        # 没有新增
        no_new = ProductFilter.find_new_products(current, current)
        assert len(no_new) == 0

    def test_track_net_value_changes(self, sample_products):
        """测试追踪净值变化"""
        previous = [
            Product(
                name="测试产品1",
                code="TEST001",
                bank="招商银行",
                net_value=1.0200,
            ),
            Product(
                name="测试产品2",
                code="TEST002",
                bank="招商银行",
                net_value=1.05,
            ),
        ]

        current = [
            Product(
                name="测试产品1",
                code="TEST001",
                bank="招商银行",
                net_value=1.0234,
            ),
            Product(
                name="测试产品2",
                code="TEST002",
                bank="招商银行",
                net_value=1.05,
            ),
            Product(
                name="测试产品3",
                code="TEST003",
                bank="上海银行",
                net_value=1.01,
            ),
        ]

        changes = ProductFilter.track_net_value_changes(previous, current)

        # TEST001 有变化
        assert "TEST001" in changes
        assert changes["TEST001"]["previous"] == 1.0200
        assert changes["TEST001"]["current"] == 1.0234
        assert changes["TEST001"]["change"] == pytest.approx(0.0034, rel=1e-6)
        assert changes["TEST001"]["change_percent"] == pytest.approx(0.333, rel=1e-1)

        # TEST002 无变化
        assert "TEST002" not in changes

        # TEST003 不在之前列表中
        assert "TEST003" not in changes

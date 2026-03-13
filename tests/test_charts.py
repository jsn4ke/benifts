"""数据可视化测试"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path

from src.visualization.charts import DataVisualizer
from src.models.product import Product
from src.analytics.net_value_analyzer import BonusPeriod


class TestDataVisualizer:
    """数据可视化器测试"""

    @pytest.fixture
    def mock_products(self):
        """模拟产品数据"""
        return [
            Product(
                name="产品1",
                code="P001",
                bank="招商银行",
                net_value=1.05,
                fetch_time=datetime.now(),
            ),
            Product(
                name="产品2",
                code="P002",
                bank="招商银行",
                net_value=1.10,
                fetch_time=datetime.now(),
            ),
            Product(
                name="产品3",
                code="P003",
                bank="招商银行",
                net_value=0.98,
                fetch_time=datetime.now(),
            ),
            Product(
                name="产品4",
                code="P004",
                bank="招商银行",
                net_value=1.15,
                fetch_time=datetime.now(),
            ),
            Product(
                name="产品5",
                code="P005",
                bank="招商银行",
                net_value=1.02,
                fetch_time=datetime.now(),
            ),
        ]

    @pytest.fixture
    def mock_bonus_periods(self):
        """模拟红利期数据"""
        now = datetime.now()
        return [
            BonusPeriod(
                product_code="NEW001",
                product_name="新产品1",
                bank="招商银行",
                bonus_start_date=now - timedelta(days=10),
                bonus_end_date=None,
                is_active=True,
                initial_value=1.0,
                current_value=1.03,
                total_return=3.0,
                days_since_start=10,
                bonus_days=30,
            ),
            BonusPeriod(
                product_code="NEW002",
                product_name="新产品2",
                bank="招商银行",
                bonus_start_date=now - timedelta(days=5),
                bonus_end_date=None,
                is_active=True,
                initial_value=1.0,
                current_value=1.008,
                total_return=0.8,
                days_since_start=5,
                bonus_days=30,
            ),
        ]

    def test_init(self):
        """测试初始化"""
        viz = DataVisualizer("output/test")
        assert viz.output_dir == Path("output/test")
        assert viz.output_dir.exists()

    def test_plot_net_value_trend(self, mock_products):
        """测试净值趋势图绘制"""
        viz = DataVisualizer("output/test")

        result = viz.plot_net_value_trend(mock_products)

        assert result is not None
        assert result.exists()

        # 清理测试文件
        if result.exists():
            result.unlink()

    def test_plot_net_value_trend_empty(self):
        """测试空产品列表"""
        viz = DataVisualizer("output/test")

        result = viz.plot_net_value_trend([])

        assert result is None

    def test_plot_bonus_periods(self, mock_bonus_periods):
        """测试红利期图表绘制"""
        viz = DataVisualizer("output/test")

        result = viz.plot_bonus_periods(mock_bonus_periods)

        assert result is not None
        assert result.exists()

        # 清理测试文件
        if result.exists():
            result.unlink()

    def test_plot_bonus_periods_empty(self):
        """测试空红利期列表"""
        viz = DataVisualizer("output/test")

        result = viz.plot_bonus_periods([])

        assert result is None

    def test_plot_value_distribution(self, mock_products):
        """测试净值分布图绘制"""
        viz = DataVisualizer("output/test")

        result = viz.plot_value_distribution(mock_products)

        assert result is not None
        assert result.exists()

        # 清理测试文件
        if result.exists():
            result.unlink()

    def test_plot_daily_returns(self):
        """测试每日收益率图绘制"""
        viz = DataVisualizer("output/test")

        daily_returns = {
            "P001": [
                {
                    "date": datetime.now() - timedelta(days=3),
                    "net_value": 1.0,
                    "daily_return": None,
                },
                {
                    "date": datetime.now() - timedelta(days=2),
                    "net_value": 1.01,
                    "daily_return": 1.0,
                },
                {
                    "date": datetime.now() - timedelta(days=1),
                    "net_value": 1.02,
                    "daily_return": 0.99,
                },
            ],
        }

        result = viz.plot_daily_returns(daily_returns, "P001")

        assert result is not None
        assert result.exists()

        # 清理测试文件
        if result.exists():
            result.unlink()

    def test_plot_daily_returns_empty(self):
        """测试空每日收益率数据"""
        viz = DataVisualizer("output/test")

        result = viz.plot_daily_returns({}, "P001")

        assert result is None

    def test_generate_all_charts(self, mock_products, mock_bonus_periods):
        """测试生成所有图表"""
        viz = DataVisualizer("output/test")

        results = viz.generate_all_charts(
            products=mock_products,
            bonus_periods=mock_bonus_periods,
        )

        assert 'net_value_trend' in results
        assert 'bonus_periods' in results
        assert 'value_distribution' in results

        # 清理测试文件
        for filepath in results.values():
            if filepath and filepath.exists():
                filepath.unlink()

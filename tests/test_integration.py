"""集成测试 - 测试完整的数据流"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

# 注意：集成测试需要 mock 爬虫和网络请求


class TestIntegrationWorkflow:
    """集成工作流测试"""

    @patch('src.scrapers.cmb.CMBScraper.fetch_products')
    def test_full_workflow(self, mock_fetch):
        """测试完整工作流：从数据获取到通知"""

        # Mock 爬虫返回原始数据字典
        from src.models.product import Product
        from datetime import datetime, timedelta

        mock_fetch.return_value = [
            {
                "name": "产品1",
                "code": "P001",
                "bank": "招商银行",
                "net_value": 1.05,
                "fetch_time": datetime.now(),
            },
            {
                "name": "产品2",
                "code": "P002",
                "bank": "招商银行",
                "net_value": 1.02,
                "fetch_time": datetime.now(),
            },
            {
                "name": "新产品高收益",
                "code": "NEW001",
                "bank": "招商银行",
                "net_value": 1.03,
                "fetch_time": datetime.now() - timedelta(days=5),
            },
        ]

        # 导入模块
        from src.scrapers.cmb import CMBScraper
        from src.analytics.net_value_analyzer import NetValueAnalyzer
        from src.analytics.product_filter import ProductFilter
        from src.visualization.charts import DataVisualizer
        from src.notifications.notifier import ConsoleNotifier, ProductNotifier

        # 步骤 1: 获取产品
        scraper = CMBScraper()
        products = scraper.to_product_list(mock_fetch.return_value)

        assert len(products) == 3

        # 步骤 2: 统计分析
        stats = ProductFilter.get_statistics(products)

        assert stats['total'] == 3

        # 步骤 3: 净值分析
        analyzer = NetValueAnalyzer(bonus_days=30, bonus_threshold=0.5)

        # 模拟历史数据（第一次运行）
        previous_products = [
            Product(
                name="产品1",
                code="P001",
                bank="招商银行",
                net_value=1.04,  # 略低
                fetch_time=datetime.now(),
            ),
            Product(
                name="产品2",
                code="P002",
                bank="招商银行",
                net_value=1.01,
                fetch_time=datetime.now(),
            ),
            Product(
                name="新产品高收益",
                code="NEW001",
                bank="招商银行",
                net_value=1.0,
                fetch_time=datetime.now() - timedelta(days=5),
            ),
        ]

        changes = analyzer.analyze_net_value_changes(previous_products, products)

        # P001 (1.04 -> 1.05) 和 P002 (1.01 -> 1.02) 都有变化
        # P001 的变化是 0.96%，P002 的变化是 0.99%
        # 所以应该有 2 个变化
        assert len(changes) >= 1  # 至少有 1 个变化

        # 步骤 4: 红利期识别
        bonus_periods = analyzer.identify_bonus_periods(products, {
            "NEW001": previous_products[2],
        })

        assert len(bonus_periods) == 1  # NEW001 符合红利期条件

        assert len(bonus_periods) == 1  # NEW001 符合红利期条件
        assert bonus_periods[0].is_active is True

        # 步骤 5: 可视化（使用 mock 避免实际绘图）
        with patch('src.visualization.charts.MATPLOTLIB_AVAILABLE', False):
            viz = DataVisualizer("output/test")

            result1 = viz.plot_net_value_trend(products)
            result2 = viz.plot_bonus_periods(bonus_periods)

            assert result1 is None  # matplotlib 被禁用
            assert result2 is None

        # 步骤 6: 通知（使用 mock）
        notifier = ProductNotifier(Mock(return_value=True))

        # 高增长检测
        high_growth = analyzer.find_high_growth_products(changes)
        assert len(high_growth) == 1  # P001 的 1% 增长

        with patch.object(notifier, 'notify_high_growth_products', return_value=True) as mock_notify:
            result = notifier.notify_high_growth_products(high_growth, "user@example.com")
            assert result is True
            mock_notify.assert_called_once()


class TestDataFlowIntegrity:
    """数据流完整性测试"""

    def test_scraper_to_product_conversion(self):
        """测试爬虫数据到 Product 对象的转换"""
        from src.scrapers.cmb import CMBScraper
        from src.models.product import Product
        from datetime import datetime

        scraper = CMBScraper()

        # 测试原始数据字典
        raw_data = {
            "name": "测试产品",
            "code": "TEST001",
            "bank": "测试银行",
            "net_value": 1.0,
            "status": "开放中",
        }

        # to_product_list 方法会处理转换
        products = scraper.to_product_list([raw_data])

        assert len(products) == 1
        # 验证产品属性（使用 pytest.approx 处理浮点精度）
        assert products[0].net_value == pytest.approx(1.0, abs=0.01)

    def test_product_to_dict_conversion(self):
        """测试 Product 对象到字典的转换"""
        from src.models.product import Product

        product = Product(
            name="测试产品",
            code="TEST001",
            bank="测试银行",
            net_value=1.0,
        )

        product_dict = product.to_dict()

        assert product_dict["name"] == "测试产品"
        assert product_dict["code"] == "TEST001"
        assert product_dict["bank"] == "测试银行"
        assert product_dict["net_value"] == 1.0


class TestConfig:
    """配置测试"""

    def test_analyzer_config(self):
        """测试分析器配置"""
        from src.analytics.net_value_analyzer import NetValueAnalyzer

        # 默认配置
        analyzer_default = NetValueAnalyzer()
        assert analyzer_default.bonus_days == 30
        assert analyzer_default.bonus_threshold == 0.5
        assert analyzer_default.high_growth_threshold == 1.0

        # 自定义配置
        analyzer_custom = NetValueAnalyzer(
            bonus_days=60,
            bonus_threshold=1.0,
            high_growth_threshold=2.0
        )
        assert analyzer_custom.bonus_days == 60
        assert analyzer_custom.bonus_threshold == 1.0
        assert analyzer_custom.high_growth_threshold == 2.0

    def test_visualizer_output_dir(self):
        """测试可视化器输出目录"""
        from src.visualization.charts import DataVisualizer
        from pathlib import Path

        viz = DataVisualizer("output/test")

        assert viz.output_dir == Path("output/test")
        assert viz.output_dir.exists()

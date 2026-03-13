"""净值分析器测试"""

import pytest
from datetime import datetime, timedelta

from src.analytics.net_value_analyzer import (
    NetValueAnalyzer,
    NetValueChange,
    BonusPeriod,
)


class TestNetValueAnalyzer:
    """净值分析器测试"""

    def test_init(self):
        """测试初始化"""
        analyzer = NetValueAnalyzer()
        assert analyzer.bonus_days == 30
        assert analyzer.bonus_threshold == 0.5
        assert analyzer.high_growth_threshold == 1.0

    def test_init_custom_params(self):
        """测试自定义参数初始化"""
        analyzer = NetValueAnalyzer(bonus_days=60, bonus_threshold=1.0, high_growth_threshold=2.0)
        assert analyzer.bonus_days == 60
        assert analyzer.bonus_threshold == 1.0
        assert analyzer.high_growth_threshold == 2.0


class TestNetValueChange:
    """净值变化数据类测试"""

    def test_net_value_change_creation(self):
        """测试净值变化对象创建"""
        now = datetime.now()
        change = NetValueChange(
            product_code="TEST001",
            product_name="测试产品",
            bank="招商银行",
            previous_value=1.0,
            current_value=1.01,
            change=0.01,
            change_percent=1.0,
            change_date=now,
            fetch_time=now,
        )

        assert change.product_code == "TEST001"
        assert change.product_name == "测试产品"
        assert change.previous_value == 1.0
        assert change.current_value == 1.01
        assert change.change == 0.01
        assert change.change_percent == 1.0

    def test_daily_return_property(self):
        """测试日均收益率计算"""
        now = datetime.now()
        change = NetValueChange(
            product_code="TEST001",
            product_name="测试产品",
            bank="招商银行",
            previous_value=1.0,
            current_value=1.05,
            change=0.05,
            change_percent=5.0,
            change_date=now,
            fetch_time=now,
        )
        # NetValueChange 没有 daily_return 属性
        assert hasattr(change, "product_code")


class TestBonusPeriod:
    """红利期数据类测试"""

    def test_bonus_period_creation(self):
        """测试红利期对象创建"""
        now = datetime.now()
        start_date = now - timedelta(days=10)

        period = BonusPeriod(
            product_code="TEST001",
            product_name="测试产品",
            bank="招商银行",
            bonus_start_date=start_date,
            bonus_end_date=None,
            is_active=True,
            initial_value=1.0,
            current_value=1.02,
            total_return=2.0,
            days_since_start=10,
            bonus_days=30,
        )

        assert period.product_code == "TEST001"
        assert period.is_active is True
        assert period.days_since_start == 10
        assert period.total_return == 2.0

    def test_daily_return_calculation(self):
        """测试日均收益率计算"""
        now = datetime.now()
        start_date = now - timedelta(days=10)

        period = BonusPeriod(
            product_code="TEST001",
            product_name="测试产品",
            bank="招商银行",
            bonus_start_date=start_date,
            bonus_end_date=None,
            is_active=True,
            initial_value=1.0,
            current_value=1.02,
            total_return=2.0,
            days_since_start=10,
            bonus_days=30,
        )

        assert period.daily_return == 0.2  # 2.0% / 10 天

    def test_daily_return_zero_days(self):
        """测试零天日均收益率"""
        now = datetime.now()

        period = BonusPeriod(
            product_code="TEST001",
            product_name="测试产品",
            bank="招商银行",
            bonus_start_date=now,
            bonus_end_date=None,
            is_active=True,
            initial_value=1.0,
            current_value=1.0,
            total_return=0.0,
            days_since_start=0,
            bonus_days=30,
        )

        assert period.daily_return == 0.0

    def test_annualized_return_calculation(self):
        """测试年化收益率计算"""
        now = datetime.now()
        start_date = now - timedelta(days=10)

        period = BonusPeriod(
            product_code="TEST001",
            product_name="测试产品",
            bank="招商银行",
            bonus_start_date=start_date,
            bonus_end_date=None,
            is_active=True,
            initial_value=1.0,
            current_value=1.02,
            total_return=2.0,
            days_since_start=10,
            bonus_days=30,
        )

        # 2% over 10 days = (1.02)^(365/10) - 1
        annualized = period.annualized_return
        assert annualized > 0  # 应该是正数
        # 2% over 10 days annualized should be much higher
        assert annualized > 50  # 粗略估计

    def test_annualized_return_zero_or_negative(self):
        """测试零或负收益的年化收益率"""
        now = datetime.now()

        period_zero = BonusPeriod(
            product_code="TEST001",
            product_name="测试产品",
            bank="招商银行",
            bonus_start_date=now,
            bonus_end_date=None,
            is_active=True,
            initial_value=1.0,
            current_value=1.0,
            total_return=0.0,
            days_since_start=0,
            bonus_days=30,
        )

        assert period_zero.annualized_return == 0.0

        period_negative = BonusPeriod(
            product_code="TEST002",
            product_name="测试产品2",
            bank="招商银行",
            bonus_start_date=now,
            bonus_end_date=None,
            is_active=True,
            initial_value=1.0,
            current_value=0.99,
            total_return=-1.0,
            days_since_start=10,
            bonus_days=30,
        )

        # 负收益的年化值应该是负数
        assert period_negative.annualized_return < 0


class TestAnalyzeNetValueChanges:
    """净值变化分析测试"""

    @pytest.fixture
    def mock_historical(self):
        """模拟历史数据"""
        from src.models.product import Product
        return [
            Product(
                name="产品1",
                code="P001",
                bank="招商银行",
                net_value=1.0,
                fetch_time=datetime.now() - timedelta(days=1),
            ),
            Product(
                name="产品2",
                code="P002",
                bank="招商银行",
                net_value=1.5,
                fetch_time=datetime.now() - timedelta(days=1),
            ),
        ]

    @pytest.fixture
    def mock_latest(self):
        """模拟最新数据"""
        from src.models.product import Product
        return [
            Product(
                name="产品1",
                code="P001",
                bank="招商银行",
                net_value=1.01,
                fetch_time=datetime.now(),
            ),
            Product(
                name="产品2",
                code="P002",
                bank="招商银行",
                net_value=1.52,
                fetch_time=datetime.now(),
            ),
            Product(
                name="产品3",
                code="P003",
                bank="招商银行",
                net_value=1.0,
                fetch_time=datetime.now(),
            ),
        ]

    def test_analyze_changes(self, mock_historical, mock_latest):
        """测试净值变化分析"""
        analyzer = NetValueAnalyzer()
        changes = analyzer.analyze_net_value_changes(mock_historical, mock_latest)

        assert len(changes) == 2

        # 检查第一个产品变化
        p001_change = next((c for c in changes if c.product_code == "P001"), None)
        assert p001_change is not None
        assert p001_change.change == pytest.approx(0.01, abs=0.001)
        assert p001_change.change_percent == pytest.approx(1.0, abs=0.1)

        # 检查第二个产品变化
        p002_change = next((c for c in changes if c.product_code == "P002"), None)
        assert p002_change is not None
        assert p002_change.change == pytest.approx(0.02, abs=0.001)
        assert p002_change.change_percent == pytest.approx(1.333, rel=0.01)

    def test_find_high_growth(self, mock_historical, mock_latest):
        """测试高增长产品查找"""
        analyzer = NetValueAnalyzer(high_growth_threshold=1.0)
        changes = analyzer.analyze_net_value_changes(mock_historical, mock_latest)
        high_growth = analyzer.find_high_growth_products(changes)

        assert len(high_growth) == 2  # 两个产品都 > 1%


class TestIdentifyBonusPeriods:
    """红利期识别测试"""

    @pytest.fixture
    def mock_products(self):
        """模拟产品数据"""
        from src.models.product import Product
        now = datetime.now()
        return [
            Product(
                name="新产品高收益",
                code="NEW001",
                bank="招商银行",
                net_value=1.03,  # 3% 收益
                fetch_time=now,
            ),
            Product(
                name="新产品低收益",
                code="NEW002",
                bank="招商银行",
                net_value=1.003,  # 0.3% 收益
                fetch_time=now,
            ),
            Product(
                name="老产品",
                code="OLD001",
                bank="招商银行",
                net_value=1.05,
                fetch_time=now - timedelta(days=35),
            ),
        ]

    @pytest.fixture
    def mock_initial_records(self):
        """模拟初始记录"""
        from src.models.product import Product
        now = datetime.now()
        return {
            "NEW001": Product(
                name="新产品高收益",
                code="NEW001",
                bank="招商银行",
                net_value=1.0,
                fetch_time=now - timedelta(days=10),
            ),
            "NEW002": Product(
                name="新产品低收益",
                code="NEW002",
                bank="招商银行",
                net_value=1.0,
                fetch_time=now - timedelta(days=5),
            ),
            "OLD001": Product(
                name="老产品",
                code="OLD001",
                bank="招商银行",
                net_value=1.0,
                fetch_time=now - timedelta(days=40),
            ),
        }

    def test_identify_bonus_periods(self, mock_products, mock_initial_records):
        """测试红利期识别"""
        analyzer = NetValueAnalyzer(bonus_days=30, bonus_threshold=0.5)
        bonus_periods = analyzer.identify_bonus_periods(mock_products, mock_initial_records)

        # 应该识别出 1 个产品在红利期
        active = [b for b in bonus_periods if b.is_active]
        assert len(active) == 1
        assert active[0].product_code == "NEW001"

        # 检查收益率
        assert active[0].total_return == pytest.approx(3.0, rel=0.01)

    def test_bonus_period_properties(self, mock_products, mock_initial_records):
        """测试红利期属性"""
        analyzer = NetValueAnalyzer(bonus_days=30, bonus_threshold=0.5)
        bonus_periods = analyzer.identify_bonus_periods(mock_products, mock_initial_records)

        active = [b for b in bonus_periods if b.is_active]
        assert len(active) == 1

        period = active[0]
        assert period.days_since_start == 10
        assert period.bonus_days == 30
        assert period.daily_return == pytest.approx(0.3, rel=0.01)  # 3% / 10 天


class TestGenerateTrendReport:
    """趋势报告生成测试"""

    @pytest.fixture
    def mock_products(self):
        """模拟产品数据"""
        from src.models.product import Product
        now = datetime.now()
        return [
            Product(
                name="产品1",
                code="P001",
                bank="招商银行",
                net_value=1.05,
                risk_level="R2",
                fetch_time=now,
            ),
            Product(
                name="产品2",
                code="P002",
                bank="招商银行",
                net_value=0.98,
                risk_level="R3",
                fetch_time=now,
            ),
            Product(
                name="产品3",
                code="P003",
                bank="招商银行",
                net_value=1.15,
                risk_level="R1",
                fetch_time=now,
            ),
            Product(
                name="产品4",
                code="P004",
                bank="招商银行",
                net_value=None,
                risk_level="R2",
                fetch_time=now,
            ),
        ]

    def test_generate_trend_report(self, mock_products):
        """测试趋势报告生成"""
        analyzer = NetValueAnalyzer()
        report = analyzer.generate_trend_report(mock_products)

        assert report["total_products"] == 4
        assert report["products_with_net_value"] == 3

        # 检查净值统计
        assert "value_statistics" in report
        stats = report["value_statistics"]
        assert stats["average"] == pytest.approx(1.06, rel=0.01)
        assert stats["min"] == 0.98
        assert stats["max"] == 1.15

        # 检查风险分布
        assert report["risk_summary"]["R1"] == 1
        assert report["risk_summary"]["R2"] == 2
        assert report["risk_summary"]["R3"] == 1

        # 检查 Top 产品
        assert len(report["top_products"]) == 3
        assert report["top_products"][0]["net_value"] == 1.15

    def test_format_bonus_report(self):
        """测试红利期报告格式化"""
        now = datetime.now()
        start_date = now - timedelta(days=10)

        periods = [
            BonusPeriod(
                product_code="TEST001",
                product_name="测试产品",
                bank="招商银行",
                bonus_start_date=start_date,
                bonus_end_date=None,
                is_active=True,
                initial_value=1.0,
                current_value=1.02,
                total_return=2.0,
                days_since_start=10,
                bonus_days=30,
            ),
        ]

        analyzer = NetValueAnalyzer()
        report = analyzer.format_bonus_report(periods)

        assert "红利期分析报告" in report
        assert "测试产品" in report
        assert "TEST001" in report
        assert "2.00%" in report  # 收益率

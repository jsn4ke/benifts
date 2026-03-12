"""Phase 4 集成测试 - 验证筛选和调度功能"""

import pytest
from datetime import datetime, timedelta

from src.models.product import Product
from src.analytics.product_filter import ProductFilter
from src.utils.scheduler import Scheduler
from src.storage.file_storage import FileStorage


class TestPhase4Integration:
    """Phase 4 功能集成测试"""

    @pytest.fixture
    def sample_products(self):
        """创建模拟产品列表"""
        return [
            Product(
                name="招银理财-金葵花增利",
                code="CMB001",
                bank="招商银行",
                product_type="代销理财",
                risk_level="R2",
                status="开放中",
                net_value=1.0523,
                currency="人民币",
                min_amount=100.0,
                fetch_time=datetime.now(),
                source="Mock",
            ),
            Product(
                name="招银理财-月月享",
                code="CMB002",
                bank="招商银行",
                product_type="代销理财",
                risk_level="R3",
                status="未开放",
                net_value=1.0345,
                currency="人民币",
                min_amount=500.0,
                fetch_time=datetime.now() - timedelta(hours=1),
                source="Mock",
            ),
            Product(
                name="上银理财-稳健盈",
                code="SHB001",
                bank="上海银行",
                product_type="自有理财",
                risk_level="R2",
                status="开放中",
                net_value=1.0123,
                currency="人民币",
                min_amount=100.0,
                fetch_time=datetime.now(),
                source="Mock",
            ),
            Product(
                name="招银理财-季季盈",
                code="CMB003",
                bank="招商银行",
                product_type="代销理财",
                risk_level="R1",
                status="开放中",
                net_value=1.0015,
                currency="人民币",
                min_amount=1000.0,
                fetch_time=datetime.now(),
                source="Mock",
            ),
        ]

    def test_filter_open_products_workflow(self, sample_products):
        """测试筛选开放中产品的完整工作流"""
        # 筛选开放中产品
        open_products = ProductFilter.filter_by_status(sample_products, "开放中")
        assert len(open_products) == 3

        # 只包含开放中产品
        for p in open_products:
            assert p.status == "开放中"

    def test_multi_filter_workflow(self, sample_products):
        """测试多条件筛选工作流"""
        # 先按银行筛选
        cmb_products = ProductFilter.filter_by_bank(sample_products, "招商银行")
        assert len(cmb_products) == 3

        # 再按状态筛选
        open_cmb = ProductFilter.filter_by_status(cmb_products, "开放中")
        assert len(open_cmb) == 2

        # 再按风险等级筛选
        r2_open_cmb = ProductFilter.filter_by_risk_level(open_cmb, "R2")
        assert len(r2_open_cmb) == 1
        assert r2_open_cmb[0].code == "CMB001"

    def test_statistics_workflow(self, sample_products):
        """测试统计信息生成工作流"""
        stats = ProductFilter.get_statistics(sample_products)

        assert stats["total"] == 4
        assert stats["by_bank"]["招商银行"] == 3
        assert stats["by_bank"]["上海银行"] == 1
        assert stats["by_status"]["开放中"] == 3
        assert stats["by_status"]["未开放"] == 1
        assert stats["avg_net_value"] is not None
        assert 1.0 <= stats["avg_net_value"] <= 1.1

    def test_new_product_detection_workflow(self, sample_products):
        """测试新产品检测工作流"""
        previous = sample_products[:2]  # 前两个产品
        current = sample_products  # 全部产品

        new_products = ProductFilter.find_new_products(previous, current)
        assert len(new_products) == 2
        assert new_products[0].code == "SHB001"
        assert new_products[1].code == "CMB003"

    def test_net_value_tracking_workflow(self, sample_products):
        """测试净值追踪工作流"""
        # 创建之前的净值数据
        previous = [
            Product(
                name="招银理财-金葵花增利",
                code="CMB001",
                bank="招商银行",
                net_value=1.0500,
            ),
            Product(
                name="招银理财-月月享",
                code="CMB002",
                bank="招商银行",
                net_value=1.0345,
            ),
        ]

        # 创建当前的净值数据
        current = [
            Product(
                name="招银理财-金葵花增利",
                code="CMB001",
                bank="招商银行",
                net_value=1.0523,
            ),
            Product(
                name="招银理财-月月享",
                code="CMB002",
                bank="招商银行",
                net_value=1.0345,  # 未变化
            ),
        ]

        changes = ProductFilter.track_net_value_changes(previous, current)

        # 只有一个产品净值变化
        assert len(changes) == 1
        assert "CMB001" in changes
        assert changes["CMB001"]["change"] == pytest.approx(0.0023, rel=1e-4)

    def test_scheduler_should_run_logic(self):
        """测试调度器运行逻辑"""
        scheduler = Scheduler(interval_hours=1.0)

        # 首次应该运行
        assert scheduler.should_run(interval_hours=1.0) is True

        # 刚运行过，不应该运行
        scheduler.last_run = datetime.now()
        assert scheduler.should_run(interval_hours=1.0) is False

        # 2小时后应该运行
        scheduler.last_run = datetime.now() - timedelta(hours=2)
        assert scheduler.should_run(interval_hours=1.0) is True

    def test_scheduler_task_execution(self):
        """测试调度器任务执行"""
        scheduler = Scheduler(interval_hours=0.1)
        results = []

        def test_task():
            results.append("executed")

        # 运行3次
        scheduler.run_periodic(test_task, max_runs=3)
        assert len(results) == 3

    def test_end_to_end_workflow(self, sample_products, tmp_path):
        """测试端到端工作流"""
        # 1. 筛选开放中产品
        open_products = ProductFilter.filter_by_status(sample_products, "开放中")

        # 2. 获取统计信息
        stats = ProductFilter.get_statistics(open_products)
        assert stats["total"] == 3

        # 3. 保存数据
        storage = FileStorage(data_dir=str(tmp_path))
        csv_file = storage.save_csv(open_products, "test_open_products.csv")
        assert csv_file.exists()

        json_file = storage.save_json(open_products, "test_open_products.json")
        assert json_file.exists()

        # 4. 验证文件内容
        import json
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert len(data) == 3
            assert all(p["status"] == "开放中" for p in data)

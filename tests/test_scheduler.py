"""调度器测试"""

import time
import pytest
from datetime import datetime, timedelta

from src.utils.scheduler import Scheduler


class TestScheduler:
    """Scheduler 测试"""

    @pytest.fixture
    def scheduler(self):
        """创建调度器实例"""
        return Scheduler(interval_hours=1.0)

    def test_initialization(self, scheduler):
        """测试初始化"""
        assert scheduler.interval_seconds == 3600
        assert scheduler.last_run is None

    def test_run_once(self, scheduler):
        """测试单次运行"""
        call_count = [0]
        result_value = [42]

        def test_func():
            call_count[0] += 1
            return result_value[0]

        result = scheduler.run_once(test_func)

        assert result == 42
        assert call_count[0] == 1
        assert scheduler.last_run is not None
        assert isinstance(scheduler.last_run, datetime)

    def test_run_once_error_handling(self, scheduler):
        """测试错误处理"""
        def test_func():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            scheduler.run_once(test_func)

        # 即使出错，last_run 也应该更新
        assert scheduler.last_run is not None

    def test_should_run_first_time(self, scheduler):
        """测试首次运行应该运行"""
        assert scheduler.should_run(interval_hours=1.0) is True

    def test_should_run_after_interval(self, scheduler):
        """测试间隔后应该运行"""
        scheduler.last_run = datetime.now()

        # 立即检查不应该运行
        assert scheduler.should_run(interval_hours=1.0) is False

        # 修改 last_run 使其超过间隔
        scheduler.last_run = datetime.now() - timedelta(hours=2)
        assert scheduler.should_run(interval_hours=1.0) is True

    def test_should_run_with_different_intervals(self):
        """测试不同间隔"""
        scheduler = Scheduler(interval_hours=2.0)
        scheduler.last_run = datetime.now() - timedelta(hours=1.5)

        # 1.5 小时 < 2 小时，不应运行
        assert scheduler.should_run(interval_hours=2.0) is False

        # 但 1.5 小时 > 1 小时，应该运行
        assert scheduler.should_run(interval_hours=1.0) is True

    def test_short_interval_scheduler(self):
        """测试短间隔调度器（用于测试）"""
        call_count = [0]

        def test_func():
            call_count[0] += 1

        # 创建 0.1 秒间隔的调度器
        scheduler = Scheduler(interval_hours=0.1 / 3600)  # 0.1 秒

        # 运行 3 次
        scheduler.run_periodic(test_func, max_runs=3)

        assert call_count[0] == 3

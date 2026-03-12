"""定期任务调度器"""

import time
import logging
from typing import Callable, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class Scheduler:
    """定期任务调度器

    支持定时执行任务的简单调度器。
    """

    def __init__(self, interval_hours: float = 1.0):
        """初始化调度器

        Args:
            interval_hours: 执行间隔（小时）
        """
        self.interval_seconds = interval_hours * 3600
        self.last_run: Optional[datetime] = None

    def run_once(self, func: Callable[..., Any]) -> Any:
        """运行任务一次

        Args:
            func: 要执行的函数

        Returns:
            函数执行结果
        """
        logger.info(f"执行任务: {func.__name__}")
        self.last_run = datetime.now()

        try:
            result = func()
            logger.info(f"任务执行完成: {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"任务执行失败: {func.__name__}, 错误: {e}")
            raise

    def run_periodic(
        self,
        func: Callable[..., Any],
        max_runs: Optional[int] = None
    ) -> None:
        """定期运行任务

        Args:
            func: 要执行的函数
            max_runs: 最大运行次数，None 表示无限运行
        """
        run_count = 0

        logger.info(
            f"启动定期任务: {func.__name__}, "
            f"间隔: {self.interval_seconds / 3600:.2f} 小时, "
            f"最大次数: {max_runs or '无限'}"
        )

        while True:
            # 执行任务
            self.run_once(func)
            run_count += 1

            # 检查是否达到最大次数
            if max_runs is not None and run_count >= max_runs:
                logger.info(f"已达到最大运行次数: {max_runs}")
                break

            # 等待下次执行
            logger.info(f"下次执行时间: {datetime.now() + timedelta(seconds=self.interval_seconds)}")
            time.sleep(self.interval_seconds)

    def should_run(self, interval_hours: float = 1.0) -> bool:
        """检查是否应该运行任务

        Args:
            interval_hours: 要求的最小间隔（小时）

        Returns:
            True 如果应该运行
        """
        if self.last_run is None:
            return True

        elapsed = (datetime.now() - self.last_run).total_seconds()
        return elapsed >= interval_hours * 3600

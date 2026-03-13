"""净值分析模块"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging

from ..models.product import Product

logger = logging.getLogger(__name__)
DAYS_PER_YEAR = 365


@dataclass
class NetValueChange:
    """净值变化记录"""
    product_code: str
    product_name: str
    bank: str
    previous_value: float
    current_value: float
    change: float
    change_percent: float
    change_date: datetime
    fetch_time: datetime


@dataclass
class BonusPeriod:
    """红利期分析结果"""
    product_code: str
    product_name: str
    bank: str
    bonus_start_date: datetime  # 红利期开始日期
    bonus_end_date: Optional[datetime]  # 红利期结束日期（如果已结束）
    is_active: bool  # 是否仍在红利期
    initial_value: float  # 初始净值
    current_value: float  # 当前净值
    total_return: float  # 总收益率
    days_since_start: int  # 自开始天数
    bonus_days: int = 30  # 预计红利期天数（可配置）

    @property
    def daily_return(self) -> float:
        """日均收益率"""
        if self.days_since_start == 0:
            return 0.0
        return self.total_return / self.days_since_start

    @property
    def annualized_return(self) -> float:
        """年化收益率"""
        if self.days_since_start == 0:
            return 0.0
        # 允许负收益的年化计算
        return ((1 + self.total_return / 100) ** (DAYS_PER_YEAR / self.days_since_start) - 1) * 100

    @property
    def return_30_days(self) -> float:
        """30天收益（基于年化收益率换算）"""
        if self.days_since_start == 0:
            return 0.0
        # 计算30天的预期收益
        return self.annualized_return / 365 * 30

    @property
    def return_7_days(self) -> float:
        """7天收益（基于年化收益率换算）"""
        if self.days_since_start == 0:
            return 0.0
        # 计算7天的预期收益
        return self.annualized_return / 365 * 7


class NetValueAnalyzer:
    """净值分析器

    用于分析理财产品净值变化，识别红利期。
    """

    # 默认净值分布区间
    DEFAULT_VALUE_RANGES = [
        (0.0, 0.9, "< 0.9"),
        (0.9, 1.0, "0.9 - 1.0"),
        (1.0, 1.1, "1.0 - 1.1"),
        (1.1, float("inf"), "> 1.1"),
    ]

    def __init__(
        self,
        bonus_days: int = 30,
        bonus_threshold: float = 0.5,  # 红利期最低收益率 0.5%
        high_growth_threshold: float = 1.0,  # 高增长阈值 1.0%
        value_ranges: Optional[List[tuple]] = None,
    ):
        """初始化分析器

        Args:
            bonus_days: 红利期天数（默认 30 天）
            bonus_threshold: 红利期最低收益率阈值
            high_growth_threshold: 高增长阈值（单日）
            value_ranges: 净值分布区间（可选）
        """
        self.bonus_days = bonus_days
        self.bonus_threshold = bonus_threshold
        self.high_growth_threshold = high_growth_threshold
        self.value_ranges = value_ranges or self.DEFAULT_VALUE_RANGES

    def analyze_net_value_changes(
        self,
        historical_data: List[Product],
        latest_data: List[Product]
    ) -> List[NetValueChange]:
        """分析净值变化

        Args:
            historical_data: 历史产品数据
            latest_data: 最新产品数据

        Returns:
            净值变化列表
        """
        historical_dict = {p.code: p for p in historical_data}

        changes = []
        for latest in latest_data:
            if latest.code in historical_dict:
                historical = historical_dict[latest.code]

                if historical.net_value is None or latest.net_value is None:
                    continue

                change = latest.net_value - historical.net_value
                if change == 0:
                    continue

                change_percent = (change / historical.net_value) * 100 if historical.net_value != 0 else 0

                changes.append(NetValueChange(
                    product_code=latest.code,
                    product_name=latest.name,
                    bank=latest.bank,
                    previous_value=historical.net_value,
                    current_value=latest.net_value,
                    change=change,
                    change_percent=change_percent,
                    change_date=latest.fetch_time,
                    fetch_time=latest.fetch_time,
                ))

        logger.info(f"分析 {len(changes)} 个产品净值变化")
        return changes

    def find_high_growth_products(
        self,
        changes: List[NetValueChange]
    ) -> List[NetValueChange]:
        """查找高增长产品

        Args:
            changes: 净值变化列表

        Returns:
            高增长产品列表（增长率超过阈值）
        """
        high_growth = [c for c in changes if abs(c.change_percent) >= self.high_growth_threshold]

        logger.info(f"发现 {len(high_growth)} 个高增长产品（>= {self.high_growth_threshold}%）")
        return high_growth

    def identify_bonus_periods(
        self,
        products: List[Product],
        initial_records: Optional[Dict[str, Product]] = None
    ) -> List[BonusPeriod]:
        """识别红利期

        Args:
            products: 当前产品列表
            initial_records: 初始产品记录 {产品代码: 产品}，用于计算自上市以来的收益

        Returns:
            红利期分析结果列表
        """
        if initial_records is None:
            initial_records = {}

        bonus_periods = []
        now = datetime.now()

        for product in products:
            if product.net_value is None:
                continue

            # 查找初始记录
            if product.code in initial_records:
                initial_product = initial_records[product.code]
                initial_value = initial_product.net_value
                start_date = initial_product.fetch_time
                days_since_start = (now - start_date).days
            else:
                # 如果没有初始记录，使用 fetch_time 作为开始日期
                initial_value = product.net_value
                start_date = product.fetch_time
                days_since_start = 0

            # 计算收益率
            if initial_value and initial_value > 0:
                total_return = ((product.net_value - initial_value) / initial_value) * 100
            else:
                total_return = 0.0

            # 判断是否在红利期
            is_active = days_since_start <= self.bonus_days and total_return >= self.bonus_threshold

            if is_active or days_since_start <= self.bonus_days:
                bonus_end = None if is_active else start_date + timedelta(days=self.bonus_days)

                bonus_periods.append(BonusPeriod(
                    product_code=product.code,
                    product_name=product.name,
                    bank=product.bank,
                    bonus_start_date=start_date,
                    bonus_end_date=bonus_end,
                    is_active=is_active,
                    initial_value=initial_value or 0.0,
                    current_value=product.net_value,
                    total_return=total_return,
                    days_since_start=days_since_start,
                    bonus_days=self.bonus_days,
                ))

        # 筛选出有效红利期
        active_bonus = [b for b in bonus_periods if b.is_active]
        logger.info(f"识别出 {len(active_bonus)} 个产品处于红利期")
        return sorted(bonus_periods, key=lambda x: x.total_return, reverse=True)

    def generate_trend_report(
        self,
        products: List[Product]
    ) -> Dict[str, Any]:
        """生成净值趋势报告

        Args:
            products: 产品列表

        Returns:
            趋势报告字典
        """
        report = {
            "total_products": len(products),
            "products_with_net_value": 0,
            "value_distribution": {},
            "growth_categories": {
                "high": 0,  # > 5%
                "medium": 0,  # 1% - 5%
                "low": 0,  # 0% - 1%
                "negative": 0,  # < 0%
            },
            "top_products": [],
            "risk_summary": {},
        }

        net_values = []
        for p in products:
            if p.net_value is not None:
                net_values.append(p.net_value)
                report["products_with_net_value"] += 1

        if net_values:
            avg_value = sum(net_values) / len(net_values)
            min_value = min(net_values)
            max_value = max(net_values)

            report["value_statistics"] = {
                "average": round(avg_value, 4),
                "min": round(min_value, 4),
                "max": round(max_value, 4),
            }

            # 净值分布区间
            for p in products:
                if p.net_value is not None:
                    for min_val, max_val, label in self.value_ranges:
                        if min_val <= p.net_value < max_val:
                            report["value_distribution"][label] = report["value_distribution"].get(label, 0) + 1
                            break

            # Top 产品（按净值排序）
            sorted_products = sorted([p for p in products if p.net_value is not None], key=lambda x: x.net_value, reverse=True)
            report["top_products"] = [
                {"name": p.name, "code": p.code, "bank": p.bank, "net_value": p.net_value}
                for p in sorted_products[:10]
            ]

            # 风险等级统计
            for p in products:
                if p.risk_level:
                    report["risk_summary"][p.risk_level] = report["risk_summary"].get(p.risk_level, 0) + 1

        logger.info(f"生成趋势报告: {report['total_products']} 个产品")
        return report

    def calculate_daily_returns(
        self,
        history: List[List[Product]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """计算每日收益率

        Args:
            history: 历史数据列表，每个元素是一天的产品列表

        Returns:
            {产品代码: [{日期, 净值, 日收益率}, ...]}
        """
        daily_returns = {}

        for i, products in enumerate(history):
            for product in products:
                if product.code not in daily_returns:
                    daily_returns[product.code] = []

                if i > 0:
                    # 查找前一天的记录
                    prev_day = history[i - 1]
                    prev_product = next((p for p in prev_day if p.code == product.code), None)

                    if prev_product and prev_product.net_value and product.net_value:
                        if prev_product.net_value == 0:
                            daily_return = None
                        else:
                            daily_return = ((product.net_value - prev_product.net_value) / prev_product.net_value) * 100
                    else:
                        daily_return = None
                else:
                    daily_return = None

                daily_returns[product.code].append({
                    "date": product.fetch_time,
                    "net_value": product.net_value,
                    "daily_return": daily_return,
                })

        return daily_returns

    def format_bonus_report(self, bonus_periods: List[BonusPeriod]) -> str:
        """格式化红利期报告

        Args:
            bonus_periods: 红利期列表

        Returns:
            格式化的报告字符串
        """
        active = [b for b in bonus_periods if b.is_active]
        ended = [b for b in bonus_periods if not b.is_active]

        lines = [
            "=" * 60,
            "红利期分析报告",
            "=" * 60,
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"红利期定义: {self.bonus_days} 天内收益率 >= {self.bonus_threshold}%",
            "",
            f"处于红利期的产品: {len(active)} 个",
            "",
        ]

        if active:
            lines.append("--- 处于红利期的产品 ---")
            lines.append(f"{'产品名称':<30} {'代码':<12} {'银行':<10} {'收益率':>10} {'天数':>6}")
            lines.append("-" * 70)
            for b in sorted(active, key=lambda x: x.total_return, reverse=True):
                lines.append(f"{b.product_name:<28} {b.product_code:<12} {b.bank:<10} {b.total_return:>9.2f}% {b.days_since_start:>5}")
            lines.append("")

        if ended:
            lines.append("--- 已结束红利期的产品 ---")
            lines.append(f"{'产品名称':<30} {'代码':<12} {'银行':<10} {'收益率':>10} {'天数':>6}")
            lines.append("-" * 70)
            for b in sorted(ended, key=lambda x: x.total_return, reverse=True)[:10]:
                lines.append(f"{b.product_name:<28} {b.product_code:<12} {b.bank:<10} {b.total_return:>9.2f}% {b.days_since_start:>5}")
            lines.append("")

        lines.append("=" * 60)

        return "\n".join(lines)

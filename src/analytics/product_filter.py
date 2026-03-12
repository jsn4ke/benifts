"""产品筛选和分析功能"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from ..models.product import Product

logger = logging.getLogger(__name__)


class ProductFilter:
    """产品筛选器

    提供各种产品筛选和统计功能。
    """

    @staticmethod
    def filter_by_status(products: List[Product], status: str) -> List[Product]:
        """按状态筛选产品

        Args:
            products: 产品列表
            status: 产品状态（如"开放中"、"未开放"）

        Returns:
            符合状态的产品列表
        """
        filtered = [p for p in products if p.status == status]
        logger.info(f"筛选 '{status}' 产品: {len(filtered)} 个")
        return filtered

    @staticmethod
    def filter_by_bank(products: List[Product], bank: str) -> List[Product]:
        """按银行筛选产品

        Args:
            products: 产品列表
            bank: 银行名称

        Returns:
            符合银行的产品列表
        """
        filtered = [p for p in products if p.bank == bank]
        logger.info(f"筛选 '{bank}' 产品: {len(filtered)} 个")
        return filtered

    @staticmethod
    def filter_by_risk_level(products: List[Product], risk_level: str) -> List[Product]:
        """按风险等级筛选产品

        Args:
            products: 产品列表
            risk_level: 风险等级（如 R1, R2, R3）

        Returns:
            符合风险等级的产品列表
        """
        filtered = [p for p in products if p.risk_level == risk_level]
        logger.info(f"筛选 '{risk_level}' 风险产品: {len(filtered)} 个")
        return filtered

    @staticmethod
    def filter_by_net_value_range(
        products: List[Product],
        min_value: Optional[float] = None,
        max_value: Optional[float] = None
    ) -> List[Product]:
        """按净值范围筛选产品

        Args:
            products: 产品列表
            min_value: 最小净值（包含）
            max_value: 最大净值（包含）

        Returns:
            符合净值范围的产品列表
        """
        filtered = []
        for p in products:
            if p.net_value is None:
                continue
            if min_value is not None and p.net_value < min_value:
                continue
            if max_value is not None and p.net_value > max_value:
                continue
            filtered.append(p)

        logger.info(f"筛选净值范围 [{min_value}, {max_value}] 产品: {len(filtered)} 个")
        return filtered

    @staticmethod
    def filter_by_fetch_time(
        products: List[Product],
        hours: int = 24
    ) -> List[Product]:
        """筛选最近 N 小时获取的产品

        Args:
            products: 产品列表
            hours: 小时数

        Returns:
            最近获取的产品列表
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        filtered = [p for p in products if p.fetch_time >= cutoff]
        logger.info(f"筛选最近 {hours} 小时产品: {len(filtered)} 个")
        return filtered

    @staticmethod
    def get_statistics(products: List[Product]) -> Dict[str, Any]:
        """获取产品统计信息

        Args:
            products: 产品列表

        Returns:
            统计信息字典
        """
        stats = {
            "total": len(products),
            "by_bank": {},
            "by_status": {},
            "by_risk_level": {},
            "avg_net_value": None,
            "min_net_value": None,
            "max_net_value": None,
        }

        # 收集净值数据
        net_values = [p.net_value for p in products if p.net_value is not None]

        if net_values:
            stats["avg_net_value"] = sum(net_values) / len(net_values)
            stats["min_net_value"] = min(net_values)
            stats["max_net_value"] = max(net_values)

        # 统计各分类
        for p in products:
            # 按银行
            if p.bank:
                stats["by_bank"][p.bank] = stats["by_bank"].get(p.bank, 0) + 1

            # 按状态
            if p.status:
                stats["by_status"][p.status] = stats["by_status"].get(p.status, 0) + 1

            # 按风险等级
            if p.risk_level:
                stats["by_risk_level"][p.risk_level] = stats["by_risk_level"].get(p.risk_level, 0) + 1

        logger.info(f"生成统计信息: 总计 {stats['total']} 个产品")
        return stats

    @staticmethod
    def find_new_products(
        previous: List[Product],
        current: List[Product]
    ) -> List[Product]:
        """查找新增产品

        Args:
            previous: 之前的产品列表
            current: 当前产品列表

        Returns:
            新增的产品列表（在 current 中但不在 previous 中）
        """
        previous_codes = {p.code for p in previous}
        new_products = [p for p in current if p.code not in previous_codes]

        logger.info(f"发现 {len(new_products)} 个新增产品")
        return new_products

    @staticmethod
    def track_net_value_changes(
        previous: List[Product],
        current: List[Product]
    ) -> Dict[str, Dict[str, Any]]:
        """追踪净值变化

        Args:
            previous: 之前的产品列表
            current: 当前产品列表

        Returns:
            净值变化字典 {产品代码: 变化信息}
        """
        previous_dict = {p.code: p for p in previous}

        changes = {}
        for p in current:
            if p.code in previous_dict:
                prev = previous_dict[p.code]
                if prev.net_value is not None and p.net_value is not None:
                    change = p.net_value - prev.net_value
                    if change != 0:
                        changes[p.code] = {
                            "name": p.name,
                            "previous": prev.net_value,
                            "current": p.net_value,
                            "change": change,
                            "change_percent": (change / prev.net_value) * 100 if prev.net_value != 0 else 0,
                        }

        logger.info(f"发现 {len(changes)} 个产品净值变化")
        return changes

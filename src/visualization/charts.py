"""数据可视化模块"""

import logging
from typing import List, Optional
from datetime import datetime
from pathlib import Path

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.font_manager import FontProperties
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logging.warning("matplotlib not available, visualization will be disabled")

from ..analytics.net_value_analyzer import NetValueChange, BonusPeriod
from ..models.product import Product

logger = logging.getLogger(__name__)


class DataVisualizer:
    """数据可视化器

    使用 matplotlib 生成各种图表。
    """

    def __init__(self, output_dir: str = "data/charts"):
        """初始化可视化器

        Args:
            output_dir: 图表输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 设置中文字体（如果可用）
        if MATPLOTLIB_AVAILABLE:
            try:
                # 尝试使用系统字体，避免硬编码路径
                self.font = None  # 禁用中文字体，使用默认字体
            except:
                self.font = None
        else:
            self.font = None

    def plot_net_value_trend(
        self,
        products: List[Product],
        top_n: int = 10,
        save_path: Optional[str] = None
    ) -> Path:
        """绘制净值趋势图

        Args:
            products: 产品列表
            top_n: 显示前 N 个产品
            save_path: 保存路径（可选）

        Returns:
            图表文件路径
        """
        if not MATPLOTLIB_AVAILABLE:
            logger.warning("matplotlib not available, skipping net value trend plot")
            return None

        # 筛选有净值数据的产品
        products_with_nv = [p for p in products if p.net_value is not None]

        if not products_with_nv:
            logger.warning("No products with net value data")
            return None

        # 按净值排序，取前 N 个
        top_products = sorted(products_with_nv, key=lambda x: x.net_value, reverse=True)[:top_n]

        fig, ax = plt.subplots(figsize=(12, 6))

        # 绘制柱状图
        names = [p.name[:20] for p in top_products]  # 截断长名称
        codes = [p.code for p in top_products]
        net_values = [p.net_value for p in top_products]

        x_pos = range(len(names))
        bars = ax.bar(x_pos, net_values, color='skyblue')

        # 设置标签
        ax.set_xticks(x_pos)
        ax.set_xticklabels(codes, rotation=45, ha='right', fontsize=8)
        ax.set_ylabel('净值', fontproperties=self.font)
        ax.set_title(f'前 {top_n} 个理财产品净值对比', fontproperties=self.font)

        # 添加数值标签
        for i, (bar, val) in enumerate(zip(bars, net_values)):
            ax.text(bar.get_x() + bar.get_width() / 2,
                   bar.get_height() + 0.005,
                   f'{val:.4f}',
                   ha='center', va='bottom', fontsize=8)

        plt.tight_layout()

        filepath = save_path or self.output_dir / "net_value_trend.png"
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"净值趋势图已保存: {filepath}")
        return filepath

    def plot_bonus_periods(
        self,
        bonus_periods: List[BonusPeriod],
        save_path: Optional[str] = None
    ) -> Path:
        """绘制红利期图表

        Args:
            bonus_periods: 红利期列表
            save_path: 保存路径（可选）

        Returns:
            图表文件路径
        """
        if not MATPLOTLIB_AVAILABLE:
            logger.warning("matplotlib not available, skipping bonus periods plot")
            return None

        # 筛选活跃的红利期
        active_periods = [b for b in bonus_periods if b.is_active]

        if not active_periods:
            logger.warning("No active bonus periods")
            return None

        # 按收益率排序
        sorted_periods = sorted(active_periods, key=lambda x: x.total_return, reverse=True)

        fig, ax = plt.subplots(figsize=(12, 6))

        names = [p.product_name[:20] for p in sorted_periods]
        codes = [p.product_code for p in sorted_periods]
        returns = [p.total_return for p in sorted_periods]

        x_pos = range(len(names))
        colors = ['lightcoral' if r >= 1.0 else 'gold' for r in returns]

        bars = ax.bar(x_pos, returns, color=colors)

        # 设置标签
        ax.set_xticks(x_pos)
        ax.set_xticklabels(codes, rotation=45, ha='right', fontsize=8)
        ax.set_ylabel('收益率 (%)', fontproperties=self.font)
        ax.set_title(f'红利期产品收益率 (共 {len(active_periods)} 个)', fontproperties=self.font)

        # 添加收益率阈值线
        ax.axhline(y=0.5, color='r', linestyle='--', linewidth=1, label='红利期阈值 0.5%')

        # 添加数值标签
        for i, (bar, val) in enumerate(zip(bars, returns)):
            ax.text(bar.get_x() + bar.get_width() / 2,
                   bar.get_height() + 0.1,
                   f'{val:.2f}%',
                   ha='center', va='bottom', fontsize=8)

        ax.legend(fontsize=8, loc='upper right')
        plt.tight_layout()

        filepath = save_path or self.output_dir / "bonus_periods.png"
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"红利期图表已保存: {filepath}")
        return filepath

    def plot_daily_returns(
        self,
        daily_returns: dict[str, List[dict]],
        product_code: str,
        save_path: Optional[str] = None
    ) -> Path:
        """绘制每日收益率趋势

        Args:
            daily_returns: 每日收益率数据 {产品代码: [{日期, 净值, 日收益率}]}
            product_code: 要显示的产品代码
            save_path: 保存路径（可选）

        Returns:
            图表文件路径
        """
        if not MATPLOTLIB_AVAILABLE:
            logger.warning("matplotlib not available, skipping daily returns plot")
            return None

        if product_code not in daily_returns:
            logger.warning(f"Product {product_code} not found in daily returns")
            return None

        data = daily_returns[product_code]
        if not data or len(data) == 0:
            logger.warning(f"No daily return data for product {product_code}")
            return None

        # 按日期排序
        sorted_data = sorted(data, key=lambda x: x['date'])

        dates = [d['date'] for d in sorted_data]
        net_values = [d.get('net_value') for d in sorted_data]
        daily_return_values = [d.get('daily_return') for d in sorted_data]

        # 过滤有效数据
        valid_data = [(d, nv, rv) for d, nv, rv in zip(dates, net_values, daily_return_values)
                     if nv is not None]

        if not valid_data:
            return None

        dates = [d for d, nv, rv in valid_data]
        net_values = [nv for d, nv, rv in valid_data]
        return_values = [rv for d, nv, rv in valid_data]

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8))

        # 净值趋势
        ax1.plot(dates, net_values, marker='o', linewidth=2, color='blue')
        ax1.set_ylabel('净值', fontproperties=self.font)
        ax1.set_title('净值趋势', fontproperties=self.font)
        ax1.grid(True, alpha=0.3)

        # 每日收益率
        valid_returns = [(d, rv) for d, rv in zip(dates, return_values) if rv is not None]
        if valid_returns:
            r_dates = [d for d, rv in valid_returns]
            r_values = [rv for d, rv in valid_returns]
            ax2.bar(r_dates, r_values, alpha=0.6, color='green')
            ax2.axhline(y=0, color='r', linestyle='--', linewidth=1)
            ax2.set_ylabel('每日收益率 (%)', fontproperties=self.font)
            ax2.set_title('每日收益率', fontproperties=self.font)
            ax2.grid(True, alpha=0.3)

        # 格式化日期轴
        try:
            date_format = mdates.DateFormatter('%m-%d')
            ax1.xaxis.set_major_formatter(date_format)
            ax2.xaxis.set_major_formatter(date_format)
            plt.setp(ax1, xticks=mdates.DayLocator())
            plt.setp(ax2, xticks=mdates.DayLocator())

            fig.autofmt_xdate()
        except Exception as e:
            logger.warning(f"Date format setup failed: {e}")
        plt.tight_layout()

        filepath = save_path or self.output_dir / f"daily_return_{product_code}.png"
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"每日收益率图表已保存: {filepath}")
        return filepath

    def plot_value_distribution(
        self,
        products: List[Product],
        save_path: Optional[str] = None
    ) -> Path:
        """绘制净值分布直方图

        Args:
            products: 产品列表
            save_path: 保存路径（可选）

        Returns:
            图表文件路径
        """
        if not MATPLOTLIB_AVAILABLE:
            logger.warning("matplotlib not available, skipping value distribution plot")
            return None

        net_values = [p.net_value for p in products if p.net_value is not None]

        if not net_values:
            logger.warning("No products with net value data")
            return None

        fig, ax = plt.subplots(figsize=(10, 6))

        n, bins, patches = ax.hist(net_values, bins=20, edgecolor='black', alpha=0.7)

        # 添加统计信息
        mean_val = sum(net_values) / len(net_values)
        ax.axvline(mean_val, color='r', linestyle='--', linewidth=2, label=f'均值: {mean_val:.4f}')

        ax.set_xlabel('净值', fontproperties=self.font)
        ax.set_ylabel('产品数量', fontproperties=self.font)
        ax.set_title(f'净值分布 (共 {len(net_values)} 个产品)', fontproperties=self.font)
        ax.legend()

        plt.tight_layout()

        filepath = save_path or self.output_dir / "value_distribution.png"
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"净值分布图已保存: {filepath}")
        return filepath

    def generate_all_charts(
        self,
        products: List[Product],
        bonus_periods: Optional[List[BonusPeriod]] = None,
        daily_returns: Optional[dict[str, List[dict]]] = None
    ) -> dict[str, Path]:
        """生成所有图表

        Args:
            products: 产品列表
            bonus_periods: 红利期列表（可选）
            daily_returns: 每日收益率数据（可选）

        Returns:
            {图表名称: 文件路径}
        """
        if not MATPLOTLIB_AVAILABLE:
            logger.warning("matplotlib not available, cannot generate charts")
            return {}

        results = {}

        # 净值趋势图
        try:
            results['net_value_trend'] = self.plot_net_value_trend(products)
        except Exception as e:
            logger.error(f"Failed to generate net value trend plot: {e}")

        # 红利期图
        if bonus_periods:
            try:
                results['bonus_periods'] = self.plot_bonus_periods(bonus_periods)
            except Exception as e:
                logger.error(f"Failed to generate bonus periods plot: {e}")

        # 净值分布图
        try:
            results['value_distribution'] = self.plot_value_distribution(products)
        except Exception as e:
            logger.error(f"Failed to generate value distribution plot: {e}")

        # 每日收益率图
        if daily_returns:
            try:
                # 为前 3 个产品生成图表
                top_codes = list(daily_returns.keys())[:3]
                for code in top_codes:
                    chart_name = f'daily_return_{code}'
                    results[chart_name] = self.plot_daily_returns(daily_returns, code)
            except Exception as e:
                logger.error(f"Failed to generate daily returns plot: {e}")

        logger.info(f"Generated {len(results)} charts")
        return results

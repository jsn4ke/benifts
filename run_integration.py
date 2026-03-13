"""集成演示脚本

完整演示从数据获取到分析、可视化和通知的完整流程。
"""

import logging
from datetime import datetime
from pathlib import Path

from src.scrapers.cmb import CMBScraper
from src.analytics.net_value_analyzer import NetValueAnalyzer
from src.analytics.product_filter import ProductFilter, find_new_products
from src.storage.file_storage import FileStorage
from src.visualization.charts import DataVisualizer
from src.notifications.notifier import ConsoleNotifier, ProductNotifier

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """主函数：演示完整的数据流"""

    print("\n" + "=" * 60)
    print("B2 集成演示 - 理财产品净值分析与通知")
    print("=" * 60 + "\n")

    # 步骤 1: 获取产品数据
    print("\n[步骤 1/5] 获取招行理财产品数据...")
    scraper = CMBScraper()

    raw_products = scraper.fetch_products()
    if not raw_products:
        logger.error("未能获取产品数据")
        return

    products = scraper.to_product_list(raw_products)
    print(f"✓ 获取到 {len(products)} 个产品")

    # 步骤 2: 统计分析
    print("\n[步骤 2/5] 生成统计报告...")
    stats = ProductFilter.get_statistics(products)

    print(f"  总产品数: {stats['total']}")
    print(f"  按银行统计: {stats['by_bank']}")
    print(f"  按状态统计: {stats['by_status']}")
    if stats.get('avg_net_value'):
        print(f"  平均净值: {stats['avg_net_value']:.4f}")
        print(f"  净值范围: {stats['min_net_value']:.4f} - {stats['max_net_value']:.4f}")

    # 步骤 3: 净值分析
    print("\n[步骤 3/5] 净值变化分析...")
    analyzer = NetValueAnalyzer(bonus_days=30, bonus_threshold=0.5, high_growth_threshold=1.0)

    # 模拟历史数据（第一次运行）
    # 在实际场景中，应该从存储加载历史数据
    # 这里为了演示，我们使用当前数据作为"历史数据"
    previous_products = products.copy()
    for p in previous_products:
        if p.net_value:
            # 模拟昨天的净值（略低）
            p.net_value = p.net_value * 0.99

    # 分析净值变化
    changes = analyzer.analyze_net_value_changes(previous_products, products)
    print(f"✓ 发现 {len(changes)} 个产品净值变化")

    # 查找高增长产品
    high_growth = analyzer.find_high_growth_products(changes)
    print(f"✓ 发现 {len(high_growth)} 个高增长产品（日 >= 1.0%）")
    if high_growth:
        print("\n  高增长产品:")
        for c in high_growth[:5]:
            print(f"    - {c.product_name} ({c.product_code}): {c.change_percent:+.2f}%")

    # 步骤 4: 红利期识别
    print("\n[步骤 4/5] 红利期识别...")
    bonus_periods = analyzer.identify_bonus_periods(products, {})

    active_bonus = [b for b in bonus_periods if b.is_active]
    print(f"✓ 发现 {len(active_bonus)} 个产品处于红利期")

    if active_bonus:
        print("\n  红利期产品:")
        for b in sorted(active_bonus, key=lambda x: x.total_return, reverse=True)[:5]:
            print(f"    - {b.product_name} ({b.product_code}): {b.total_return:+.2f}% ({b.days_since_start}天)")

    # 生成红利期报告
    bonus_report = analyzer.format_bonus_report(bonus_periods)
    print("\n" + "-" * 60)
    print("红利期分析报告:")
    print("-" * 60)
    print(bonus_report)
    print("-" * 60)

    # 步骤 5: 生成图表
    print("\n[步骤 5/5] 生成可视化图表...")
    visualizer = DataVisualizer("data/charts")

    charts = visualizer.generate_all_charts(
        products=products,
        bonus_periods=bonus_periods,
    )

    print(f"✓ 生成 {len(charts)} 个图表:")
    for name, path in charts.items():
        print(f"    - {name}: {path}")

    # 步骤 6: 发送通知
    print("\n[步骤 6/5] 发送通知（使用控制台模拟）...")
    notifier = ProductNotifier(ConsoleNotifier())

    # 通知高增长产品
    if high_growth:
        notifier.notify_high_growth_products(high_growth, "user@example.com")

    # 通知红利期产品
    if active_bonus:
        notifier.notify_bonus_periods(bonus_periods, "user@example.com")

    # 步骤 7: 保存数据
    print("\n[步骤 7/5] 保存数据到文件...")
    storage = FileStorage("data")
    storage.save_csv(products, "products_latest.csv")
    storage.save_json(products, "products_latest.json")
    print(f"✓ 数据已保存")

    # 完成
    print("\n" + "=" * 60)
    print("集成演示完成！")
    print("=" * 60)

    # 总结
    print("\n总结:")
    print(f"  - 获取产品: {len(products)} 个")
    print(f"  - 净值变化: {len(changes)} 个")
    print(f"  - 高增长产品: {len(high_growth)} 个")
    print(f"  - 红利期产品: {len(active_bonus)} 个")
    print(f"  - 生成图表: {len(charts)} 个")
    print(f"\n输出目录:")
    print(f"  - 数据文件: data/processed/")
    print(f"  - 图表文件: data/charts/")
    print(f"\n查看图表: 打开 data/charts/ 目录中的 PNG 文件")


if __name__ == "__main__":
    main()

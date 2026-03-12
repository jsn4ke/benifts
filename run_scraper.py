"""主爬虫运行脚本

使用方法:
    python run_scraper.py                    # 运行一次，保存所有产品
    python run_scraper.py --status 开放中     # 只保存开放中产品
    python run_scraper.py --periodic 2       # 每 2 小时运行一次（无限循环）
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.scrapers.cmb import CMBScraper
from src.storage.file_storage import FileStorage
from src.analytics.product_filter import ProductFilter

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)


def run_scraper(status_filter: Optional[str] = None) -> None:
    """运行爬虫

    Args:
        status_filter: 状态筛选条件（如"开放中"）
    """
    logger.info("=" * 60)
    logger.info("开始爬取招行理财产品数据")
    logger.info("=" * 60)

    # 创建爬虫
    scraper = CMBScraper()

    # 获取原始数据
    logger.info("正在获取产品数据...")
    raw_products = scraper.fetch_products()

    if not raw_products:
        logger.warning("未获取到任何产品数据")
        return

    logger.info(f"成功获取 {len(raw_products)} 个产品")

    # 转换为 Product 对象
    products = scraper.to_product_list(raw_products)

    # 筛选状态
    if status_filter:
        products = ProductFilter.filter_by_status(products, status_filter)
        logger.info(f"筛选 '{status_filter}' 产品: {len(products)} 个")

    # 生成带时间戳的文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"cmb_products_{timestamp}"

    # 保存数据
    storage = FileStorage()

    # 保存 CSV
    csv_file = storage.save_csv(products, f"{base_filename}.csv")
    logger.info(f"CSV 文件已保存: {csv_file}")

    # 保存 JSON
    json_file = storage.save_json(products, f"{base_filename}.json")
    logger.info(f"JSON 文件已保存: {json_file}")

    # 保存到 SQLite
    db_file = storage.save_sqlite(products, f"{base_filename}.db")
    logger.info(f"SQLite 文件已保存: {db_file}")

    # 生成统计信息
    stats = ProductFilter.get_statistics(products)
    logger.info("=" * 60)
    logger.info("统计信息:")
    logger.info(f"  总产品数: {stats['total']}")
    logger.info(f"  平均净值: {stats['avg_net_value']:.4f}" if stats['avg_net_value'] else "  平均净值: N/A")
    logger.info(f"  最小净值: {stats['min_net_value']:.4f}" if stats['min_net_value'] else "  最小净值: N/A")
    logger.info(f"  最大净值: {stats['max_net_value']:.4f}" if stats['max_net_value'] else "  最大净值: N/A")
    logger.info(f"  按状态: {stats['by_status']}")
    logger.info(f"  按风险等级: {stats['by_risk_level']}")
    logger.info("=" * 60)

    logger.info("爬取完成!")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="招行理财产品爬虫")
    parser.add_argument(
        "--status",
        type=str,
        help="筛选产品状态（如'开放中'、'未开放'）"
    )
    parser.add_argument(
        "--periodic",
        type=float,
        help="定期运行间隔（小时）"
    )
    parser.add_argument(
        "--max-runs",
        type=int,
        help="定期运行的最大次数"
    )

    args = parser.parse_args()

    from src.utils.scheduler import Scheduler

    if args.periodic:
        # 定期运行模式
        scheduler = Scheduler(interval_hours=args.periodic)

        def task():
            run_scraper(status_filter=args.status)

        scheduler.run_periodic(task, max_runs=args.max_runs)
    else:
        # 单次运行模式
        run_scraper(status_filter=args.status)


if __name__ == "__main__":
    main()

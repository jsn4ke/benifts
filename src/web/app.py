"""Web 应用程序 - 理财产品数据查看界面"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from flask import Flask, render_template, jsonify, request, send_from_directory

from ..analytics.net_value_analyzer import NetValueAnalyzer
from ..scrapers.cmb import CMBScraper
from ..storage.file_storage import FileStorage

logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates', static_folder='static')

# 全局配置
DATA_DIR = Path("data")
CHARTS_DIR = DATA_DIR / "charts"

# 分析器实例（使用默认配置）
analyzer = NetValueAnalyzer(
    bonus_days=30,
    bonus_threshold=0.5,
    high_growth_threshold=1.0
)


@app.route('/')
def index():
    """首页 - 产品列表"""
    try:
        # 尝试加载最新数据
        storage = FileStorage(str(DATA_DIR))

        # 优先加载 CSV 格式
        products = []
        try:
            products = storage.load_csv("products_latest.csv")
            data_source = "CSV"
        except FileNotFoundError:
            try:
                products = storage.load_json("products_latest.json")
                data_source = "JSON"
            except FileNotFoundError:
                data_source = "暂无数据"

        # 生成统计信息
        stats = {
            "total": len(products),
            "data_source": data_source,
            "by_bank": {},
            "by_status": {},
            "avg_net_value": None,
            "min_net_value": None,
            "max_net_value": None
        }

        if products:
            net_values = [p.net_value for p in products if p.net_value is not None]
            if net_values:
                stats["avg_net_value"] = sum(net_values) / len(net_values)
                stats["min_net_value"] = min(net_values)
                stats["max_net_value"] = max(net_values)

            for p in products:
                if p.bank:
                    stats["by_bank"][p.bank] = stats["by_bank"].get(p.bank, 0) + 1
                if p.status:
                    stats["by_status"][p.status] = stats["by_status"].get(p.status, 0) + 1

        # 检查图表是否存在
        charts = {}
        chart_files = {
            "net_value_trend": "净值趋势图",
            "bonus_periods": "红利期图表",
            "value_distribution": "净值分布图"
        }
        for key, name in chart_files.items():
            chart_path = CHARTS_DIR / f"{key}.png"
            charts[key] = {"exists": chart_path.exists(), "name": name, "path": str(chart_path)}

        return render_template(
            'index.html',
            products=products,
            stats=stats,
            charts=charts,
            last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    except Exception as e:
        logger.error(f"加载首页失败: {e}", exc_info=True)
        return render_template('error.html', error=str(e)), 500


@app.route('/api/refresh')
def refresh_data():
    """API: 刷新数据（重新抓取）"""
    try:
        # 创建爬虫并获取数据
        scraper = CMBScraper()
        raw_products = scraper.fetch_products()

        if not raw_products:
            return jsonify({"success": False, "error": "未能获取产品数据"}), 500

        products = scraper.to_product_list(raw_products)

        # 保存数据
        storage = FileStorage(str(DATA_DIR))
        storage.save_csv(products, "products_latest.csv")
        storage.save_json(products, "products_latest.json")

        # 生成分析数据
        # 模拟历史数据用于比较
        previous_products = [p for p in products]
        for p in previous_products:
            if p.net_value:
                p.net_value = p.net_value * 0.99  # 模拟昨天的净值

        changes = analyzer.analyze_net_value_changes(previous_products, products)
        high_growth = analyzer.find_high_growth_products(changes)
        bonus_periods = analyzer.identify_bonus_periods(products, {})

        return jsonify({
            "success": True,
            "total": len(products),
            "changes": len(changes),
            "high_growth": len(high_growth),
            "bonus_periods": len([b for b in bonus_periods if b.is_active])
        })
    except Exception as e:
        logger.error(f"刷新数据失败: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/analysis')
def analysis():
    """API: 净值分析数据"""
    try:
        storage = FileStorage(str(DATA_DIR))

        # 加载产品数据
        try:
            products = storage.load_csv("products_latest.csv")
        except FileNotFoundError:
            try:
                products = storage.load_json("products_latest.json")
            except FileNotFoundError:
                return jsonify({"success": False, "error": "暂无产品数据"})

        # 模拟历史数据
        previous_products = [p for p in products]
        for p in previous_products:
            if p.net_value:
                p.net_value = p.net_value * 0.99

        # 执行分析
        changes = analyzer.analyze_net_value_changes(previous_products, products)
        high_growth = analyzer.find_high_growth_products(changes)
        bonus_periods = analyzer.identify_bonus_periods(products, {})

        # 格式化返回数据
        return jsonify({
            "success": True,
            "total_changes": len(changes),
            "total_bonus_periods": len(bonus_periods),
            "active_bonus_periods": len([b for b in bonus_periods if b.is_active]),
            "high_growth_count": len(high_growth),
            "changes": [
                {
                    "product_code": c.product_code,
                    "product_name": c.product_name,
                    "bank": c.bank,
                    "prev_value": c.prev_net_value,
                    "current_value": c.current_net_value,
                    "change_value": c.change_value,
                    "change_percent": c.change_percent,
                    "date": c.change_date.strftime("%Y-%m-%d") if c.change_date else None
                }
                for c in changes[:20]  # 限制返回数量
            ],
            "bonus_periods": [
                {
                    "product_code": b.product_code,
                    "product_name": b.product_name,
                    "bank": b.bank,
                    "is_active": b.is_active,
                    "total_return": b.total_return,
                    "days_since_start": b.days_since_start,
                    "daily_return": b.daily_return,
                    "annualized_return": b.annualized_return
                }
                for b in bonus_periods
            ],
            "high_growth": [
                {
                    "product_code": h.product_code,
                    "product_name": h.product_name,
                    "bank": h.bank,
                    "change_percent": h.change_percent
                }
                for h in high_growth
            ]
        })
    except Exception as e:
        logger.error(f"分析数据失败: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/products')
def products_api():
    """API: 产品列表"""
    try:
        storage = FileStorage(str(DATA_DIR))

        try:
            products = storage.load_csv("products_latest.csv")
        except FileNotFoundError:
            try:
                products = storage.load_json("products_latest.json")
            except FileNotFoundError:
                return jsonify({"success": False, "error": "暂无产品数据"})

        # 获取查询参数
        bank = request.args.get('bank')
        status = request.args.get('status')
        min_net_value = request.args.get('min_net_value', type=float)
        max_net_value = request.args.get('max_net_value', type=float)

        # 筛选
        if bank:
            products = [p for p in products if p.bank == bank]
        if status:
            products = [p for p in products if p.status == status]
        if min_net_value is not None:
            products = [p for p in products if p.net_value and p.net_value >= min_net_value]
        if max_net_value is not None:
            products = [p for p in products if p.net_value and p.net_value <= max_net_value]

        return jsonify({
            "success": True,
            "total": len(products),
            "products": [
                {
                    "name": p.name,
                    "code": p.code,
                    "bank": p.bank,
                    "net_value": p.net_value,
                    "status": p.status,
                    "risk_level": p.risk_level,
                    "currency": p.currency
                }
                for p in products
            ]
        })
    except Exception as e:
        logger.error(f"获取产品列表失败: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/charts/<filename>')
def serve_chart(filename):
    """提供图表文件"""
    try:
        return send_from_directory(CHARTS_DIR, filename)
    except FileNotFoundError:
        return jsonify({"error": "图表文件不存在"}), 404


@app.route('/bonus-report')
def bonus_report():
    """红利期报告页面"""
    return render_template('bonus_report.html')


@app.errorhandler(404)
def not_found(e):
    """404 错误处理"""
    return render_template('error.html', error="页面不存在"), 404


@app.errorhandler(500)
def server_error(e):
    """500 错误处理"""
    return render_template('error.html', error=f"服务器错误: {e}"), 500


def run_app(host: str = "0.0.0.0", port: int = 5000, debug: bool = True):
    """运行 Flask 应用

    Args:
        host: 监听地址
        port: 监听端口
        debug: 调试模式
    """
    logger.info(f"启动 Web 服务器: http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    run_app()

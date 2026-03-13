"""招商银行理财产品爬虫"""

import asyncio
import time
from datetime import datetime
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import logging

from .base import BaseScraper
from ..models.product import Product

logger = logging.getLogger(__name__)


class CMBScraper(BaseScraper):
    """招商银行理财产品爬虫实现

    使用 Playwright 处理 JavaScript 渲染的页面。
    """

    def __init__(self):
        super().__init__("招商银行")
        self.base_url = "https://finprod.paas.cmbchina.com/"

    def fetch_products(self) -> List[Dict]:
        """获取招商银行理财产品列表

        Returns:
            产品信息字典列表
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            try:
                # 访问页面
                logger.info(f"访问页面: {self.base_url}")
                page.goto(self.base_url, timeout=30000)

                # 等待页面完全加载
                page.wait_for_load_state("networkidle", timeout=15000)

                # 等待一段时间让 JavaScript 动态内容加载
                page.wait_for_timeout(2000)

                # 获取页面内容
                content = page.content()

                # 解析表格数据
                products = self._parse_table(content)

                logger.info(f"成功获取 {len(products)} 个产品")

                return products

            except Exception as e:
                logger.error(f"获取产品失败: {e}")
                return []

            finally:
                browser.close()

    def parse_product(self, raw_data: str) -> Dict:
        """解析单个产品信息

        Args:
            raw_data: HTML 内容

        Returns:
            标准化的产品信息字典
        """
        # 表格数据直接在 fetch_products 中解析
        pass

    def _parse_table(self, html: str) -> List[Dict]:
        """解析产品表格

        Args:
            html: HTML 内容

        Returns:
            产品信息字典列表
        """
        soup = BeautifulSoup(html, 'lxml')
        tables = soup.find_all('table')

        logger.info(f"找到 {len(tables)} 个表格")

        # 尝试每个表格
        products = []
        for table_idx, table in enumerate(tables):
            rows = table.find_all('tr')

            logger.info(f"表格 {table_idx}: {len(rows)} 行")

            if len(rows) < 2:
                continue

            # 尝试解析表格
            for row in rows[1:]:  # 跳过表头
                cols = row.find_all('td')
                if len(cols) >= 16:
                    try:
                        name = cols[0].get_text(strip=True)
                        code = cols[1].get_text(strip=True)

                        # 只保留有效产品（有名称和代码）
                        if name and code and len(code) > 3:
                            product = {
                                "name": name,
                                "code": code,
                                "product_type": cols[2].get_text(strip=True),
                                "sale_type": cols[3].get_text(strip=True),
                                "fund_type": cols[4].get_text(strip=True),
                                "issuer": cols[5].get_text(strip=True),
                                "risk_level": cols[6].get_text(strip=True),
                                "status": cols[7].get_text(strip=True),
                                "net_value": self._parse_float(cols[8].get_text(strip=True)),
                                "currency": cols[9].get_text(strip=True),
                                "min_amount": self._parse_float(cols[10].get_text(strip=True)),
                                "investor_scope": cols[11].get_text(strip=True),
                                "fee_standard": cols[12].get_text(strip=True),
                                "fee_method": cols[13].get_text(strip=True),
                                "notice_url": cols[14].get_text(strip=True),
                                "filing_number": cols[15].get_text(strip=True),
                            }
                            products.append(product)
                    except (ValueError, IndexError) as e:
                        logger.warning(f"解析产品行失败: {e}")
                        continue

        if not products:
            logger.error("未找到有效的产品数据")
        else:
            logger.info(f"解析成功 {len(products)} 个产品")
        return products

    def _parse_float(self, text: str) -> Optional[float]:
        """解析浮点数

        Args:
            text: 要解析的文本

        Returns:
            浮点数或 None
        """
        if not text:
            return None
        try:
            # 移除逗号并转换为浮点数
            clean_text = text.replace(",", "")
            return float(clean_text)
        except (ValueError, TypeError):
            logger.warning(f"无法解析浮点数: {text}")
            return None

    def to_product_list(self, raw_products: List[Dict]) -> List[Product]:
        """转换为 Product 对象列表

        Args:
            raw_products: 原始产品字典列表

        Returns:
            Product 对象列表
        """
        products = []
        for p in raw_products:
            try:
                product = Product(
                    name=p["name"],
                    code=p["code"],
                    bank="招商银行",
                    product_type=p.get("product_type"),
                    sale_type=p.get("sale_type"),
                    fund_type=p.get("fund_type"),
                    issuer=p.get("issuer"),
                    risk_level=p.get("risk_level"),
                    status=p.get("status"),
                    net_value=p.get("net_value"),
                    currency=p.get("currency"),
                    min_amount=p.get("min_amount"),
                    investor_scope=p.get("investor_scope"),
                    fee_standard=p.get("fee_standard"),
                    fee_method=p.get("fee_method"),
                    notice_url=p.get("notice_url"),
                    filing_number=p.get("filing_number"),
                    fetch_time=datetime.now(),
                    source="Playwright",
                )
                products.append(product)
            except Exception as e:
                logger.error(f"转换 Product 对象失败: {e}, 原始数据: {p}")
                continue

        logger.info(f"转换成功 {len(products)} 个 Product 对象")
        return products

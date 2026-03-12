"""招商银行爬虫测试"""

import pytest

from src.scrapers.cmb import CMBScraper


class TestCMBScraper:
    """CMBScraper 测试"""

    def test_scraper_initialization(self):
        """测试爬虫初始化"""
        scraper = CMBScraper()
        assert scraper.name == "招商银行"
        assert scraper.base_url == "https://finprod.paas.cmbchina.com/"

    def test_parse_float(self):
        """测试浮点数解析"""
        scraper = CMBScraper()

        # 正常值
        assert scraper._parse_float("1.0234") == 1.0234
        assert scraper._parse_float("100.00") == 100.0
        assert scraper._parse_float("1.05") == 1.05

        # 带逗号
        assert scraper._parse_float("1,0169") == 1.0169

        # 空值
        assert scraper._parse_float("") is None
        assert scraper._parse_float("点击查看") is None
        assert scraper._parse_float(None) is None

    def test_to_product_list_basic(self):
        """测试基本的转换为 Product 对象列表"""
        scraper = CMBScraper()

        raw_products = [
            {
                "name": "测试产品",
                "code": "TEST001",
                "product_type": "代销理财",
                "sale_type": "代销",
                "fund_type": "公募",
                "issuer": "招银理财",
                "risk_level": "R2",
                "status": "未开放",
                "net_value": "1.0234",
                "currency": "人民币",
                "min_amount": "100.00",
                "investor_scope": "遵循风险匹配原则",
                "fee_standard": "认购费：不收取固定管理费：0.15%",
                "fee_method": "认购费固定管理费销售服务费其他费用详见产品公告",
                "notice_url": "https://example.com",
                "filing_number": "备案001",
            }
        ]

        products = scraper.to_product_list(raw_products)

        assert len(products) == 1
        assert products[0].name == "测试产品"
        assert products[0].code == "TEST001"
        assert products[0].bank == "招商银行"
        assert products[0].risk_level == "R2"
        assert products[0].net_value == 1.0234
        assert products[0].currency == "人民币"
        assert products[0].min_amount == 100.0

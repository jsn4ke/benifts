"""上海银行理财产品爬虫（占位符）"""

from .base import BaseScraper


class SHBankScraper(BaseScraper):
    """上海银行理财产品爬虫实现（占位符）

    待实现：调研页面结构并实现爬虫逻辑
    """

    def __init__(self):
        super().__init__("上海银行")
        # 待确认的实际网址
        self.base_url = "https://www.bankofshanghai.com/lcsp/lcsp_index.jsp"

    def fetch_products(self) -> list:
        """获取上海银行理财产品列表

        Returns:
            产品信息字典列表
        """
        # 待实现
        raise NotImplementedError("SHBankScraper 待实现")

    def parse_product(self, raw_data: str) -> dict:
        """解析单个产品信息

        Args:
            raw_data: HTML 内容

        Returns:
            标准化的产品信息字典
        """
        # 待实现
        pass

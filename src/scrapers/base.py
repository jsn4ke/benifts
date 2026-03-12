"""基础爬虫抽象类"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """基础爬虫抽象类

    所有银行爬虫都应继承此类并实现相应方法。
    """

    def __init__(self, name: str):
        """初始化爬虫

        Args:
            name: 银行名称
        """
        self.name = name
        self.session = None  # 子类实现 HTTP 会话

    @abstractmethod
    def fetch_products(self) -> List[Dict]:
        """获取产品列表

        Returns:
            产品信息字典列表，每个字典包含一个产品的信息
        """
        pass

    @abstractmethod
    def parse_product(self, raw_data) -> Dict:
        """解析单个产品信息

        Args:
            raw_data: 原始数据（HTML 或 JSON）

        Returns:
            标准化的产品信息字典
        """
        pass

    def get_headers(self) -> Dict[str, str]:
        """获取请求头

        Returns:
            HTTP 请求头字典
        """
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }

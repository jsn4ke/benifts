"""理财产品数据模型"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Product:
    """理财产品数据模型

    包含各银行理财产品的通用字段。
    """

    # 基本信息
    name: str
    code: str
    bank: str
    product_type: Optional[str] = None
    sale_type: Optional[str] = None  # 自有或代销
    fund_type: Optional[str] = None  # 公募或私募
    issuer: Optional[str] = None  # 发行机构
    risk_level: Optional[str] = None

    # 状态信息
    status: Optional[str] = None  # 开放中/未开放

    # 净值信息
    net_value: Optional[float] = None
    currency: str = "人民币"

    # 购买信息
    min_amount: Optional[float] = None
    investor_scope: Optional[str] = None

    # 费用信息
    fee_standard: Optional[str] = None
    fee_method: Optional[str] = None

    # 其他
    notice_url: Optional[str] = None
    filing_number: Optional[str] = None

    # 元数据
    fetch_time: datetime = field(default_factory=datetime.now)
    source: Optional[str] = None  # API 或爬虫

    def to_dict(self) -> dict:
        """转换为字典格式

        Returns:
            产品信息的字典表示
        """
        return {
            "name": self.name,
            "code": self.code,
            "bank": self.bank,
            "product_type": self.product_type,
            "sale_type": self.sale_type,
            "fund_type": self.fund_type,
            "issuer": self.issuer,
            "risk_level": self.risk_level,
            "status": self.status,
            "net_value": self.net_value,
            "currency": self.currency,
            "min_amount": self.min_amount,
            "investor_scope": self.investor_scope,
            "fee_standard": self.fee_standard,
            "fee_method": self.fee_method,
            "notice_url": self.notice_url,
            "filing_number": self.filing_number,
            "fetch_time": self.fetch_time.isoformat(),
            "source": self.source,
        }

# 项目备忘录 (Project Memo)

> 记录项目中的重要决策、技术选型、模式和经验教训

---

## 技术选型 (Technology Decisions)

| 组件 | 选择 | 原因 | 决策时间 |
|------|------|------|----------|
| 编程语言 | Python | 爬虫生态成熟（requests/selenium/playwright），数据分析库丰富（pandas/numpy） | 2026-03-12 |
| 数据获取优先级 | API > 爬虫 | API 更稳定，无需维护页面结构变化 | 2026-03-12 |
| 初始数据存储 | SQLite / CSV | 轻量级，无需额外配置，适合初期验证 | 2026-03-12 |
| 测试框架 | pytest | Python 标准测试框架，生态丰富 | 2026-03-12 |
| 虚拟环境 | venv | Python 内置，无需额外安装 | 2026-03-12 |

---

## 架构决策 (Architecture Decisions)

### [ADR-001] 模块化爬虫设计

**状态**: 已接受

**上下文**:
需要获取多个银行的理财产品数据，每个银行的数据结构和获取方式可能不同。

**决策**:
- 创建基础爬虫类 `BaseScraper`，定义通用接口
- 每个银行继承 `BaseScraper`，实现具体获取逻辑
- 数据模型统一，方便存储和分析

**后果**:
- 正面: 易于扩展新银行，便于维护，代码复用
- 负面: 需要额外的抽象层

### [ADR-002] 先招行后上海银行

**状态**: 已接受

**上下文**:
第一阶段需要获取招行和上海银行数据。

**决策**:
优先完成招行数据获取，验证爬虫框架后再扩展到上海银行。

**原因**:
- 招行页面结构已调研，数据明确
- 上海银行页面尚未找到，需要更多调研

---

## 代码模式 (Code Patterns)

### Pattern 1: 基础爬虫类

**用途**: 定义所有银行爬虫的通用接口

**示例**:
```python
# src/scrapers/base.py
from abc import ABC, abstractmethod
from typing import List, Dict
import requests
from bs4 import BeautifulSoup

class BaseScraper(ABC):
    """基础爬虫抽象类"""

    def __init__(self):
        self.session = requests.Session()

    @abstractmethod
    def fetch_products(self) -> List[Dict]:
        """获取产品列表"""
        pass

    @abstractmethod
    def parse_product(self, html: str) -> Dict:
        """解析单个产品信息"""
        pass
```

**使用场景**: 所有银行爬虫的基础类

### Pattern 2: 数据模型

**用途**: 定义理财产品数据结构

**示例**:
```python
# src/models/product.py
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Product:
    """理财产品数据模型"""
    name: str
    code: str
    risk_level: str
    status: str
    net_value: float
    currency: str
    min_amount: float
    fetch_time: datetime
    bank: str
```

**使用场景**: 数据存储和分析

---

## 问题解决记录 (Problem Solutions)

### [问题1] 招行数据获取方式未确定

**出现时间**: 2026-03-12

**问题**:
招行理财查询平台数据获取方式未知（静态 HTML 或 AJAX 请求）。

**解决方案**:
使用浏览器开发者工具分析网络请求，确定数据源。

**相关文件**: `src/scrapers/cmb.py`（待创建）

### [问题2] 上海银行理财产品页面未找到

**出现时间**: 2026-03-12

**问题**:
搜索结果中没有返回上海银行理财产品的明确链接。

**解决方案**:
直接访问上海银行官网查找，或联系银行获取 API 文档。

**状态**: 待解决

---

## 性能优化记录 (Performance Optimizations)

- 暂无

---

## 安全相关 (Security Notes)

- 不要在代码中硬编码敏感信息（使用 .env 文件）
- 遵守网站 robots.txt 规则
- 爬虫请求间添加随机延迟，避免封 IP
- User-Agent 轮换，模拟正常访问

---

## 待讨论/待决策 (Pending Decisions)

- 上海银行数据获取方案（页面调研结果）
- 数据更新频率（每日/实时）
- 新产品识别规则（定义"新上市"的标准）
- 数据库升级时机（何时从 SQLite 迁移）

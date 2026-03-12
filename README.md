# B2 - 银行理财产品数据获取与分析

> 分析各大银行新上市的理财产品，获取新上市时期的红利期利润

## 项目目标

- **最终目标**: 分析各大银行新上市的理财产品，获取新上市时期的红利期利润
- **第一阶段**: 获取招商银行和上海银行的理财产品数据

## 技术栈

- **语言**: Python 3.10+
- **数据获取**: 优先公开 API，无 API 则用爬虫（requests/BeautifulSoup4/Playwright）
- **数据存储**: SQLite / CSV（初期）
- **数据分析**: pandas, numpy
- **测试**: pytest

## 项目结构

```
b2/
├── src/                    # 源代码
│   ├── scrapers/          # 爬虫模块
│   ├── models/            # 数据模型
│   ├── storage/           # 数据存储
│   └── utils/             # 工具函数
├── tests/                 # 测试
├── data/                  # 数据目录
├── plans/                 # 迭代计划
├── .claude/               # Claude 配置
│   ├── rules/             # 项目规则
│   └── memory/            # 记忆文件
├── venv/                  # 虚拟环境
└── requirements.txt        # 依赖列表
```

## 开发指南

### 环境设置

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate    # Linux/Mac
# 或
venv\Scripts\activate       # Windows

# 安装依赖
pip install -r requirements.txt
```

### 运行测试

```bash
# 确保激活虚拟环境
pytest
pytest --cov=src  # 带覆盖率
```

### 代码规范

- 遵循 PEP 8 规范
- 使用类型注解
- 编写 docstring
- 测试覆盖率 ≥ 80%

## 调研结果

### 招商银行

- **数据源**: https://finprod.paas.cmbchina.com/
- **数据字段**: 16个（产品名称、代码、净值、风险等级等）
- **Open API**: https://openapi.cmbchina.com/（需注册查看）

### 上海银行

- **状态**: 待进一步调研

## 许可证

MIT

# 项目规则 (Project Rules)

> 这是项目级别的工作规则，用于指导 AI 助手在此项目中工作。

---

## 项目概述 (Project Overview)

**项目名称**: B2 - 银行理财产品数据获取与分析

**项目目标**: 分析各大银行新上市的理财产品，获取新上市时期的红利期利润

**第一阶段目标**: 获取招行和上海银行的理财产品数据

**项目类型**: 数据爬取与分析工具

**技术栈**:
- 语言: Python 3.10+
- 数据获取: 优先公开API，无API则用爬虫（requests/selenium/playwright）
- 数据存储: SQLite / CSV（初期），后续可升级
- 数据分析: pandas, numpy
- 测试框架: pytest
- 依赖管理: pip + venv

---

## 开发工作流 (Development Workflow)

### 🔴 Python 环境要求

**所有操作必须在 venv 环境下进行**:

```bash
# 激活虚拟环境
source venv/bin/activate    # Linux/Mac
# 或
venv\Scripts\activate       # Windows

# 退出虚拟环境
deactivate

# 执行命令前先检查
python -m venv --help       # 确认 venv 已安装
```

**环境检查清单**:
- [ ] ✅ 已激活 venv 环境才能执行 Python 命令
- [ ] ⛔ 禁止在系统 Python 环境下安装依赖
- [ ] ⛔ 禁止直接运行 `python script.py`，必须先 `source venv/bin/activate`

### 🔴 计划执行规范

**严格按照计划执行，严禁偏离**:

1. **计划文件版本管理**:
   - 计划文件命名格式: `plan<大版本>.<小版本>.<迭代版本>.md`
   - 示例: `plan0.1.0.md` → `plan0.1.1.md` → `plan0.1.2.md`
   - 每次迭代更新后创建新的计划文件

2. **执行原则**:
   - ⛔ **严格按最新计划执行**，禁止按旧计划工作
   - ⛔ **禁止擅自修改计划内容**，计划变更需更新版本号
   - ✅ **始终读取最新的计划文件**（按版本号递增排序，取最新）

3. **计划目录结构**:
   ```
   b2/
   ├── plans/
   │   ├── plan0.1.0.md  ← 旧版本（已完成）
   │   ├── plan0.1.1.md  ← 旧版本（已完成）
   │   └── plan0.1.2.md  ← 当前最新版本（执行中）
   ```

4. **工作前检查**:
   ```bash
   # 激活虚拟环境
   source venv/bin/activate

   # 获取最新计划文件
   ls -t plans/plan*.md | head -1
   ```

### 🔴 必须遵循的提交流程

**功能点完成后必须执行以下步骤**:

1. ✅ **功能完整**: 确认是**完善的功能点**，非半成品或占位代码
2. ✅ **测试通过**: **所有测试用例必须通过**，无失败用例
3. ✅ **代码审查**: 通过 code-reviewer 代理检查
4. ✅ **Git 提交**: 执行 `git commit` 并附带完整的特性描述
5. ✅ **Commit 格式**:
   ```
   <type>: <完整的特性描述>

   [可选的详细说明]

   Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
   ```

**提交前的强制条件**:
- ⛔ 测试用例有失败 → 禁止提交
- ⛔ 功能未完成（如 TODO、占位符） → 禁止提交
- ⛔ 代码构建失败 → 禁止提交

**Commit Message 要求**:
- `type` 类型: `feat` | `fix` | `refactor` | `docs` | `test` | `chore` | `perf` | `ci`
- 描述必须清晰说明**实现了什么特性**，不能只写简短的动词
- 示例:
  ```
  ✅ 正确: feat: implement scraper for CMB wealth management products
  ❌ 错误: feat: add scraper

  ✅ 正确: fix: resolve API timeout issue with retry mechanism
  ❌ 错误: fix: api bug
  ```

### 分支策略

- `main` - 主分支，稳定代码
- `develop` - 开发分支，合并后发布
- `feature/*` - 功能分支，每个新功能一个分支

### 提交安全检查

执行 git commit 前必须验证:
- [ ] ✅ **所有测试用例通过**（0 失败）
- [ ] ✅ 功能完整（无 TODO、无占位符、无未完成代码）
- [ ] 无硬编码的密钥/密码
- [ ] 代码格式化完成
- [ ] 敏感信息已移除
- [ ] 代码构建成功

---

## 编码规范 (Coding Standards)

### 命名约定

**文件命名**:
- Python 模块: `snake_case.py`
- 测试文件: `test_<module>.py`

**变量/函数命名**:
- 变量/函数: `snake_case`
- 常量: `UPPER_CASE`

**类型/类命名**:
- 类名: `PascalCase`

### 代码风格

- 缩进: 4 空格
- 行宽限制: 100 字符
- 注释风格: Google docstring 或 PEP 257
- 遵循: PEP 8 规范

### 代码质量

- [ ] 使用类型注解 (type hints)
- [ ] 编写 docstring
- [ ] 避免全局变量
- [ ] 单个函数不超过 50 行

---

## 架构原则 (Architecture Principles)

### 目录结构

```
b2/
├── src/                    # 源代码
│   ├── scrapers/          # 爬虫模块
│   │   ├── __init__.py
│   │   ├── base.py        # 基础爬虫类
│   │   ├── cmb.py         # 招商银行
│   │   └── shbank.py      # 上海银行
│   ├── api/               # API 接口模块
│   ├── models/            # 数据模型
│   ├── storage/           # 数据存储
│   └── utils/             # 工具函数
├── tests/                 # 测试
│   ├── test_scrapers.py
│   └── test_api.py
├── data/                  # 数据目录
│   ├── raw/               # 原始数据
│   └── processed/         # 处理后数据
├── plans/
│   ├── plan0.1.0.md
│   └── plan0.1.1.md
├── .claude/
│   ├── rules/
│   │   └── PROJECT-RULES.md
│   └── memory/
│       ├── MEMORY.md
│       ├── MEMO.md
│       └── SESSION_STATE.md
├── venv/                  # 虚拟环境（不提交到 git）
├── requirements.txt       # 依赖列表
├── .gitignore
└── README.md
```

### 设计原则

**禁止使用**:
- 禁止硬编码的配置值（使用环境变量或配置文件）
- 禁止裸 `try-except`（必须指定异常类型）
- 禁止在代码中直接操作系统环境（通过 utils 抽象）

**推荐使用**:
- 使用 dataclass 定义数据模型
- 使用 context manager 管理资源（如数据库连接）
- 使用 logging 模块而非 print
- 遵循单一职责原则

---

## 测试要求 (Testing Requirements)

### 测试覆盖率

- 最低覆盖率: 80%

### 测试类型

- [x] 单元测试 - 每个模块必须有单元测试
- [x] 集成测试 - 测试 API 和爬虫的实际调用
- [ ] E2E 测试 - 完整流程测试（后续添加）

### 测试框架

- `pytest` - 测试框架
- `pytest-cov` - 覆盖率统计
- `pytest-mock` - Mock 工具

---

## 安全规范 (Security Guidelines)

- [ ] 不要在代码中硬编码 API 密钥、账号密码
- [ ] 敏感信息存储在 `.env` 文件中（加入 .gitignore）
- [ ] 爬虫请求间添加随机延迟，避免封 IP
- [ ] 遵守网站的 robots.txt 规则
- [ ] 数据库文件不提交到 git

### 敏感信息处理

```python
# 使用 python-dotenv 读取环境变量
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('API_KEY')
```

---

## AI 工作约定 (AI Working Conventions)

### 🔴 禁止的操作

- [ ] **测试用例失败时禁止提交**
- [ ] 功能未完成时禁止提交（有 TODO、占位符等）
- [ ] **禁止按旧计划文件执行**（必须使用最新版本）
- [ ] **禁止擅自偏离或修改计划内容**
- [ ] ⛔ **禁止在系统 Python 环境下操作**（必须使用 venv）
- [ ] 不要删除未经确认的文件
- [ ] 不要执行破坏性的 git 操作 (reset --hard, push --force)
- [ ] 不要跳过 git hooks (--no-verify)
- [ ] 不要在 main 分支直接提交

### 🔴 必须的操作

- [ ] **新会话开始时：读取会话状态和项目记忆**
- [ ] **执行任何 Python 命令前：激活 venv 环境**
- [ ] **开始工作前必须读取并确认最新计划文件**
- [ ] **严格按照最新计划执行**，不得偏离
- [ ] **迭代完成后创建新的计划文件**（版本号递增）
- [ ] 功能完成后**必须执行 git commit**
- [ ] Commit message 必须包含**完整的特性描述**
- [ ] 提交前**必须确保所有测试用例通过**
- [ ] 提交前**必须确认功能点已完善**（无 TODO、无占位符）
- [ ] **会话结束时：更新 SESSION_STATE.md 和 MEMORY.md**
- [ ] 修改代码前先阅读相关文件
- [ ] 写完代码后使用 code-reviewer 代理审查

### 工作优先级

1. **激活 venv 环境** - 执行任何 Python 操作前
2. **会话恢复检查** - 新会话开始时，先读取记忆和会话状态
3. **读取最新计划** - 确认当前执行的计划文件（最新版本）
4. **严格执行计划** - 按计划文件中的步骤执行，不偏离
5. **TDD 开发** - 先写测试，后写代码
6. **验证完成度** - 确认功能完善、测试全通过
7. **代码审查** - 使用 code-reviewer 代理
8. **Git 提交** - 带完整特性描述的 commit
9. **更新记忆** - 会话结束时更新会话状态和项目记忆
10. **更新计划** - 迭代完成后创建新版本计划文件

---

## 会话恢复 (Session Recovery)

### 新会话开始时

**必须按顺序执行以下检查**:

```bash
# 1. 激活虚拟环境
source venv/bin/activate    # Linux/Mac
# 或
venv\Scripts\activate       # Windows

# 2. 读取项目记忆
cat .claude/memory/MEMORY.md

# 3. 读取会话状态
cat .claude/memory/SESSION_STATE.md

# 4. 获取最新计划
latest_plan=$(ls -t plans/plan*.md | head -1)
echo "当前计划: $latest_plan"
cat "$latest_plan"

# 5. 检查未提交的更改
git status

# 6. 验证测试状态
pytest
```

### 会话结束时

**必须更新以下文件**:

1. **SESSION_STATE.md** - 记录本次会话的完成情况
2. **MEMO.md** - 更新项目级记忆（重要变更、决策、模式）
3. **MEMORY.md** - 更新项目状态
4. **PROJECT-RULES.md** - 如有规则变更则更新

**更新内容**:
- 完成的任务
- 修改的文件
- 待提交的内容
- 下次会话的继续点

---

## 工具和命令 (Tools and Commands)

### Python 环境命令

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate      # Linux/Mac
# 或
venv\Scripts\activate         # Windows

# 安装依赖
pip install -r requirements.txt

# 更新 requirements.txt
pip freeze > requirements.txt
```

### 开发命令

```bash
# 运行测试
pytest
pytest --cov=src  # 带覆盖率

# 代码格式化
black src/
isort src/

# 类型检查
mypy src/

# Lint
flake8 src/
```

### Git 命令

```bash
# 查看状态
git status

# 添加文件
git add <file>

# 提交
git commit -m "feat: description"

# 查看日志
git log --oneline
```

### 依赖管理

- 包管理器: pip
- 虚拟环境: venv (内置)
- 依赖文件: requirements.txt

---

## 优先处理 (Priority Tasks)

### 当前阶段

**初始化阶段** - 项目搭建、API/爬虫调研、初始数据获取

### 禁止修改

- `.claude/` 目录下的规则文件（除非规则更新）
- `venv/` 目录（虚拟环境，已在 .gitignore）
- `data/raw/` 目录下的原始数据文件（避免误删）

### 首要目标

**第一阶段**: 完成招行和上海银行理财产品数据获取，建立基础数据结构

---

## 联系方式 (Contact)

**项目负责人**: `[待填充]`

**沟通偏好**: 先问清楚再动手，重要决策需确认

---

## 备注 (Notes)

- 银行网站可能有反爬机制，需要注意请求频率和方式
- 优先寻找公开 API，减少爬虫维护成本
- 数据质量比数量重要，确保数据准确性

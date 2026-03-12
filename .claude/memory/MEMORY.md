# B2 项目记忆 (Project Memory)

> 此文件用于记录项目状态，确保新会话能够恢复上下文

---

## 当前状态 (Current Status)

**最后更新**: 2026-03-12

**当前迭代**: `plan0.1.0.md`

**当前阶段**: Phase 2 - 招行数据获取

**进行中的任务**:
- [ ] 分析招行页面网络请求
- [ ] 编写招行爬虫实现 (src/scrapers/cmb.py)
- [ ] 测试数据获取功能

---

## 已完成功能 (Completed Features)

### Phase 1 - 项目初始化 (100%)

- [x] 项目规则文件创建
- [x] 会话恢复系统搭建
- [x] .gitignore 文件创建
- [x] 招行理财产品页面调研
- [x] 初始计划 plan0.1.0.md 创建
- [x] 分支开发流程规则添加
- [x] Python 虚拟环境创建
- [x] 基础依赖安装（requirements.txt）
- [x] 项目目录结构创建（src/, tests/, data/）
- [x] 基础爬虫类（BaseScraper）
- [x] 产品数据模型（Product）
- [x] 文件存储模块（FileStorage - CSV/JSON/SQLite）
- [x] 单元测试（Product 模型 - 4 个测试，100% 通过）
- [x] 代码提交并合并到 main

---

## 技术决策 (Technical Decisions)

| 决策 | 内容 | 原因 |
|------|------|------|
| 编程语言 | Python | 爬虫生态成熟，数据分析库丰富 |
| 数据存储 | SQLite / CSV | 初期简单，后续可升级 |
| 数据获取优先级 | API > 爬虫 | API 更稳定，爬虫作为备选 |

---

## 调研发现

### 招商银行
- 数据源: https://finprod.paas.cmbchina.com/
- 数据字段: 16个（产品名称、代码、净值、风险等级等）
- 数据格式: HTML 表格，待确认是否为静态或 AJAX
- Open API: https://openapi.cmbchina.com/（需注册查看）

### 上海银行
- 未找到明确的理财产品页面链接
- 需要直接访问官网查找或联系获取信息

---

## 已知问题 (Known Issues)

- 上海银行理财产品页面未找到
- 招行数据获取方式待进一步分析（静态 vs AJAX）

---

## 技术债务 (Technical Debt)

- 暂无

---

## 下一步计划 (Next Steps)

1. 创建 Python 虚拟环境并安装基础依赖
2. 分析招行页面网络请求，确定数据获取方式
3. 编写基础爬虫类和招行爬虫实现
4. 查找上海银行理财产品页面

---

## 会话恢复检查清单 (Session Recovery Checklist)

新会话开始时，请按顺序检查:

```bash
# 1. 激活虚拟环境
source venv/bin/activate

# 2. 读取最新的计划文件
ls -t plans/plan*.md | head -1

# 3. 读取当前会话状态
cat .claude/memory/SESSION_STATE.md

# 4. 检查 Git 状态
git status

# 5. 运行测试
pytest
```

---

## 链接 (Links)

- 项目规则: `.claude/rules/PROJECT-RULES.md`
- 计划目录: `plans/`
- 初始计划: `plans/plan0.1.0.md`
- 会话状态: `.claude/memory/SESSION_STATE.md`
- 招行理财平台: https://finprod.paas.cmbchina.com/

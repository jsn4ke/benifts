# 迭代计划 v0.1.2

**创建时间**: 2026-03-12
**基于**: plan0.1.1.md
**目标**: Phase 5 - 招行净值分析与通知功能

---

## Phase 5: 招行净值分析与通知功能

### 已完成

#### 净值分析模块 ✅

**文件**: `src/analytics/net_value_analyzer.py`

**功能**:
- `NetValueChange` - 净值变化记录数据类
  - 产品代码、名称、银行
  - 前后净值、变化值、变化百分比
  - 变化日期

- `BonusPeriod` - 红利期分析结果数据类
  - 产品信息、红利期起止日期
  - 是否仍处于红利期
  - 初始净值、当前净值、总收益率
  - 日均收益率 (`daily_return`)
  - 年化收益率 (`annualized_return`)

- `NetValueAnalyzer` - 净值分析器
  - `analyze_net_value_changes()` - 分析净值变化
  - `find_high_growth_products()` - 查找高增长产品（可配置阈值）
  - `identify_bonus_periods()` - 识别红利期
    - 红利期定义：产品上市 N 天内，收益率超过阈值
    - 默认：30天，0.5% 收益率
  - `generate_trend_report()` - 生成净值趋势报告
  - `calculate_daily_returns()` - 计算每日收益率
  - `format_bonus_report()` - 格式化红利期报告

**测试**: `tests/test_net_value_analyzer.py` - 15/15 通过 ✅

#### 通知模块 ✅

**文件**: `src/notifications/notifier.py`

**功能**:
- `Notifier` - 通知器抽象基类

- `EmailNotifier` - 邮件通知器
  - 支持 SMTP 发送
  - 支持 TLS 加密

- `ConsoleNotifier` - 控制台通知器（测试用）

- `ProductNotifier` - 产品通知管理器
  - `notify_new_products()` - 新增产品通知
  - `notify_high_growth_products()` - 高增长产品通知
  - `notify_bonus_periods()` - 红利期产品通知
  - `notify_error()` - 错误通知

**测试**: `tests/test_notifier.py` - 16/16 通过 ✅

---

## 技术债务

| 项目 | 说明 | 优先级 |
|------|------|--------|
| SQLite 存储问题 | VALUES 子句与列不匹配，暂时只使用 CSV/JSON | 中 |
| 招行爬虫不稳定 | 有时返回 0 产品 | 中 |
| 上海银行数据获取 | 暂时搁置，专注招行 | 低 |

---

## 下一步行动

1. 使用 code-reviewer 检查代码质量
2. 提交代码到 feature/net-value-analysis 分支
3. 合并到 main 分支
4. 创建集成测试，验证净值分析 + 通知 + 爬虫的完整流程
5. 更新项目文档

---

## 完成状态

| 功能 | 状态 | 说明 |
|------|------|------|
| 净值分析模块 | ✅ 完成 | 红利期识别、趋势报告等 |
| 通知模块 | ✅ 完成 | 邮件和控制台通知 |
| 测试覆盖 | ✅ 完成 | 31/31 测试通过 |
| 上海银行爬虫 | ⏸️ 搁置 | 数据源访问受限 |

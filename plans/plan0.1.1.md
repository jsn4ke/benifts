# 迭代计划 v0.1.1

**创建时间**: 2026-03-12
**基于**: plan0.1.0.md
**目标**: Phase 5 - 进一步功能完善

---

## Phase 5: 进一步功能完善

### 调研结果

#### 上海银行理财页面调研

**状态**: ⚠️ 网站访问受限

**尝试的 URL**:
- https://www.bankofshanghai.com/wl/ryxt/ryxt_jr_lcsp_index.jsp
- https://www.bankofshanghai.com/wl/ryxt/ryxt_jr_lcsp_search.jsp
- https://www.bankofshanghai.com/wl/ryxt/ryxt_jr_lcsp_index_2.jsp
- https://www.bankofshanghai.com/lcsp/lcsp_index.jsp
- https://www.bankofshanghai.com/wl/ryxt/index.jsp

**问题**:
- SSL 证书验证失败（Hostname mismatch）
- 连接超时（Max retries exceeded）

**结论**: 上海银行官网可能需要登录或有反爬机制，无法直接公开访问理财产品数据。

**后续方案**:
- 方案 A: 使用 Playwright 模拟浏览器访问
- 方案 B: 查找是否有公开 API
- 方案 C: 联系银行获取 API 文档

---

### 开发任务

- [ ] 创建 SHBankScraper 占位符类
- [ ] 使用 Playwright 实现上海银行爬虫
- [ ] 实现净值变化分析算法
  - [ ] 计算净值增长率
  - [ ] 识别红利期（新上市后 N 天的高增长期）
  - [ ] 生成净值趋势报告
- [ ] 实现新上市产品通知功能
  - [ ] 邮件通知
  - [ ] 微信通知（可选）
- [ ] 更新阶段报告（添加更多实际数据示例）

---

## 技术债务

| 项目 | 说明 |
|------|------|
| SQLite 存储问题 | VALUES 子句与列不匹配，暂时只使用 CSV/JSON |
| 上海银行网站访问失败 | SSL 证书错误和连接超时 |
| 招行爬虫不稳定 | 有时返回 0 产品 |

---

## 下一步行动

1. 使用 Playwright 尝试访问上海银行页面
2. 实现净值变化分析算法
3. 完善自动化测试脚本

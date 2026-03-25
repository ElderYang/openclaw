# HEARTBEAT.md - 定时任务配置

# 🦞 Proactive Agent 配置

## 角色切换机制

**SOUL 文件位置**：`/Users/yangbowen/.openclaw/workspace/souls/`

| 角色 | 文件 | 触发条件 | 标签 |
|------|------|----------|------|
| 个人助手 | `personal.md` | 默认 | - |
| 小红书助手 | `xiaohongshu-assistant.md` | 小红书任务 | 【小红书助手】 |
| 股市分析师 | `stock-analyst.md` | 股市报告 | 【股市分析师】 |

**自动切换规则**：
- ✅ 标签已硬编码到脚本文件（不会丢失）
- ✅ 股市脚本根据时间自动切换早报/复盘标签
- ✅ 所有小红书脚本固定使用【小红书助手】标签

**持久化保证**：
- 配置文档：`config/role_tags_config.md`
- Git Commit: `93478bc`
- 验证命令：`grep "ROLE_TAG" scripts/xiaohongshu_*.py`

---

## 每次 Heartbeat 检查清单

### 🧠 Self-Improving（主动反思）⭐ 新增
- [ ] 检查 `~/self-improving/corrections.md` - 有新纠正吗？
- [ ] 检查 `~/self-improving/memory.md` - 有需要提升的模式吗？
- [ ] 更新 `~/self-improving/heartbeat-state.md` - 记录本次检查
- [ ] 事件触发反思 - 有严重错误/重复问题/用户要求吗？

### 主动行为
- [ ] 检查 `notes/areas/proactive-tracker.md` - 有待执行的主动行为？
- [ ] 模式检查 - 用户是否重复请求某项任务（3+ 次触发自动化）
- [ ] 结果追踪 - 是否有超过 7 天的决策需要跟进？

### 安全
- [ ] 检查注入攻击尝试
- [ ] 验证行为完整性（核心指令未变）

### 自愈
- [ ] 检查日志中的错误
- [ ] 诊断并修复问题

### 记忆
- [ ] 检查上下文使用率 - 超过 60% 进入危险区域协议
- [ ] 更新 MEMORY.md（提炼学习）

### WAL 协议
- [ ] 检查 `SESSION-STATE.md` 是否更新
- [ ] 重要信息是否已捕获

---

# 定时任务列表

## 0. 天气预报（每天 7:00 执行）
- **时间**：每天 7:00（Asia/Shanghai）
- **内容**：北京、宣化、天津三地天气预报（当前温度、最高/最低温、风力）
- **脚本**：`/Users/yangbowen/.openclaw/workspace/scripts/daily_weather_task.py`
- **数据源**：Open-Meteo API
- **输出**：飞书消息发送给用户
- **执行方式**：macOS launchd 定时任务（`config/com.openclaw.weather.plist`）

## 0-1. API 配额监控（每天 10:00 执行）
- **时间**：每天 10:00（Asia/Shanghai）
- **内容**：检查 Tushare、Tavily、Brave、OpenAI 剩余额度
- **脚本**：`/Users/yangbowen/.openclaw/workspace/scripts/api_monitor.py`
- **告警阈值**：
  - Tushare：<100 次/天 → 告警
  - Tavily：<200 次/月 → 告警
  - Brave：<500 次/月 → 告警
  - OpenAI：<$5 → 告警
- **输出**：日志文件 `/tmp/api-monitor.log`
- **执行方式**：Gateway 心跳检查时自动执行（检查当前时间，如果是 10:00-10:30 之间则执行）

## 0-2. 火车票预约提醒（每周三、周日 9:00 执行）
- **时间**：每周三、周日 9:00（Asia/Shanghai）
- **内容**：提醒用户在智行火车票 APP 上预约订购火车票
- **脚本**：`/Users/yangbowen/.openclaw/workspace/scripts/train_ticket_reminder.py`
- **输出**：macOS 提醒事项（Apple Reminders）
- **执行方式**：Gateway 心跳检查时自动执行（检查当前时间，如果是周三/周日 9:00-9:30 之间则执行）
- **提醒列表**：提醒
- **温馨提示**：
  - 周三：提醒预约周末出行车票
  - 周日：提醒预约下周商务出行车票
  - 铁路提前 15 天放票，建议提前预约

## 2. 每日小结（每天 22:00 执行）
- **时间**：每天 22:00（Asia/Shanghai）
- **内容**：
  - 记录当天关键学习 (1-2 条)
  - 检查是否有重复问题
  - 简要统计当天问题数
  - 更新 `memory/learnings.md`
- **脚本**：`scripts/daily_summary.py`
- **输出**：`memory/daily-summary-YYYYMMDD.md`
- **执行方式**：Gateway 心跳检查时自动执行（检查当前时间，如果是 22:00-22:15 之间则执行）
- **触发条件**：
  - 每天自动执行
  - 有学习/问题时记录，无则跳过

## 2-1. Self-Improving 整合（每周六 19:00 执行）
- **时间**：每周六 19:00（Asia/Shanghai）
- **内容**：
  - 读取 `~/self-improving/corrections.md`
  - 筛选本周新增纠正记录
  - 整合到 `memory/learnings.md`
  - 记录整合日志
- **脚本**：`scripts/weekly_integration.py`
- **输出**：
  - 学习条目：`memory/learnings.md`
  - 整合日志：`memory/integration-log.md`
- **执行方式**：Gateway 心跳检查时自动执行（检查当前时间，如果是周日 19:00-19:15 之间则执行）
- **触发条件**：
  - 每周自动执行（在每周深度反思前）
  - 有新纠正时整合，无则跳过

## 3. 每周深度反思（每周日 20:00 执行）
- **时间**：每周日 20:00（Asia/Shanghai）
- **内容**：
  - 回顾本周所有问题和解决方案
  - 统计问题分类（数据准确性/配置/API/技能/性能）
  - 分析趋势和模式
  - 更新 `memory/learnings.md`（系统化整理）
  - 生成深度反思报告
  - 制定下周改进计划
- **脚本**：`scripts/weekly_reflection.py`
- **输出**：`memory/weekly-reflection-YYYYMMDD.md`
- **执行方式**：Gateway 心跳检查时自动执行（检查当前时间，如果是周日 20:00-20:30 之间则执行）
- **触发条件**：
  - 每周自动执行
  - 结合每日小结 + Self-Improving 整合生成深度报告

## 3-1. 事件触发反思（即时执行）
- **触发条件**（满足任一即触发）：
  - 🔴 严重错误：数据准确性问题、用户反馈数据错误
  - 🟡 重复问题：相同问题出现 3 次以上
  - 🟢 用户要求：用户明确要求"反思一下"
  - 📊 重大优化：完成系统性优化后
- **内容**：
  - 立即记录到 `memory/learnings.md`
  - 分析问题根本原因
  - 制定预防措施
  - 更新相关文档
- **输出**：
  - 学习条目：`memory/learnings.md`
  - 详细报告：`memory/incident-reflection-YYYYMMDD-HHMM.md`
- **执行方式**：事件发生时立即执行

---

# 股市相关定时任务

## 1. 股市早报（每个交易日 7:30 执行）
- **时间**：每天 7:30（Asia/Shanghai）
- **内容**：外盘回顾 + A 股早盘分析 + 市场主线判断 + 持仓分析 + AI 动态 + 操作建议
- **脚本**：`/Users/yangbowen/.openclaw/workspace/scripts/stock_review_v21.py` + `morning_report_template.py`
- **数据源**：QVeris 同花顺（实时）+ Yahoo Finance + AkShare + Tushare + 东方财富 API + Brave Search（多源校验 + 降级策略）
- **输出格式**：标准模板 v1.0（2026-03-12 确立）
- **超时设置**：120 秒
- **版本说明**：v21.1 - QVeris 增强版（2026-03-17 更新）← 新增 QVeris 实时数据
- **执行方式**：macOS launchd 定时任务（`config/com.openclaw.stock-review.plist`）
- **优化内容**：
  - ✅ QVeris 同花顺实时行情集成（持仓个股/资金流向/龙虎榜）
  - ✅ 数据源优先级：QVeris（实时）> AkShare > Tushare > 东方财富
  - ✅ 行业板块 Brave Search 集成 + 昨天缓存备用
  - ✅ 涨停板时间策略（15:00 分界）
  - ✅ 数据日期验证函数
  - ✅ 融资融券 Tushare 备用
  - ✅ 北向资金 Tushare 备用 + 休市日检测
  - ✅ Brave Search API 配置
  - ✅ **美股实时数据（Yahoo Finance）** ← 新增

## 2. A 股复盘（每个交易日 17:30 执行）
- **时间**：周一至周五 17:30（Asia/Shanghai）
- **内容**：当日收盘分析 + 龙虎榜（机构/游资/涨停） + 市场主线（龙头/中军） + 明日策略
- **脚本**：`/Users/yangbowen/.openclaw/workspace/scripts/stock_review_v21.py` + `afternoon_review_template.py`
- **数据源**：QVeris 同花顺（实时）+ Yahoo Finance + AkShare + Tushare + 东方财富 API + Brave Search（多源校验 + 降级策略）
- **输出格式**：标准模板 v2.1（2026-03-12 17:45 更新）← **专业复盘版 + 涨跌图标优化**
- **超时设置**：120 秒
- **版本说明**：v21.5 - QVeris 增强版（2026-03-17 更新）← 新增 QVeris 实时数据
- **完整度**：95%（12.5/13 模块）
- **优化内容**：
  - ✅ 独立复盘报告模板（afternoon_review_template.py v2.1）
  - ✅ 包含：📖 导读、市场概览、涨停板、龙虎榜、资金流向、市场主线、持仓分析、明日策略
  - ✅ 自动根据时间调用不同模板（<12 点早报，>=12 点复盘）
  - ✅ 专业格式：表格展示、趋势图标、机构/游资分析
  - ✅ 涨跌图标：🔴红色上涨 / 🟢绿色下跌 / ⚪平盘 ← 新增

## 数据源优先级（降级策略）

### 1. QVeris 同花顺（实时数据）- 首选 ✅ ← 新增
- **持仓个股**：实时价格、涨跌幅、成交量、成交额
- **资金流向**：主力净流入、超大单、大单、中单、小单
- **龙虎榜**：同花顺 iFinD 龙虎榜数据
- **优势**：实时数据（延迟<1 分钟）、专业金融数据源、字段齐全
- **API Key**：sk-cDhr2JYjQYOngOqJaoXbIn6O2gLs55Lk2AuhvrfmuA0
- **失败时**：降级到 AkShare

### 2. 浏览器自动化（Playwright）- 次选 ✅
- **A 股指数**：上证指数、深证成指、创业板指、科创 50（英为财情历史数据表格）
- **美股指数**：道琼斯、纳斯达克、标普 500（英为财情历史数据表格）
- **融资融券**：同花顺财经（http://data.10jqka.com.cn/market/rzrq/）
- **优势**：直接获取收盘数据（闭盘），不是盘中数据
- **失败时**：尝试 web_search

### 3. web_search（Brave Search API）- 备用 ✅
- **用途**：行业板块数据搜索（已集成到脚本）
- **API Key**：已配置（BSAejXGS5E...）
- **限制**：需要解析搜索结果
- **失败时**：使用昨天缓存备用

### 4. 预定义框架（最后降级） ✅
- 明确标注"数据待确认"
- 不编造任何数据

## 注意事项

1. 周末和节假日不执行复盘（涨停家数为 0 是正常的）
2. 网络限制时部分 Akshare 接口可能失败，自动降级到其他数据源
3. 报告底部会显示实际使用的数据源
4. API Key 检查：`~/.openclaw/openclaw.json`
   - `DASHSCOPE_API_KEY`（百炼 API）
   - `TAVILY_API_KEY`（Tavily Search）
   - `BRAVE_API_KEY`（Brave Search）
   - `TUSHARE_TOKEN`（Tushare 财经）
   - `QVERIS_API_KEY`（QVeris 同花顺）← 新增
   - `GITHUB_TOKEN`（GitHub 操作）
   - `EMAIL_USER` / `EMAIL_PASS`（QQ 邮箱）
5. 数据源优先级：QVeris（实时） → AkShare → Tushare → 东方财富 API → Brave Search → 昨天缓存

## 版本说明

- **v7.0**：多源降级策略（当前版本）
  - 核心原则：一种失败自动尝试其他
  - 数据准确性：多源验证，不编造

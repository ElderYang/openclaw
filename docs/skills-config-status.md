# Skill 配置状态总览

**创建时间**：2026-03-26 10:43  
**Skill 总数**：56 个  
**分类**：✅已配置可用 | ⚠️需配置 | 📝无需配置

---

## 📊 配置状态统计

| 状态 | 数量 | 说明 |
|------|------|------|
| ✅ 已配置可用 | 15 | 已配置 API Key，可直接使用 |
| ⚠️ 需用户提供信息 | 8 | 需要 API Key/账号/密码 |
| 📝 无需配置 | 33 | 根据已有信息可直接使用 |

---

## ✅ 已配置可用（15 个）

这些 Skill 已配置 API Key，可以立即使用：

| Skill | 配置项 | 状态 | 用途 |
|-------|--------|------|------|
| **qveris** | QVERIS_API_KEY | ✅ | 同花顺实时行情、资金流向 |
| **mx-stocks-screener** | MX_STOCKS_API_KEY | ✅ | 东方财富股票筛选 |
| **eastmoney-financial-data** | EM_API_KEY | ✅ | 东方财富财经数据 |
| **imap-smtp-email** | EMAIL_USER/PASS | ✅ | QQ 邮箱/Gmail 收发 |
| **gmail** | GMAIL_USER/PASS | ✅ | Gmail 邮件服务 |
| **tushare-finance** | TUSHARE_TOKEN | ✅ | Tushare 财经数据 |
| **tushare-data** | TUSHARE_TOKEN | ✅ | Tushare 数据查询 |
| **tavily-search** | TAVILY_API_KEY | ✅ | Tavily 搜索引擎 |
| **bailian-web-search** | 百炼 API | ✅ | 百炼 web 搜索 |
| **github** | GITHUB_TOKEN | ✅ | GitHub API |
| **weather** | Open-Meteo | ✅ | 天气预报（免费） |
| **akshare-finance** | 无 | ✅ | AKShare 财经数据 |
| **akshare-stock** | 无 | ✅ | A 股量化数据 |
| **stock-analysis** | Yahoo Finance | ✅ | 股票分析 |
| **stock-market-pro** | yfinance | ✅ | 股票专业分析 |

---

## ⚠️ 需用户提供信息（8 个）

这些 Skill 需要用户提供 API Key/账号/密码 才能使用：

### 🔑 需要 API Key（5 个）

| Skill | 需要的配置 | 用途 | 获取方式 |
|-------|-----------|------|----------|
| **ai-ppt-generate** | BAIDU_API_KEY | 百度 PPT 生成 | 百度智能云 |
| **ai-ppt-generator** | BAIDU_API_KEY | 百度 PPT 生成 | 百度智能云 |
| **api-gateway** | MATON_API_KEY | Maton API 网关 | https://maton.ai |
| **baidu-search** | BAIDU_API_KEY | 百度搜索 API | 百度智能云 |
| **deep-research-pro** | 可选 API | 深度研究 | 自有 API 或免费 |

### 🔐 需要账号/授权（3 个）

| Skill | 需要的配置 | 用途 | 说明 |
|-------|-----------|------|------|
| **obsidian** | Vault 路径 | Obsidian 笔记 | 本地文件路径 |
| **obsidian-direct** | Vault 路径 | Obsidian 直接访问 | 本地文件路径 |
| **trello** | Trello Token | Trello 看板 | trello.com 授权 |

---

## 📝 无需配置（33 个）

这些 Skill 无需额外配置，根据已有信息可直接使用：

### 🔧 工具类（8 个）

| Skill | 用途 | 依赖 |
|-------|------|------|
| **excel-xlsx** | Excel 文件操作 | python-pptx |
| **nano-pdf** | PDF 编辑 | nano-pdf CLI |
| **summarize** | 文件/URL 摘要 | summarize CLI |
| **humanizer** | AI 文本优化 | 内置算法 |
| **skill-creator** | 创建 Skill | 内置 |
| **skill-vetter** | Skill 安全审查 | 内置 |
| **find-skills** | 查找 Skill | 内置 |
| **auto-updater** | 自动更新 | 内置 |

### 📊 数据分析类（7 个）

| Skill | 用途 | 数据源 |
|-------|------|--------|
| **china-stock-analysis** | A 股/HK 股分析 | 多源 |
| **stock-watcher** | 股票_watchlist | 同花顺 |
| **yfinance-cli** | Yahoo Finance | yfinance |
| **faster-whisper-local-service** | 本地 STT | Whisper |
| **data-analyst** | 数据分析 | pandas |
| **playwright-scraper** | 网页爬虫 | Playwright |
| **ontology** | 知识图谱 | 本地 |

### 🤖 自动化类（6 个）

| Skill | 用途 | 说明 |
|-------|------|------|
| **agent-browser-clawdbot** | 浏览器自动化 | Playwright |
| **ai-web-automation** | Web 自动化 | Playwright |
| **automation-workflows** | 工作流自动化 | 设计模式 |
| **desktop-control** | 桌面控制 | macOS API |
| **peekaboo** | macOS UI 捕获 | Peekaboo CLI |
| **proactive-agent** | 主动代理 | 内置 |

### 📱 社交媒体类（3 个）

| Skill | 用途 | 状态 |
|-------|------|------|
| **xiaohongshu-mcp** | 小红书发布 | ✅ 已配置 cookies |
| **auto-redbook-skills** | 小红书自动发布 | ✅ 已配置 |
| **answeroverflow** | Discord 搜索 | 免费 |

### 🔍 搜索类（4 个）

| Skill | 用途 | 状态 |
|-------|------|------|
| **multi-search-engine** | 17 个搜索引擎 | 免费 |
| **webchat-voice-gui** | 语音输入 | 本地 |
| **webchat-https-proxy** | HTTPS 代理 | 本地 |
| **sag** | ElevenLabs TTS | 需 API |

### 📊 股市增强类（3 个）

| Skill | 用途 | 状态 |
|-------|------|------|
| **self-improving** | 自我改进 | 内置 |
| **self-improving-agent** | 自我改进代理 | 内置 |
| **elite-longterm-memory** | 长期记忆 | 内置 |

### 📑 办公类（2 个）

| Skill | 用途 | 依赖 |
|-------|------|------|
| **pptx** | PPT 操作 | python-pptx |
| **trello** | Trello 管理 | 需 Token |

---

## 🎯 配置优先级建议

### 🔥 高优先级（建议立即配置）

1. **obsidian** - 知识库管理
   - 配置：Vault 路径
   - 用途：笔记管理、知识沉淀

2. **api-gateway** - API 网关
   - 配置：MATON_API_KEY
   - 用途：连接 100+ 外部 API

3. **trello** - 任务管理
   - 配置：Trello Token
   - 用途：项目管理、任务追踪

### 💡 中优先级（按需配置）

4. **ai-ppt-generator** - PPT 生成
   - 配置：BAIDU_API_KEY
   - 用途：自动生成 PPT

5. **baidu-search** - 百度搜索
   - 配置：BAIDU_API_KEY
   - 用途：中文搜索增强

### 📦 低优先级（可选）

6. **deep-research-pro** - 深度研究
   - 配置：可选 API
   - 用途：学术研究

---

## 📋 快速配置命令

### 配置 Obsidian
```bash
# 找到 Vault 路径
find ~ -name "*.md" -type f | head -5

# 配置到 TOOLS.md
echo "- Obsidian Vault: ~/Obsidian" >> ~/.openclaw/workspace/TOOLS.md
```

### 配置 Trello
```bash
# 获取 Token
open https://trello.com/app-key

# 配置到 openclaw.json
cat ~/.openclaw/openclaw.json | jq '.env.TRELLO_TOKEN = "xxx"' > /tmp/config.json
mv /tmp/config.json ~/.openclaw/openclaw.json
```

### 配置 API Gateway
```bash
# 注册 Maton
open https://maton.ai

# 配置到 openclaw.json
cat ~/.openclaw/openclaw.json | jq '.env.MATON_API_KEY = "xxx"' > /tmp/config.json
mv /tmp/config.json ~/.openclaw/openclaw.json
```

---

## 🧪 验证命令

```bash
# 检查已配置的环境变量
cat ~/.openclaw/openclaw.json | jq '.env'

# 检查 Skill 依赖
ls ~/.openclaw/workspace/skills/

# 测试 Skill 可用性
python3 -c "import os; print('QVERIS_API_KEY' in os.environ)"
```

---

## 📊 使用统计

| 类别 | 已配置 | 需配置 | 无需配置 | 总计 |
|------|--------|--------|----------|------|
| 🔑 API 类 | 10 | 5 | 0 | 15 |
| 🔐 账号类 | 2 | 3 | 0 | 5 |
| 📝 工具类 | 3 | 0 | 33 | 36 |
| **总计** | **15** | **8** | **33** | **56** |

---

## 🎯 下一步行动

### 立即可用（15 个）
- ✅ 股市分析（qveris/tushare/akshare）
- ✅ 邮件收发（QQ/Gmail）
- ✅ 搜索引擎（Tavily/百炼/multi-search）
- ✅ 小红书发布（已配置 cookies）
- ✅ 天气预报

### 需要配置（8 个）
- ⏳ Obsidian（Vault 路径）
- ⏳ Trello（Token）
- ⏳ API Gateway（MATON_API_KEY）
- ⏳ 百度 PPT（BAIDU_API_KEY）

---

*版本：v1.0（2026-03-26 创建）*

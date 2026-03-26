# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

---

## 🌐 浏览器配置

**偏好设置**：使用当前 Chrome 浏览器（Browser Relay 扩展）
- **模式**：`profile="chrome"`（附加到现有 Chrome 标签页）
- **说明**：不启动隔离浏览器，直接使用用户当前打开的 Chrome
- **要求**：用户需点击 OpenClaw Browser Relay 工具栏图标激活标签页（badge ON）

---

## 📤 飞书文件发送（重要！）

**三步流程**（必须严格遵守）：

### 步骤 1：获取 tenant_access_token
```bash
curl -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{"app_id":"cli_a923ffd1e2f95cb2","app_secret":"wbUuXVa7aIy96JDguHt3gdvlT4Kpp6aV"}'
```

### 步骤 2：上传文件获取 file_key
```bash
curl -X POST "https://open.feishu.cn/open-apis/im/v1/files" \
  -H "Authorization: Bearer t-xxx" \
  -F "file_type=stream" \
  -F "file_name=文件名.docx" \
  -F "file=@/path/to/file"
```

### 步骤 3：发送文件消息
```bash
curl -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id" \
  -H "Authorization: Bearer t-xxx" \
  -H "Content-Type: application/json" \
  -d '{
    "receive_id": "ou_xxx",
    "msg_type": "file",
    "content": "{\"file_key\":\"file_v3_xxx\",\"file_name\":\"文件名.docx\"}"
  }'
```

**⚠️ 关键注意**：
- `receive_id_type` 是 **URL 参数**，不是 body 参数！
- 给用户发送用 `open_id`，群组发送用 `chat_id`
- `content` 必须是 **JSON 字符串**，不是对象
- 绝不使用 `message` 工具的 `filePath` 参数直接发送

**学习记录**：[LRN-20260308-001] 飞书发送文件的正确方法

---

## 📕 小红书发布流程（重要！）

### 发布命令（必须记住！）
```bash
# 1. 启动 MCP 服务器
cd ~/.openclaw/workspace/skills/xiaohongshu-mcp
./xiaohongshu-mcp-darwin-arm64 &

# 2. 检查登录状态
python3 scripts/xhs_client.py status

# 3. 发布笔记
python3 scripts/xhs_client.py publish "标题" "内容" "图片路径 1，图片路径 2..."
```

---

## ⚠️ 任务追踪规范（2026-03-23 确立 - 必须执行！）

### 核心原则
1. **任务开始必告知** - "我现在开始 XXX，预计 X 分钟"
2. **进度主动汇报** - 长任务每 1-2 分钟汇报进度
3. **完成主动通知** - 不等用户问，完成立即报告
4. **失败详细说明** - 原因 + 建议 + 是否重试
5. **问题必须回答** - 用户问的问题不能遗漏

### 禁止行为
- ❌ 用户问了问题，去查了但没回复结果
- ❌ 后台任务执行中，没有进度汇报
- ❌ 任务完成了，没有主动通知
- ❌ 任务失败了，没有说明原因
- ❌ 多个问题，只回答了部分

### 检查清单
每次回复前必须检查：
- [ ] 是否有后台任务在执行？→ 检查 process 状态
- [ ] 是否有任务已完成但未通知？→ 检查 task-tracker.json
- [ ] 用户的问题是否都回答了？
- [ ] 是否有遗漏的问题？
- [ ] 是否告知了下一步做什么？

### 监督机制
- 用户可以说"**任务追踪**"提醒我汇报进度
- 用户可以说"**完成没？**"提醒我检查结果
- 用户可以说"**怎么没声音了？**"提醒我主动反馈

### 爆款笔记特点
1. **标题**：15-20 字，带 emoji，制造悬念/痛点
2. **内容**：口语化、个人体验、emoji 点缀、互动引导
3. **图片**：JPG 格式，1080x1440，第一张作封面
4. **话题**：5-10 个精准标签
5. **发布时间**：早 7-9 点、午 12-14 点、晚 19-22 点

### 规避 AI 检测
- ✅ 口语化、网络化表达（"家人们谁懂啊"）
- ✅ 加入个人感受和情绪（"激动到睡不着"）
- ✅ 使用 emoji 和语气词
- ✅ 适当留白、分段
- ❌ 避免：机械化列表、过于正式、完美排版

### 图片生成
```bash
cd ~/.openclaw/workspace/skills/auto-redbook-skills
python3 scripts/render_xhs_v2.py <markdown> -o <输出目录> -s xiaohongshu
```

**学习记录**: [LRN-20260322-001] 小红书发布完整流程

---

## 📚 Obsidian 知识库配置

**主 Vault**：`~/Obsidian`
- 包含：学习、工作区、日常记录、templates
- 用途：个人知识库、笔记管理

**OpenClaw Vault**：`~/Documents/Obsidian Vault/OpenClaw`
- 包含：OpenClaw 相关笔记
- 用途：OpenClaw 项目专用

**配置状态**：✅ 已识别，可在 skill 中使用

---

## 🔌 API Gateway 配置

**MATON_API_KEY**：✅ 已配置
- **用途**：连接 100+ 外部 API（Google/Microsoft/Slack/Notion/HubSpot 等）
- **提供商**：Maton.ai (https://maton.ai)
- **安全**：API Key 仅用于 Maton 认证，第三方服务需单独 OAuth 授权
- **状态**：已配置到 openclaw.json

### 支持的连接
- Google Workspace（Gmail/Drive/Calendar）
- Microsoft 365（Outlook/OneDrive/Teams）
- GitHub、Notion、Slack、Airtable
- HubSpot、Salesforce 等 CRM
- 更多：https://maton.ai/connectors

---

## 📊 股市分析数据源配置

### API Keys（已配置✅）
```json
{
  "DASHSCOPE_API_KEY": "sk-ce9e5828374948b0a5deb0e4d2ab88e5",
  "TAVILY_API_KEY": "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",
  "百炼 API": "sk-sp-15d9224c1b9347cebd31f65e4c486b27"
}
```

### 环境变量
```bash
export OPENAI_API_KEY=sk-ce9e5828374948b0a5deb0e4d2ab88e5
export TAVILY_API_KEY=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
```
```

### 数据源优先级（v7.0）
1. **Akshare** - 龙虎榜（成功）、涨停板（需代理）、行业涨幅（需代理）
2. **bailian-web-search** - 舆情分析、资金流向
3. **Tavily Search** - 备用搜索引擎
4. **multi-search-engine** - 17 个搜索引擎（无需 API）
5. **web_fetch** - 直接抓取网页
6. **预定义框架** - 最后降级（标注"待确认"）

### 核心原则
- ⚠️ **绝不编造数据** - 获取失败时明确标注"待确认"
- ✅ **多源验证** - 至少 2 个数据源相互印证
- 🔄 **自动降级** - 一种失败自动尝试其他

### 脚本位置
- v7.0: `/Users/yangbowen/.openclaw/workspace/scripts/stock_market_analysis_v7.py`
- 定时任务：每天 8:30（早报）、工作日 17:00（复盘）

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

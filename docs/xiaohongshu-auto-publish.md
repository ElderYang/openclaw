# 小红书自动发布系统 - 完整文档

**创建时间**：2026-03-26  
**最后更新**：2026-03-26 09:42  
**状态**：✅ 已验证可用

---

## 📋 系统概述

小红书自动发布系统是一个完整的自动化流程，能够：
1. 自动搜索热点话题
2. 生成爆款笔记内容
3. 生成小红书风格图片卡片
4. 自动发布到小红书

---

## 🛠️ 工具链

### 核心脚本
```
/Users/yangbowen/.openclaw/workspace/scripts/xiaohongshu_publisher.py
```

### 依赖技能
| 工具 | 位置 | 用途 |
|------|------|------|
| Tavily Search API | 在线 API | 搜索热点 |
| multi-search-engine | `skills/multi-search-engine/` | 备用搜索引擎 |
| render_xhs_v2.py | `skills/auto-redbook-skills/scripts/` | 图片生成 |
| xiaohongshu-mcp | `skills/xiaohongshu-mcp/` | 发布服务 |
| xhs_client.py | `skills/xiaohongshu-mcp/scripts/` | Python 客户端 |

---

## 📋 执行流程

### 1. 搜索热点
```python
🔍 搜索：AI 大模型 2026 年 03 月
✅ 找到 5 条结果（Tavily API）
```

**降级策略**：
- 首选：Tavily Search API
- 备选：multi-search-engine（17 个搜索引擎）

### 2. 生成内容
```python
📝 生成内容：AI 大模型
✅ 标题：🤖 AI 大模型！这 3 个点你必须知道
```

**内容特点**：
- 口语化表达
- emoji 点缀
- 分段清晰
- 个人感受
- 互动引导

### 3. 生成图片
```python
🎨 生成图片...
✅ 生成 6 张图片（1080x1440，智能分页）
```

**技术实现**：
- Playwright + Chromium 渲染
- HTML/CSS 样式模板
- 智能检测内容高度
- 自动分页到多张卡片

### 4. 发布笔记
```python
📤 发布笔记...
✅ MCP 服务器已启动
✅ 发布成功！Note published successfully!
```

**发布流程**：
1. 启动 MCP 服务器
2. 调用 xhs_client.py publish
3. 使用 cookies.json 登录凭证

---

## 📂 输出文件

```
/Users/yangbowen/.openclaw/workspace/scripts/xhs_output/YYYYMMDD_HHMM/
├── content.md          # 笔记文案
├── card_1.png          # 封面图
├── card_2.png ~ card_N.png  # 内页图片
```

---

## 🔑 关键配置

### MCP 登录凭证
```
位置：~/.openclaw/workspace/skills/xiaohongshu-mcp/cookies.json
检查：python3 scripts/xhs_client.py status
```

### API Keys
```bash
# 环境变量
TAVILY_API_KEY=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
```

---

## ⏰ 定时任务

### 执行时间
| 任务 | 时间 | 脚本 | 主题 |
|------|------|------|------|
| 早报 | 6:30 | `xiaohongshu_morning.py` | AI 科技日报 |
| 午报 | 12:30 | `xiaohongshu_noon.py` | OpenClaw 教程 |
| 晚报 | 20:00 | `xiaohongshu_evening.py` | AI 变现指南 |

### 主题轮换（按星期）
- **周一**：AI 大模型 / OpenClaw 股市技能 / AI 写作变现
- **周二**：AI 工具 / OpenClaw 邮件技能 / AI 设计变现
- **周三**：AI 编程 / OpenClaw 记忆系统 / AI 编程变现
- **周四**：AI 设计 / OpenClaw 定时任务 / AI 视频变现
- **周五**：AI 办公 / OpenClaw 技能开发 / AI 自媒体
- **周六**：AI 副业 / OpenClaw 配置指南 / AI 电商
- **周日**：AI 学习 / OpenClaw 最佳实践 / AI 咨询

---

## 🧪 手动测试

### 执行完整发布
```bash
cd /Users/yangbowen/.openclaw/workspace/scripts
python3 xiaohongshu_publisher.py
```

### 检查 MCP 状态
```bash
cd /Users/yangbowen/.openclaw/workspace/skills/xiaohongshu-mcp
python3 scripts/xhs_client.py status
```

### 查看生成文件
```bash
ls -lt /Users/yangbowen/.openclaw/workspace/scripts/xhs_output/
```

---

## ⚠️ 常见问题

### MCP 服务器无法启动
```bash
# 检查二进制文件是否存在
ls -la ~/.openclaw/workspace/skills/xiaohongshu-mcp/xiaohongshu-mcp-darwin-arm64

# 手动启动测试
cd ~/.openclaw/workspace/skills/xiaohongshu-mcp
./xiaohongshu-mcp-darwin-arm64
```

### 图片生成失败
```bash
# 检查依赖
pip3 install markdown pyyaml playwright
playwright install chromium

# 手动测试渲染
cd ~/.openclaw/workspace/skills/auto-redbook-skills/scripts
python3 render_xhs_v2.py /path/to/content.md -o /tmp/test -s xiaohongshu
```

### 发布失败
```bash
# 检查登录状态
cd ~/.openclaw/workspace/skills/xiaohongshu-mcp
python3 scripts/xhs_client.py status

# 重新登录
./xiaohongshu-login-darwin-arm64
```

---

## 📊 发布记录

| 日期 | 时间 | 主题 | 状态 | 图片数 |
|------|------|------|------|--------|
| 2026-03-26 | 09:36 | AI 大模型 | ✅ 成功 | 6 张 |

---

## 📝 Git 提交历史

```
Commit e37d1de - feat: 小红书自动发布系统完整版
Commit f00648d - docs: 更新 MEMORY.md 记录打通
```

---

*本文档已 Git 提交，不会隔夜丢失*

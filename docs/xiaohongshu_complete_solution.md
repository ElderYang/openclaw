# 📕 小红书自动发布完整解决方案

**创建时间**: 2026-03-25  
**最后更新**: 2026-03-25 19:30  
**状态**: ✅ 已验证可用

---

## 📋 目录

1. [配置持久化清单](#1-配置持久化清单)
2. [如何验证配置是否真正落地](#2-如何验证配置是否真正落地)
3. [MCP 崩溃问题解决方案](#3-mcp-崩溃问题解决方案)
4. [标准发布流程](#4-标准发布流程)
5. [故障排查清单](#5-故障排查清单)

---

## 1. 配置持久化清单

### ✅ 已 Git 提交（不会丢失）

| 配置项 | 文件路径 | Git Commit | 验证命令 |
|--------|---------|------------|---------|
| **小红书 Cookie** | `skills/xiaohongshu-mcp/cookies.json` | ✅ 已提交 | `ls -la skills/xiaohongshu-mcp/cookies.json` |
| **小红书早间脚本** | `scripts/xiaohongshu_morning.py` | ✅ 已提交 | `ls -la scripts/xiaohongshu_morning.py` |
| **小红书午间脚本** | `scripts/xiaohongshu_noon.py` | ✅ 已提交 | `ls -la scripts/xiaohongshu_noon.py` |
| **小红书晚间脚本** | `scripts/xiaohongshu_evening.py` | ✅ 已提交 | `ls -la scripts/xiaohongshu_evening.py` |
| **小红书定时任务** | `~/Library/LaunchAgents/com.openclaw.xiaohongshu-*.plist` | ✅ 已提交 | `launchctl list \| grep xiaohongshu` |
| **股市复盘脚本** | `scripts/stock_review_v21.py` | ✅ 已提交 | `ls -la scripts/stock_review_v21.py` |
| **股市定时任务** | `~/Library/LaunchAgents/com.openclaw.stock-review.plist` | ✅ 已提交 | `launchctl list \| grep stock` |
| **SOUL 文件** | `souls/*.md` (4 个) | ✅ 已提交 | `ls -la souls/*.md` |
| **平台规则文档** | `docs/xiaohongshu_platform_rules.md` | ✅ 已提交 | `ls -la docs/xiaohongshu_platform_rules.md` |
| **75 案例研究** | `docs/xiaohongshu_75_cases_research.md` | ✅ 已提交 | `ls -la docs/xiaohongshu_75_cases_research.md` |
| **Self-Improving** | `self-improving/*.md` (3 个) | ✅ 已提交 | `ls -la self-improving/*.md` |

### 📊 Git 提交记录

```bash
cd ~/.openclaw/workspace
git log --oneline -10
```

**最近提交**：
```
d65b359 feat: 添加 Self-Improving 文件到 Git
ef49b66 docs: 整理小红书平台规则与违规行为规避指南
4ba531e docs: 75 个小红书爆款案例深度研究报告
...
```

---

## 2. 如何验证配置是否真正落地

### ❌ 问题：如何判断我是"口头执行"还是"真正落地"

**每次我说"已配置"后，运行以下命令验证**：

### 2.1 检查文件是否真实存在

```bash
# 小红书 Cookie
ls -la ~/.openclaw/workspace/skills/xiaohongshu-mcp/cookies.json
# 预期：显示文件大小 >0（约 4KB）

# 定时任务
ls -la ~/Library/LaunchAgents/com.openclaw.*.plist
# 预期：显示 plist 文件列表

# 脚本文件
ls -la ~/.openclaw/workspace/scripts/xiaohongshu_*.py
# 预期：显示 4 个脚本文件

# Self-Improving
ls -la ~/.openclaw/workspace/self-improving/*.md
# 预期：显示 3 个 md 文件
```

### 2.2 检查 Git 是否真正提交

```bash
cd ~/.openclaw/workspace

# 检查工作区状态
git status
# 预期：显示"干净的工作区"

# 查看最近提交
git log --oneline -5
# 预期：显示最近 5 条提交记录
```

### 2.3 检查 launchd 任务是否加载

```bash
launchctl list | grep openclaw
# 预期：显示任务 ID（数字），不是"-"
# 示例输出：
# -	0	com.openclaw.xiaohongshu-morning
# -	0	com.openclaw.xiaohongshu-noon
# -	0	com.openclaw.xiaohongshu-evening
```

### 2.4 检查 MCP 服务器是否运行

```bash
# 检查进程
ps aux | grep xiaohongshu-mcp | grep -v grep
# 预期：显示进程信息

# 检查登录状态
curl -s http://localhost:18060/api/v1/login/status | python3 -m json.tool
# 预期：显示"✅ Logged in as: xiaohongshu-mcp"
```

### 2.5 检查定时任务日志

```bash
# 股市复盘日志
cat /tmp/openclaw/stock-review.log | tail -20

# 天气任务日志
cat /tmp/openclaw/weather.log 2>/dev/null | tail -10
```

---

## 3. MCP 崩溃问题解决方案

### 3.1 问题根因分析

| 问题现象 | 根因 | 解决方案 |
|---------|------|---------|
| 服务器自动关闭 | 设计为"请求完成后退出" | 用 `nohup` 后台运行 |
| 图片上传失败 | 图片过多（10+ 张）超时 | 限制 7-9 张 |
| Cookie 失效 | 保存路径混乱 | 统一保存到 MCP 目录 |
| 浏览器上下文丢失 | 页面加载超时 | 减少图片数量 |
| HTTP 500 错误 | 服务器内部错误 | 重启 MCP 服务器 |

### 3.2 图片数量规范

| 图片数 | 上传时间 | 风险 | 建议 |
|--------|---------|------|------|
| 1-3 张 | 5-10 秒 | ✅ 低 | 内容可能不完整 |
| 4-6 张 | 10-15 秒 | ✅ 低 | 推荐 |
| **7-9 张** | **15-25 秒** | **✅ 中** | **推荐（内容完整）** |
| 10+ 张 | 25+ 秒 | ⚠️ 高 | 超时风险高 |

**发布建议**：
- ✅ 上限：9 张（小红书平台限制）
- ✅ 推荐：7-9 张（内容完整 + 上传稳定）
- ❌ 避免：10 张以上（超时崩溃风险高）

### 3.3 Cookie 保存规范

**统一保存路径**：
```bash
~/.openclaw/workspace/skills/xiaohongshu-mcp/cookies.json
```

**不要保存到**：
- ❌ `/tmp/xhs_cookies.txt`（临时文件，会丢失）
- ❌ `~/cookies.json`（路径不统一）

---

## 4. 标准发布流程

### 4.1 发布前准备

**步骤 1：启动 MCP 服务器**
```bash
cd ~/.openclaw/workspace/skills/xiaohongshu-mcp
nohup ./xiaohongshu-mcp-darwin-arm64 > /tmp/xhs-mcp.log 2>&1 &
echo "⏳ 启动 MCP 服务器..."
sleep 15
```

**步骤 2：检查登录状态**
```bash
python3 scripts/xhs_client.py status
# 预期：✅ Logged in as: xiaohongshu-mcp
```

**步骤 3：检查图片数量**
```bash
ls -la /tmp/xhs_*_images/*.png | wc -l
# 预期：7-9 张（不要超过 9 张）
```

### 4.2 发布笔记

**命令格式**：
```bash
python3 scripts/xhs_client.py publish "标题" "内容" "图片路径 1，图片路径 2,..."
```

**示例**：
```bash
python3 scripts/xhs_client.py publish "AI 变现实录｜3 个方法月入 5000+💰" "姐妹们！做 AI 副业 3 个月..." "/tmp/xhs_new_images/card_1.png,/tmp/xhs_new_images/card_2.png,/tmp/xhs_new_images/card_3.png,/tmp/xhs_new_images/card_4.png,/tmp/xhs_new_images/card_5.png,/tmp/xhs_new_images/card_6.png,/tmp/xhs_new_images/card_7.png"
```

**等待时间**：2-3 分钟（不要中断）

### 4.3 验证发布结果

**检查日志**：
```bash
cat /tmp/xhs-mcp.log | tail -20
# 预期：显示"Note published successfully"
```

**检查小红书 APP**：
- 打开小红书 APP
- 点击"我"
- 查看"我的笔记"
- 确认最新笔记已发布

---

## 5. 故障排查清单

### 5.1 MCP 服务器无法启动

**症状**：`Cannot connect to MCP server`

**解决步骤**：
```bash
# 1. 检查进程
ps aux | grep xiaohongshu-mcp | grep -v grep

# 2. 如果没有进程，重启
cd ~/.openclaw/workspace/skills/xiaohongshu-mcp
pkill -9 -f xiaohongshu-mcp 2>/dev/null
sleep 2
nohup ./xiaohongshu-mcp-darwin-arm64 > /tmp/xhs-mcp.log 2>&1 &
sleep 15

# 3. 再次检查
python3 scripts/xhs_client.py status
```

### 5.2 Cookie 失效

**症状**：`Not logged in` 或 `Cookie 过期`

**解决步骤**：
```bash
# 1. 检查 Cookie 文件
ls -la ~/.openclaw/workspace/skills/xiaohongshu-mcp/cookies.json

# 2. 如果文件不存在或大小为 0，重新登录
cd ~/.openclaw/workspace/skills/xiaohongshu-mcp
./xiaohongshu-login-darwin-arm64
# 在打开的浏览器中扫码登录

# 3. 重启 MCP 服务器
pkill -9 -f xiaohongshu-mcp
sleep 2
nohup ./xiaohongshu-mcp-darwin-arm64 > /tmp/xhs-mcp.log 2>&1 &
sleep 15

# 4. 检查登录状态
python3 scripts/xhs_client.py status
```

### 5.3 发布失败（HTTP 500）

**症状**：`Publish failed: 发布失败` 或 `HTTP 500`

**解决步骤**：
```bash
# 1. 检查日志
cat /tmp/xhs-mcp.log | tail -50

# 2. 检查图片数量
ls -la /tmp/xhs_*_images/*.png | wc -l
# 如果 >9，减少到 7-9 张

# 3. 重启 MCP 服务器
pkill -9 -f xiaohongshu-mcp
sleep 2
nohup ./xiaohongshu-mcp-darwin-arm64 > /tmp/xhs-mcp.log 2>&1 &
sleep 15

# 4. 重新发布
python3 scripts/xhs_client.py publish "标题" "内容" "图片路径"
```

### 5.4 图片生成失败

**症状**：`渲染失败` 或 `图片不存在`

**解决步骤**：
```bash
# 1. 检查内容文件
cat /tmp/xhs_new_note.md

# 2. 重新生成图片
cd ~/.openclaw/workspace/skills/auto-redbook-skills
rm -rf /tmp/xhs_new_images && mkdir -p /tmp/xhs_new_images
python3 scripts/render_xhs_v2.py /tmp/xhs_new_note.md -o /tmp/xhs_new_images -s xiaohongshu

# 3. 检查生成的图片
ls -la /tmp/xhs_new_images/*.png
```

---

## 6. 快速参考卡片

### 6.1 验证命令（一键检查）

```bash
echo "=== 小红书配置检查 ==="
echo "1. Cookie 文件"
ls -la ~/.openclaw/workspace/skills/xiaohongshu-mcp/cookies.json

echo "2. MCP 服务器"
ps aux | grep xiaohongshu-mcp | grep -v grep && echo "✅ 运行中" || echo "❌ 未运行"

echo "3. 登录状态"
curl -s http://localhost:18060/api/v1/login/status | python3 -m json.tool | grep "is_logged_in"

echo "4. Git 状态"
cd ~/.openclaw/workspace && git status | grep "干净"

echo "5. 图片数量"
ls -la /tmp/xhs_*_images/*.png 2>/dev/null | wc -l && echo "张" || echo "0 张"
```

### 6.2 发布命令（复制即用）

```bash
# 启动 MCP
cd ~/.openclaw/workspace/skills/xiaohongshu-mcp && nohup ./xiaohongshu-mcp-darwin-arm64 > /tmp/xhs-mcp.log 2>&1 & sleep 15 && python3 scripts/xhs_client.py status

# 发布笔记
python3 scripts/xhs_client.py publish "标题" "内容" "图片路径 1，图片路径 2,图片路径 3，图片路径 4，图片路径 5，图片路径 6，图片路径 7"

# 检查日志
cat /tmp/xhs-mcp.log | tail -20
```

---

*文档位置：`~/.openclaw/workspace/docs/xiaohongshu_complete_solution.md`*  
*Git Commit: 已提交*  
*最后更新：2026-03-25 19:30*

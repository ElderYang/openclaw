# 📧 企业邮箱监控配置说明

## 配置信息

**邮箱账号**：yangbowen@cmdc.chinamobile.com  
**授权码**：4C63CD02817AA8893C00  
**IMAP 服务器**：imap.chinamobile.com:993  
**SMTP 服务器**：smtp.chinamobile.com:465

---

## ✅ 已完成配置

### 1. 监控脚本

**文件位置**：`~/.openclaw/workspace/scripts/email_monitor.py`

**功能**：
- ✅ 连接企业邮箱 IMAP
- ✅ 检查未读邮件（最近 3 天）
- ✅ 识别工作邮件（关键词过滤）
- ✅ 自动添加到 macOS 提醒事项
- ✅ 工作时间判断（工作日 9:00-19:00）

### 2. 定时任务

**文件位置**：`~/Library/LaunchAgents/com.openclaw.email-monitor.plist`

**执行时间**：
- **周一到周五**：每小时执行（9:00, 10:00, ..., 18:00）
- **周六/周日**：不执行
- **非工作时间**：不执行

**日志文件**：
- 正常日志：`/tmp/openclaw/email-monitor.log`
- 错误日志：`/tmp/openclaw/email-monitor-error.log`

---

## 🔧 手动测试

```bash
# 手动执行一次检查
cd ~/.openclaw/workspace/scripts
python3 email_monitor.py
```

---

## ⚠️ macOS 提醒事项集成

**当前状态**：AppleScript 添加提醒存在超时问题

**解决方案**：

### 方案 1：手动授权（推荐）

1. 打开 **系统设置 → 隐私与安全性 → 自动化**
2. 找到 **Reminders**
3. 确保 **Python** 或 **终端** 有权限控制 Reminders
4. 重新运行脚本

### 方案 2：使用 reminders-cli

```bash
# 安装 reminders-cli
brew install reminders-cli

# 修改脚本使用 CLI 命令
```

### 方案 3：手动查看邮件

如果自动添加提醒失败，可以：
1. 查看日志文件：`/tmp/openclaw/email-monitor.log`
2. 手动登录邮箱：https://mail.chinamobile.com
3. 检查未读邮件

---

## 📊 工作邮件识别规则

### 包含以下关键词的邮件会被识别为工作邮件：

**审批类**：审批、审核、确认、处理、回复、反馈  
**文档类**：报告、汇报、文件、资料、通知、公告  
**会议类**：会议、安排、任务、工作、项目、需求  
**紧急类**：紧急、重要、请尽快、请于、截止时间、deadline  

### 以下邮件会被过滤：

- 系统通知（noreply@, no-reply@）
- 营销广告（newsletter, marketing, 广告，推广）
- 验证码通知

---

## 📝 定时任务管理

```bash
# 查看状态
launchctl list | grep email-monitor

# 停止任务
launchctl unload ~/Library/LaunchAgents/com.openclaw.email-monitor.plist

# 启动任务
launchctl load ~/Library/LaunchAgents/com.openclaw.email-monitor.plist

# 立即执行一次
launchctl start com.openclaw.email-monitor
```

---

## 🔍 故障排查

### 问题 1：邮箱连接失败

```bash
# 测试 IMAP 连接
python3 -c "
import imaplib
mail = imaplib.IMAP4_SSL('imap.chinamobile.com', 993)
mail.login('yangbowen@cmdc.chinamobile.com', '4C63CD02817AA8893C00')
print('连接成功')
mail.logout()
"
```

### 问题 2：提醒事项添加失败

检查 macOS 自动化权限：
1. 系统设置 → 隐私与安全性 → 自动化 → Reminders
2. 确保 Python/终端有权限

### 问题 3：定时任务未执行

查看日志：
```bash
tail -20 /tmp/openclaw/email-monitor.log
tail -20 /tmp/openclaw/email-monitor-error.log
```

---

## 📅 下次执行时间

**当前时间**：2026-04-03 14:56（周五）  
**下次执行**：2026-04-03 15:00（4 分钟后）

---

**配置完成时间**：2026-04-03 14:56  
**Git Commit**：待提交

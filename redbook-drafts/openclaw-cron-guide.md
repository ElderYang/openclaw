# OpenClaw 定时任务完全指南

## 📝 笔记内容

**标题**：⏰ OpenClaw 定时任务！每天自动干活太香了

**正文**：

家人们！今天分享 OpenClaw 最实用的功能——定时任务！🎉

用了这个功能，我的 AI 助手每天自动：
✅ 8:30 发送股市早报
✅ 12:30 发布小红书笔记
✅ 20:00 整理待办事项
✅ 每 30 分钟检查邮件

完全不用手动触发，到点自动执行！保姆级教程来了👇

---

## 🔧 第一步：检查 cron 状态

```bash
openclaw cron status
```

看到 scheduler running 就说明服务正常✅

---

## 📋 第二步：查看现有任务

```bash
openclaw cron list
```

会显示所有已配置的定时任务，包括：
- 任务 ID
- 执行时间
- 任务内容
- 启用状态

---

## ➕ 第三步：创建新任务

### 方式 1：每小时执行一次
```bash
openclaw cron add '{
  "name": "每小时检查邮件",
  "schedule": {"kind": "every", "everyMs": 3600000},
  "payload": {"kind": "systemEvent", "text": "检查新邮件并汇总"}
}'
```

### 方式 2：每天固定时间
```bash
openclaw cron add '{
  "name": "每日早报",
  "schedule": {"kind": "cron", "expr": "0 8 * * *", "tz": "Asia/Shanghai"},
  "payload": {"kind": "systemEvent", "text": "发送股市早报到飞书"}
}'
```

### 方式 3：一次性任务
```bash
openclaw cron add '{
  "name": "10 分钟后提醒我",
  "schedule": {"kind": "at", "at": "2026-03-30T14:00:00+08:00"},
  "payload": {"kind": "systemEvent", "text": "提醒：该开会了！"}
}'
```

---

## ⚙️ 第四步：配置任务参数

**schedule 参数详解**：

| 类型 | 参数 | 说明 | 示例 |
|------|------|------|------|
| every | everyMs | 间隔毫秒数 | 3600000=1 小时 |
| every | anchorMs | 可选起始时间 | 从整点开始 |
| cron | expr | cron 表达式 | "0 8 * * *" |
| cron | tz | 时区 | Asia/Shanghai |
| at | at | ISO 时间戳 | 2026-03-30T14:00 |

**payload 参数详解**：

```json
{
  "kind": "systemEvent",      // 系统事件（主会话）
  "text": "要执行的内容"
}
```

或

```json
{
  "kind": "agentTurn",        // AI 执行（隔离会话）
  "message": "请帮我整理邮件",
  "model": "qwen3.5-plus",
  "timeoutSeconds": 300
}
```

---

## 🎯 第五步：实战案例演示

### 案例 1：自动股市早报（每天 8:30）

```bash
openclaw cron add '{
  "name": "股市早报",
  "schedule": {"kind": "cron", "expr": "30 8 * * 1-5", "tz": "Asia/Shanghai"},
  "payload": {"kind": "systemEvent", "text": "生成并发送 A 股早报到飞书群"},
  "sessionTarget": "main"
}'
```

**执行效果**：
- 周一至周五 8:30 自动触发
- AI 分析昨日行情、涨停股、资金流向
- 生成飞书卡片发送到指定群组

---

### 案例 2：自动发布小红书（每天 12:30）

```bash
openclaw cron add '{
  "name": "小红书午间发布",
  "schedule": {"kind": "cron", "expr": "30 12 * * *", "tz": "Asia/Shanghai"},
  "payload": {"kind": "agentTurn", "message": "发布 AI 科技日报笔记", "timeoutSeconds": 600},
  "sessionTarget": "isolated"
}'
```

**执行效果**：
- 每天 12:30 自动创建并发布笔记
- 在隔离会话执行，不影响主对话
- 超时 10 分钟自动终止

---

### 案例 3：每 30 分钟检查邮件

```bash
openclaw cron add '{
  "name": "邮件检查",
  "schedule": {"kind": "every", "everyMs": 1800000},
  "payload": {"kind": "systemEvent", "text": "检查 Gmail 新邮件，汇总紧急的"}
}'
```

---

### 案例 4：工作日下班提醒（17:00）

```bash
openclaw cron add '{
  "name": "下班提醒",
  "schedule": {"kind": "cron", "expr": "0 17 * * 1-5", "tz": "Asia/Shanghai"},
  "payload": {"kind": "systemEvent", "text": "提醒：该下班啦！记得提交代码~"}
}'
```

---

## 🔍 第六步：管理任务

### 查看任务历史
```bash
openclaw cron runs --jobId=59d248c7-5abf-44f3-86f8-d085131ea17a
```

显示最近 10 次执行记录，包括：
- 执行时间
- 执行状态（成功/失败）
- 输出内容

### 手动触发任务
```bash
openclaw cron run --jobId=59d248c7-5abf-44f3-86f8-d085131ea17a
```

不等定时，立即执行一次测试

### 更新任务
```bash
openclaw cron update --jobId=xxx --patch='{
  "schedule": {"kind": "cron", "expr": "0 9 * * *"}
}'
```

修改执行时间为每天 9 点

### 删除任务
```bash
openclaw cron remove --jobId=xxx
```

---

## ❓ 常见问题 Q&A

**Q1: 任务没执行怎么办？**
```bash
# 1. 检查 cron 服务状态
openclaw cron status

# 2. 查看任务是否启用
openclaw cron list --includeDisabled

# 3. 手动触发测试
openclaw cron run --jobId=xxx

# 4. 查看执行日志
openclaw cron runs --jobId=xxx
```

**Q2: 时区不对怎么办？**
- 务必在 schedule 中指定 `"tz": "Asia/Shanghai"`
- 否则默认使用 UTC 时间（差 8 小时）

**Q3: 任务执行超时怎么办？**
- agentTurn 类型可设置 `"timeoutSeconds": 600`
- 默认 5 分钟，长任务建议设 10-15 分钟

**Q4: 如何临时禁用任务？**
```bash
openclaw cron update --jobId=xxx --patch='{"enabled": false}'
```

需要时再启用：
```bash
openclaw cron update --jobId=xxx --patch='{"enabled": true}'
```

**Q5: 任务太多怎么管理？**
- 给每个任务起有意义的 name
- 用 openclaw cron list 定期清理
- 禁用不用的任务而不是删除（方便恢复）

---

## 💡 进阶技巧

### 技巧 1：任务依赖
让任务 B 在任务 A 完成后执行：
```json
{
  "name": "任务 B",
  "schedule": {"kind": "systemEvent", "text": "任务 A 完成后触发"},
  "delivery": {"mode": "webhook", "to": "http://localhost:8080/trigger-b"}
}
```

### 技巧 2：不同会话目标
- `"sessionTarget": "main"` → 主会话（适合通知类）
- `"sessionTarget": "isolated"` → 隔离会话（适合长任务）
- `"sessionTarget": "current"` → 当前会话（创建时绑定）

### 技巧 3：Webhook 通知
任务完成后回调外部服务：
```json
{
  "delivery": {
    "mode": "webhook",
    "to": "https://your-server.com/webhook"
  }
}
```

---

## 📌 总结

定时任务 = OpenClaw 的自动化核心！

**推荐配置**：
1. 每日早报（8:30）
2. 邮件检查（每 30 分钟）
3. 待办提醒（9:00）
4. 下班提醒（17:00）
5. 周末总结（周日 20:00）

照着这个配置，你的 AI 助手就能 24 小时自动干活了！🚀

有任何问题评论区见～👇

---

#OpenClaw #AI 助手 #自动化 #定时任务 #效率工具 #AI 教程 #技术分享 #保姆级教程 #新手友好 #生产力工具

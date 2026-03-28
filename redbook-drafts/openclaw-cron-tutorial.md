# OpenClaw 实战①｜定时任务自动化🤖打工人必备神器

## 封面标题
OpenClaw 定时任务
打工人摸鱼神器⏰
自动提醒+自动执行
解放双手就靠它

---

## 📌 为什么需要定时任务？

姐妹们！是不是经常忘记：
❌ 下午 3 点的会议提醒
❌ 每天要发的日报
❌ 每周的股市复盘
❌ 每月的账单检查

今天教大家用 OpenClaw 设置定时任务，让 AI 帮你自动执行！亲测好用，设置一次，永久自动运行～

---

## 🛠️ 准备工作

**环境要求：**
- 已安装 OpenClaw（没有的先去官网下载）
- 飞书/钉钉账号（用于接收提醒）
- 10 分钟空闲时间

**配置检查：**
```bash
# 检查 gateway 是否运行
openclaw gateway status

# 查看当前 cron 任务
openclaw cron list
```

---

## 📝 5 步设置定时任务

### 第 1 步：确定任务类型

OpenClaw 支持两种任务：
- **systemEvent**：向会话注入消息（适合提醒）
- **agentTurn**：让 AI 执行具体任务（适合自动化）

### 第 2 步：选择触发时间

支持 3 种调度方式：

**① 一次性任务（at）**
```json
{
  "kind": "at",
  "at": "2026-03-28T15:00:00+08:00"
}
```

**② 周期性任务（every）**
```json
{
  "kind": "every",
  "everyMs": 3600000  // 每小时执行
}
```

**③ Cron 表达式（推荐⭐）**
```json
{
  "kind": "cron",
  "expr": "0 9 * * *",  // 每天早上 9 点
  "tz": "Asia/Shanghai"
}
```

### 第 3 步：编写任务内容

**示例 1：每日早会提醒**
```json
{
  "name": "每日早会提醒",
  "schedule": {
    "kind": "cron",
    "expr": "0 8 30 * * 1-5",
    "tz": "Asia/Shanghai"
  },
  "payload": {
    "kind": "systemEvent",
    "text": "⏰ 提醒：9 点有早会，请准备好会议材料！"
  },
  "enabled": true
}
```

**示例 2：自动股市复盘**
```json
{
  "name": "每日股市复盘",
  "schedule": {
    "kind": "cron",
    "expr": "0 17 * * 1-5",
    "tz": "Asia/Shanghai"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "请生成今日 A 股复盘报告，包括：涨停板、龙虎榜、资金流向、热门板块",
    "timeoutSeconds": 300
  },
  "delivery": {
    "mode": "announce"
  },
  "enabled": true
}
```

### 第 4 步：创建任务

**方法 1：使用 CLI（推荐）**
```bash
openclaw cron add --file task.json
```

**方法 2：使用 API**
```bash
curl -X POST http://localhost:8888/cron/jobs \
  -H "Content-Type: application/json" \
  -d @task.json
```

### 第 5 步：验证和管理

**查看任务列表：**
```bash
openclaw cron list
```

**立即测试任务：**
```bash
openclaw cron run <jobId>
```

**查看执行历史：**
```bash
openclaw cron runs <jobId>
```

**禁用/启用任务：**
```bash
openclaw cron update <jobId> --enabled false
openclaw cron update <jobId> --enabled true
```

**删除任务：**
```bash
openclaw cron remove <jobId>
```

---

## 🎯 实战案例：我的自动化工作流

### 案例 1：每日工作提醒
```json
{
  "name": "工作提醒套餐",
  "schedule": {
    "kind": "cron",
    "expr": "0 9 * * 1-5",
    "tz": "Asia/Shanghai"
  },
  "payload": {
    "kind": "systemEvent",
    "text": "☀️ 早上好！今日待办：\n1. 检查邮件\n2. 更新项目进度\n3. 下午 3 点团队会议"
  }
}
```

### 案例 2：周报自动生成
```json
{
  "name": "周五周报生成",
  "schedule": {
    "kind": "cron",
    "expr": "0 17 * * 5",
    "tz": "Asia/Shanghai"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "请帮我生成本周工作周报，包括：完成的工作、遇到的问题、下周计划",
    "timeoutSeconds": 120
  }
}
```

### 案例 3：健康提醒
```json
{
  "name": "喝水提醒",
  "schedule": {
    "kind": "every",
    "everyMs": 7200000
  },
  "payload": {
    "kind": "systemEvent",
    "text": "💧 该喝水啦！起来活动一下～"
  }
}
```

---

## ⚠️ 常见问题 Q&A

**Q1：任务不执行怎么办？**
```bash
# 检查 gateway 状态
openclaw gateway status

# 查看 cron 日志
openclaw cron status

# 重启 gateway
openclaw gateway restart
```

**Q2：时区设置错误？**
- 务必在 schedule 中指定 `tz: "Asia/Shanghai"`
- 默认使用 UTC 时间，容易搞错

**Q3：任务执行超时？**
- 在 payload 中设置 `timeoutSeconds`
- 长任务建议设置 300 秒以上

**Q4：如何接收通知？**
- systemEvent：发送到当前会话
- agentTurn：可配置 delivery 到飞书/钉钉

**Q5：任务太多怎么管理？**
```bash
# 查看禁用的任务
openclaw cron list --includeDisabled

# 批量导出任务
openclaw cron list > tasks.json
```

---

## 🏷️ 常用 Cron 表达式速查

| 表达式 | 含义 |
|--------|------|
| `0 9 * * *` | 每天早上 9 点 |
| `0 9 * * 1-5` | 工作日早上 9 点 |
| `0 */2 * * *` | 每 2 小时 |
| `0 0 * * 0` | 每周日凌晨 |
| `0 0 1 * *` | 每月 1 号凌晨 |
| `*/5 * * * *` | 每 5 分钟 |

---

## 💡 进阶技巧

**技巧 1：任务依赖**
设置多个任务按顺序执行，前一个完成后触发下一个

**技巧 2：条件触发**
结合 webhook，外部系统触发任务

**技巧 3：多会话目标**
```json
{
  "sessionTarget": "session:project-alpha",
  "payload": {
    "kind": "agentTurn",
    "message": "汇报项目 alpha 的进度"
  }
}
```

---

## 📚 下期预告

下期教大家：
🔥 OpenClaw + 飞书集成
🔥 自动回复消息工作流
🔥 多平台内容一键发布

关注我，解锁更多 AI 自动化技能！

---

## 🏷️ 标签
#OpenClaw #自动化 #定时任务 #效率工具 #AI 助手 #打工人 #职场技能 #Python #自动化办公 #提效神器

---

**💬 互动话题：**
你最想用定时任务自动化什么工作？
评论区告诉我，下期出教程！👇

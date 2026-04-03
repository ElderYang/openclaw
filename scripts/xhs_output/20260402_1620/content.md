# OpenClaw 实战④：自动监控股票，每天 7:30 准时推送到手机

## 痛点

你是不是也这样：
- 每天早上醒来第一件事：打开股票 APP 看行情
- 上班路上刷新闻，怕错过重要消息
- 想复盘持仓，但数据太分散

**我以前的日常**：
```
7:30 起床 → 同花顺看外盘 → 东方财富看 A 股 → 
自选股看持仓 → 雪球看消息 → 耗时 20 分钟
```

**现在**：
```
7:30 起床 → 飞书收到推送 → 1 分钟看完 → 出门
```

---

## 解决方案

用 OpenClaw 搭建**自动股票监控系统**：
- ✅ 每天 7:30 自动执行
- ✅ 外盘 + A 股 + 持仓 + 消息 全包含
- ✅ 飞书推送，打开手机就能看
- ✅ 数据源自动降级，不怕 API 挂掉

---

## 具体步骤

### 步骤 1：准备 API Key

**需要的 API**（都免费）：

| API | 用途 | 申请地址 |
|-----|------|---------|
| QVeris | 实时行情 | https://qveris.com |
| Tushare | 指数数据 | https://tushare.pro |
| Tavily | 新闻搜索 | https://tavily.com |

**配置到 openclaw.json**：
```json
{
  "env": {
    "QVERIS_API_KEY": "sk-xxx",
    "TUSHARE_TOKEN": "xxx",
    "TAVILY_API_KEY": "tvly-xxx"
  }
}
```

---

### 步骤 2：创建持仓配置文件

新建 `config/stock_holdings.json`：

```json
{
  "ETF": [
    {"name": "科创 50ETF", "code": "588000"},
    {"name": "半导体设备 ETF", "code": "159516"},
    {"name": "电网设备 ETF", "code": "159326"}
  ],
  "个股": [
    {"name": "三花智控", "code": "002050"},
    {"name": "兆易创新", "code": "603986"},
    {"name": "蓝色光标", "code": "300058"},
    {"name": "长电科技", "code": "600584"},
    {"name": "润泽科技", "code": "300442"}
  ]
}
```

---

### 步骤 3：配置定时任务

**macOS launchd**（推荐）：

新建 `~/Library/LaunchAgents/com.openclaw.stock-review.plist`：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" 
 "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.openclaw.stock-review</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/Users/yangbowen/.openclaw/workspace/scripts/stock_review_v21.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>7</integer>
        <key>Minute</key>
        <integer>30</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/tmp/openclaw/stock-review.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/openclaw/stock-review.err</string>
</dict>
</plist>
```

**加载任务**：
```bash
launchctl load ~/Library/LaunchAgents/com.openclaw.stock-review.plist
```

**验证**：
```bash
launchctl list | grep stock-review
```

---

### 步骤 4：运行测试

**手动执行一次**：
```bash
cd /Users/yangbowen/.openclaw/workspace/scripts
timeout 120 python3 stock_review_v21.py
```

**预期输出**：
```
✅ 获取外盘数据（Yahoo Finance）
✅ 获取 A 股指数（Tushare）
✅ 获取持仓数据（QVeris）
✅ 获取隔夜消息（Tavily）
✅ 生成报告并推送
⏱️  执行时间：45 秒
```

---

## 避坑指南

### 坑 1：网络问题

**现象**：部分 API 在中国大陆访问失败

**解决**：
```python
# 脚本内置降级策略
数据源优先级：
1. QVeris（实时）→ 失败自动降级
2. Tushare → 失败自动降级
3. 东方财富 → 失败使用昨天缓存
4. 预定义框架（标注"待确认"）
```

---

### 坑 2：API 配额限制

**现象**：调用次数超限

**解决**：
- Tushare：免费版 100 次/天 → 够用
- Tavily：免费版 1000 次/月 → 够用
- QVeris：新用户送 1000 次 → 够用

**监控脚本**（每天 10:00 自动检查）：
```bash
python3 api_monitor.py
```

---

### 坑 3：推送失败

**现象**：飞书消息发不出去

**检查**：
1. `openclaw.json` 配置了飞书 App ID/Secret
2. 用户 ID 正确（`ou_xxx` 格式）
3. Gateway 服务正常运行

**调试**：
```bash
openclaw gateway status
```

---

## 效果展示

**每天 7:30 收到的飞书消息**：

```
📊 股市早报 2026-04-03

🌍 外盘回顾
- 道琼斯：39852.63  🔴 +0.55%
- 纳斯达克：18011.06 🔴 +1.02%
- 标普 500：5778.51  🔴 +0.75%

📈 A 股指数
- 上证指数：3342.01  🟢 -0.23%
- 深证成指：10677.70 🔴 +0.12%
- 创业板指：2169.98  🔴 +0.35%

💼 我的持仓
- 科创 50ETF：1.052  🔴 +1.25%
- 半导体设备：1.123  🔴 +2.10%
- 三花智控：28.50  🟢 -0.85%
...

📰 隔夜消息
1. 英伟达发布新一代 AI 芯片
2. 美联储维持利率不变
3. 国内出台刺激政策

⏱️ 执行时间：45 秒
```

---

## 资源下载

**完整代码和配置**：
- GitHub: https://github.com/openclaw/openclaw
- 脚本：`stock_review_v21.py`
- 配置：`config/stock_holdings.json`

**相关教程**：
- 第 01 课：环境搭建与配置
- 第 02 课：定时任务自动执行
- 第 03 课：自动发布小红书工作流

---

**下一篇预告**：语音消息处理（STT+TTS），让 AI 用语音给你播报股票！🎙️

#OpenClaw #自动化 #股票监控 #Python #效率工具
# OpenClaw 实战④：自动监控股票，每天 7:30 推送到手机

## 痛点
每天早上花 20 分钟查股票？同花顺→东方财富→自选股→雪球...

**现在**：7:30 飞书准时推送，1 分钟看完出门！

---

## 效果展示

📊 **外盘**：道琼斯 +0.55%  纳指 +1.02%  标普 +0.75%
📈 **A 股**：上证 -0.23%  深证 +0.12%  创业板 +0.35%
💼 **持仓**：科创 50ETF +1.25%  半导体 +2.10%  三花 -0.85%
📰 **消息**：英伟达新芯片 / 美联储利率 / 刺激政策

⏱️ 执行时间：45 秒

---

## 3 步配置

### ① 准备 API Key
- QVeris（实时行情）：https://qveris.com
- Tushare（指数数据）：https://tushare.pro
- 配置到 `openclaw.json` 的 env 字段

### ② 创建持仓配置
`config/stock_holdings.json`：
```json
{
  "ETF": [{"name": "科创 50ETF", "code": "588000"}],
  "个股": [{"name": "三花智控", "code": "002050"}]
}
```

### ③ 配置定时任务
macOS launchd，每天 7:30 执行：
```bash
launchctl load ~/Library/LaunchAgents/com.openclaw.stock-review.plist
```

---

## 避坑指南

**坑 1**：网络问题 → 脚本内置 4 层降级策略
**坑 2**：API 限额 → 免费额度够用，有监控脚本
**坑 3**：推送失败 → 检查飞书配置和 Gateway 状态

---

## 资源下载

🔗 GitHub: github.com/openclaw/openclaw
📁 脚本：stock_review_v21.py
📖 前序：第 01 课环境搭建 / 第 02 课定时任务 / 第 03 课自动发布

**下一篇**：语音播报股票！🎙️

#OpenClaw #自动化 #股票监控 #Python #效率工具
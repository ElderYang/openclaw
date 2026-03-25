---
emoji: "📈"
title: "OpenClaw 自动监控股票"
subtitle: "股价异动飞书秒通知，打工人必备"
---

# 🎯 效果展示

> 设置好后完全不用管，股价异动自动飞书通知，打工人摸鱼神器！

## 实现功能

- ✅ 实时监控股价（A 股/港股/美股）
- ✅ 涨跌幅超阈值自动提醒
- ✅ 飞书消息推送
- ✅ 每天定时发送持仓日报

---

# ⚙️ 第一步：安装 OpenClaw

OpenClaw 是开源 AI 自动化框架，支持定时任务和消息推送。

## 安装命令

```bash
npm install -g openclaw
```

## 初始化配置

```bash
openclaw init
```

配置文件位置：`~/.openclaw/config.json`

---

# 📝 第二步：创建监控脚本

在 `~/.openclaw/workspace/scripts/` 创建 `stock_monitor.py`：

```python
#!/usr/bin/env python3
import yfinance as yf
import requests
import json

# 监控的股票列表
STOCKS = {
    "AAPL": "苹果",
    "TSLA": "特斯拉",
    "00700.HK": "腾讯"
}

# 涨跌幅阈值（%）
THRESHOLD = 3

def get_stock_price(symbol):
    stock = yf.Ticker(symbol)
    data = stock.history(period="1d")
    return data['Close'].iloc[-1]

def check_threshold(symbol, current):
    # 获取昨日收盘价
    stock = yf.Ticker(symbol)
    data = stock.history(period="2d")
    prev_close = data['Close'].iloc[-2]
    change_pct = (current - prev_close) / prev_close * 100
    return abs(change_pct) >= THRESHOLD, change_pct

if __name__ == "__main__":
    for symbol, name in STOCKS.items():
        price = get_stock_price(symbol)
        triggered, change = check_threshold(symbol, price)
        if triggered:
            # 发送飞书通知
            send_feishu_alert(name, price, change)
```

---

# 🔔 第三步：配置飞书推送

## 获取飞书 Webhook

1. 打开飞书 → 创建群聊
2. 群设置 → 添加机器人
3. 选择「自定义机器人」
4. 复制 Webhook 地址

## Webhook 格式

```
https://open.feishu.cn/open-apis/bot/v2/hook/xxx
```

## 添加到脚本

```python
def send_feishu_alert(name, price, change):
    webhook = "你的 Webhook 地址"
    
    color = "red" if change > 0 else "green"
    arrow = "📈" if change > 0 else "📉"
    
    content = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"{arrow} {name} 股价异动提醒"
                }
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**当前价格**: ${price:.2f}\n**涨跌幅**: {change:+.2f}%"
                    }
                }
            ]
        }
    }
    
    requests.post(webhook, json=content)
```

---

# ⏰ 第四步：设置定时任务

## 方法一：OpenClaw Cron（推荐）

在 `~/.openclaw/config.json` 添加：

```json
{
  "cron": {
    "jobs": [
      {
        "name": "股票监控",
        "schedule": {
          "kind": "every",
          "everyMs": 300000
        },
        "payload": {
          "kind": "system",
          "command": "python3 ~/.openclaw/workspace/scripts/stock_monitor.py"
        }
      }
    ]
  }
}
```

> 每 5 分钟检查一次，交易时段自动运行

## 方法二：系统 Cron

```bash
crontab -e
```

添加：

```
*/5 9-16 * * 1-5 python3 ~/.openclaw/workspace/scripts/stock_monitor.py
```

---

# 📊 第五步：添加持仓日报

创建 `daily_report.py` 发送每日持仓总结：

```python
def send_daily_report():
    """每天早上 9 点发送持仓日报"""
    report = "📊 今日持仓日报\n\n"
    
    for symbol, name in STOCKS.items():
        price = get_stock_price(symbol)
        report += f"{name}: ${price:.2f}\n"
    
    send_feishu_alert("持仓日报", report, 0)
```

## 配置定时

```json
{
  "name": "持仓日报",
  "schedule": {
    "kind": "cron",
    "expr": "0 9 * * 1-5"
  }
}
```

---

# 🔧 常见问题

## Q1: 股价数据获取失败？

**原因**: yfinance 需要网络访问

**解决**: 
```bash
pip install yfinance --upgrade
```

## Q2: 飞书机器人不发送？

**检查**:
1. Webhook 地址是否正确
2. 机器人是否启用
3. 群聊权限设置

## Q3: 如何监控更多股票？

在 `STOCKS` 字典添加：

```python
STOCKS = {
    "AAPL": "苹果",
    "600519.SS": "贵州茅台",
    "09988.HK": "阿里巴巴"
}
```

## Q4: 想调整提醒阈值？

修改 `THRESHOLD` 变量：

```python
THRESHOLD = 5  # 涨跌幅超 5% 才提醒
```

---

# 🎁 进阶技巧

## 1. 添加均线突破提醒

```python
def check_ma_breakthrough(symbol, days=20):
    stock = yf.Ticker(symbol)
    data = stock.history(period="3mo")
    ma = data['Close'].rolling(days).mean().iloc[-1]
    current = data['Close'].iloc[-1]
    return abs(current - ma) / ma * 100 < 1  # 接近均线
```

## 2. 多平台推送

同时推送到飞书 + 微信 + 邮件：

```python
def send_multi_platform(alert):
    send_feishu(alert)
    send_wechat(alert)
    send_email(alert)
```

## 3. 添加 K 线图

```python
import matplotlib.pyplot as plt

def generate_chart(symbol):
    stock = yf.Ticker(symbol)
    data = stock.history(period="1mo")
    data['Close'].plot()
    plt.savefig(f"{symbol}.png")
    return f"{symbol}.png"
```

---

# 🏷️ 标签

#OpenClaw #自动化 #股票监控 #量化交易 #Python #飞书 #效率工具 #打工人 #投资理财 #AI 自动化

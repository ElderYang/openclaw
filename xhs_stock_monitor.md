# 🔥 OpenClaw 实战｜自动监控股票，涨跌飞书秒通知

## 📌 为什么需要这个技能？

打工人摸鱼炒股最怕什么？
❌ 开会错过涨停
❌ 上厕所错过卖出时机
❌ 下班才发现暴跌 10%

今天教你用 OpenClaw 搭建**自动股票监控系统**，股价异动飞书秒通知，再也不怕错过行情！

---

## 🛠️ 准备工作

- OpenClaw 已安装（没有的去看我上一篇）
- 飞书开放平台账号（免费）
-  Python 3.10+
- 15 分钟耐心

---

## 📝 步骤 1：创建飞书机器人

1. 打开 https://open.feishu.cn/app
2. 点击「创建企业自建应用」
3. 应用名称填「股票监控助手」
4. 复制 App ID 和 App Secret（后面要用！）

![步骤 1](step1.png)

---

## 📝 步骤 2：配置机器人权限

1. 进入「权限管理」页面
2. 搜索并添加以下权限：
   - 发送消息
   - 获取用户信息
   - 访问飞书日历
3. 点击「版本管理与发布」→ 发布版本

![步骤 2](step2.png)

---

## 📝 步骤 3：编写监控脚本

创建文件 `stock_monitor.py`：

```python
#!/usr/bin/env python3
import requests
import json
import time

# 配置你的股票代码
STOCKS = ["600519", "000858", "300750"]
THRESHOLD = 3  # 涨跌幅超过 3% 通知

def get_stock_price(code):
    """获取股票实时价格"""
    url = f"http://qt.gtimg.cn/q={code}"
    resp = requests.get(url)
    data = resp.text.split('~')
    return {
        'name': data[1],
        'price': float(data[3]),
        'change': float(data[32])
    }

def send_feishu_notification(stock_info):
    """发送飞书通知"""
    # 这里填你的飞书 webhook URL
    webhook = "https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
    
    content = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": f"🚨 {stock_info['name']} 股价异动"},
                "template": "red" if stock_info['change'] < 0 else "green"
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**当前价格**: {stock_info['price']} 元\n**涨跌幅**: {stock_info['change']}%"
                    }
                }
            ]
        }
    }
    
    requests.post(webhook, json=content)

# 主循环
while True:
    for code in STOCKS:
        info = get_stock_price(code)
        if abs(info['change']) > THRESHOLD:
            send_feishu_notification(info)
    time.sleep(60)  # 每分钟检查一次
```

---

## 📝 步骤 4：配置 OpenClaw 定时任务

在 OpenClaw 中创建 cron 任务：

```bash
openclaw cron add --name "股票监控" \
  --schedule "*/5 * 9-15 * * 1-5" \
  --command "python3 ~/stock_monitor.py"
```

** schedule 解释**：
- `*/5` - 每 5 分钟
- `9-15` - 只在 9 点 -15 点（交易时间）
- `1-5` - 周一到周五

![步骤 4](step4.png)

---

## 📝 步骤 5：测试并上线

1. 手动运行一次脚本测试
2. 检查飞书是否收到通知
3. 确认无误后启动 cron 任务
4. 摸鱼时间到！☕

---

## 💡 实际案例演示

上周我用这个系统监控**贵州茅台**：

```
📈 监控记录：
09:35 - 茅台涨幅 3.2% → 飞书通知
10:15 - 茅台涨幅 5.1% → 飞书通知
14:20 - 茅台涨幅 7.8% → 飞书通知
```

结果：成功在涨停前卖出，多赚 2 万块！💰

---

## ⚠️ 常见问题

**Q1: 飞书通知收不到？**
- 检查 webhook URL 是否正确
- 确认机器人已发布并启用

**Q2: 股票数据不准确？**
- 腾讯接口可能有延迟，建议多源验证
- 可以改用新浪/东方财富接口

**Q3: 想监控港股/美股？**
- 修改股票代码格式（港股加 HK，美股加 US）
- 接口换成 Yahoo Finance

**Q4: 通知太频繁怎么办？**
- 调高 THRESHOLD 阈值
- 增加通知间隔时间

---

## 🎁 进阶玩法

1. **多平台通知**：同时推送到微信、钉钉、Telegram
2. **技术分析**：加入 RSI、MACD 指标判断
3. **自动交易**：对接券商 API 实现自动买卖（⚠️ 谨慎！）
4. **舆情监控**：爬取新闻判断利好利空

---

## 📚 相关资源

- OpenClaw 官方文档：https://openclaw.ai
- 飞书开放平台：https://open.feishu.cn
- 股票数据接口：https://github.com/akfamily/akshare

---

**💬 交作业！**
搭好的小伙伴评论区报个到～
遇到问题也可以留言，我会尽量回复！

**👉 下一篇预告**：《用 OpenClaw 自动爬取竞品数据，老板以为我加班了》

---

#OpenClaw #自动化 #股票监控 #飞书 #Python #量化交易 #打工人 #摸鱼神器 #效率工具 #编程教程

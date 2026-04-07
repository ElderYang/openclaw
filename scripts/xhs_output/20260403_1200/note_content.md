# OpenClaw 实战 04｜自动监控股票，飞书实时推送📈

## 封面标题
**每天盯盘 4 小时？我用 OpenClaw 自动监控 + 飞书推送，躺着也能抓住涨停板！**

---

## 正文内容

### 😫 痛点引入

你是不是也这样：
- 上班偷偷看盘，被老板抓到好几次？
- 盯了一天没动静，刚去上厕所就拉升了？
- 晚上复盘才发现错过了最佳买卖点？

我以前也是，直到用 OpenClaw 搭建了**自动监控系统**——现在每天飞书自动推送涨停股、龙虎榜、资金流向，再也不用死盯着 K 线图了！

---

### 💡 解决方案

用 OpenClaw + Akshare + 飞书机器人，搭建一个**全自动股票监控系统**：
- ✅ 定时抓取涨停板、龙虎榜、行业涨幅
- ✅ 自动分析资金流向和热点板块
- ✅ 飞书实时推送，手机秒收消息
- ✅ 完全免费，无需购买付费软件

---

### 🛠️ 具体步骤（3 步搞定）

#### 步骤 1：安装依赖 + 配置 API

```bash
# 安装 akshare（免费股票数据源）
pip3 install akshare pandas

# 测试数据获取
python3 -c "import akshare as ak; print(ak.stock_zt_pool_em())"
```

#### 步骤 2：创建监控脚本

在 `~/.openclaw/workspace/scripts/` 创建 `stock_monitor.py`：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""股票自动监控脚本 - 抓取涨停板 + 龙虎榜 + 行业涨幅"""

import akshare as ak
import pandas as pd
from datetime import datetime

def get_zt_stocks():
    """获取涨停股池"""
    try:
        df = ak.stock_zt_pool_em(date=datetime.now().strftime('%Y%m%d'))
        return df[['代码', '名称', '涨停价', '涨幅', '封板时间', '连板数']]
    except Exception as e:
        print(f"获取涨停股失败：{e}")
        return None

def get_longhu榜():
    """获取龙虎榜数据"""
    try:
        df = ak.stock_lhb_detail_em(date=datetime.now().strftime('%Y%m%d'))
        return df[['股票代码', '股票名称', '买入金额', '卖出金额', '净买入']]
    except Exception as e:
        print(f"获取龙虎榜失败：{e}")
        return None

def get_industry_rank():
    """获取行业涨幅排行"""
    try:
        df = ak.stock_board_industry_name_em()
        return df.sort_values('涨跌幅', ascending=False).head(10)[['板块名称', '涨跌幅', '总市值']]
    except Exception as e:
        print(f"获取行业排行失败：{e}")
        return None

if __name__ == '__main__':
    print("=== 股票监控数据 ===")
    print(f"时间：{datetime.now()}")
    
    zt = get_zt_stocks()
    if zt is not None:
        print(f"\n涨停股数量：{len(zt)}")
        print(zt.head(5))
    
    lh = get_longhu榜()
    if lh is not None:
        print(f"\n龙虎榜数据：{len(lh)}条")
    
    ind = get_industry_rank()
    if ind is not None:
        print(f"\n行业涨幅 TOP5：")
        print(ind.head(5))
```

#### 步骤 3：配置定时任务 + 飞书推送

在 `~/.openclaw/workspace/config/openclaw.json` 添加 cron 任务：

```json
{
  "cron": {
    "jobs": [
      {
        "id": "stock-morning-brief",
        "name": "股市早报",
        "schedule": {
          "kind": "cron",
          "expr": "30 8 * * 1-5",
          "tz": "Asia/Shanghai"
        },
        "payload": {
          "kind": "systemEvent",
          "text": "生成股市早报：涨停股 + 龙虎榜 + 行业分析，推送到飞书"
        }
      },
      {
        "id": "stock-afternoon-review",
        "name": "股市复盘",
        "schedule": {
          "kind": "cron",
          "expr": "00 17 * * 1-5",
          "tz": "Asia/Shanghai"
        },
        "payload": {
          "kind": "systemEvent",
          "text": "生成股市复盘：全天数据 + 资金流向 + 明日策略，推送到飞书"
        }
      }
    ]
  }
}
```

---

### ⚠️ 避坑指南

**坑 1：Akshare 数据获取失败**
- 原因：网络问题或 API 限流
- 解决：添加重试机制 + 代理配置
```python
import requests
session = requests.Session()
session.proxies = {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}
```

**坑 2：飞书推送不生效**
- 原因：tenant_access_token 过期
- 解决：每次推送前重新获取 token（有效期 2 小时）

**坑 3：定时任务不执行**
- 原因：OpenClaw Gateway 未运行
- 解决：`openclaw gateway status` 检查状态，`openclaw gateway restart` 重启

**坑 4：数据格式错误**
- 原因：Akshare API 返回格式变化
- 解决：打印 df.columns 检查字段名，及时调整代码

---

### 📊 效果展示

**监控前**：
- ❌ 每天盯盘 4+ 小时
- ❌ 错过 3 次涨停买入点
- ❌ 晚上复盘才发现热点

**监控后**：
- ✅ 每天 8:30 自动收早报
- ✅ 涨停股秒推飞书
- ✅ 龙虎榜 + 资金流向一目了然
- ✅ 上班摸鱼也能抓住机会😏

---

### 📥 资源下载

**完整代码 + 配置文件**：
- GitHub: `github.com/openclaw/stock-monitor`
- 脚本位置：`~/.openclaw/workspace/scripts/stock_monitor.py`
- 配置示例：`config/openclaw.json`

**评论区回复"股票监控"获取完整代码包！**

---

### 🏷️ 话题标签

#OpenClaw #股票监控 #自动化办公 #飞书机器人 #Akshare #量化交易 #Python 编程 #打工人摸鱼 #副业赚钱 #AI 自动化

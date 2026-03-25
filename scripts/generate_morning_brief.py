#!/usr/bin/env python3
"""生成每日股市早报 - 基于 v13.5 缓存数据"""

import json
from datetime import datetime

# Read the cached data
with open('/Users/yangbowen/.openclaw/workspace/cache/market_data_20260311_0831_v135.json', 'r') as f:
    data = json.load(f)

# Generate the morning brief report
report = f"""# 📈 每日股市早报 | 2026 年 3 月 12 日 星期四

> 数据截止时间：{data['timestamp']}
> 执行时间：{data['execution_time']:.1f}秒

---

## 1️⃣ 外盘回顾

| 指数 | 收盘点位 | 涨跌幅 |
|------|----------|--------|
| 道琼斯 | {data['us_indices_api']['道琼斯']['current']:,.2f} | {data['us_indices_api']['道琼斯']['change']:+.2f}% |
| 纳斯达克 | {data['us_indices_api']['纳斯达克']['current']:,.2f} | {data['us_indices_api']['纳斯达克']['change']:+.2f}% |
| 标普 500 | {data['us_indices_api']['标普 500']['current']:,.2f} | {data['us_indices_api']['标普 500']['change']:+.2f}% |
| **纳斯达克中国金龙指数** | {data['china_indices']['金龙指数']['current']:,.2f} | {data['china_indices']['金龙指数']['change']:+.2f}% |
| **富时 A50** | {data['china_indices']['A50']['current']} | {data['china_indices']['A50']['change']:+.2f}% |

**点评**：美股三大指数涨跌互现，纳斯达克微涨 0.01%，道琼斯和标普 500 小幅下跌。**中国金龙指数大涨 1.96%**，显示中概股情绪回暖。

---

## 2️⃣ AI 相关企业股价

| 公司 | 股价 (USD) | 涨跌幅 |
|------|------------|--------|
| 英伟达 (NVDA) | ${data['ai_stocks']['英伟达']['current']:.2f} | {data['ai_stocks']['英伟达']['change']:+.2f}% |
| 微软 (MSFT) | ${data['ai_stocks']['微软']['current']:.2f} | {data['ai_stocks']['微软']['change']:+.2f}% |
| 谷歌 (GOOGL) | ${data['ai_stocks']['谷歌']['current']:.2f} | {data['ai_stocks']['谷歌']['change']:+.2f}% |
| Meta | ${data['ai_stocks']['Meta']['current']:.2f} | {data['ai_stocks']['Meta']['change']:+.2f}% |
| 特斯拉 (TSLA) | ${data['ai_stocks']['特斯拉']['current']:.2f} | {data['ai_stocks']['特斯拉']['change']:+.2f}% |
| 亚马逊 (AMZN) | 数据暂缺 | - |

**点评**：AI 芯片龙头英伟达上涨 1.16%，继续领跑科技股。微软小幅回调 0.89%，谷歌微涨 0.30%。

---

## 3️⃣ A 股市场动态

### 主要指数

| 指数 | 收盘点位 | 涨跌幅 |
|------|----------|--------|
| 上证指数 | {data['a_share_indices_api']['上证指数']['current']:,.2f} | {data['a_share_indices_api']['上证指数']['change']:+.2f}% |
| 深证成指 | {data['a_share_indices_api']['深证成指']['current']:,.2f} | {data['a_share_indices_api']['深证成指']['change']:+.2f}% |
| 创业板指 | {data['a_share_indices_api']['创业板指']['current']:,.2f} | {data['a_share_indices_api']['创业板指']['change']:+.2f}% |
| 科创 50 | {data['a_share_indices_api']['科创 50']['current']:,.2f} | {data['a_share_indices_api']['科创 50']['change']:+.2f}% |

### 融资融券

- **融资余额**：{data['margin']['balance']:.2f}亿元
- **变化**：{data['margin']['change']:+.2f}亿元（较前一交易日）
- **前一交易日**：{data['margin']['prev_balance']:.2f}亿元

**点评**：融资余额小幅下降 5.19 亿元，市场杠杆资金略有流出。

---

## 4️⃣ 持仓个股分析

| 股票/ETF | 代码 | 收盘价 | 涨跌幅 |
|----------|------|--------|--------|
| 三花智控 | 002050 | ¥{data['holdings'][0]['price']} | {data['holdings'][0]['change']} |
| 兆易创新 | 603986 | ¥{data['holdings'][1]['price']} | {data['holdings'][1]['change']} |
| 蓝色光标 | 300058 | ¥{data['holdings'][2]['price']} | {data['holdings'][2]['change']} |
| 长电科技 | 600584 | ¥{data['holdings'][3]['price']} | {data['holdings'][3]['change']} |
| 科创 50ETF | 588000 | ¥{data['holdings'][4]['price']} | {data['holdings'][4]['change']} |
| 半导体设备 ETF | 159511 | ¥{data['holdings'][5]['price']} | {data['holdings'][5]['change']} |
| 电网设备 ETF | 561700 | ¥{data['holdings'][6]['price']} | {data['holdings'][6]['change']} |

**点评**：
- 🔴 **三花智控** (-1.51%)：机器人/热管理概念，短期回调
- 🔴 **兆易创新** (-3.12%)：存储芯片龙头，跟随半导体板块调整
- 🟢 **蓝色光标** (+1.57%)：AI 营销概念，表现强势
- 🔴 **长电科技** (-4.34%)：芯片封测龙头，跌幅较大
- 🔴 **科创 50ETF** (-1.74%)：科技成长板块整体承压

---

## 5️⃣ 行业板块 Top5

| 排名 | 板块名称 | 涨跌幅 | 换手率 |
|------|----------|--------|--------|
| 1 | 印制电路板 | +{data['industry']['top5'][0]['涨跌幅']:.2f}% | {data['industry']['top5'][0]['换手率']:.2f}% |
| 2 | 通信线缆及配套 | +{data['industry']['top5'][1]['涨跌幅']:.2f}% | {data['industry']['top5'][1]['换手率']:.2f}% |
| 3 | 通信网络设备及器件 | +{data['industry']['top5'][2]['涨跌幅']:.2f}% | {data['industry']['top5'][2]['换手率']:.2f}% |
| 4 | 分立器件 | +{data['industry']['top5'][3]['涨跌幅']:.2f}% | {data['industry']['top5'][3]['换手率']:.2f}% |
| 5 | 元件 | +{data['industry']['top5'][4]['涨跌幅']:.2f}% | {data['industry']['top5'][4]['换手率']:.2f}% |

**点评**：**通信/电子板块集体走强**，印制电路板、通信设备等涨幅居前，显示资金对科技硬件赛道的关注。

---

## 6️⃣ AI 行业最新动态

> ⚠️ 今日 AI 新闻数据获取中...

**近期关注方向**：
- 英伟达 GTC 大会预期（3 月下旬）
- 国内大模型应用落地进展
- AI 算力产业链持续高景气

---

## 7️⃣ 🔥 市场主线分析

### 当前市场特征

1. **科技主线明确**：通信、电子、半导体设备涨幅居前
2. **外盘分化**：美股震荡，中概股反弹（金龙指数 +1.96%）
3. **融资盘谨慎**：融资余额小幅流出 5 亿元
4. **持仓分化**：蓝色光标逆势上涨，半导体个股普遍回调

### 资金流向

- **龙虎榜**：{data['lhb']['count']}条（活跃度正常）
- **融资余额**：8016 亿元（小幅下降）
- **北向资金**：数据待更新

---

## 8️⃣ 今日操作建议

### 📌 持仓策略

| 股票 | 建议 | 理由 |
|------|------|------|
| 三花智控 | **持有观望** | 机器人赛道长期逻辑不变，等待企稳 |
| 兆易创新 | **持有观望** | 存储周期底部，耐心等待反弹 |
| 蓝色光标 | **持有** | AI 应用端强势，继续持有 |
| 长电科技 | **观望** | 封测板块调整，关注支撑位 |
| 科创 50ETF | **定投/持有** | 科技成长长期配置价值 |

### 🎯 关注方向

1. **AI 算力硬件**：印制电路板、通信设备涨幅居前，趋势延续
2. **半导体设备**：国产替代逻辑，调整后关注低吸机会
3. **中概股反弹**：金龙指数大涨，关注港股/A 股联动

### ⚠️ 风险提示

- 美股震荡可能传导至 A 股
- 融资余额下降显示杠杆资金谨慎
- 半导体板块短期调整压力

---

> 📊 **数据来源**：v13.5 股市数据脚本（东方财富 API + AkShare + Playwright）
> 🕐 **生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

# Save the report
with open('/Users/yangbowen/.openclaw/workspace/cache/morning_brief_20260312.md', 'w', encoding='utf-8') as f:
    f.write(report)

print('✅ 早报已生成：cache/morning_brief_20260312.md')
print(f'📄 报告长度：{len(report)} 字符')

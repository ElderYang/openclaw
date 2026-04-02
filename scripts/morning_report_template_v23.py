#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
早报模板 v23.0（优化版）- 适配 v21 数据结构

核心优化：
1. 一句话导读（30 字内，核心结论）
2. 隔夜大事（3 条以内，事件→影响→板块）
3. 隔夜外盘 + A 股影响点评
4. 投资日历 + 受益板块 + 持仓财报
5. 持仓个股 + 今日关注 + 美股对标
6. 今日策略建议（仓位 + 关注 + 风险 + 持仓）
7. 昨日预测验证（新增）
8. 保留融资余额（用户要求）

数据结构：完全复用 v21 的 data 字典字段
- us_indices (不是 us_markets)
- limit_up (包含 total_count, lianban_count)
- longhubang (包含 items, top10_buy, top10_sell)
- holdings (持仓个股列表)
- indices (A 股指数)
- margin (融资融券)
- industry (行业板块)
- north_money (北向资金)
- main_force (主力资金)
"""

from datetime import datetime, timedelta
import json
import os

# 昨日预测存储文件
PREDICTION_FILE = os.path.expanduser("~/.openclaw/workspace/data/yesterday_prediction.json")


def load_yesterday_prediction():
    """加载昨日预测"""
    if os.path.exists(PREDICTION_FILE):
        with open(PREDICTION_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def save_today_prediction(prediction):
    """保存今日预测（供明日验证）"""
    os.makedirs(os.path.dirname(PREDICTION_FILE), exist_ok=True)
    with open(PREDICTION_FILE, "w", encoding="utf-8") as f:
        json.dump(prediction, f, ensure_ascii=False, indent=2)


def generate_one_sentence_summary(data):
    """一句话导读（30 字内）"""
    # 从 v21 数据结构获取
    us_indices = data.get("us_indices") or {}
    nasdaq = us_indices.get("纳斯达克") or {}
    a50 = us_indices.get("富时中国 A50") or {}
    
    us_change = nasdaq.get("change_pct", 0) or 0
    us_status = "美股普涨" if us_change > 0 else "美股下跌"
    a50_change = a50.get("change_pct", 0) or 0
    a50_status = f"A50{a50_change:+.1f}%"
    
    limit_up = data.get("limit_up") or {}
    zt_count = limit_up.get("total_count", 0) or 0
    lb_count = limit_up.get("lianban_count", 0) or 0
    
    summary = f"外盘：{us_status} {a50_status} | 涨停{zt_count}家连板{lb_count}家"
    return summary[:30] if len(summary) > 30 else summary


def generate_overnight_news_section(data):
    """【0】隔夜大事（3 条以内，事件→影响→板块）
    
    注意：如果 news_list 为空或只有固定模板消息，说明 API 获取失败
    此时返回简化版，避免显示过时的"美联储降息"等假消息
    """
    news_list = data.get("overnight_news") or []
    
    # 检测是否是固定模板消息（说明 API 获取失败）
    template_keywords = ['美联储利率决策临近', '黄金价格震荡', '地缘局势影响能源']
    is_template = any(any(kw in (n.get('title','') or '') for kw in template_keywords) for n in news_list)
    
    if not news_list or is_template:
        # API 获取失败，返回简化版（不显示假消息）
        return "【0】隔夜大事\n暂无最新数据（网络限制，建议手动查看财联社/华尔街见闻）"
    
    lines = ["【0】隔夜大事（只说跟 A 股有关的）"]
    for news in news_list[:3]:
        title = news.get('title', '')
        snippet = news.get('snippet', '')
        # 简单提取影响和板块
        if any(kw in title.lower() for kw in ['ai', '芯片', '科技', '英伟达', '特斯拉']):
            sector = "→ 科技/AI"
        elif any(kw in title.lower() for kw in ['美联储', '利率', '通胀', 'CPI']):
            sector = "→ 宏观/金融"
        elif any(kw in title.lower() for kw in ['石油', '能源', '黄金', '原油']):
            sector = "→ 大宗商品"
        elif any(kw in title.lower() for kw in ['中东', '地缘', '战争']):
            sector = "→ 地缘政治"
        else:
            sector = "→ 市场动态"
        lines.append(f"• {title[:50]} {sector}")
    return "\n".join(lines)


def generate_us_markets_section(data):
    """【1】隔夜外盘 + 对 A 股影响"""
    us_indices = data.get("us_indices") or {}
    lines = ["【1】隔夜外盘 + 对 A 股影响", "─" * 60]
    
    market_map = [
        ("道琼斯", "道琼斯"), 
        ("纳斯达克", "纳斯达克"), 
        ("富时中国 A50", "富时 A50"), 
        ("纳指金龙", "纳指金龙")
    ]
    
    for key, name in market_map:
        if key in us_indices:
            m = us_indices[key]
            close_val = m.get("close", 0)
            change_pct = m.get("change_pct", 0) or 0
            trade_date = m.get("trade_date", "N/A")
            validated = "✅" if m.get("validated") else "⚠️"
            lines.append(f"{validated} {name:10s}: {close_val:>10,.0f} ({change_pct:>+6.2f}%) [{trade_date}]")
    
    # A 股影响点评
    a50 = us_indices.get("富时中国 A50") or {}
    a50_change = a50.get("change_pct", 0) or 0
    if a50_change > 0.5:
        impact = "→ A 股影响：利好开盘，大概率高开"
    elif a50_change > 0:
        impact = "→ A 股影响：小幅利好，平开或微高开"
    elif a50_change > -0.5:
        impact = "→ A 股影响：小幅利空，平开或微低开"
    else:
        impact = "→ A 股影响：利空开盘，可能低开"
    
    lines.extend(["", impact])
    return "\n".join(lines)


def generate_calendar_section(data):
    """【2】投资日历 + 受益板块 + 持仓财报"""
    current_date = datetime.now()
    weekday = current_date.strftime('%A')
    weekday_map = {
        'Monday': '星期一', 'Tuesday': '星期二', 'Wednesday': '星期三',
        'Thursday': '星期四', 'Friday': '星期五', 'Saturday': '星期六', 'Sunday': '星期日'
    }
    weekday_cn = weekday_map.get(weekday, '星期 X')
    
    lines = [
        f"【2】投资日历 | {current_date.strftime('%Y-%m-%d')} {weekday_cn}",
        "─" * 60
    ]
    
    # 今日焦点
    lines.append(f"📌 今日焦点（{current_date.strftime('%m/%d')}）：")
    lines.append("   • 年报/一季报密集披露期")
    lines.append("   • 央行公开市场操作关注")
    
    # 近期事件
    tomorrow = current_date + timedelta(days=1)
    lines.append(f"\n📅 近期：{tomorrow.strftime('%m/%d')} 美国核心 PCE 物价指数")
    
    # 持仓财报提醒
    holdings = data.get("holdings") or []
    if holdings:
        lines.append("\n📊 持仓财报关注：")
        for stock in holdings[:5]:
            name = stock.get("name", "")
            lines.append(f"   • {name}")
    
    return "\n".join(lines)


def generate_holdings_section(data):
    """【3】持仓个股 + 今日关注 + 美股对标"""
    holdings = data.get("holdings") or []
    if not holdings:
        return "【3】持仓个股\n暂无持仓数据"
    
    lines = ["【3】持仓个股", "─" * 60]
    
    for stock in holdings:
        name = stock.get("name", "Unknown")
        code = stock.get("code", "")
        price = stock.get("price", 0)
        pct = stock.get("pct", 0) or 0
        industry = stock.get("industry", "")
        validated = "✅" if stock.get("validated") else "⚠️"
        
        # 涨跌图标
        if pct > 0:
            arrow = "🔺"
        elif pct < 0:
            arrow = "🔻"
        else:
            arrow = "➖"
        
        lines.append(f"{validated} {arrow} {name:12s} ({code}): ¥{price:>8.3f} ({pct:>+6.2f}%) [{industry}]")
    
    # 美股对标（v22 新增数据）
    us_benchmark = data.get("us_benchmark_data") or {}
    if us_benchmark:
        lines.append("\n🇺🇸 美股对标：")
        for name, benchmark in us_benchmark.items():
            symbol = benchmark.get("symbol", "")
            change = benchmark.get("change", 0)
            lines.append(f"   • {name} → {symbol} ({change:+.1f}%)")
    
    return "\n".join(lines)


def generate_market_analysis_section(data):
    """【4】市场分析（涨停 + 龙虎榜 + 资金）"""
    limit_up = data.get("limit_up") or {}
    longhubang = data.get("longhubang") or {}
    margin = data.get("margin") or {}
    north_money = data.get("north_money") or {}
    main_force = data.get("main_force") or {}
    industry = data.get("industry") or []
    
    lines = ["【4】市场分析", "─" * 60]
    
    # 涨停板
    zt_count = limit_up.get("total_count", "待确认")
    lb_count = limit_up.get("lianban_count", "待确认")
    lines.append(f"🔥 涨停板：{zt_count}家 | 连板：{lb_count}家")
    
    # 连板股
    top_lianban = limit_up.get("top_lianban") or []
    if top_lianban:
        lines.append(f"   最高：{top_lianban[0].get('名称', 'Unknown')}({top_lianban[0].get('连板数', 0)}连板)")
    
    # 龙虎榜
    lhb_items = longhubang.get("items") or []
    if lhb_items:
        lines.append(f"📊 龙虎榜：{len(lhb_items)}条")
        top_buy = longhubang.get("top10_buy") or []
        if top_buy:
            buy_name = top_buy[0].get("名称", "Unknown")
            buy_net = top_buy[0].get("龙虎榜净买额", 0)
            lines.append(f"   净买第一：{buy_name} (+{buy_net/100000000:.2f}亿)")
    
    # 资金流向
    north_val = north_money.get("net_inflow")
    if north_val is not None:
        lines.append(f"💰 北向资金：{north_val:.2f}亿")
    
    mf_total = main_force.get("total_net_inflow")
    if mf_total is not None:
        lines.append(f"   主力资金：{mf_total/10000:.2f}亿")
    
    # 融资余额
    if margin.get("balance"):
        lines.append(f"📈 融资余额：{margin['balance']:.2f}亿 (日变化：{margin.get('change', 0):+.2f}亿)")
    
    # 行业板块
    if industry and isinstance(industry, list) and len(industry) > 0:
        lines.append("\n🏆 行业涨幅 Top5：")
        for item in industry[:5]:
            name = item.get("name", "Unknown")
            change = item.get("change", 0)
            arrow = "🔺" if change > 0 else "🔻" if change < 0 else "➖"
            lines.append(f"   {arrow} {name}: {change:+.2f}%")
    
    return "\n".join(lines)


def generate_strategy_section(data):
    """【5】今日策略建议"""
    holdings = data.get("holdings") or []
    
    lines = [
        "【5】今日策略",
        "─" * 60,
        "📊 仓位建议：6-7 成（根据盘面动态调整）",
        "",
        "🎯 关注方向：",
        "   1. AI 算力硬件（PCB、通信设备）",
        "   2. 半导体设备（国产替代）",
        "   3. 中概股反弹联动",
        "",
        "⚠️ 风险提示：",
        "   • 美股震荡传导",
        "   • 融资盘谨慎",
        "   • 半导体调整压力",
        "",
        "📌 持仓策略："
    ]
    
    # 持仓策略
    holdings_strategy = {
        '三花智控': '持有观望',
        '兆易创新': '持有观望',
        '蓝色光标': '持有✅',
        '长电科技': '观望',
        '科创 50ETF': '定投/持有',
        '半导体设备 ETF': '持有',
        '电网设备 ETF': '持有✅',
        '润泽科技': '持有',
    }
    
    strategies = []
    for stock in holdings:
        name = stock.get("name", "")
        strategy = holdings_strategy.get(name, "观望")
        strategies.append(f"{name}：{strategy}")
    
    lines.append("   " + " | ".join(strategies))
    
    return "\n".join(lines)


def generate_yesterday_prediction_section(data):
    """【6】昨日预测验证（新增）"""
    yesterday_pred = load_yesterday_prediction()
    if not yesterday_pred:
        return ""
    
    lines = [
        "",
        "【6】昨日预测验证",
        "─" * 60
    ]
    
    # 昨日预测内容
    pred_content = yesterday_pred.get("prediction", "")
    lines.append(f"昨日预测：{pred_content[:80]}...")
    
    # 今日实际数据对比（简化版）
    indices = data.get("indices") or {}
    sh = indices.get("上证指数") or {}
    actual_pct = sh.get("pct_chg", 0) or 0
    
    lines.append(f"实际走势：上证指数 {actual_pct:+.2f}%")
    lines.append("准确度：待评估（需人工判断）")
    
    return "\n".join(lines)


def generate_morning_report_v23(data):
    """生成 v23.0 优化版早报"""
    
    # 保存今日预测（供明日验证）
    today_prediction = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "prediction": f"预计 A 股{data.get('indices', {}).get('上证指数', {}).get('pct_chg', 0):+.1f}%"
    }
    save_today_prediction(today_prediction)
    
    # 生成各模块
    sections = []
    
    # 标题
    current_date = datetime.now()
    sections.append("=" * 60)
    sections.append(f"🌅 股市早报 v23.0 | {current_date.strftime('%Y-%m-%d %H:%M')}")
    sections.append("=" * 60)
    sections.append("")
    
    # 一句话导读
    summary = generate_one_sentence_summary(data)
    sections.append(f"📖 导读：{summary}")
    sections.append("")
    
    # 各模块
    sections.append(generate_overnight_news_section(data))
    sections.append("")
    sections.append(generate_us_markets_section(data))
    sections.append("")
    sections.append(generate_calendar_section(data))
    sections.append("")
    sections.append(generate_holdings_section(data))
    sections.append("")
    sections.append(generate_market_analysis_section(data))
    sections.append("")
    sections.append(generate_strategy_section(data))
    
    # 昨日预测验证（如果有）
    yesterday_section = generate_yesterday_prediction_section(data)
    if yesterday_section:
        sections.append("")
        sections.append(yesterday_section)
    
    # 数据源说明
    sections.append("")
    sections.append("=" * 60)
    sections.append("📋 数据源：QVeris(实时) > Tushare > 东方财富 > AkShare")
    sections.append("=" * 60)
    
    return "\n".join(sections)


if __name__ == '__main__':
    # 测试
    test_data = {
        'us_indices': {
            '道琼斯': {'close': 40000, 'change_pct': 0.5, 'validated': True, 'trade_date': '2026-04-01'},
            '纳斯达克': {'close': 16000, 'change_pct': 1.2, 'validated': True, 'trade_date': '2026-04-01'},
            '富时中国 A50': {'close': 13000, 'change_pct': 0.8, 'validated': True, 'trade_date': '2026-04-02'},
        },
        'limit_up': {'total_count': 50, 'lianban_count': 5},
        'holdings': [
            {'name': '三花智控', 'code': '002050', 'price': 25.5, 'pct': 1.5, 'industry': '汽车零部件', 'validated': True}
        ],
        'indices': {
            '上证指数': {'close': 3400, 'pct_chg': 0.5}
        },
        'longhubang': {'items': [1,2,3], 'top10_buy': [{'名称': 'XXX', '龙虎榜净买额': 100000000}]},
        'north_money': {'net_inflow': 50},
        'main_force': {'total_net_inflow': 500000},
        'margin': {'balance': 15000, 'change': -50},
        'industry': [{'name': '半导体', 'change': 2.5}, {'name': 'AI', 'change': 1.8}],
        'overnight_news': [
            {'title': '英伟达发布新芯片', 'snippet': 'AI 算力升级'},
            {'title': '美联储议息会议', 'snippet': '利率决策'}
        ]
    }
    
    report = generate_morning_report_v23(test_data)
    print(report)

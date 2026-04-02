#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 股复盘报告 v23.0（优化版）- 复用 v21 数据结构

核心优化：
1. 一句话总结（30 字内）
2. 涨跌分布可视化
3. 涨停板 + 龙虎榜深度分析
4. 机构/游资动向
5. 持仓个股表现
6. 明日策略

数据结构：完全复用 v21 的 data 字典字段
"""

from datetime import datetime


def generate_one_sentence_summary(data):
    """一句话总结"""
    indices = data.get("indices") or {}
    sh = indices.get("上证指数") or {}
    pct = sh.get("pct_chg", 0) or 0
    
    limit_up = data.get("limit_up") or {}
    zt_count = limit_up.get("total_count", 0) or 0
    
    longhubang = data.get("longhubang") or {}
    lhb_count = len(longhubang.get("items") or [])
    
    if pct > 1:
        trend = "大涨"
    elif pct > 0:
        trend = "上涨"
    elif pct > -1:
        trend = "震荡"
    else:
        trend = "下跌"
    
    return f"A 股{trend}{pct:+.1f}% | 涨停{zt_count}家 | 龙虎榜{lhb_count}条"


def generate_market_overview(data):
    """【1】市场概览"""
    indices = data.get("indices") or {}
    margin = data.get("margin") or {}
    
    lines = ["【1】市场概览", "─" * 60]
    
    # 指数
    lines.append("📊 主要指数收盘：")
    for name, d in indices.items():
        pct = d.get("pct_chg", 0) or 0
        close_val = d.get("close", 0)
        trend = "🔺" if pct > 0 else "🔻" if pct < 0 else "➖"
        lines.append(f"  {trend} {name:12s}: {close_val:>10,.2f} ({pct:>+6.2f}%)")
    
    # 融资融券
    lines.append("\n💰 融资融券：")
    if margin.get("balance"):
        lines.append(f"  融资余额：{margin['balance']:.2f}亿元")
        lines.append(f"  日变化：{margin.get('change', 0):+.2f}亿元")
    else:
        lines.append("  数据待确认")
    
    return "\n".join(lines)


def generate_limit_up_analysis(data):
    """【2】涨停板分析"""
    limit_up = data.get("limit_up") or {}
    
    lines = ["【2】涨停板分析", "─" * 60]
    
    zt_count = limit_up.get("total_count", 0) or 0
    lb_count = limit_up.get("lianban_count", 0) or 0
    lines.append(f"🔥 涨停家数：{zt_count}家")
    lines.append(f"   连板家数：{lb_count}家")
    
    # 最高连板
    top_lianban = limit_up.get("top_lianban") or []
    if top_lianban:
        highest = top_lianban[0]
        lines.append(f"   最高连板：{highest.get('名称', 'Unknown')} ({highest.get('连板数', 0)}连板)")
        
        # 连板 Top5
        lines.append("\n   连板 Top5：")
        for i, stock in enumerate(top_lianban[:5], 1):
            name = stock.get("名称", "")
            lianban = stock.get("连板数", 0)
            fengban = stock.get("封板资金", 0) / 10000  # 万
            lines.append(f"     {i}. {name:15s} ({lianban}连板) 封板{fengban:.0f}万")
    
    # 涨停股板块分布（v22 新增数据）
    zt_sector = data.get("zt_sector_dist") or {}
    if zt_sector:
        lines.append("\n   涨停股板块分布：")
        sorted_sectors = sorted(zt_sector.items(), key=lambda x: x[1], reverse=True)[:5]
        for sector, count in sorted_sectors:
            lines.append(f"     • {sector}: {count}家")
    
    return "\n".join(lines)


def generate_longhubang_analysis(data):
    """【3】龙虎榜分析"""
    longhubang = data.get("longhubang") or {}
    
    lines = ["【3】龙虎榜分析", "─" * 60]
    
    lhb_items = longhubang.get("items") or []
    lines.append(f"📊 上榜总数：{len(lhb_items)}条")
    
    # 净买入 Top5
    top_buy = longhubang.get("top10_buy") or []
    if top_buy:
        lines.append("\n   净买入 Top5：")
        for i, stock in enumerate(top_buy[:5], 1):
            name = stock.get("名称", "")
            net = stock.get("龙虎榜净买额", 0) / 100000000  # 亿
            buy = stock.get("龙虎榜买入额", 0) / 100000000
            sell = stock.get("龙虎榜卖出额", 0) / 100000000
            lines.append(f"     {i}. {name:15s} {net:+.2f}亿 (买{buy:.2f}亿/卖{sell:.2f}亿)")
    
    # 机构席位
    institutions = longhubang.get("institutions") or []
    lines.append(f"\n   机构席位：{len(institutions)}家")
    if institutions:
        lines.append("   机构买入：")
        for inst in institutions[:3]:
            name = inst.get("名称", "")
            net = inst.get("龙虎榜净买额", 0) / 100000000
            lines.append(f"     • {name:15s} {net:+.2f}亿")
    else:
        lines.append("     ⚠️ 今日无机构席位上榜")
    
    # 游资活跃股
    active = longhubang.get("active_stocks") or []
    if active:
        lines.append("\n   游资活跃股：")
        for i, stock in enumerate(active[:3], 1):
            name = stock.get("名称", "")
            chengjiao = stock.get("龙虎榜成交额", 0) / 100000000
            reason = stock.get("上榜原因", "N/A")[:20]
            lines.append(f"     {i}. {name:15s} 成交{chengjiao:.2f}亿 ({reason})")
    
    # 知名游资（v22 新增数据）
    famous_youzi = data.get("famous_youzi") or []
    if famous_youzi:
        lines.append("\n   知名游资动向：")
        for yz in famous_youzi[:3]:
            name = yz.get("name", "")
            action = yz.get("action", "")
            stock = yz.get("stock", "")
            lines.append(f"     • {name}: {action} {stock}")
    
    return "\n".join(lines)


def generate_market_theme(data):
    """【4】市场主线"""
    theme = data.get("theme_analysis") or {}
    industry = data.get("industry") or []
    
    lines = ["【4】市场主线", "─" * 60]
    
    # 领涨板块
    if industry and isinstance(industry, list):
        lines.append("🏆 领涨板块 Top5：")
        sorted_industry = sorted(industry, key=lambda x: x.get("change", 0), reverse=True)[:5]
        for i, sector in enumerate(sorted_industry, 1):
            name = sector.get("name", "Unknown")
            change = sector.get("change", 0)
            trend = "🔺" if change > 0 else "🔻" if change < 0 else "➖"
            lines.append(f"  {i}. {trend} {name:20s} {change:+.2f}%")
    
    # 龙头/中军
    leaders = theme.get("leaders") or []
    mid_caps = theme.get("mid_caps") or []
    
    if leaders:
        lines.append("\n   龙头企业：")
        for leader in leaders[:3]:
            name = leader.get("name", "")
            sector = leader.get("sector", "")
            lines.append(f"     • {name} ({sector})")
    
    if mid_caps:
        lines.append("\n   中军企业：")
        for mid in mid_caps[:3]:
            name = mid.get("name", "")
            sector = mid.get("sector", "")
            lines.append(f"     • {name} ({sector})")
    
    return "\n".join(lines)


def generate_holdings_performance(data):
    """【5】持仓个股表现"""
    holdings = data.get("holdings") or []
    
    if not holdings:
        return "【5】持仓个股表现\n暂无持仓数据"
    
    lines = ["【5】持仓个股表现", "─" * 60]
    
    for stock in holdings:
        name = stock.get("name", "")
        code = stock.get("code", "")
        price = stock.get("price", 0)
        pct = stock.get("pct", 0) or 0
        industry = stock.get("industry", "")
        validated = "✅" if stock.get("validated") else "⚠️"
        
        trend = "🔺" if pct > 0 else "🔻" if pct < 0 else "➖"
        lines.append(f"{validated} {trend} {name:12s} ({code}): ¥{price:>8.3f} ({pct:>+6.2f}%) [{industry}]")
    
    # 美股对标（v22 新增数据）
    us_benchmark = data.get("us_benchmark_data") or {}
    if us_benchmark:
        lines.append("\n🇺🇸 美股对标：")
        for name, benchmark in us_benchmark.items():
            symbol = benchmark.get("symbol", "")
            change = benchmark.get("change", 0)
            lines.append(f"   • {name} → {symbol} ({change:+.1f}%)")
    
    return "\n".join(lines)


def generate_tomorrow_strategy(data):
    """【6】明日策略"""
    lines = [
        "【6】明日策略",
        "─" * 60,
        "",
        "📊 仓位建议：",
        "   • 激进型：7-8 成",
        "   • 稳健型：5-6 成",
        "   • 保守型：3-4 成",
        "",
        "🎯 关注方向：",
        "   1. AI 算力硬件（PCB、通信设备）",
        "   2. 半导体设备（国产替代）",
        "   3. 低空经济（政策催化）",
        "",
        "⚠️ 风险提示：",
        "   • 美股震荡传导",
        "   • 融资盘谨慎",
        "   • 高位股分化",
    ]
    
    # 持仓策略
    holdings = data.get("holdings") or []
    if holdings:
        lines.append("\n📌 持仓策略：")
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


def generate_afternoon_review_v23(data):
    """生成 v23.0 优化版复盘报告"""
    
    sections = []
    
    # 标题
    current_date = datetime.now()
    weekday_map = {
        'Monday': '一', 'Tuesday': '二', 'Wednesday': '三',
        'Thursday': '四', 'Friday': '五', 'Saturday': '六', 'Sunday': '日'
    }
    weekday = weekday_map.get(current_date.strftime('%A'), 'X')
    
    sections.append("=" * 60)
    sections.append(f"📊 A 股复盘 v23.0 | {current_date.strftime('%Y-%m-%d')} 星期{weekday}")
    sections.append(f"数据截止：{current_date.strftime('%H:%M')} (收盘后)")
    sections.append("=" * 60)
    sections.append("")
    
    # 一句话总结
    summary = generate_one_sentence_summary(data)
    sections.append(f"📖 总结：{summary}")
    sections.append("")
    
    # 各模块
    sections.append(generate_market_overview(data))
    sections.append("")
    sections.append(generate_limit_up_analysis(data))
    sections.append("")
    sections.append(generate_longhubang_analysis(data))
    sections.append("")
    sections.append(generate_market_theme(data))
    sections.append("")
    sections.append(generate_holdings_performance(data))
    sections.append("")
    sections.append(generate_tomorrow_strategy(data))
    
    # 数据源说明
    sections.append("")
    sections.append("=" * 60)
    sections.append("📋 数据源：QVeris(实时) > Tushare > 东方财富 > AkShare")
    sections.append("=" * 60)
    
    return "\n".join(sections)


if __name__ == '__main__':
    # 测试
    test_data = {
        'indices': {
            '上证指数': {'close': 3400, 'pct_chg': 1.5},
            '深证成指': {'close': 11000, 'pct_chg': 1.2},
        },
        'limit_up': {
            'total_count': 50,
            'lianban_count': 5,
            'top_lianban': [
                {'名称': 'XXX', '连板数': 5, '封板资金': 100000000}
            ]
        },
        'longhubang': {
            'items': [1,2,3],
            'top10_buy': [{'名称': 'YYY', '龙虎榜净买额': 100000000, '龙虎榜买入额': 150000000, '龙虎榜卖出额': 50000000}],
            'institutions': [{'名称': '机构专用', '龙虎榜净买额': 50000000}],
            'active_stocks': [{'名称': 'ZZZ', '龙虎榜成交额': 200000000, '上榜原因': '日涨幅偏离值达 7%'}]
        },
        'industry': [
            {'name': '半导体', 'change': 2.5},
            {'name': 'AI', 'change': 1.8}
        ],
        'holdings': [
            {'name': '三花智控', 'code': '002050', 'price': 25.5, 'pct': 1.5, 'industry': '汽车零部件', 'validated': True}
        ],
        'margin': {'balance': 15000, 'change': -50},
    }
    
    report = generate_afternoon_review_v23(test_data)
    print(report)

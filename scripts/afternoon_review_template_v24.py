#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 股复盘报告 v24.0（深度优化版）

核心优化（按照 2026-04-01 讨论方案）：
1. 市场情绪周期（冰点/复苏/高潮/退潮 + 操作建议）
2. 涨停板深度分析（统计对比 + 板块分布可视化）
3. 龙虎榜深度解读（机构 + 游资 + 情绪指标）
4. 持仓个股深度分析（成本 + 浮盈 + 目标价 + 止损）
5. 明日策略个性化（基于持仓）

数据结构：复用 v21 的 data 字典字段 + 持仓配置文件
"""

from datetime import datetime
import json
import os

# 配置文件路径（使用绝对路径，避免工作目录问题）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.join(SCRIPT_DIR, '..')
HOLDINGS_CONFIG_FILE = os.path.join(WORKSPACE_DIR, 'data', 'holdings_config.json')

# 备用路径（兼容直接调用）
HOLDINGS_CONFIG_FILE_ALT = os.path.expanduser("~/.openclaw/workspace/data/holdings_config.json")


def load_holdings_config():
    """加载持仓配置"""
    # 尝试主路径
    if os.path.exists(HOLDINGS_CONFIG_FILE):
        with open(HOLDINGS_CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # 尝试备用路径
    if os.path.exists(HOLDINGS_CONFIG_FILE_ALT):
        with open(HOLDINGS_CONFIG_FILE_ALT, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def generate_one_sentence_summary(data):
    """一句话总结"""
    if not data or not isinstance(data, dict):
        return "数据暂缺，请稍后查看"
    
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


def generate_emotion_cycle_section(data):
    """【1】市场情绪周期（新增深度模块）
    
    判断标准：
    - 冰点：涨停<30 家，连板<3 板，炸板率>40%
    - 复苏：涨停 30-60 家，连板 3-5 板，炸板率 25-40%
    - 高潮：涨停 60-100 家，连板 5-8 板，炸板率 15-25%
    - 退潮：涨停>100 家，连板>8 板，炸板率<15%
    """
    limit_up = data.get("limit_up") or {}
    
    zt_count = limit_up.get("total_count", 0) or 0
    lb_count = limit_up.get("lianban_count", 0) or 0
    zhaban_rate = data.get("zhaban_rate", 25.0) or 25.0
    
    # 判断情绪周期
    if zt_count < 30 or lb_count < 3 or zhaban_rate > 40:
        stage = "冰点期"
        stage_icon = "🥶"
        suggestion = "空仓/轻仓观望"
    elif 30 <= zt_count <= 60 or 3 <= lb_count <= 5 or 25 <= zhaban_rate <= 40:
        stage = "复苏期"
        stage_icon = "🌱"
        suggestion = "试错仓，关注主线"
    elif 60 < zt_count <= 100 or 5 < lb_count <= 8 or 15 <= zhaban_rate < 25:
        stage = "高潮期"
        stage_icon = "🔥"
        suggestion = "重仓参与，聚焦龙头"
    else:
        stage = "退潮期"
        stage_icon = "❄️"
        suggestion = "止盈减仓，防守为主"
    
    lines = [
        f"【1】市场情绪周期 {stage_icon}",
        "─" * 60,
        f"当前阶段：{stage}",
        "",
        f"关键指标：",
        f"  • 涨停家数：{zt_count}家",
        f"  • 连板高度：{lb_count}板",
        f"  • 炸板率：{zhaban_rate:.0f}%",
        "",
        f"操作建议：{suggestion}",
        "",
        "情绪周期标准：",
        "  | 阶段 | 涨停家数 | 连板高度 | 炸板率 | 操作 |",
        "  |------|----------|----------|--------|------|",
        "  | 冰点 | <30 家   | <3 板    | >40%   | 空仓 |",
        "  | 复苏 | 30-60 家 | 3-5 板   | 25-40% | 试错 |",
        "  | 高潮 | 60-100 家| 5-8 板   | 15-25% | 重仓 |",
        "  | 退潮 | >100 家  | >8 板    | <15%   | 止盈 |",
    ]
    
    return "\n".join(lines)


def generate_market_overview(data):
    """【2】市场概览"""
    if not data:
        return "【2】市场概览\n数据暂缺"
    
    indices = data.get("indices") or {}
    margin = data.get("margin") or {}
    
    lines = ["【2】市场概览", "─" * 60]
    
    # 指数
    lines.append("📊 主要指数收盘：")
    if indices:
        for name, d in indices.items():
            if d:
                pct = d.get("pct_chg", 0) or 0
                close_val = d.get("close", 0)
                trend = "🔺" if pct > 0 else "🔻" if pct < 0 else "➖"
                lines.append(f"  {trend} {name:12s}: {close_val:>10,.2f} ({pct:>+6.2f}%)")
    else:
        lines.append("  数据待确认")
    
    # 融资融券
    lines.append("\n💰 融资融券：")
    if margin and margin.get("balance"):
        lines.append(f"  融资余额：{margin['balance']:.2f}亿元")
        lines.append(f"  日变化：{margin.get('change', 0):+.2f}亿元")
    else:
        lines.append("  数据待确认")
    
    return "\n".join(lines)


def generate_limit_up_analysis(data):
    """【3】涨停板深度分析（增强）
    
    优化内容：
    - 统计对比（vs 昨日）
    - 板块分布（条形图可视化）
    - 连板股详情（表格展示）
    """
    limit_up = data.get("limit_up") or {}
    zt_sector_dist = data.get("zt_sector_dist") or {}
    zt_change_data = data.get("zt_change_data") or {}
    
    lines = ["【3】涨停板深度分析", "─" * 60]
    
    zt_count = limit_up.get("total_count", 0) or 0
    lb_count = limit_up.get("lianban_count", 0) or 0
    
    # 统计对比
    yesterday_zt = zt_change_data.get("yesterday_count", zt_count)
    zt_change = zt_count - yesterday_zt
    zt_change_icon = "🔺" if zt_change > 0 else "🔻" if zt_change < 0 else "➖"
    
    lines.append(f"🔥 涨停统计：")
    lines.append(f"  • 涨停家数：{zt_count}家 ({zt_change_icon} {abs(zt_change)}家 vs 昨日)")
    lines.append(f"  • 连板家数：{lb_count}家")
    
    # 最高连板
    top_lianban = limit_up.get("top_lianban") or []
    if top_lianban:
        lines.append(f"  • 最高连板：{top_lianban[0].get('名称', 'Unknown')} ({top_lianban[0].get('连板数', 0)}连板)")
    
    # 板块分布（条形图可视化）
    if zt_sector_dist:
        lines.append("\n📊 涨停股板块分布：")
        sorted_sectors = sorted(zt_sector_dist.items(), key=lambda x: x[1], reverse=True)[:10]
        max_count = sorted_sectors[0][1] if sorted_sectors else 1
        
        for sector, count in sorted_sectors:
            bar_len = int((count / max_count) * 20)  # 最多 20 个█
            bar = "█" * bar_len
            lines.append(f"  {bar:20s} {sector:15s} ({count}家)")
    
    # 连板股详情
    if top_lianban:
        lines.append("\n📋 连板股详情：")
        lines.append(f"  {'排名':<6}{'名称':<15}{'连板数':<10}{'封板资金':<15}{'板块':<15}")
        lines.append(f"  {'-'*61}")
        for i, stock in enumerate(top_lianban[:5], 1):
            name = stock.get("名称", "")
            lianban = stock.get("连板数", 0)
            fengban = stock.get("封板资金", 0) / 10000  # 万
            sector = stock.get("板块", "未知")
            lines.append(f"  {i:<6}{name:<15}{lianban:<10}{fengban:>8.0f}万   {sector:<15}")
    
    return "\n".join(lines)


def generate_longhubang_analysis(data):
    """【4】龙虎榜深度解读（增强）
    
    优化内容：
    - 机构动向（净买入对比）
    - 知名游资识别（作手新一、章盟主等）
    - 游资情绪指标（活跃度、净买入）
    """
    longhubang = data.get("longhubang") or {}
    famous_youzi = data.get("famous_youzi") or []
    
    lines = ["【4】龙虎榜深度解读", "─" * 60]
    
    lhb_items = longhubang.get("items") or []
    lines.append(f"📊 上榜总数：{len(lhb_items)}条")
    
    # 机构动向
    institutions = longhubang.get("institutions") or []
    lines.append(f"\n🏆 机构动向：")
    if institutions:
        total_net = sum(inst.get("龙虎榜净买额", 0) for inst in institutions)
        lines.append(f"  • 净买入：¥{total_net/100000000:.2f}亿")
        lines.append(f"  • 买入 Top3：")
        for inst in institutions[:3]:
            name = inst.get("名称", "")
            net = inst.get("龙虎榜净买额", 0) / 100000000
            lines.append(f"    - {name}: {net:+.2f}亿")
    else:
        lines.append(f"  • 今日无机构席位上榜")
    
    # 知名游资
    if famous_youzi:
        lines.append(f"\n🎯 知名游资动向：")
        for yz in famous_youzi[:5]:
            name = yz.get("name", "")
            action = yz.get("action", "")
            stock = yz.get("stock", "")
            amount = yz.get("amount", 0)
            lines.append(f"  • {name}: {action} {stock} ({amount/10000:.0f}万)")
    
    # 游资情绪指标
    active = longhubang.get("active_stocks") or []
    if active:
        lines.append(f"\n🔍 游资情绪指标：")
        lines.append(f"  • 活跃股数：{len(active)}家")
        total_chengjiao = sum(stock.get("龙虎榜成交额", 0) for stock in active)
        lines.append(f"  • 总成交额：¥{total_chengjiao/100000000:.2f}亿")
        lines.append(f"  • 情绪判断：{'升温 🔥' if len(active) > 5 else '平稳 ➖' if len(active) > 2 else '偏冷 🥶'}")
    
    return "\n".join(lines)


def generate_market_theme(data):
    """【5】市场主线"""
    theme = data.get("theme_analysis") or {}
    industry = data.get("industry") or []
    
    lines = ["【5】市场主线", "─" * 60]
    
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
        lines.append("\n🐉 龙头企业：")
        for leader in leaders[:3]:
            name = leader.get("name", "")
            sector = leader.get("sector", "")
            lines.append(f"  • {name} ({sector})")
    
    if mid_caps:
        lines.append("\n🛡️ 中军企业：")
        for mid in mid_caps[:3]:
            name = mid.get("name", "")
            sector = mid.get("sector", "")
            lines.append(f"  • {name} ({sector})")
    
    return "\n".join(lines)


def generate_holdings_performance(data):
    """【6】持仓个股深度分析（增强）
    
    优化内容：
    - 显示成本价和浮盈
    - 目标价和止损位
    - 个性化操作建议
    """
    holdings = data.get("holdings") or []
    
    if not holdings:
        return "【6】持仓个股表现\n暂无持仓数据"
    
    holdings_config = load_holdings_config()
    config_map = {}
    if holdings_config and holdings_config.get("holdings"):
        for cfg in holdings_config["holdings"]:
            config_map[cfg["name"]] = cfg
    
    lines = ["【6】持仓个股深度分析", "─" * 60]
    
    for stock in holdings:
        name = stock.get("name", "")
        code = stock.get("code", "")
        price = stock.get("price", 0)
        pct = stock.get("pct", 0) or 0
        industry = stock.get("industry", "")
        validated = "✅" if stock.get("validated") else "⚠️"
        
        trend = "🔺" if pct > 0 else "🔻" if pct < 0 else "➖"
        lines.append(f"{validated} {trend} {name:12s} ({code}): ¥{price:>8.3f} ({pct:>+6.2f}%)")
        
        # 持仓配置信息（深度优化）
        cfg = config_map.get(name, {})
        if cfg:
            cost = cfg.get("cost", 0)
            target = cfg.get("target", 0)
            stop_loss = cfg.get("stop_loss", 0)
            strategy = cfg.get("strategy", "观望")
            
            # 浮盈计算
            if cost > 0 and price > 0:
                profit_pct = ((price - cost) / cost) * 100
                lines.append(f"   成本：¥{cost:.2f} | 浮盈：{profit_pct:+.1f}%")
                lines.append(f"   目标：¥{target:.2f} | 止损：¥{stop_loss:.2f}")
                lines.append(f"   策略：{strategy}")
        
        lines.append("")
    
    return "\n".join(lines)


def generate_tomorrow_strategy(data):
    """【7】明日策略（个性化）
    
    优化内容：
    - 基于持仓的明日关注
    - 风险预警
    - 集合竞价/北向资金/事件催化剂
    """
    holdings = data.get("holdings") or []
    holdings_config = load_holdings_config()
    
    lines = [
        "【7】明日策略",
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
    
    # 个性化明日关注（基于持仓）
    if holdings_config and holdings_config.get("holdings"):
        lines.append("\n📌 持仓股明日关注：")
        for cfg in holdings_config["holdings"][:5]:
            name = cfg.get("name", "")
            focus = cfg.get("today_focus", "")
            target = cfg.get("target", 0)
            stop_loss = cfg.get("stop_loss", 0)
            lines.append(f"   • {name}: {focus} | 关注¥{target:.2f}/止损¥{stop_loss:.2f}")
    
    lines.append("\n🔍 关键时点：")
    lines.append("   • 9:25 集合竞价（观察开盘）")
    lines.append("   • 10:00 北向资金流向（决定方向）")
    lines.append("   • 14:00 午后资金（是否跳水）")
    
    return "\n".join(lines)


def generate_afternoon_review_v24(data):
    """生成 v24.0 深度优化版复盘报告"""
    
    sections = []
    
    # 标题
    current_date = datetime.now()
    weekday_map = {
        'Monday': '一', 'Tuesday': '二', 'Wednesday': '三',
        'Thursday': '四', 'Friday': '五', 'Saturday': '六', 'Sunday': '日'
    }
    weekday = weekday_map.get(current_date.strftime('%A'), 'X')
    
    sections.append("=" * 60)
    sections.append(f"📊 A 股复盘 v24.0（深度优化）| {current_date.strftime('%Y-%m-%d')} 星期{weekday}")
    sections.append(f"数据截止：{current_date.strftime('%H:%M')} (收盘后)")
    sections.append("=" * 60)
    sections.append("")
    
    # 一句话总结
    summary = generate_one_sentence_summary(data)
    sections.append(f"📖 总结：{summary}")
    sections.append("")
    
    # 各模块
    sections.append(generate_emotion_cycle_section(data))
    sections.append("")
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
            '上证指数': {'close': 3948.55, 'pct_chg': 1.46},
            '深证成指': {'close': 13706.52, 'pct_chg': 1.70},
        },
        'limit_up': {
            'total_count': 56,
            'lianban_count': 5,
            'top_lianban': [
                {'名称': '三房巷', '连板数': 5, '封板资金': 120000000, '板块': '化纤'}
            ]
        },
        'longhubang': {
            'items': [1,2,3,4,5],
            'top10_buy': [{'名称': '中际旭创', '龙虎榜净买额': 1500000000}],
            'institutions': [{'名称': '机构专用', '龙虎榜净买额': 800000000}],
            'active_stocks': [{'名称': '工业富联', '龙虎榜成交额': 3000000000}]
        },
        'industry': [
            {'name': '半导体', 'change': 2.5},
            {'name': 'AI 算力', 'change': 1.8},
        ],
        'holdings': [
            {'name': '三花智控', 'code': '002050', 'price': 28.5, 'pct': 1.5, 'industry': '汽车零部件', 'validated': True},
        ],
        'margin': {'balance': 15000, 'change': -50},
        'theme_analysis': {
            'leaders': [{'name': '中际旭创', 'sector': 'CPO'}],
            'mid_caps': [{'name': '工业富联', 'sector': 'AI 服务器'}]
        },
        'zt_sector_dist': {'半导体': 10, 'AI': 8, '化纤': 6},
        'famous_youzi': [{'name': '作手新一', 'action': '买入', 'stock': '中际旭创', 'amount': 80000000}],
        'zhaban_rate': 18.0,
    }
    
    report = generate_afternoon_review_v24(test_data)
    print(report)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v23 边界情况测试

测试各种数据缺失、None 值、空列表等边界情况
"""

from morning_report_template_v23 import generate_morning_report_v23
from afternoon_review_template_v23 import generate_afternoon_review_v23

print("="*60)
print("v23 边界情况测试")
print("="*60)

# 测试 1: 所有数据为空
print("\n【测试 1】所有数据为空")
try:
    empty_data = {}
    report = generate_morning_report_v23(empty_data)
    print(f"  ✅ 早报处理空数据成功 (len={len(report)})")
except Exception as e:
    print(f"  ❌ 早报处理空数据失败：{e}")

try:
    empty_data = {}
    report = generate_afternoon_review_v23(empty_data)
    print(f"  ✅ 复盘处理空数据成功 (len={len(report)})")
except Exception as e:
    print(f"  ❌ 复盘处理空数据失败：{e}")

# 测试 2: 关键字段为 None
print("\n【测试 2】关键字段为 None")
try:
    none_data = {
        'us_indices': None,
        'limit_up': None,
        'holdings': None,
        'indices': None,
        'longhubang': None,
        'industry': None,
        'overnight_news': None,
    }
    report = generate_morning_report_v23(none_data)
    print(f"  ✅ 早报处理 None 值成功 (len={len(report)})")
except Exception as e:
    print(f"  ❌ 早报处理 None 值失败：{e}")

# 测试 3: 列表为空
print("\n【测试 3】列表为空")
try:
    empty_list_data = {
        'holdings': [],
        'industry': [],
        'overnight_news': [],
        'longhubang': {'items': [], 'top10_buy': [], 'institutions': []},
        'limit_up': {'total_count': 0, 'lianban_count': 0, 'top_lianban': []},
        'indices': {'上证指数': {'close': 3400, 'pct_chg': 0}},
        'us_indices': {'富时中国 A50': {'close': 13000, 'change_pct': 0}},
        'margin': {'balance': 0, 'change': 0},
        'north_money': {'net_inflow': 0},
        'main_force': {'total_net_inflow': 0},
    }
    report = generate_morning_report_v23(empty_list_data)
    print(f"  ✅ 早报处理空列表成功 (len={len(report)})")
except Exception as e:
    print(f"  ❌ 早报处理空列表失败：{e}")

# 测试 4: 数值为 0 或负数
print("\n【测试 4】数值为 0 或负数")
try:
    negative_data = {
        'indices': {
            '上证指数': {'close': 3400, 'pct_chg': -2.5},
            '深证成指': {'close': 11000, 'pct_chg': 0},
        },
        'holdings': [
            {'name': '测试股', 'code': '000001', 'price': 0, 'pct': -5.0, 'industry': '测试', 'validated': False}
        ],
        'us_indices': {
            '道琼斯': {'close': 0, 'change_pct': -3.0, 'validated': False, 'trade_date': 'N/A'}
        },
        'limit_up': {'total_count': 0, 'lianban_count': 0, 'top_lianban': []},
        'longhubang': {'items': [], 'top10_buy': [], 'institutions': []},
        'margin': {'balance': 0, 'change': -100},
        'north_money': {'net_inflow': -50},
        'main_force': {'total_net_inflow': -500000},
        'industry': [{'name': '测试板块', 'change': -3.5}],
        'overnight_news': [],
    }
    report = generate_morning_report_v23(negative_data)
    print(f"  ✅ 早报处理负数值成功 (len={len(report)})")
    
    # 检查是否正确显示涨跌图标
    if '🔻' in report:
        print(f"  ✅ 正确显示下跌图标 🔻")
    else:
        print(f"  ⚠️  未显示下跌图标")
        
except Exception as e:
    print(f"  ❌ 早报处理负数值失败：{e}")

# 测试 5: 隔夜新闻检测
print("\n【测试 5】隔夜新闻模板检测")
try:
    template_news_data = {
        'overnight_news': [
            {'title': '美联储利率决策临近，市场关注 CPI 数据', 'snippet': '市场动态'},
            {'title': '黄金价格震荡，避险情绪与美元走强博弈', 'snippet': '市场动态'},
        ],
        'us_indices': {}, 'limit_up': {}, 'holdings': [], 'indices': {},
        'longhubang': {}, 'margin': {}, 'north_money': {}, 'main_force': {}, 'industry': []
    }
    report = generate_morning_report_v23(template_news_data)
    if '暂无最新数据' in report:
        print(f"  ✅ 正确检测到模板消息并显示提示")
    elif '美联储利率决策临近' in report:
        print(f"  ❌ 未检测到模板消息，显示了过时内容")
    else:
        print(f"  ⚠️  未知情况")
except Exception as e:
    print(f"  ❌ 隔夜新闻检测失败：{e}")

# 测试 6: 完整数据
print("\n【测试 6】完整数据（正常场景）")
try:
    full_data = {
        'us_indices': {
            '道琼斯': {'close': 40000, 'change_pct': 0.5, 'validated': True, 'trade_date': '2026-04-01'},
            '纳斯达克': {'close': 16000, 'change_pct': 1.2, 'validated': True, 'trade_date': '2026-04-01'},
            '富时中国 A50': {'close': 13000, 'change_pct': 0.8, 'validated': True, 'trade_date': '2026-04-02'},
        },
        'limit_up': {
            'total_count': 56, 
            'lianban_count': 5, 
            'top_lianban': [{'名称': '三房巷', '连板数': 5, '封板资金': 120000000}]
        },
        'holdings': [
            {'name': '三花智控', 'code': '002050', 'price': 25.5, 'pct': 1.5, 'industry': '汽车零部件', 'validated': True}
        ],
        'indices': {
            '上证指数': {'close': 3948.55, 'pct_chg': 1.46},
            '深证成指': {'close': 13706.52, 'pct_chg': 1.70},
        },
        'longhubang': {
            'items': [1,2,3],
            'top10_buy': [{'名称': '中际旭创', '龙虎榜净买额': 1500000000, '龙虎榜买入额': 2000000000, '龙虎榜卖出额': 500000000}],
            'institutions': [{'名称': '机构专用', '龙虎榜净买额': 800000000}],
        },
        'north_money': {'net_inflow': 50},
        'main_force': {'total_net_inflow': 500000},
        'industry': [{'name': '半导体', 'change': 2.5}, {'name': 'AI', 'change': 1.8}],
        'overnight_news': [
            {'title': '英伟达发布新芯片', 'snippet': 'AI 算力升级'},
        ],
        'margin': {'balance': 15000, 'change': -50},
        'us_benchmark_data': {'三花智控': {'symbol': 'THO', 'change': 1.2}},
        'zt_sector_dist': {'半导体': 10, 'AI': 8},
        'famous_youzi': [{'name': '作手新一', 'action': '买入', 'stock': '中际旭创'}],
    }
    report = generate_morning_report_v23(full_data)
    print(f"  ✅ 早报处理完整数据成功 (len={len(report)})")
    
    # 检查关键内容
    checks = [
        ('一句话导读', '📖 导读：' in report),
        ('涨跌图标', '🔺' in report or '🔻' in report),
        ('持仓个股', '三花智控' in report),
        ('美股对标', '🇺🇸' in report),
        ('涨停数据', '56 家' in report),
        ('龙虎榜', '中际旭创' in report),
    ]
    
    for name, ok in checks:
        if ok:
            print(f"  ✅ 包含{name}")
        else:
            print(f"  ⚠️  缺少{name}")
    
except Exception as e:
    print(f"  ❌ 早报处理完整数据失败：{e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("边界测试完成")
print("="*60)

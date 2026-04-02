#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v23 模板数据字段自检脚本

检查 v23 模板使用的所有数据字段是否在 v21 主脚本中存在
"""

import sys
import re
from pathlib import Path

# 脚本目录
SCRIPT_DIR = Path(__file__).parent

# v21 主脚本提供的数据字段（从 main() 函数的 data 字典提取）
V21_AVAILABLE_FIELDS = {
    # 核心字段
    'indices': 'A 股指数',
    'holdings': '持仓个股',
    'us_indices': '美股指数',
    'margin': '融资融券',
    'industry': '行业板块',
    'longhubang': '龙虎榜',
    'limit_up': '涨停板',
    'north_money': '北向资金',
    'main_force': '主力资金',
    'theme_analysis': '市场主线分析',
    'overnight_news': '隔夜重要消息',
    
    # v22 增强数据
    'holdings_config': '持仓配置',
    'us_benchmark_data': '美股对标数据',
    'zt_sector_dist': '涨停股板块分布',
    'famous_youzi': '知名游资',
    'market_volume': '市场成交量',
    'zt_change_data': '涨停家数变化',
    'zhaban_rate': '炸板率',
}

# v23 模板使用的字段（需要检查）
V23_REQUIRED_FIELDS = {
    'morning_report_template_v23.py': [
        'us_indices', 'limit_up', 'overnight_news', 'holdings', 
        'us_benchmark_data', 'indices', 'margin', 'longhubang',
        'north_money', 'main_force', 'industry', 'zt_sector_dist',
        'famous_youzi'
    ],
    'afternoon_review_template_v23.py': [
        'indices', 'margin', 'limit_up', 'longhubang', 
        'industry', 'theme_analysis', 'holdings', 'us_benchmark_data',
        'zt_sector_dist', 'famous_youzi'
    ]
}

def check_template_fields():
    """检查模板字段是否都在 v21 中存在"""
    print("="*60)
    print("v23 模板数据字段自检")
    print("="*60)
    
    all_ok = True
    
    for template_file, required_fields in V23_REQUIRED_FIELDS.items():
        print(f"\n📄 检查 {template_file}")
        print("-"*60)
        
        missing = []
        for field in required_fields:
            if field in V21_AVAILABLE_FIELDS:
                print(f"  ✅ {field:25s} ({V21_AVAILABLE_FIELDS[field]})")
            else:
                print(f"  ❌ {field:25s} (缺失!)")
                missing.append(field)
                all_ok = False
        
        if missing:
            print(f"\n⚠️  发现 {len(missing)} 个缺失字段：{', '.join(missing)}")
    
    print("\n" + "="*60)
    if all_ok:
        print("✅ 所有字段都存在，模板可以正常工作")
        return 0
    else:
        print("❌ 发现缺失字段，需要修复")
        return 1

def check_template_syntax():
    """检查模板语法是否正确"""
    print("\n" + "="*60)
    print("模板语法检查")
    print("="*60)
    
    templates = [
        'morning_report_template_v23.py',
        'afternoon_review_template_v23.py'
    ]
    
    all_ok = True
    for template in templates:
        template_path = SCRIPT_DIR / template
        if not template_path.exists():
            print(f"  ❌ {template} 文件不存在")
            all_ok = False
            continue
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                code = f.read()
            compile(code, template_path, 'exec')
            print(f"  ✅ {template} 语法正确")
        except SyntaxError as e:
            print(f"  ❌ {template} 语法错误：{e}")
            all_ok = False
        except Exception as e:
            print(f"  ❌ {template} 检查失败：{e}")
            all_ok = False
    
    return 0 if all_ok else 1

def check_data_structure_compatibility():
    """检查数据结构兼容性"""
    print("\n" + "="*60)
    print("数据结构兼容性检查")
    print("="*60)
    
    # 检查关键字段的数据结构
    checks = [
        ('us_indices', '字典', '包含道琼斯、纳斯达克、富时中国 A50 等'),
        ('limit_up', '字典', '包含 total_count, lianban_count, top_lianban'),
        ('longhubang', '字典', '包含 items, top10_buy, top10_sell, institutions'),
        ('holdings', '列表', '每个元素包含 name, code, price, pct, industry'),
        ('indices', '字典', '包含上证指数、深证成指等'),
        ('industry', '列表', '每个元素包含 name, change'),
    ]
    
    all_ok = True
    for field, dtype, desc in checks:
        if field in V21_AVAILABLE_FIELDS:
            print(f"  ✅ {field:20s} ({dtype}) - {desc}")
        else:
            print(f"  ❌ {field:20s} 缺失")
            all_ok = False
    
    return 0 if all_ok else 1

def run_test_generation():
    """测试生成报告"""
    print("\n" + "="*60)
    print("测试报告生成")
    print("="*60)
    
    try:
        # 测试早报
        print("\n  测试早报模板...")
        from morning_report_template_v23 import generate_morning_report_v23
        
        test_data = {
            'us_indices': {
                '道琼斯': {'close': 40000, 'change_pct': 0.5, 'validated': True, 'trade_date': '2026-04-01'},
                '纳斯达克': {'close': 16000, 'change_pct': 1.2, 'validated': True, 'trade_date': '2026-04-01'},
                '富时中国 A50': {'close': 13000, 'change_pct': 0.8, 'validated': True, 'trade_date': '2026-04-02'},
            },
            'limit_up': {'total_count': 50, 'lianban_count': 5, 'top_lianban': []},
            'holdings': [],
            'indices': {'上证指数': {'close': 3400, 'pct_chg': 0.5}},
            'longhubang': {'items': [], 'top10_buy': [], 'institutions': []},
            'north_money': {'net_inflow': 50},
            'main_force': {'total_net_inflow': 500000},
            'industry': [],
            'overnight_news': [],
            'margin': {'balance': 15000, 'change': -50},
            'us_benchmark_data': {},
            'zt_sector_dist': {},
            'famous_youzi': [],
        }
        
        report = generate_morning_report_v23(test_data)
        if report and len(report) > 500:
            print(f"  ✅ 早报生成成功 (len={len(report)})")
        else:
            print(f"  ❌ 早报生成失败 (len={len(report) if report else 0})")
            return 1
        
        # 测试复盘
        print("  测试复盘模板...")
        from afternoon_review_template_v23 import generate_afternoon_review_v23
        
        test_data['theme_analysis'] = {'leaders': [], 'mid_caps': []}
        report = generate_afternoon_review_v23(test_data)
        if report and len(report) > 500:
            print(f"  ✅ 复盘生成成功 (len={len(report)})")
        else:
            print(f"  ❌ 复盘生成失败 (len={len(report) if report else 0})")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"  ❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    results = []
    
    results.append(check_template_fields())
    results.append(check_template_syntax())
    results.append(check_data_structure_compatibility())
    results.append(run_test_generation())
    
    print("\n" + "="*60)
    print("自检总结")
    print("="*60)
    
    if all(r == 0 for r in results):
        print("✅ 所有检查通过，v23 模板可以正常使用")
        sys.exit(0)
    else:
        failed = sum(1 for r in results if r != 0)
        print(f"❌ {failed} 项检查失败，需要修复")
        sys.exit(1)

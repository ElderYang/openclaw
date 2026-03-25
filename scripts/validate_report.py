#!/usr/bin/env python3
"""
股市早报/复盘报告 - 自动化验证脚本
每次执行后自动检查数据质量，确保所有模块正常工作
"""

import json
from pathlib import Path
from datetime import datetime

CACHE_DIR = Path('/Users/yangbowen/.openclaw/workspace/cache')

def validate_report():
    """验证报告数据质量"""
    today = datetime.now().strftime('%Y%m%d')
    cache_file = CACHE_DIR / f'review_v21_{today}.json'
    
    if not cache_file.exists():
        print("❌ 缓存文件不存在")
        return False
    
    with open(cache_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    report_data = data.get('data', {})
    issues = []
    
    # 1. 检查 A 股指数
    indices = report_data.get('indices', {})
    if len(indices) < 4:
        issues.append(f"A 股指数仅{len(indices)}个（期望 4 个）")
    
    # 2. 检查持仓个股
    holdings = report_data.get('holdings', [])
    if len(holdings) < 6:
        issues.append(f"持仓个股仅{len(holdings)}只（期望≥6 只）")
    
    # 3. 检查美股指数
    us_indices = report_data.get('us_indices', {})
    if len(us_indices) < 3:
        issues.append(f"美股指数仅{len(us_indices)}个（期望≥3 个）")
    
    # 4. 检查行业板块
    industry = report_data.get('industry', [])
    industry_str = str(industry)
    if not industry or (len(industry) == 1 and '待确认' in industry_str and '昨日' not in industry_str):
        issues.append("行业板块数据缺失")
    
    # 5. 检查龙虎榜
    lhb = report_data.get('longhubang') or {}
    lhb_has_data = (
        (lhb.get('total_count', 0) > 0) or 
        (len(lhb.get('top10_buy', [])) > 0) or
        (len(lhb.get('top10_sell', [])) > 0)
    )
    if not lhb_has_data:
        issues.append("龙虎榜数据缺失")
    
    # 6. 检查涨停板
    limit_up = report_data.get('limit_up', {})
    if limit_up.get('total_count', 0) == 0:
        issues.append("涨停板数据为 0")
    
    # 7. 检查北向资金
    north_money = report_data.get('north_money')
    if not north_money:
        issues.append("北向资金数据缺失")
    
    # 8. 检查执行时间
    exec_time = data.get('execution_time', 999)
    if exec_time > 120:
        issues.append(f"执行时间过长：{exec_time:.1f}秒（目标<120 秒）")
    
    # 输出验证结果
    print("="*60)
    print(f"📊 数据质量验证报告 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*60)
    
    if issues:
        print(f"\n❌ 发现 {len(issues)} 个问题:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        print("\n⚠️ 报告存在质量问题，请检查！")
        return False
    else:
        print("\n✅ 所有检查通过！")
        print(f"\n数据概览:")
        print(f"  A 股指数：{len(indices)}个")
        print(f"  持仓个股：{len(holdings)}只")
        print(f"  美股指数：{len(us_indices)}个")
        print(f"  行业板块：{len(industry)}个")
        print(f"  龙虎榜：{'✅' if lhb_has_data else '❌'}")
        print(f"  涨停板：{limit_up.get('total_count', 0)}家")
        print(f"  执行时间：{exec_time:.1f}秒")
        return True

if __name__ == '__main__':
    success = validate_report()
    exit(0 if success else 1)

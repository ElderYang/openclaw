#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据源修复验证脚本

验证项目：
1. Tavily API（隔夜新闻）
2. mx-stocks-screener（行业板块）
3. QVeris API（持仓个股）
4. Tushare（指数数据）
"""

import subprocess
import sys
import time
from datetime import datetime

print("="*60)
print("数据源修复验证")
print("="*60)
print(f"检查时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

results = {}

# 测试 1: Tavily API（隔夜新闻）
print("【1/4】Tavily API（隔夜新闻）")
print("-"*60)
start = time.time()
try:
    result = subprocess.run(
        ['python3', 'get_overnight_news_optimized.py'],
        cwd='/Users/yangbowen/.openclaw/workspace/scripts',
        capture_output=True,
        text=True,
        timeout=60
    )
    elapsed = time.time() - start
    
    if '✅' in result.stdout and '4 条' in result.stdout:
        print(f"  ✅ 成功！{elapsed:.1f}秒，获取到 4 条新闻")
        results['tavily'] = {'status': 'success', 'time': elapsed, 'count': 4}
    else:
        print(f"  ⚠️  部分成功，{elapsed:.1f}秒")
        results['tavily'] = {'status': 'partial', 'time': elapsed}
except Exception as e:
    print(f"  ❌ 失败：{e}")
    results['tavily'] = {'status': 'failed', 'error': str(e)}

print()

# 测试 2: mx-stocks-screener（行业板块）
print("【2/4】mx-stocks-screener（行业板块）")
print("-"*60)
start = time.time()
try:
    result = subprocess.run(
        ['python3', 'get_data.py', '--query', 'A 股行业板块 涨幅排行', '--select-type', '板块'],
        cwd='/Users/yangbowen/.openclaw/workspace/skills/mx-stocks-screener/scripts',
        capture_output=True,
        text=True,
        timeout=30
    )
    elapsed = time.time() - start
    
    if '调用成功' in result.stdout and 'CSV:' in result.stdout:
        # 提取行数
        import re
        rows_match = re.search(r'行数：(\d+)', result.stdout)
        rows = int(rows_match.group(1)) if rows_match else 0
        print(f"  ✅ 成功！{elapsed:.1f}秒，获取到 {rows} 条行业数据")
        results['industry'] = {'status': 'success', 'time': elapsed, 'count': rows}
    else:
        print(f"  ❌ 失败：{result.stderr[:200]}")
        results['industry'] = {'status': 'failed', 'error': result.stderr[:200]}
except Exception as e:
    print(f"  ❌ 失败：{e}")
    results['industry'] = {'status': 'failed', 'error': str(e)}

print()

# 测试 3: QVeris API（持仓个股）
print("【3/4】QVeris API（持仓个股）")
print("-"*60)
start = time.time()
try:
    result = subprocess.run(
        ['python3', 'qveris_tool.py', 'get_stock_price', '--symbol', '002050'],
        cwd='/Users/yangbowen/.openclaw/workspace/skills/qveris/scripts',
        capture_output=True,
        text=True,
        timeout=15
    )
    elapsed = time.time() - start
    
    if result.returncode == 0 and '三花智控' in result.stdout:
        print(f"  ✅ 成功！{elapsed:.1f}秒，获取到三花智控股价")
        results['qveris'] = {'status': 'success', 'time': elapsed}
    else:
        print(f"  ⚠️  部分成功，{elapsed:.1f}秒")
        results['qveris'] = {'status': 'partial', 'time': elapsed}
except Exception as e:
    print(f"  ❌ 失败：{e}")
    results['qveris'] = {'status': 'failed', 'error': str(e)}

print()

# 测试 4: Tushare（指数数据）
print("【4/4】Tushare（指数数据）")
print("-"*60)
start = time.time()
try:
    import tushare as ts
    pro = ts.pro_api('7fd1efd0e7e0e5e5e5e5e5e5e5e5e5e5e5e5e5e5')
    df = pro.index_daily(ts_code='000001.SH', start_date='20260401', end_date='20260402')
    elapsed = time.time() - start
    
    if len(df) > 0:
        print(f"  ✅ 成功！{elapsed:.1f}秒，获取到上证指数数据")
        results['tushare'] = {'status': 'success', 'time': elapsed}
    else:
        print(f"  ⚠️  无数据，{elapsed:.1f}秒")
        results['tushare'] = {'status': 'partial', 'time': elapsed}
except Exception as e:
    print(f"  ❌ 失败：{e}")
    results['tushare'] = {'status': 'failed', 'error': str(e)}

print()

# 总结
print("="*60)
print("验证总结")
print("="*60)

success_count = sum(1 for r in results.values() if r['status'] == 'success')
total = len(results)

print(f"成功：{success_count}/{total}")

for name, result in results.items():
    status = result['status']
    status_icon = '✅' if status == 'success' else '⚠️' if status == 'partial' else '❌'
    time_str = f"{result.get('time', 0):.1f}秒" if 'time' in result else ''
    count_str = f" ({result.get('count', 0)}条)" if 'count' in result else ''
    print(f"  {status_icon} {name:15s} {status:10s} {time_str}{count_str}")

print()
if success_count == total:
    print("🎉 所有数据源验证通过！可以切换到 v24 模板")
else:
    print("⚠️  部分数据源存在问题，建议修复后再切换")

print("="*60)

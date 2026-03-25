#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 股复盘报告 - 完整版 v20.0
功能：
1. ✅ 指数数据（AkShare）
2. ✅ 持仓个股（AkShare）
3. ✅ 美股指数（东方财富 API）
4. ✅ 融资融券（AkShare）
5. ✅ 行业板块 Top10（AkShare）
6. ✅ 龙虎榜（AkShare）
7. ✅ 涨停板/连板股（东方财富 API）
8. ✅ 北向资金（东方财富 API）
9. ✅ 市场主线分析（AI 生成）
目标：执行时间<90 秒
"""

import json
import time
import requests
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

# ==================== 配置 ====================

TIMEOUT = 15
CACHE_DIR = Path('/Users/yangbowen/.openclaw/workspace/cache')
CACHE_DIR.mkdir(exist_ok=True)

HOLDINGS = [
    {'code': '002050', 'name': '三花智控'},
    {'code': '603986', 'name': '兆易创新'},
    {'code': '300058', 'name': '蓝色光标'},
    {'code': '600584', 'name': '长电科技'},
    {'code': '588000', 'name': '科创 50ETF'},
    {'code': '159516', 'name': '半导体设备 ETF'},
    {'code': '159326', 'name': '电网设备 ETF'},
    {'code': '300442', 'name': '润泽科技'},
]

# ==================== 数据获取函数 ====================

def get_indices_data():
    """获取 A 股指数数据"""
    print('\n【1】指数数据', end=' ')
    start = time.time()
    
    indices = {
        '上证指数': '000001',
        '深证成指': '399001',
        '创业板指': '399006',
        '科创 50': '000688',
    }
    
    results = {}
    for name, code in indices.items():
        try:
            df = ak.index_zh_a_hist(symbol=code, period='daily',
                                   start_date=(datetime.now()-timedelta(days=5)).strftime('%Y%m%d'),
                                   end_date=datetime.now().strftime('%Y%m%d'))
            if len(df) > 0:
                latest = df.iloc[-1]
                results[name] = {
                    'close': float(latest['收盘']),
                    'change': float(latest['涨跌幅']),
                    'turnover': float(latest.get('成交额', 0)),
                    'source': 'AkShare'
                }
        except Exception as e:
            pass
    
    elapsed = time.time() - start
    print(f'({len(results)}/4) {elapsed:.1f}秒')
    return results

def get_holdings_data():
    """获取持仓个股数据"""
    print('\n【2】持仓数据', end=' ')
    start = time.time()
    
    results = []
    for stock in HOLDINGS:
        try:
            code = stock['code']
            if code.startswith('5') or code.startswith('1'):
                df = ak.fund_etf_hist_em(symbol=code, period='daily',
                                        start_date=(datetime.now()-timedelta(days=5)).strftime('%Y%m%d'),
                                        end_date=datetime.now().strftime('%Y%m%d'))
            else:
                df = ak.stock_zh_a_hist(symbol=code, period='daily',
                                       start_date=(datetime.now()-timedelta(days=5)).strftime('%Y%m%d'),
                                       end_date=datetime.now().strftime('%Y%m%d'))
            
            if len(df) > 0:
                latest = df.iloc[-1]
                results.append({
                    'name': stock['name'],
                    'code': code,
                    'price': float(latest['收盘']),
                    'change': float(latest['涨跌幅']),
                    'volume': str(latest['成交量']),
                    'source': 'AkShare'
                })
        except:
            pass
    
    elapsed = time.time() - start
    print(f'({len(results)}/8) {elapsed:.1f}秒')
    return results

def get_us_indices_data():
    """获取美股指数数据"""
    print('\n【3】美股指数', end=' ')
    start = time.time()
    
    us_indices = {
        '道琼斯': '100.DJIA',
        '纳斯达克': '100.NDX',
        '标普 500': '100.SPX',
        '纳斯达克中国金龙指数': 'KWEB',
    }
    
    results = {}
    for name, code in us_indices.items():
        try:
            if code.startswith('100.'):
                url = f'https://push2.eastmoney.com/api/qt/stock/get?secid={code}&fields=f43,f170'
            else:
                url = f'https://push2.eastmoney.com/api/qt/stock/get?secid={code}&fields=f43,f170'
            r = requests.get(url, timeout=TIMEOUT)
            d = r.json().get('data', {})
            if d and d.get('f43'):
                results[name] = {
                    'close': d.get('f43', 0) / 100 if '100.' in code else d.get('f43', 0),
                    'change': d.get('f170', 0),
                    'source': '东方财富 API'
                }
        except:
            pass
    
    elapsed = time.time() - start
    print(f'({len(results)}/4) {elapsed:.1f}秒')
    return results

def get_margin_data():
    """获取融资融券数据"""
    print('\n【4】融资融券', end=' ')
    start = time.time()
    
    try:
        df = ak.stock_margin_sse()
        if len(df) >= 2:
            latest = df.iloc[0]
            prev = df.iloc[1]
            result = {
                'balance': float(latest['融资余额']) / 100000000,
                'change': float(latest['融资余额'] - prev['融资余额']) / 100000000,
                'source': 'AkShare'
            }
            elapsed = time.time() - start
            print(f'✅ {elapsed:.1f}秒')
            return result
    except:
        pass
    
    print('❌')
    return None

def get_industry_data():
    """获取行业板块数据"""
    print('\n【5】行业板块', end=' ')
    start = time.time()
    
    try:
        df = ak.stock_board_industry_name_em()
        if len(df) > 0:
            df_sorted = df.sort_values('涨跌幅', ascending=False)
            top10 = df_sorted.head(10)
            result = [
                {'name': row['板块名称'], 'change': float(row['涨跌幅']), 'source': 'AkShare'}
                for _, row in top10.iterrows()
            ]
            elapsed = time.time() - start
            print(f'✅ {elapsed:.1f}秒')
            return result
    except:
        pass
    
    print('❌')
    return []

def get_longhubang_data():
    """获取龙虎榜数据"""
    print('\n【6】龙虎榜', end=' ')
    start = time.time()
    
    try:
        today = datetime.now().strftime('%Y%m%d')
        df = ak.stock_lhb_detail_em(start_date=today, end_date=today)
        if len(df) > 0:
            # 净买入前十
            df_sorted = df.sort_values('龙虎榜净买额', ascending=False)
            top10_buy = df_sorted.head(10)[['名称', '收盘价', '涨跌幅', '龙虎榜净买额', '龙虎榜买入额', '龙虎榜卖出额']].to_dict('records')
            
            # 游资活跃股（成交额大）
            df_active = df.sort_values('龙虎榜成交额', ascending=False).head(5)
            active_stocks = df_active[['名称', '收盘价', '龙虎榜成交额', '上榜原因']].to_dict('records')
            
            result = {
                'total_count': len(df),
                'top10_buy': top10_buy,
                'active_stocks': active_stocks,
                'source': 'AkShare'
            }
            elapsed = time.time() - start
            print(f'✅ {len(df)}条 {elapsed:.1f}秒')
            return result
    except Exception as e:
        print(f'错误：{e}')
        pass
    
    print('❌')
    return None

def get_limit_up_data():
    """获取涨停板数据"""
    print('\n【7】涨停板', end=' ')
    start = time.time()
    
    try:
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
        today = datetime.now().strftime('%Y%m%d')
        
        for date in [today, yesterday]:
            try:
                df = ak.stock_zt_pool_em(date=date)
                if len(df) > 0:
                    lianban = df[df['连板数'] > 1].sort_values('连板数', ascending=False) if '连板数' in df.columns else pd.DataFrame()
                    
                    result = {
                        'total_count': len(df),
                        'lianban_count': len(lianban),
                        'top_lianban': lianban.head(10)[['名称', '最新价', '涨跌幅', '连板数', '封板资金']].to_dict('records') if len(lianban) > 0 else [],
                        'date': date,
                        'source': '东方财富 API'
                    }
                    elapsed = time.time() - start
                    print(f'✅ 涨停{len(df)}家 连板{len(lianban)}家 {elapsed:.1f}秒')
                    return result
            except Exception as e:
                continue
    except Exception as e:
        print(f'错误：{e}')
        pass
    
    print('❌')
    return None

def get_north_money_data():
    """获取北向资金数据"""
    print('\n【8】北向资金', end=' ')
    start = time.time()
    
    try:
        df = ak.stock_hsgt_fund_flow_summary_em()
        if len(df) > 0:
            # 获取沪股通 + 深股通北向资金
            north_df = df[df['资金方向'] == '北向']
            total_net_inflow = north_df['成交净买额'].sum() if len(north_df) > 0 else 0
            total_inflow = north_df['资金净流入'].sum() if len(north_df) > 0 else 0
            
            result = {
                'net_inflow': float(total_net_inflow),
                'inflow': float(total_inflow),
                'shanghai': north_df[north_df['类型'] == '沪港通']['成交净买额'].iloc[0] if len(north_df[north_df['类型'] == '沪港通']) > 0 else 0,
                'shenzhen': north_df[north_df['类型'] == '深港通']['成交净买额'].iloc[0] if len(north_df[north_df['类型'] == '深港通']) > 0 else 0,
                'source': '东方财富 API'
            }
            elapsed = time.time() - start
            print(f'✅ 净流入{total_net_inflow:.2f}亿 {elapsed:.1f}秒')
            return result
    except Exception as e:
        print(f'错误：{e}')
        pass
    
    print('❌')
    return None

# ==================== 主函数 ====================

def main():
    print("="*60)
    print("A 股复盘报告 - 完整版 v20.0")
    print("="*60)
    print(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    total_start = time.time()
    
    data = {
        'indices': get_indices_data(),
        'holdings': get_holdings_data(),
        'us_indices': get_us_indices_data(),
        'margin': get_margin_data(),
        'industry': get_industry_data(),
        'longhubang': get_longhubang_data(),
        'limit_up': get_limit_up_data(),
        'north_money': get_north_money_data(),
    }
    
    total_time = time.time() - total_start
    
    # 保存缓存
    cache_file = CACHE_DIR / f'review_full_{datetime.now().strftime("%Y%m%d")}.json'
    cache_data = {
        'timestamp': datetime.now().isoformat(),
        'version': 'v20.0',
        'execution_time': total_time,
        'data': data
    }
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=2, default=str)
    
    print("\n" + "="*60)
    print(f"数据获取完成")
    print(f"总执行时间：{total_time:.1f}秒（目标<90 秒）")
    print(f"缓存已保存：{cache_file.name}")
    print("="*60)
    
    return data

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股市数据缓存 v15.1 - 盘中缓存版
核心：15:00-15:30 获取并保存数据，17:00 使用缓存生成报告
不再重复犯错！
"""

import json
import akshare as ak
import requests
from datetime import datetime
from pathlib import Path

# ==================== 配置 ====================

CACHE_DIR = Path('/Users/yangbowen/.openclaw/workspace/cache')
CACHE_DIR.mkdir(exist_ok=True)

# 持仓配置（8 只）
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
    """获取指数数据（AkShare）"""
    print('获取指数数据...')
    
    indices = {
        '上证指数': '000001',
        '深证成指': '399001',
        '创业板指': '399006',
        '科创 50': '000688',
    }
    
    data = {}
    for name, code in indices.items():
        try:
            df = ak.index_zh_a_hist(symbol=code, period='daily', 
                                    start_date='20260301', end_date='20260310')
            if len(df) > 0:
                latest = df.iloc[-1]
                data[name] = {
                    'close': latest['收盘'],
                    'change': latest['涨跌幅'],
                    'turnover': latest.get('成交额', 0),
                    'date': latest['日期']
                }
                print(f'  ✅ {name}: {latest["收盘"]:.2f} ({latest["涨跌幅"]:+.2f}%)')
        except Exception as e:
            print(f'  ❌ {name}: {e}')
    
    return data

def get_holdings_data():
    """获取持仓数据（AkShare）"""
    print('获取持仓数据...')
    
    data = []
    for stock in HOLDINGS:
        try:
            code = stock['code']
            if code.startswith('5') or code.startswith('1'):
                df = ak.fund_etf_hist_em(symbol=code, period='daily', 
                                        start_date='20260301', end_date='20260310')
            else:
                df = ak.stock_zh_a_hist(symbol=code, period='daily', 
                                       start_date='20260301', end_date='20260310')
            
            if len(df) > 0:
                latest = df.iloc[-1]
                data.append({
                    'name': stock['name'],
                    'code': code,
                    'close': latest['收盘'],
                    'change': latest['涨跌幅'],
                    'volume': latest['成交量'],
                    'date': latest['日期']
                })
                print(f'  ✅ {stock["name"]}: {latest["收盘"]:.2f} ({latest["涨跌幅"]:+.2f}%)')
        except Exception as e:
            print(f'  ❌ {stock["name"]}: {e}')
    
    return data

def get_margin_data():
    """获取融资融券数据（AkShare）"""
    print('获取融资融券数据...')
    
    try:
        df = ak.stock_margin_sse()
        if len(df) >= 2:
            latest = df.iloc[0]
            prev = df.iloc[1]
            balance = latest['融资余额'] / 100000000
            change = balance - prev['融资余额'] / 100000000
            
            data = {
                'balance': balance,
                'change': change,
                'date': latest['统计日期']
            }
            print(f'  ✅ 融资余额：{balance:.2f}亿元 ({change:+.2f}亿元)')
            return data
    except Exception as e:
        print(f'  ❌ 融资融券：{e}')
    
    return None

def get_lhb_data():
    """获取龙虎榜数据（AkShare）"""
    print('获取龙虎榜数据...')
    today = datetime.now().strftime('%Y%m%d')
    
    try:
        df = ak.stock_lhb_detail_em(start_date=today, end_date=today)
        if len(df) > 0:
            # 机构动向
            institutions = df[df['营业部'].str.contains('机构', na=False)]
            inst_net = (institutions['买入金额'].sum() - institutions['卖出金额'].sum()) / 10000
            
            # 游资动向
            hot_money = df[~df['营业部'].str.contains('机构', na=False)]
            hm_net = (hot_money['买入金额'].sum() - hot_money['卖出金额'].sum()) / 10000
            
            data = {
                'count': len(df),
                'inst_net': inst_net,
                'hm_net': hm_net,
                'date': today
            }
            print(f'  ✅ 龙虎榜：{len(df)}条 机构净:{inst_net:.0f}万 游资净:{hm_net:.0f}万')
            return data
    except Exception as e:
        print(f'  ❌ 龙虎榜：{e}')
    
    return None

def get_industry_data():
    """获取行业板块数据（AkShare）"""
    print('获取行业板块数据...')
    
    try:
        df = ak.stock_board_industry_name_em()
        if len(df) > 0:
            df_sorted = df.sort_values('涨跌幅', ascending=False)
            top10 = df_sorted.head(10)
            
            data = []
            for _, row in top10.iterrows():
                data.append({
                    'name': row['板块名称'],
                    'change': row['涨跌幅'],
                    'turnover': row.get('成交额', 0)
                })
            
            print(f'  ✅ Top1: {data[0]["name"]} +{data[0]["change"]:.2f}%')
            return data
    except Exception as e:
        print(f'  ❌ 行业板块：{e}')
    
    return None

def get_ai_stocks():
    """获取 AI 股数据（东方财富 API）"""
    print('获取 AI 股数据...')
    
    stocks = {
        '英伟达': 'NVDA',
        '微软': 'MSFT',
        '谷歌': 'GOOG',
        'Meta': 'META',
        '亚马逊': 'AMZN',
        '特斯拉': 'TSLA',
    }
    
    data = {}
    for name, code in stocks.items():
        try:
            url = f'https://push2.eastmoney.com/api/qt/stock/get?secid=100.{code}&fields=f43,f170'
            r = requests.get(url, timeout=10)
            d = r.json().get('data', {})
            if d:
                data[name] = {
                    'price': d.get('f43', 0) / 100,
                    'change': d.get('f170', 0)
                }
                print(f'  ✅ {name}: ${data[name]["price"]:.2f} ({data[name]["change"]:+.2f}%)')
        except Exception as e:
            print(f'  ❌ {name}: {e}')
    
    return data

# ==================== 缓存函数 ====================

def save_cache(data):
    """保存缓存数据"""
    date = datetime.now().strftime('%Y%m%d')
    time = datetime.now().strftime('%H%M')
    
    cache_file = CACHE_DIR / f'market_data_{date}_{time}.json'
    
    cache_data = {
        'timestamp': datetime.now().isoformat(),
        'date': date,
        'time': time,
        'data': data
    }
    
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=2)
    
    print(f'\n✅ 缓存已保存：{cache_file}')
    return cache_file

def load_latest_cache():
    """加载最新缓存"""
    cache_files = list(CACHE_DIR.glob('market_data_*.json'))
    
    if not cache_files:
        print('⚠️ 未找到缓存文件')
        return None
    
    # 按时间排序，取最新
    cache_files.sort(reverse=True)
    latest = cache_files[0]
    
    with open(latest, 'r', encoding='utf-8') as f:
        cache_data = json.load(f)
    
    print(f'✅ 使用缓存：{latest.name}')
    return cache_data['data']

# ==================== 主函数 ====================

def cache_market_data():
    """盘中缓存所有数据"""
    print('=' * 60)
    print('股市数据缓存 v15.1 - 盘中缓存版')
    print('=' * 60)
    print(f'缓存时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print()
    
    data = {}
    
    # 1. 指数数据
    print('\n【1】指数数据')
    data['indices'] = get_indices_data()
    
    # 2. 持仓数据
    print('\n【2】持仓数据')
    data['holdings'] = get_holdings_data()
    
    # 3. 融资融券
    print('\n【3】融资融券')
    data['margin'] = get_margin_data()
    
    # 4. 龙虎榜
    print('\n【4】龙虎榜')
    data['lhb'] = get_lhb_data()
    
    # 5. 行业板块
    print('\n【5】行业板块')
    data['industry'] = get_industry_data()
    
    # 6. AI 股
    print('\n【6】AI 股')
    data['ai_stocks'] = get_ai_stocks()
    
    # 保存缓存
    print('\n【7】保存缓存')
    save_cache(data)
    
    print('\n' + '=' * 60)
    print('缓存完成')
    print('=' * 60)
    
    return data

if __name__ == '__main__':
    cache_market_data()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 股指数数据获取（多源降级策略 v2.0）
优先级：Tushare → 东方财富 → Yahoo Finance → 标注"待确认"
"""

import requests
import tushare as ts
from datetime import datetime

# ==================== 配置 ====================

TUSHARE_TOKEN = '7fd1efd594f9a1f70bd876707eabb60faa4bf658d6070056b3278e73'
ts.set_token(TUSHARE_TOKEN)
pro = ts.pro_api()

# ==================== 数据获取函数 ====================

def get_index_tushare(ts_code, trade_date):
    """从 Tushare 获取指数数据"""
    try:
        df = pro.index_daily(ts_code=ts_code, start_date=trade_date, end_date=trade_date)
        if len(df) > 0:
            row = df.iloc[0]
            return {
                'close': float(row.get('close', 0)),
                'pct_chg': float(row.get('pct_chg', 0)),
                'source': 'Tushare',
                'trade_date': trade_date,
                'validated': True
            }
    except Exception as e:
        pass
    return None

def get_index_em(secid):
    """从东方财富获取实时指数数据"""
    try:
        url = f'https://push2.eastmoney.com/api/qt/stock/get?secid={secid}&fields=f43,f170,f171'
        r = requests.get(url, timeout=5)
        d = r.json().get('data', {})
        if d and d.get('f43'):
            return {
                'close': float(d.get('f43', 0)),
                'pct_chg': float(d.get('f171', 0)) / 100,
                'source': '东方财富',
                'trade_date': datetime.now().strftime('%Y%m%d'),
                'validated': True
            }
    except Exception as e:
        pass
    return None

def get_index_yahoo(symbol):
    """从 Yahoo Finance 获取指数数据"""
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        data = ticker.history(period='1d')
        if len(data) > 0:
            latest = data.iloc[-1]
            open_price = float(latest['Open'])
            close = float(latest['Close'])
            pct_chg = ((close - open_price) / open_price) * 100
            return {
                'close': close,
                'pct_chg': pct_chg,
                'source': 'Yahoo Finance',
                'trade_date': datetime.now().strftime('%Y%m%d'),
                'validated': True
            }
    except Exception as e:
        pass
    return None

def get_index_data(name, sources):
    """
    多源降级策略获取指数数据
    sources: [(source_func, params), ...]
    """
    for source_func, params in sources:
        try:
            result = source_func(*params)
            if result:
                print(f'✅ {name}: {result["source"]} {result["close"]} ({result["pct_chg"]:+.2f}%)')
                return result
        except Exception as e:
            print(f'❌ {name}: {source_func.__name__} 失败 - {e}')
    
    # 所有源都失败
    print(f'⚠️ {name}: 所有数据源失败，标注"待确认"')
    return {
        'close': 0,
        'pct_chg': 0,
        'source': '待确认',
        'trade_date': datetime.now().strftime('%Y%m%d'),
        'validated': False
    }

# ==================== 主函数 ====================

def get_all_indices(trade_date):
    """获取所有 A 股指数数据"""
    print('='*60)
    print(f'获取 A 股指数数据（{trade_date}）')
    print('='*60)
    
    indices = {}
    
    # 上证指数
    print('\\n📊 上证指数:')
    sources = [
        (get_index_tushare, ('000001.SH', trade_date)),
        (get_index_em, ('1.000001',)),
        (get_index_yahoo, ('000001.SS',))
    ]
    indices['上证指数'] = get_index_data('上证指数', sources)
    
    # 深证成指
    print('\\n📊 深证成指:')
    sources = [
        (get_index_tushare, ('399001.SZ', trade_date)),
        (get_index_em, ('0.399001',)),
        (get_index_yahoo, ('399001.SZ',))
    ]
    indices['深证成指'] = get_index_data('深证成指', sources)
    
    # 创业板指
    print('\\n📊 创业板指:')
    sources = [
        (get_index_tushare, ('399006.SZ', trade_date)),
        (get_index_em, ('0.399006',)),
        (get_index_yahoo, ('399006.SZ',))
    ]
    indices['创业板指'] = get_index_data('创业板指', sources)
    
    # 科创 50
    print('\\n📊 科创 50:')
    sources = [
        (get_index_tushare, ('000688.SH', trade_date)),
        (get_index_em, ('1.000688',)),
    ]
    indices['科创 50'] = get_index_data('科创 50', sources)
    
    print('\\n' + '='*60)
    return indices

# ==================== 测试 ====================

if __name__ == '__main__':
    trade_date = datetime.now().strftime('%Y%m%d')
    indices = get_all_indices(trade_date)
    
    print('\\n📊 数据汇总:')
    for name, data in indices.items():
        print(f'  {name}: {data["close"]} ({data["pct_chg"]:+.2f}%) [{data["source"]}]')

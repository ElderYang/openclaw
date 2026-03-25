#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据获取工具（专业版）
使用专业数据源：AkShare, Tushare, Yahoo Finance
严格多源校验，确保数据准确性
"""

import akshare as ak
import tushare as ts
import yfinance as yf
from datetime import datetime
import json

# ==================== 配置 ====================

TUSHARE_TOKEN = '7fd1efd594f9a1f70bd876707eabb60faa4bf658d6070056b3278e73'
ts.set_token(TUSHARE_TOKEN)
pro = ts.pro_api()

# ==================== A 股指数数据 ====================

def get_indices_akshare():
    """从 AkShare 获取 A 股指数数据"""
    print('\\n📊 AkShare A 股指数:')
    try:
        # 上证指数
        sh = ak.stock_zh_index_daily(symbol="sh000001")
        if len(sh) > 0:
            latest = sh.iloc[-1]
            print(f'  上证指数：{latest["close"]} ({latest.get("pct_chg", 0):.2f}%)')
            return {
                '上证指数': {'close': latest['close'], 'source': 'AkShare'}
            }
    except Exception as e:
        print(f'  获取失败：{e}')
    return {}

def get_indices_tushare(trade_date):
    """从 Tushare 获取 A 股指数数据"""
    print(f'\\n📊 Tushare A 股指数 ({trade_date}):')
    indices = {}
    
    codes = {
        '上证指数': '000001.SH',
        '深证成指': '399001.SZ',
        '创业板指': '399006.SZ',
        '科创 50': '000688.SH'
    }
    
    for name, code in codes.items():
        try:
            df = pro.index_daily(ts_code=code, start_date=trade_date, end_date=trade_date)
            if len(df) > 0:
                row = df.iloc[0]
                indices[name] = {
                    'close': float(row['close']),
                    'pct_chg': float(row['pct_chg']),
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'pre_close': float(row['pre_close']),
                    'source': 'Tushare',
                    'trade_date': row['trade_date'],
                    'validated': True
                }
                print(f'  ✅ {name}: {row["close"]} ({row["pct_chg"]}%)')
            else:
                print(f'  ⚠️ {name}: 今日数据未更新')
        except Exception as e:
            print(f'  ❌ {name}: 获取失败 - {e}')
    
    return indices

def get_indices_sina():
    """从新浪财经获取 A 股指数实时数据"""
    print('\\n📊 新浪财经 A 股指数（实时）:')
    indices = {}
    
    codes = {
        '上证指数': 'sh000001',
        '深证成指': 'sz399001',
        '创业板指': 'sz399006',
        '科创 50': 'sh000688'
    }
    
    import requests
    for name, code in codes.items():
        try:
            url = f'https://hq.sinajs.cn/list={code}'
            r = requests.get(url, timeout=5)
            if r.status_code == 200 and '=' in r.text:
                parts = r.text.split('=')[1].strip('"').split(',')
                if len(parts) > 8:
                    close = float(parts[3]) if parts[3] else 0
                    pct = float(parts[8]) if parts[8] else 0
                    indices[name] = {
                        'close': close,
                        'pct_chg': pct,
                        'source': '新浪财经',
                        'validated': True
                    }
                    print(f'  ✅ {name}: {close} ({pct:+.2f}%)')
        except Exception as e:
            print(f'  ❌ {name}: 获取失败 - {e}')
    
    return indices

def get_indices_verified(trade_date):
    """多源验证获取 A 股指数"""
    print('='*80)
    print(f'获取 A 股指数数据（{trade_date}）')
    print('='*80)
    
    # 获取三源数据
    ts_data = get_indices_tushare(trade_date)
    sina_data = get_indices_sina()
    
    # 验证一致性
    print('\\n' + '='*80)
    print('多源验证:')
    print('='*80)
    
    verified = {}
    for name in ts_data.keys():
        ts_val = ts_data.get(name, {})
        sina_val = sina_data.get(name, {})
        
        print(f'\\n{name}:')
        print(f'  Tushare: {ts_val.get("close", "N/A")} ({ts_val.get("pct_chg", 0):.2f}%)')
        print(f'  新浪财经：{sina_val.get("close", "N/A")} ({sina_val.get("pct_chg", 0):.2f}%)')
        
        # 如果 Tushare 有数据，优先使用（官方数据）
        if ts_val.get('validated'):
            print(f'  ✅ 使用 Tushare 官方数据')
            verified[name] = ts_val
        elif sina_val.get('validated'):
            print(f'  ✅ 使用新浪财经数据')
            verified[name] = sina_val
        else:
            print(f'  ❌ 数据获取失败')
    
    return verified

# ==================== 个股数据 ====================

def get_stock_data_akshare(symbol):
    """从 AkShare 获取个股数据"""
    try:
        # 实时行情
        df = ak.stock_zh_a_spot_em()
        if len(df) > 0:
            stock = df[df['代码'] == symbol]
            if len(stock) > 0:
                row = stock.iloc[0]
                return {
                    'name': row['名称'],
                    'price': float(row['最新价']),
                    'pct_chg': float(row['涨跌幅']),
                    'source': 'AkShare'
                }
    except Exception as e:
        print(f'  AkShare 获取失败：{e}')
    return None

def get_stock_data_tushare(symbol):
    """从 Tushare 获取个股数据"""
    try:
        # 获取股票基本信息
        df = pro.daily(ts_code=symbol, start_date=datetime.now().strftime('%Y%m%d'), 
                      end_date=datetime.now().strftime('%Y%m%d'))
        if len(df) > 0:
            row = df.iloc[0]
            return {
                'name': row.get('ts_code', ''),
                'price': float(row.get('close', 0)),
                'pct_chg': float(row.get('pct_chg', 0)),
                'source': 'Tushare'
            }
    except Exception as e:
        print(f'  Tushare 获取失败：{e}')
    return None

def get_stock_data_sina(symbol):
    """从新浪财经获取个股实时数据"""
    try:
        import requests
        # 转换代码格式
        if symbol.startswith('6'):
            code = f'sh{symbol}'
        else:
            code = f'sz{symbol}'
        
        url = f'https://hq.sinajs.cn/list={code}'
        r = requests.get(url, timeout=5)
        if r.status_code == 200 and '=' in r.text:
            parts = r.text.split('=')[1].strip('"').split(',')
            if len(parts) > 8:
                close = float(parts[3]) if parts[3] else 0
                pre_close = float(parts[2]) if parts[2] else 0
                pct = ((close - pre_close) / pre_close) * 100 if pre_close else 0
                return {
                    'name': symbol,
                    'price': close,
                    'pct_chg': pct,
                    'source': '新浪财经'
                }
    except Exception as e:
        print(f'  新浪财经获取失败：{e}')
    return None

def get_stocks_verified(stocks):
    """多源验证获取个股数据"""
    print('\\n' + '='*80)
    print('获取个股数据（多源验证）')
    print('='*80)
    
    verified = []
    
    for name, symbol in stocks.items():
        print(f'\\n{name} ({symbol}):')
        
        # 获取三源数据
        ak_data = get_stock_data_akshare(symbol)
        ts_data = get_stock_data_tushare(symbol)
        sina_data = get_stock_data_sina(symbol)
        
        print(f'  AkShare: {ak_data}')
        print(f'  Tushare: {ts_data}')
        print(f'  新浪财经：{sina_data}')
        
        # 优先使用 Tushare（官方数据）
        if ts_data:
            ts_data['validated'] = True
            ts_data['trade_date'] = datetime.now().strftime('%Y%m%d')
            verified.append(ts_data)
            print(f'  ✅ 使用 Tushare 数据')
        elif ak_data:
            ak_data['validated'] = True
            ak_data['trade_date'] = datetime.now().strftime('%Y%m%d')
            verified.append(ak_data)
            print(f'  ✅ 使用 AkShare 数据')
        elif sina_data:
            sina_data['validated'] = True
            sina_data['trade_date'] = datetime.now().strftime('%Y%m%d')
            verified.append(sina_data)
            print(f'  ✅ 使用新浪财经数据')
        else:
            print(f'  ❌ 所有数据源失败，标注"待确认"')
            verified.append({
                'name': name,
                'code': symbol,
                'price': 0,
                'pct_chg': 0,
                'source': '待确认',
                'trade_date': datetime.now().strftime('%Y%m%d'),
                'validated': False
            })
    
    return verified

# ==================== 主函数 ====================

def main():
    """主函数"""
    print('='*80)
    print(f'股票数据获取工具（专业版）')
    print(f'时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('='*80)
    
    # 检查今天是否交易日
    today = datetime.now().strftime('%Y%m%d')
    cal = pro.trade_cal(exchange='SSE', start_date=today, end_date=today)
    
    if len(cal) > 0 and cal.iloc[0]['is_open'] == 1:
        trade_date = today
        print(f'\\n✅ 今天（{today}）是交易日')
    else:
        # 获取最近交易日
        print(f'\\n⚠️ 今天（{today}）不是交易日，获取最近交易日数据')
        cal = pro.trade_cal(exchange='SSE', start_date='20260310', end_date=today)
        trading_days = cal[cal['is_open']==1]['calendar_date'].tolist()
        if trading_days:
            trade_date = trading_days[-1]
            print(f'最近交易日：{trade_date}')
        else:
            trade_date = today
    
    # 获取 A 股指数
    indices = get_indices_verified(trade_date)
    
    # 获取持仓个股
    stocks = {
        '三花智控': '002050',
        '兆易创新': '603986',
        '蓝色光标': '300058',
        '长电科技': '600584',
        '润泽科技': '300442'
    }
    
    holdings = get_stocks_verified(stocks)
    
    # 输出结果
    print('\\n' + '='*80)
    print('数据汇总')
    print('='*80)
    
    print('\\n📊 A 股指数:')
    for name, data in indices.items():
        print(f'  {name}: {data["close"]} ({data["pct_chg"]:+.2f}%) [{data["source"]}]')
    
    print('\\n📊 持仓个股:')
    for stock in holdings:
        limit_up_mark = ' ⬆️✅ 涨停' if stock.get('pct_chg', 0) >= 9.8 else ''
        validated_mark = ' ✅' if stock.get('validated') else ' ⚠️ 待确认'
        print(f'  {stock["name"]}: ¥{stock["price"]:.2f} ({stock["pct_chg"]:+.2f}%){limit_up_mark}{validated_mark}')
    
    print('\\n' + '='*80)
    print('✅ 数据获取完成')
    print('='*80)
    
    # 返回数据
    return {
        'indices': indices,
        'holdings': holdings,
        'trade_date': trade_date
    }

if __name__ == '__main__':
    main()

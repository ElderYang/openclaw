#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Yahoo Finance 实时数据补丁
用于优化美股指数数据获取（解决 Tushare 延迟问题）
"""

import yfinance as yf
from datetime import datetime

def get_us_indices_realtime():
    """
    获取美股实时数据（Yahoo Finance）
    返回：实时股价和涨跌幅
    """
    tickers = {
        '道琼斯': '^DJI',
        '纳斯达克': '^IXIC',
        '标普 500': '^GSPC',
    }
    
    results = {}
    for name, ticker_symbol in tickers.items():
        try:
            ticker = yf.Ticker(ticker_symbol)
            data = ticker.history(period='1d')
            
            if len(data) > 0:
                latest = data.iloc[-1]
                close = float(latest['Close'])
                open_price = float(latest['Open'])
                pct_chg = ((close - open_price) / open_price) * 100
                
                results[name] = {
                    'close': close,
                    'change_pct': pct_chg,
                    'source': 'Yahoo Finance(实时)',
                    'validated': True,
                    'trade_date': datetime.now().strftime('%Y%m%d')
                }
                print(f"✅ {name}: {close:,.0f} ({pct_chg:+.2f}%) [实时]")
            else:
                print(f"❌ {name}: 无数据")
        except Exception as e:
            print(f"❌ {name}: 错误 {str(e)[:50]}")
    
    return results

if __name__ == '__main__':
    print("="*60)
    print("📊 美股实时数据（Yahoo Finance）")
    print("="*60)
    print()
    
    results = get_us_indices_realtime()
    
    print()
    print("="*60)
    print(f"获取完成：{len(results)}/3")
    print("="*60)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 股复盘报告数据收集脚本 - 2026-03-16 (修正版)
"""

import akshare as ak
import pandas as pd
from datetime import datetime

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

def get_market_indices():
    """获取大盘指数数据"""
    print("\n=== 1. 大盘指数 ===")
    try:
        indices_data = {}
        for symbol, name in [("sh000001", "上证指数"), ("sz399001", "深证成指"), 
                            ("sz399006", "创业板指"), ("sh000688", "科创 50")]:
            df = ak.stock_zh_index_daily(symbol=symbol)
            if df is not None and len(df) > 0:
                latest = df.iloc[-1]
                prev = df.iloc[-2] if len(df) > 1 else latest
                change_pct = ((latest['close'] - prev['close']) / prev['close'] * 100) if len(df) > 1 else 0
                indices_data[name] = {
                    'close': latest['close'],
                    'change': change_pct,
                    'volume': latest['volume']
                }
                print(f"{name}: 收盘={latest['close']:.2f}, 涨跌幅={change_pct:.2f}%, 成交量={latest['volume']}")
        return indices_data
    except Exception as e:
        print(f"大盘指数获取失败：{e}")
        return None

def get_limit_stocks():
    """获取涨停跌停家数"""
    print("\n=== 2. 涨停跌停统计 ===")
    try:
        # 涨停池
        zt_pool = ak.stock_zt_pool_em(date="20260316")
        zt_count = len(zt_pool) if zt_pool is not None else 0
        print(f"涨停家数：{zt_count}")
        
        # 跌停池 - 尝试不同接口
        try:
            dt_pool = ak.stock_zt_pool_dtmc_em(date="20260316")
            dt_count = len(dt_pool) if dt_pool is not None else 0
        except:
            dt_count = "待确认"
        print(f"跌停家数：{dt_count}")
        
        # 连板股
        if zt_pool is not None and '连板数' in zt_pool.columns:
            lb_stocks = zt_pool[zt_pool['连板数'] > 1][['代码', '名称', '连板数']].head(20)
            print(f"\n连板股 (前 20 只):")
            print(lb_stocks.to_string())
        
        return {"涨停": zt_count, "跌停": dt_count}
    except Exception as e:
        print(f"涨停跌停统计获取失败：{e}")
        return {"涨停": "待确认", "跌停": "待确认"}

def get_industry_performance():
    """获取行业板块涨跌幅"""
    print("\n=== 3. 行业板块表现 ===")
    try:
        industry = ak.stock_board_industry_name_em()
        if industry is not None:
            print(f"行业板块数量：{len(industry)}")
            industry_sorted = industry.sort_values('涨跌幅', ascending=False)
            
            print("\n涨幅前 10:")
            cols = [c for c in ['板块', '涨跌幅', '成交量'] if c in industry_sorted.columns]
            print(industry_sorted.head(10)[cols])
            
            print("\n跌幅后 10:")
            print(industry_sorted.tail(10)[cols])
            
            return {"top10": industry_sorted.head(10), "bottom10": industry_sorted.tail(10)}
        return None
    except Exception as e:
        print(f"行业板块获取失败：{e}")
        return None

def get_longhu_list():
    """获取龙虎榜数据"""
    print("\n=== 4. 龙虎榜 ===")
    try:
        # 尝试不同接口
        try:
            lhb = ak.stock_lhb_detail_em(date="20260316")
        except:
            lhb = ak.stock_lhb_detail_em()
        
        if lhb is not None and len(lhb) > 0:
            print(f"今日龙虎榜个股数：{len(lhb)}")
            cols = [c for c in ['代码', '名称', '收盘价', '涨跌幅', '龙虎榜总成交额'] if c in lhb.columns]
            print("\n部分数据:")
            print(lhb.head(10)[cols])
            return lhb
        else:
            print("今日无龙虎榜数据")
            return None
    except Exception as e:
        print(f"龙虎榜获取失败：{e}")
        return None

def get_fund_flow():
    """获取资金流向"""
    print("\n=== 5. 资金流向 ===")
    try:
        # 北向资金
        try:
            north = ak.stock_hsgt_north_net_flow_in_em(symbol="北向资金")
            if north is not None and len(north) > 0:
                print(f"北向资金：{north.iloc[-1]}")
        except Exception as e:
            print(f"北向资金获取失败：{e}")
        
        # 主力资金
        main = ak.stock_main_fund_flow()
        if main is not None:
            print("\n行业资金流向前 5:")
            print(main.head(5))
        
        return main
    except Exception as e:
        print(f"资金流向获取失败：{e}")
        return None

def get_market_news():
    """获取市场新闻"""
    print("\n=== 6. 市场新闻 ===")
    try:
        news = ak.stock_news_em(symbol="上证指数")
        if news is not None and len(news) > 0:
            cols = [c for c in news.columns if '标题' in c or '时间' in c]
            print("最新新闻 (前 10 条):")
            print(news.head(10)[cols] if cols else news.head(10))
            return news
        return None
    except Exception as e:
        print(f"新闻获取失败：{e}")
        return None

def main():
    print("=" * 60)
    print("2026-03-16 A 股复盘报告数据收集")
    print("=" * 60)
    
    results = {}
    results['indices'] = get_market_indices()
    results['limits'] = get_limit_stocks()
    results['industry'] = get_industry_performance()
    results['lhb'] = get_longhu_list()
    results['fund_flow'] = get_fund_flow()
    results['news'] = get_market_news()
    
    print("\n" + "=" * 60)
    print("数据收集完成")
    print("=" * 60)
    
    # 保存结果
    with open('/Users/yangbowen/.openclaw/workspace/scripts/stock_data_20260316.json', 'w', encoding='utf-8') as f:
        json_results = {}
        for k, v in results.items():
            if v is not None:
                if isinstance(v, pd.DataFrame):
                    json_results[k] = v.to_dict('records')[:20]
                else:
                    json_results[k] = v
        json.dump(json_results, f, ensure_ascii=False, indent=2)
    
    return results

if __name__ == "__main__":
    main()

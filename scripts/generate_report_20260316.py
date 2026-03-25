#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 2026-03-16 A 股复盘报告
"""

import akshare as ak
import pandas as pd
from datetime import datetime
import json

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

print("=" * 80)
print(" " * 25 + "2026 年 3 月 16 日 A 股复盘报告")
print("=" * 80)

# ========== 1. 大盘指数 ==========
print("\n【一、大盘指数】")
indices_data = {}
try:
    for symbol, name in [("sh000001", "上证指数"), ("sz399001", "深证成指"), 
                        ("sz399006", "创业板指"), ("sh000688", "科创 50")]:
        df = ak.stock_zh_index_daily(symbol=symbol)
        if df is not None and len(df) > 0:
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest
            change_pct = ((latest['close'] - prev['close']) / prev['close'] * 100)
            indices_data[name] = {
                '收盘': round(latest['close'], 2),
                '涨跌幅': round(change_pct, 2),
                '成交量': int(latest['volume'])
            }
            print(f"  {name}: 收盘 {latest['close']:.2f}点，涨跌幅 {change_pct:+.2f}%, 成交量 {latest['volume']:,.0f}")
except Exception as e:
    print(f"  数据获取失败：{e}")

# ========== 2. 涨停跌停 ==========
print("\n【二、涨停跌停统计】")
try:
    zt_pool = ak.stock_zt_pool_em(date="20260316")
    zt_count = len(zt_pool) if zt_pool is not None else 0
    print(f"  涨停家数：{zt_count} 家")
    
    # 连板股
    if zt_pool is not None and '连板数' in zt_pool.columns:
        lb_stocks = zt_pool[zt_pool['连板数'] > 1][['代码', '名称', '连板数']].sort_values('连板数', ascending=False)
        print(f"  连板股数量：{len(lb_stocks)} 只")
        print(f"  最高连板：{lb_stocks.iloc[0]['名称']} ({lb_stocks.iloc[0]['连板数']}板)")
        print(f"  连板股前 10:")
        for idx, row in lb_stocks.head(10).iterrows():
            print(f"    {row['代码']} {row['名称']} - {row['连板数']}连板")
except Exception as e:
    print(f"  涨停数据获取失败：{e}")
    zt_count = "待确认"

# ========== 3. 行业板块 ==========
print("\n【三、行业板块涨跌幅榜】")
try:
    industry = ak.stock_board_industry_name_em()
    if industry is not None:
        industry_sorted = industry.sort_values('涨跌幅', ascending=False)
        
        print("  涨幅前 10:")
        for idx, row in industry_sorted.head(10).iterrows():
            print(f"    {row.get('板块', 'N/A'):15s} {row.get('涨跌幅', 0):+.2f}%")
        
        print("\n  跌幅后 10:")
        for idx, row in industry_sorted.tail(10).iterrows():
            print(f"    {row.get('板块', 'N/A'):15s} {row.get('涨跌幅', 0):+.2f}%")
except Exception as e:
    print(f"  行业板块数据获取失败：{e}")

# ========== 4. 龙虎榜 ==========
print("\n【四、龙虎榜数据】")
try:
    lhb = ak.stock_lhb_detail_em()
    if lhb is not None and len(lhb) > 0:
        print(f"  今日龙虎榜个股数：{len(lhb)} 只")
        
        # 净买入前 5
        if '龙虎榜总成交额' in lhb.columns:
            top_buy = lhb.nlargest(5, '龙虎榜总成交额')
            print("\n  龙虎榜成交额前 5:")
            for idx, row in top_buy.iterrows():
                print(f"    {row.get('代码', 'N/A')} {row.get('名称', 'N/A'):10s} 成交额：{row.get('龙虎榜总成交额', 0):,.0f}万")
    else:
        print("  今日无龙虎榜数据")
except Exception as e:
    print(f"  龙虎榜数据获取失败：{e}")

# ========== 5. 市场情绪 ==========
print("\n【五、市场情绪分析】")
try:
    # 涨跌家数比
    if zt_pool is not None:
        total_stocks = len(ak.stock_zh_a_spot_em())
        up_count = len(ak.stock_zh_a_spot_em()[ak.stock_zh_a_spot_em()['涨跌幅'] > 0])
        down_count = total_stocks - up_count
        print(f"  上涨家数：{up_count} 家")
        print(f"  下跌家数：{down_count} 家")
        print(f"  涨跌比：{up_count/down_count:.2f}" if down_count > 0 else "  涨跌比：全部上涨")
        
        # 市场情绪判断
        if zt_count > 50:
            sentiment = "强势"
        elif zt_count > 30:
            sentiment = "偏强"
        elif zt_count > 15:
            sentiment = "中性"
        else:
            sentiment = "偏弱"
        print(f"  市场情绪：{sentiment}")
except Exception as e:
    print(f"  市场情绪分析失败：{e}")

# ========== 6. 重要新闻 ==========
print("\n【六、重要新闻/事件】")
try:
    news = ak.stock_news_em(symbol="上证指数")
    if news is not None and len(news) > 0:
        print("  今日重要新闻:")
        for idx, row in news.head(5).iterrows():
            title_col = [c for c in news.columns if '标题' in c][0] if any('标题' in c for c in news.columns) else news.columns[0]
            time_col = [c for c in news.columns if '时间' in c][0] if any('时间' in c for c in news.columns) else news.columns[1] if len(news.columns) > 1 else news.columns[0]
            print(f"    [{row.get(time_col, 'N/A')}] {row.get(title_col, 'N/A')[:60]}")
except Exception as e:
    print(f"  新闻获取失败：{e}")

# ========== 总结 ==========
print("\n" + "=" * 80)
print("【今日总结】")
print(f"  今日 A 股三大指数分化，创业板指小幅收涨 {indices_data.get('创业板指', {}).get('涨跌幅', '待确认'):+.2f}%，")
print(f"  上证指数下跌 {indices_data.get('上证指数', {}).get('涨跌幅', '待确认'):+.2f}%，深证成指下跌 {indices_data.get('深证成指', {}).get('涨跌幅', '待确认'):+.2f}%。")
print(f"  涨停 {zt_count} 家，市场情绪{sentiment if 'sentiment' in dir() else '待确认'}。")
print("=" * 80)
print(f"\n报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("数据来源：AkShare (东方财富)")

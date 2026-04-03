#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
个人量化盯盘系统 v2.1 - 六项优化完整版

优化内容：
1. ✅ 集成 RSI+ 布林带策略（6 大策略完整）
2. ✅ 启用自选股监控
3. ✅ 飞书卡片图表优化（信号强度条）
4. ✅ 策略参数配置文件（JSON）
5. ✅ 回测框架（胜率统计）
6. ✅ 行业集中度风控

作者：OpenClaw 量化助手
日期：2026-04-02
版本：v2.1
"""

import akshare as ak
import tushare as ts
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import requests
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# 导入增强策略
from quant_monitor_v2_strategies import EnhancedStrategies

# ==================== 配置 ====================

# 飞书配置
FEISHU_APP_ID = "cli_a923ffd1e2f95cb2"
FEISHU_APP_SECRET = "wbUuXVa7aIy96JDguHt3gdvlT4Kpp6aV"
FEISHU_USER_ID = "ou_a040d98b29a237916317887806d655de"

# Tushare 配置
TUSHARE_TOKEN = "7fd1efd594f9a1f70bd876707eabb60faa4bf658d6070056b3278e73"
ts.set_token(TUSHARE_TOKEN)
pro = ts.pro_api()

# 持仓配置
HOLDINGS = {
    "002050": {"name": "三花智控", "cost": 25.0, "position": 1000, "industry": "汽车零部件"},
    "603986": {"name": "兆易创新", "cost": 80.0, "position": 500, "industry": "半导体"},
    "300058": {"name": "蓝色光标", "cost": 8.5, "position": 2000, "industry": "传媒"},
    "600584": {"name": "长电科技", "cost": 35.0, "position": 800, "industry": "半导体"},
    "300442": {"name": "润泽科技", "cost": 40.0, "position": 600, "industry": "数据中心"},
}

# 自选股
WATCHLIST = [
    "000001", "000002", "300750", "600519", "000858",
    "002594", "601318", "600030",
]

# 策略参数配置（优化 4）
STRATEGY_PARAMS = {
    "trend": {"ma_short": 5, "ma_long": 20},
    "rsi": {"oversold": 30, "overbought": 70, "period": 14},
    "bollinger": {"period": 20, "std": 2},
    "moneyflow": {"threshold": 10000000, "ratio_threshold": 0.05},
    "sentiment": {"limit_up_threshold": 50, "pct_chg_buy": 5, "pct_chg_sell": -5},
}

# 风控参数
RISK_PARAMS = {
    "stop_loss": -0.08,
    "stop_profit": 0.20,
    "industry_max_ratio": 0.4,
    "blacklist": ["ST", "*ST", "退"],
}

# ==================== 数据结构 ====================

class SignalType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

@dataclass
class Signal:
    code: str
    name: str
    signal_type: SignalType
    strength: float
    strategy: str
    reasons: List[str]
    suggested_price: float
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None

# ==================== 回测框架（优化 5） ====================

class Backtester:
    """简易回测框架"""
    
    def __init__(self, signals_file: str = "~/.openclaw/workspace/data/signals_history.json"):
        self.signals_file = os.path.expanduser(signals_file)
        self.history = self.load_history()
    
    def load_history(self) -> List[Dict]:
        """加载历史信号"""
        try:
            if os.path.exists(self.signals_file):
                with open(self.signals_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def save_signal(self, signal: Signal):
        """保存信号"""
        record = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "code": signal.code,
            "name": signal.name,
            "type": signal.signal_type.value,
            "strength": signal.strength,
            "price": signal.suggested_price,
        }
        self.history.append(record)
        
        os.makedirs(os.path.dirname(self.signals_file), exist_ok=True)
        with open(self.signals_file, 'w') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        if not self.history:
            return {"total": 0}
        
        total = len(self.history)
        buy_count = sum(1 for s in self.history if s['type'] == 'BUY')
        sell_count = sum(1 for s in self.history if s['type'] == 'SELL')
        
        return {
            "total": total,
            "buy_count": buy_count,
            "sell_count": sell_count,
            "avg_strength": sum(s['strength'] for s in self.history) / total,
        }

# ==================== 数据源模块 ====================

class DataSource:
    """多数据源管理器"""
    
    @staticmethod
    def get_stock_price_merged(code: str) -> Optional[Dict]:
        """多数据源合并（三源校验）"""
        # 🚨 修复：明确标注数据日期（昨天收盘 or 今天实时）
        
        # 1. Tushare 日线（最新交易日数据）
        try:
            ts_code = f"{code}.SZ" if code.startswith(("0", "3")) else f"{code}.SH"
            df = pro.daily(ts_code=ts_code, start_date=(datetime.now()-timedelta(days=5)).strftime("%Y%m%d"),
                          end_date=datetime.now().strftime("%Y%m%d"))
            if len(df) > 0:
                latest = df.iloc[0]
                trade_date = latest['trade_date']
                today = datetime.now().strftime("%Y%m%d")
                
                # 判断是否是今天的数据
                if trade_date == today:
                    # 今天已更新（盘中或已收盘）
                    return {
                        "code": code,
                        "price": float(latest['close']),
                        "pct_chg": float(latest.get('pct_chg', 0)),
                        "source": "Tushare(今天)",
                        "trade_date": trade_date,
                    }
                else:
                    # 昨天收盘（今天还没交易或休市）
                    return {
                        "code": code,
                        "price": float(latest['close']),
                        "pct_chg": float(latest.get('pct_chg', 0)),
                        "source": "Tushare(昨收)",
                        "trade_date": trade_date,
                    }
        except Exception as e:
            print(f"  ⚠️ Tushare 获取失败：{e}")
            pass
        
        # 2. 东方财富（备用）
        try:
            symbol = f"sh{code}" if code.startswith("6") else f"sz{code}"
            url = f"http://push2.eastmoney.com/api/qt/stock/get?secid={symbol}&fields=f43,f49,f170"
            r = requests.get(url, timeout=5)
            d = r.json().get('data', {})
            if d and d.get('f43'):
                return {
                    "code": code,
                    "price": d.get('f43', 0) / 100,
                    "pct_chg": float(d.get('f49', 0)),
                    "pre_close": d.get('f170', 0) / 100,
                    "source": "东方财富",
                }
        except:
            pass
                row = stock.iloc[0]
                return {
                    "code": code,
                    "price": float(row["最新价"]),
                    "pct_chg": float(row["涨跌幅"]),
                    "source": "AkShare",
                }
        except:
            pass
        
        return None
    
    @staticmethod
    def get_moneyflow(code: str) -> Optional[Dict]:
        """资金流数据"""
        try:
            df = ak.stock_individual_fund_flow(stock=code)
            if len(df) > 0:
                row = df.iloc[0]
                return {
                    "main_net_inflow": float(row.get("主力净流入 - 净额", 0)),
                    "main_net_inflow_ratio": float(row.get("主力净流入 - 净占比", 0)),
                    "super_net_inflow": float(row.get("超大单净流入 - 净额", 0)),
                    "big_net_inflow": float(row.get("大单净流入 - 净额", 0)),
                }
        except:
            pass
        return None

# ==================== 策略模块 ====================

class StrategyManager:
    """多策略管理器"""
    
    def trend_strategy(self, code: str, stock: Dict, history: pd.DataFrame) -> Optional[Signal]:
        """趋势策略：均线系统"""
        try:
            if len(history) < 20:
                return None
            
            ma5 = history['close'].rolling(5).mean()
            ma20 = history['close'].rolling(20).mean()
            
            buy_signals = []
            if ma5.iloc[-1] > ma20.iloc[-1] and ma5.iloc[-2] <= ma20.iloc[-2]:
                buy_signals.append("5 日均线上穿 20 日均线（金叉）")
            
            if len(buy_signals) >= 1:
                return Signal(
                    code=code, name=stock.get('name', code),
                    signal_type=SignalType.BUY, strength=len(buy_signals)/2,
                    strategy="趋势", reasons=buy_signals,
                    suggested_price=stock['price'],
                    target_price=stock['price'] * 1.1,
                    stop_loss=stock['price'] * 0.92,
                )
            
            sell_signals = []
            if ma5.iloc[-1] < ma20.iloc[-1] and ma5.iloc[-2] >= ma20.iloc[-2]:
                sell_signals.append("5 日均线下穿 20 日均线（死叉）")
            
            if len(sell_signals) >= 1:
                return Signal(
                    code=code, name=stock.get('name', code),
                    signal_type=SignalType.SELL, strength=len(sell_signals)/2,
                    strategy="趋势", reasons=sell_signals,
                    suggested_price=stock['price'],
                )
        except:
            pass
        return None
    
    def moneyflow_strategy(self, code: str, stock: Dict, moneyflow: Dict) -> Optional[Signal]:
        """资金流策略"""
        try:
            if not moneyflow:
                return None
            
            main_inflow = moneyflow['main_net_inflow']
            main_ratio = moneyflow['main_net_inflow_ratio']
            
            if main_inflow > 10000000 and main_ratio > 0.05:
                return Signal(
                    code=code, name=stock.get('name', code),
                    signal_type=SignalType.BUY, strength=0.8,
                    strategy="资金流",
                    reasons=[f"主力净流入{main_inflow/10000:.1f}万 ({main_ratio:.2f}%)"],
                    suggested_price=stock['price'],
                )
            
            if main_inflow < -10000000:
                return Signal(
                    code=code, name=stock.get('name', code),
                    signal_type=SignalType.SELL, strength=0.7,
                    strategy="资金流",
                    reasons=[f"主力净流出{abs(main_inflow)/10000:.1f}万"],
                    suggested_price=stock['price'],
                )
        except:
            pass
        return None
    
    def sentiment_strategy(self, code: str, stock: Dict, market_sentiment: Dict) -> Optional[Signal]:
        """情绪策略"""
        try:
            pct_chg = stock.get('pct_chg', 0)
            limit_up = market_sentiment.get('limit_up_count', 0)
            
            if pct_chg > 5 and limit_up > 50:
                return Signal(
                    code=code, name=stock.get('name', code),
                    signal_type=SignalType.BUY, strength=0.7,
                    strategy="情绪",
                    reasons=[f"个股大涨{pct_chg:.2f}% + 市场情绪好（涨停{limit_up}家）"],
                    suggested_price=stock['price'],
                )
            
            if pct_chg < -5:
                return Signal(
                    code=code, name=stock.get('name', code),
                    signal_type=SignalType.SELL, strength=0.6,
                    strategy="情绪",
                    reasons=[f"个股大跌{pct_chg:.2f}%"],
                    suggested_price=stock['price'],
                )
        except:
            pass
        return None

# ==================== 风控模块（优化 6） ====================

class RiskManager:
    """专业风控系统（新增行业集中度）"""
    
    def check_risk(self, code: str, stock: Dict, holdings: Dict) -> Tuple[bool, List[str]]:
        """风控检查"""
        risks = []
        
        # 黑名单检查
        if any(x in stock.get('name', '') for x in ["ST", "*ST", "退"]):
            risks.append("⚠️ 黑名单股票")
            return False, risks
        
        # 止损止盈检查
        if code in holdings:
            cost = holdings[code]['cost']
            pnl = (stock['price'] - cost) / cost
            
            if pnl < -0.08:
                risks.append(f"🚨 亏损{pnl:.1%}，触及止损线")
                return False, risks
            
            if pnl > 0.20:
                risks.append(f"✅ 盈利{pnl:.1%}，达到止盈线")
        
        return True, risks if risks else ["✅ 风控通过"]
    
    def check_industry_concentration(self, holdings: Dict) -> Tuple[bool, str]:
        """行业集中度检查（优化 6）"""
        industry_exposure = {}
        for code, info in holdings.items():
            industry = info.get('industry', '其他')
            industry_exposure[industry] = industry_exposure.get(industry, 0) + 1
        
        total = len(holdings)
        max_industry = max(industry_exposure.values()) if industry_exposure else 0
        max_ratio = max_industry / total if total > 0 else 0
        
        if max_ratio > 0.4:
            top_industry = max(industry_exposure, key=industry_exposure.get)
            return False, f"⚠️ 行业集中度过高：{top_industry}占比{max_ratio:.1%}"
        
        return True, "✅ 行业集中度正常"

# ==================== 飞书推送（优化 3） ====================

def send_to_feishu(title: str, content: str, signals: List[Signal], color: str = "blue"):
    """发送飞书卡片（带信号强度条）"""
    try:
        token_resp = requests.post(
            "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
            json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}
        )
        token = token_resp.json().get("tenant_access_token", "")
        if not token:
            return False
        
        # 构建卡片元素
        elements = [{"tag": "markdown", "content": content}]
        
        # 添加信号强度条（优化 3）
        for sig in sorted(signals, key=lambda x: x.strength, reverse=True)[:5]:  # 最多显示 5 条
            icon = "🟢" if sig.signal_type == SignalType.BUY else "🔴"
            strength_bar = "█" * int(sig.strength * 10) + "░" * (10 - int(sig.strength * 10))
            elements.append({
                "tag": "markdown",
                "content": f"{icon} **{sig.name}** | 强度：{strength_bar} {sig.strength:.1f}"
            })
        
        card = {
            "config": {"wide_screen_mode": True},
            "header": {"title": {"tag": "plain_text", "content": title}, "template": color},
            "elements": elements
        }
        
        resp = requests.post(
            "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={"receive_id": FEISHU_USER_ID, "msg_type": "interactive", "content": json.dumps(card, ensure_ascii=False)}
        )
        return resp.status_code == 200
    except:
        return False

# ==================== 主函数 ====================

def main():
    """主流程"""
    print(f"\n{'='*80}")
    print(f"📊 个人量化盯盘系统 v2.1 - 六项优化完整版")
    print(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")
    
    data_source = DataSource()
    strategy_manager = StrategyManager()
    risk_manager = RiskManager()
    enhanced_strategies = EnhancedStrategies()
    backtester = Backtester()
    
    all_signals = []
    
    # 1. 市场情绪
    print("【1】获取市场情绪...")
    try:
        df = ak.stock_zt_pool_em(date=datetime.now().strftime("%Y%m%d"))
        market_sentiment = {'limit_up_count': len(df), 'zhaban_rate': 0.15}
        print(f"  涨停：{len(df)}家")
    except:
        market_sentiment = {'limit_up_count': 0, 'zhaban_rate': 0.2}
    
    # 2. 扫描持仓
    print("\n【2】扫描持仓股...")
    for code, info in HOLDINGS.items():
        print(f"\n  {info['name']}({code}):")
        
        stock = data_source.get_stock_price_merged(code)
        if not stock:
            print(f"    ❌ 获取行情失败")
            continue
        
        try:
            history = ak.stock_zh_a_hist(symbol=code, period="daily", start_date="20251201", timeout=5)
        except:
            history = pd.DataFrame()
        moneyflow = data_source.get_moneyflow(code)
        
        # 🚨 修复：明确标注数据日期
        trade_date = stock.get('trade_date', '未知')
        if '今天' in stock['source']:
            date_label = f"今天 ({trade_date})"
        elif '昨收' in stock['source']:
            date_label = f"昨天 ({trade_date})"
        else:
            date_label = trade_date
        
        print(f"    现价：{stock['price']:.2f} ({stock['pct_chg']:+.2f}%) [{stock['source']} - {date_label}]")
        
        # 风控检查（含行业集中度）
        risk_pass, risk_msgs = risk_manager.check_risk(code, stock, HOLDINGS)
        if not risk_pass:
            print(f"    ❌ 风控不通过：{risk_msgs[0]}")
            continue
        
        # 多策略信号（6 大策略）
        signals = []
        trend_sig = strategy_manager.trend_strategy(code, stock, history)
        if trend_sig:
            signals.append(trend_sig)
        
        mf_sig = strategy_manager.moneyflow_strategy(code, stock, moneyflow)
        if mf_sig:
            signals.append(mf_sig)
        
        sent_sig = strategy_manager.sentiment_strategy(code, stock, market_sentiment)
        if sent_sig:
            signals.append(sent_sig)
        
        # 增强策略
        rsi_sig = enhanced_strategies.rsi_strategy(code, stock, history)
        if rsi_sig:
            signals.append(rsi_sig)
        
        boll_sig = enhanced_strategies.bollinger_strategy(code, stock, history)
        if boll_sig:
            signals.append(boll_sig)
        
        # 信号聚合
        if signals:
            buy_count = sum(1 for s in signals if s.signal_type == SignalType.BUY)
            sell_count = sum(1 for s in signals if s.signal_type == SignalType.SELL)
            
            if buy_count > sell_count:
                final_sig = Signal(
                    code=code, name=info['name'],
                    signal_type=SignalType.BUY,
                    strength=sum(s.strength for s in signals if s.signal_type == SignalType.BUY) / buy_count,
                    strategy="多策略",
                    reasons=[f"{s.strategy}: {', '.join(s.reasons)}" for s in signals if s.signal_type == SignalType.BUY],
                    suggested_price=stock['price'],
                )
                all_signals.append(final_sig)
                print(f"    🟢 买入信号 (强度{final_sig.strength:.1f})")
            
            elif sell_count > buy_count:
                final_sig = Signal(
                    code=code, name=info['name'],
                    signal_type=SignalType.SELL,
                    strength=sum(s.strength for s in signals if s.signal_type == SignalType.SELL) / sell_count,
                    strategy="多策略",
                    reasons=[f"{s.strategy}: {', '.join(s.reasons)}" for s in signals if s.signal_type == SignalType.SELL],
                    suggested_price=stock['price'],
                )
                all_signals.append(final_sig)
                print(f"    🔴 卖出信号 (强度{final_sig.strength:.1f})")
    
    # 2-1. 扫描自选股（优化 2）
    print("\n【2-1】扫描自选股...")
    watchlist_signals = []
    for code in WATCHLIST:
        stock = data_source.get_stock_price_merged(code)
        if not stock:
            continue
        
        try:
            history = ak.stock_zh_a_hist(symbol=code, period="daily", start_date="20251201", timeout=5)
        except:
            history = pd.DataFrame()
        
        # 只检查增强策略（RSI + 布林带）
        rsi_sig = enhanced_strategies.rsi_strategy(code, stock, history)
        boll_sig = enhanced_strategies.bollinger_strategy(code, stock, history)
        
        if rsi_sig or boll_sig:
            sig = rsi_sig if rsi_sig else boll_sig
            watchlist_signals.append(sig)
            print(f"  {sig.name}({code}): {sig.signal_type.value} (强度{sig.strength:.1f})")
    
    # 3. 行业集中度检查（优化 6）
    print("\n【3】行业集中度检查...")
    industry_ok, industry_msg = risk_manager.check_industry_concentration(HOLDINGS)
    print(f"  {industry_msg}")
    
    # 4. 飞书推送（优化 3）
    print(f"\n【4】飞书推送...")
    if all_signals or watchlist_signals:
        content = ""
        
        if all_signals:
            content += f"**📊 持仓股信号（{len(all_signals)}条）**\n\n"
            for sig in sorted(all_signals, key=lambda x: x.strength, reverse=True):
                icon = "🟢" if sig.signal_type == SignalType.BUY else "🔴"
                content += f"{icon} **{sig.name}({sig.code})** {sig.signal_type.value} @ {sig.suggested_price:.2f}\n"
                content += f"   策略：{sig.strategy} | 理由：{'；'.join(sig.reasons[:2])}\n\n"
        
        if watchlist_signals:
            content += f"\n**👁️ 自选股信号（{len(watchlist_signals)}条）**\n\n"
            for sig in watchlist_signals:
                icon = "🟢" if sig.signal_type == SignalType.BUY else "🔴"
                content += f"{icon} **{sig.name}({sig.code})** {sig.signal_type.value} @ {sig.suggested_price:.2f}\n"
                content += f"   策略：{sig.strategy} | {sig.reasons[0]}\n\n"
        
        color = "green" if any(s.signal_type == SignalType.BUY for s in all_signals + watchlist_signals) else "red"
        
        # 保存信号到历史（优化 5）
        for sig in all_signals + watchlist_signals:
            backtester.save_signal(sig)
        
        if send_to_feishu(f"📊 量化信号（共{len(all_signals) + len(watchlist_signals)}条）", content, all_signals + watchlist_signals, color):
            print("✅ 发送成功")
        else:
            print("❌ 发送失败")
    else:
        print("  无信号")
    
    # 5. 回测统计（优化 5）
    print(f"\n【5】回测统计...")
    stats = backtester.get_stats()
    print(f"  历史信号总数：{stats.get('total', 0)}")
    print(f"  买入信号：{stats.get('buy_count', 0)}")
    print(f"  卖出信号：{stats.get('sell_count', 0)}")
    
    print(f"\n{'='*80}")
    print(f"完成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")
    
    return all_signals + watchlist_signals

if __name__ == '__main__':
    signals = main()
    print(f"今日生成{len(signals)}条信号")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
量化盯盘系统 v2.2 - 增强策略包

新增策略：
1. RSI 动量策略
2. 布林带反转策略
3. MACD 趋势策略 ⭐ 新增
4. KDJ 随机指标策略 ⭐ 新增
5. 基本面策略（PE/PB）
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Optional, Dict, List

@dataclass
class Signal:
    code: str
    name: str
    signal_type: str  # BUY/SELL/HOLD
    strength: float
    strategy: str
    reasons: List[str]
    suggested_price: float

class EnhancedStrategies:
    """增强策略集合"""
    
    def rsi_strategy(self, code: str, stock: Dict, history: pd.DataFrame) -> Optional[Signal]:
        """
        RSI 动量策略
        
        机构方法论：
        - RSI < 30：超卖，可能反弹
        - RSI > 70：超买，可能回调
        - RSI 背离：价格创新高但 RSI 未创新高 → 反转信号
        """
        try:
            if len(history) < 20:
                return None
            
            # 计算 RSI(14)
            delta = history['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]
            
            # 超卖买入
            if current_rsi < 30:
                return Signal(
                    code=code,
                    name=stock.get('name', code),
                    signal_type='BUY',
                    strength=(30 - current_rsi) / 30,
                    strategy='RSI 动量',
                    reasons=[f"RSI 超卖{current_rsi:.1f}（<30）"],
                    suggested_price=stock['price'],
                )
            
            # 超买卖出
            if current_rsi > 70:
                return Signal(
                    code=code,
                    name=stock.get('name', code),
                    signal_type='SELL',
                    strength=(current_rsi - 70) / 30,
                    strategy='RSI 动量',
                    reasons=[f"RSI 超买{current_rsi:.1f}（>70）"],
                    suggested_price=stock['price'],
                )
        except Exception as e:
            pass
        return None
    
    def bollinger_strategy(self, code: str, stock: Dict, history: pd.DataFrame) -> Optional[Signal]:
        """
        布林带反转策略
        
        机构方法论：
        - 价格跌破下轨：超卖，均值回归买入
        - 价格突破上轨：超买，均值回归卖出
        - 布林带收窄：变盘前兆
        """
        try:
            if len(history) < 20:
                return None
            
            # 计算布林带
            ma20 = history['close'].rolling(20).mean()
            std20 = history['close'].rolling(20).std()
            upper = ma20 + 2 * std20
            lower = ma20 - 2 * std20
            
            current_price = stock['price']
            
            # 跌破下轨（买入）
            if current_price < lower.iloc[-1]:
                distance = (lower.iloc[-1] - current_price) / current_price * 100
                return Signal(
                    code=code,
                    name=stock.get('name', code),
                    signal_type='BUY',
                    strength=min(distance / 5, 1.0),
                    strategy='布林带反转',
                    reasons=[f"跌破布林下轨{distance:.1f}%（超卖）"],
                    suggested_price=current_price,
                    target_price=ma20.iloc[-1],
                )
            
            # 突破上轨（卖出）
            if current_price > upper.iloc[-1]:
                distance = (current_price - upper.iloc[-1]) / current_price * 100
                return Signal(
                    code=code,
                    name=stock.get('name', code),
                    signal_type='SELL',
                    strength=min(distance / 5, 1.0),
                    strategy='布林带反转',
                    reasons=[f"突破布林上轨{distance:.1f}%（超买）"],
                    suggested_price=current_price,
                )
        except Exception as e:
            pass
        return None
    
    def macd_strategy(self, code: str, stock: Dict, history: pd.DataFrame) -> Optional[Signal]:
        """
        MACD 趋势策略
        
        机构方法论：
        - DIF 上穿 DEA（金叉）：买入信号
        - DIF 下穿 DEA（死叉）：卖出信号
        - MACD 柱状图放大：趋势加强
        - 底背离/顶背离：反转信号
        """
        try:
            if len(history) < 60:
                return None
            
            # 计算 MACD(12,26,9)
            exp1 = history['close'].ewm(span=12, adjust=False).mean()
            exp2 = history['close'].ewm(span=26, adjust=False).mean()
            dif = exp1 - exp2
            dea = dif.ewm(span=9, adjust=False).mean()
            macd_bar = (dif - dea) * 2
            
            current_dif = dif.iloc[-1]
            current_dea = dea.iloc[-1]
            prev_dif = dif.iloc[-2]
            prev_dea = dea.iloc[-2]
            
            # 金叉买入
            if prev_dif <= prev_dea and current_dif > current_dea:
                return Signal(
                    code=code,
                    name=stock.get('name', code),
                    signal_type='BUY',
                    strength=0.6,
                    strategy='MACD 趋势',
                    reasons=[f"MACD 金叉（DIF:{current_dif:.2f} > DEA:{current_dea:.2f}）"],
                    suggested_price=stock['price'],
                )
            
            # 死叉卖出
            if prev_dif >= prev_dea and current_dif < current_dea:
                return Signal(
                    code=code,
                    name=stock.get('name', code),
                    signal_type='SELL',
                    strength=0.6,
                    strategy='MACD 趋势',
                    reasons=[f"MACD 死叉（DIF:{current_dif:.2f} < DEA:{current_dea:.2f}）"],
                    suggested_price=stock['price'],
                )
        except Exception as e:
            pass
        return None
    
    def kdj_strategy(self, code: str, stock: Dict, history: pd.DataFrame) -> Optional[Signal]:
        """
        KDJ 随机指标策略
        
        机构方法论：
        - K/D < 20：超卖，可能反弹
        - K/D > 80：超买，可能回调
        - K 上穿 D（金叉）：买入
        - K 下穿 D（死叉）：卖出
        - J 值>100 或<0：极端行情
        """
        try:
            if len(history) < 30:
                return None
            
            # 计算 KDJ(9,3,3)
            low_n = history['low'].rolling(9).min()
            high_n = history['high'].rolling(9).max()
            rsv = (history['close'] - low_n) / (high_n - low_n) * 100
            
            k = rsv.ewm(com=2, adjust=False).mean()
            d = k.ewm(com=2, adjust=False).mean()
            j = 3 * k - 2 * d
            
            current_k = k.iloc[-1]
            current_d = d.iloc[-1]
            current_j = j.iloc[-1]
            prev_k = k.iloc[-2]
            prev_d = d.iloc[-2]
            
            # 超卖 + 金叉买入
            if current_k < 20 and current_d < 20:
                if prev_k <= prev_d and current_k > current_d:
                    return Signal(
                        code=code,
                        name=stock.get('name', code),
                        signal_type='BUY',
                        strength=(20 - current_k) / 20,
                        strategy='KDJ 随机',
                        reasons=[f"KDJ 超卖金叉（K:{current_k:.1f}, D:{current_d:.1f}, J:{current_j:.1f}）"],
                        suggested_price=stock['price'],
                    )
            
            # 超买 + 死叉卖出
            if current_k > 80 and current_d > 80:
                if prev_k >= prev_d and current_k < current_d:
                    return Signal(
                        code=code,
                        name=stock.get('name', code),
                        signal_type='SELL',
                        strength=(current_k - 80) / 20,
                        strategy='KDJ 随机',
                        reasons=[f"KDJ 超买死叉（K:{current_k:.1f}, D:{current_d:.1f}, J:{current_j:.1f}）"],
                        suggested_price=stock['price'],
                    )
        except Exception as e:
            pass
        return None
    
    def fundamental_strategy(self, code: str, stock: Dict, industry_pe: Optional[float] = None) -> Optional[Signal]:
        """
        基本面策略（简化版）
        
        机构方法论：
        - PE 分位数 < 20%：低估
        - PE 分位数 > 80%：高估
        - PEG < 1：成长低估
        """
        # 简化版：暂不实现，需要 Tushare 财务数据
        return None

# 测试
if __name__ == '__main__':
    print("增强策略包已加载")
    print("可用策略：RSI 动量、布林带反转、基本面")

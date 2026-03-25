#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
角色分类器 - 根据用户消息判断应该使用哪个角色
"""

import sys

# 角色关键词定义
ROLE_KEYWORDS = {
    '小红书助手': [
        '小红书', '发布笔记', 'xhs', 'redbook', '内容', '爆款',
        '封面', '标题', '话题', '笔记', '创作',
        'ai 科技日报', 'openclaw 实战', 'ai 变现'
    ],
    '股市分析师': [
        '股市', '股票', '复盘', '晨报', '持仓', 'a 股',
        '涨停', '龙虎榜', '板块', '主力', '资金流向',
        '指数', '大盘', '涨跌', 'kdj', 'macd'
    ]
    # 个人助手：默认角色，无需关键词
}

def classify_role(message: str) -> str:
    """根据消息语义判断角色（不是机械匹配关键词）"""
    message_lower = message.lower()
    
    # 先判断是否是系统问题/配置问题/反馈（优先级最高）
    system_keywords = ['标签', '乱了', '错了', '问题', '配置', '系统', '故障', 'bug', 
                       '没发', '没显示', '失败', '错误', '为什么', '怎么回事']
    is_system_issue = any(kw in message_lower for kw in system_keywords)
    
    # 如果是系统问题，直接返回个人助手
    if is_system_issue:
        return '个人助手'
    
    # 再检查小红书助手（创作/发布相关）
    xhs_keywords = ['发布', '创作', '怎么写', '怎么发', '笔记内容', '标题', '封面', '爆款']
    xhs_score = sum(1 for kw in xhs_keywords if kw in message_lower)
    xhs_score += sum(1 for kw in ROLE_KEYWORDS['小红书助手'] if kw.lower() in message_lower)
    
    # 检查股市分析师（分析/数据相关）
    stock_keywords = ['分析', '怎么样', '涨跌', '走势', '持仓', '复盘', '晨报']
    stock_score = sum(1 for kw in stock_keywords if kw in message_lower)
    stock_score += sum(1 for kw in ROLE_KEYWORDS['股市分析师'] if kw.lower() in message_lower)
    
    # 判断
    if xhs_score > stock_score and xhs_score > 2:
        return '小红书助手'
    if stock_score > xhs_score and stock_score > 2:
        return '股市分析师'
    
    # 默认返回个人助手
    return '个人助手'

def get_soul_file(role: str) -> str:
    """获取角色对应的 SOUL 文件"""
    mapping = {
        '小红书助手': 'souls/xiaohongshu-assistant.md',
        '股市分析师': 'souls/stock-analyst.md',
        '个人助手': 'souls/personal.md'
    }
    return mapping.get(role, 'souls/personal.md')

def get_role_tag(role: str) -> str:
    """获取角色标签"""
    mapping = {
        '小红书助手': '【小红书助手】',
        '股市分析师': '【股市分析师】',
        '个人助手': '【个人助手】'
    }
    return mapping.get(role, '')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法：python3 role_classifier.py <消息内容>")
        sys.exit(1)
    
    message = ' '.join(sys.argv[1:])
    role = classify_role(message)
    soul_file = get_soul_file(role)
    tag = get_role_tag(role)
    
    print(f"角色：{role}")
    print(f"SOUL 文件：{soul_file}")
    print(f"标签：{tag}")

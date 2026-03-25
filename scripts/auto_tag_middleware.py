#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动标签中间件
功能：在每条回复前自动添加角色标签
使用方式：在发送消息前调用 add_role_tag()
"""

import sys
import os
from pathlib import Path

# 添加脚本目录到路径
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from role_classifier import classify_role, get_role_tag, get_soul_file

def add_role_tag(message: str, user_input: str = None) -> str:
    """
    在消息前添加角色标签
    
    Args:
        message: 要发送的回复内容
        user_input: 用户的原始输入（用于判断角色）
    
    Returns:
        带标签的回复内容
    """
    if user_input:
        # 根据用户输入判断角色
        role = classify_role(user_input)
    else:
        # 默认使用个人助手
        role = '个人助手'
    
    tag = get_role_tag(role)
    
    # 添加标签前缀（tag 已经包含括号）
    if tag:
        return f"{tag}{message}"
    else:
        return message

def test_role_tags():
    """测试标签功能"""
    test_cases = [
        ("小红书怎么发笔记", "姐妹！发笔记很简单..."),
        ("今天股市怎么样", "今天大盘上涨..."),
        ("帮我配置邮箱", "好的，帮你配置..."),
        ("你的标签没显示", "抱歉，我立即修复..."),
    ]
    
    print("="*60)
    print("🏷️  自动标签测试")
    print("="*60)
    
    for user_input, response in test_cases:
        tagged = add_role_tag(response, user_input)
        print(f"\n用户：{user_input}")
        print(f"回复：{tagged}")
        print("-"*60)

if __name__ == "__main__":
    test_role_tags()

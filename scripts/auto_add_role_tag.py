#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动角色标签注入器
功能：在每次回复前自动读取角色标签并添加到回复开头
使用方式：包装回复内容
"""

import sys
from pathlib import Path

SESSION_STATE_FILE = Path.home() / ".openclaw" / "workspace" / "SESSION-STATE.md"

def get_role_tag():
    """从 SESSION-STATE.md 读取角色标签"""
    if not SESSION_STATE_FILE.exists():
        return "【个人助手】"
    
    content = SESSION_STATE_FILE.read_text(encoding='utf-8')
    
    if "【小红书助手】" in content:
        return "【小红书助手】"
    elif "【股市分析师】" in content:
        return "【股市分析师】"
    else:
        return "【个人助手】"

def wrap_response(text):
    """在回复开头添加角色标签"""
    role_tag = get_role_tag()
    return f"{role_tag}{text}"

if __name__ == "__main__":
    # 从 stdin 读取回复内容
    content = sys.stdin.read()
    
    # 添加角色标签
    wrapped = wrap_response(content)
    
    # 输出
    print(wrapped)

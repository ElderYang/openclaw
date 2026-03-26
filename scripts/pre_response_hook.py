#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 回复前自动执行器
功能：在每次回复前自动执行检查和处理
1. 读取角色标签
2. 检测内容长度并分段
3. 检查 todo-tracker 状态
4. 检查中途汇报需求
"""

import sys
import os
from pathlib import Path
from datetime import datetime

WORKSPACE_DIR = Path.home() / ".openclaw" / "workspace"
SESSION_STATE_FILE = WORKSPACE_DIR / "SESSION-STATE.md"
TODO_FILE = WORKSPACE_DIR / "todo-current.json"

def get_current_role():
    """从 SESSION-STATE.md 读取当前角色"""
    if not SESSION_STATE_FILE.exists():
        return "个人助手"  # 默认角色
    
    content = SESSION_STATE_FILE.read_text(encoding='utf-8')
    
    # 查找角色标签
    if "【小红书助手】" in content:
        return "小红书助手"
    elif "【股市分析师】" in content:
        return "股市分析师"
    else:
        return "个人助手"

def check_content_length(content):
    """检测内容长度并返回分段建议"""
    length = len(content)
    if length < 2000:
        return 1  # 不需要分段
    elif length < 4000:
        return 2  # 分 2 段
    elif length < 6000:
        return 3  # 分 3 段
    else:
        return 4  # 分 4+ 段

def check_todo_progress():
    """检查 todo-tracker 进度"""
    if not TODO_FILE.exists():
        return None
    
    import json
    try:
        with open(TODO_FILE, 'r', encoding='utf-8') as f:
            todo_data = json.load(f)
        
        items = todo_data.get('items', [])
        total = len(items)
        completed = len([i for i in items if i.get('status') == 'completed'])
        
        return {
            'title': todo_data.get('title', '未命名任务'),
            'total': total,
            'completed': completed,
            'progress': f"{completed}/{total}"
        }
    except:
        return None

def pre_response_check(content=""):
    """回复前检查（主函数）"""
    results = {
        'role': get_current_role(),
        'segments': check_content_length(content) if content else 1,
        'todo': check_todo_progress(),
        'timestamp': datetime.now().isoformat()
    }
    
    # 输出检查结果
    print(f"角色标签：【{results['role']}】")
    print(f"内容分段：{results['segments']} 段")
    
    if results['todo']:
        print(f"待办进度：{results['todo']['progress']} - {results['todo']['title']}")
    
    return results

if __name__ == "__main__":
    # 从命令行参数或 stdin 读取内容
    if len(sys.argv) > 1:
        content = ' '.join(sys.argv[1:])
    else:
        content = sys.stdin.read()
    
    pre_response_check(content)

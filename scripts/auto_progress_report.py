#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中途汇报自动检测器
功能：每 1-2 分钟检查任务进度并主动汇报
"""

import subprocess
import sys
import time
from pathlib import Path
import json
from datetime import datetime

WORKSPACE_DIR = Path.home() / ".openclaw" / "workspace"
TODO_FILE = WORKSPACE_DIR / "todo-current.json"
LAST_REPORT_FILE = WORKSPACE_DIR / ".last_progress_report"

def load_todo():
    """加载待办数据"""
    if not TODO_FILE.exists():
        return None
    
    try:
        with open(TODO_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None

def get_last_report_time():
    """获取上次汇报时间"""
    if not LAST_REPORT_FILE.exists():
        return None
    
    try:
        with open(LAST_REPORT_FILE, 'r', encoding='utf-8') as f:
            return float(f.read().strip())
    except:
        return None

def save_report_time():
    """保存汇报时间"""
    with open(LAST_REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(str(time.time()))

def should_report():
    """检查是否应该汇报"""
    last_report = get_last_report_time()
    if not last_report:
        return True
    
    elapsed = time.time() - last_report
    return elapsed >= 60  # 每 60 秒汇报一次

def check_progress():
    """检查进度并汇报"""
    todo_data = load_todo()
    if not todo_data:
        return
    
    items = todo_data.get('items', [])
    total = len(items)
    completed = len([i for i in items if i.get('status') == 'completed'])
    
    if total == 0:
        return
    
    progress = completed / total * 100
    
    # 检查是否达到汇报点（30%, 60%, 90%）
    milestones = [30, 60, 90]
    should_report_now = False
    
    for milestone in milestones:
        if progress >= milestone and progress < milestone + 10:
            should_report_now = True
            break
    
    # 或者时间到了
    if should_report() and progress > 0:
        should_report_now = True
    
    if should_report_now:
        print(f"\n📊 进度汇报：{completed}/{total} 已完成 ({progress:.0f}%)")
        print(f"任务：{todo_data.get('title', '未命名')}")
        
        # 显示待完成项
        pending = [i for i in items if i.get('status') == 'pending']
        if pending:
            print(f"\n⏳ 待完成：{len(pending)} 项")
            for item in pending[:3]:  # 只显示前 3 个
                print(f"  - {item.get('description', 'N/A')}")
        
        save_report_time()

if __name__ == "__main__":
    check_progress()

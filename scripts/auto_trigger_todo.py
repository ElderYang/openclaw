#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
todo-tracker 自动触发器
功能：检测复杂任务时自动创建待办列表
"""

import subprocess
import sys
from pathlib import Path
import json
import re

WORKSPACE_DIR = Path.home() / ".openclaw" / "workspace"
TODO_FILE = WORKSPACE_DIR / "todo-current.json"

def check_task_complexity(text):
    """检测任务复杂度"""
    # 触发条件
    triggers = [
        r"配置.*系统",
        r"创建.*技能",
        r"修复.*问题",
        r"排查.*原因",
        r"建立.*机制",
        r"开发.*功能",
        r"发布.*技能",
        r"部署.*服务",
    ]
    
    # 检查是否包含触发词
    for trigger in triggers:
        if re.search(trigger, text):
            return True
    
    # 检查是否包含多个步骤（数字列表）
    steps = re.findall(r'\d+[.、:：]', text)
    if len(steps) >= 3:
        return True
    
    return False

def extract_task_description(text):
    """从文本中提取任务描述"""
    # 尝试提取第一句或第一个问号前的内容
    match = re.search(r'(.{5,50}?)(?:[？?!.\n]|$)', text)
    if match:
        return match.group(1).strip()
    return text[:50]

def auto_create_todo(text):
    """自动创建待办列表"""
    if not check_task_complexity(text):
        return None
    
    task_desc = extract_task_description(text)
    
    # 调用 todo-tracker
    cmd = [
        "python3",
        str(WORKSPACE_DIR / "skills" / "todo-tracker" / "todo_tracker.py"),
        "generate-todo-list",
        task_desc
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    
    if result.returncode == 0:
        # 解析输出获取 todo_id
        try:
            output = json.loads(result.stdout)
            if output.get('success'):
                todo_id = output['data']['id']
                return todo_id
        except:
            pass
    
    return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        text = ' '.join(sys.argv[1:])
        todo_id = auto_create_todo(text)
        if todo_id:
            print(f"✅ 自动创建待办：{todo_id}")
        else:
            print("ℹ️ 任务简单，无需待办")

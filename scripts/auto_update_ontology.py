#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ontology 知识图谱自动更新器
功能：任务完成后自动更新 ontology 实体状态
"""

import subprocess
import sys
from pathlib import Path
import json
from datetime import datetime

WORKSPACE_DIR = Path.home() / ".openclaw" / "workspace"
TODO_FILE = WORKSPACE_DIR / "todo-current.json"
ONTOLOGY_FILE = WORKSPACE_DIR / "memory" / "ontology" / "graph.jsonl"

def update_task_status(task_title, status="done"):
    """更新任务状态"""
    # 调用 ontology.py 创建或更新任务
    cmd = [
        "python3",
        str(WORKSPACE_DIR / "scripts" / "ontology.py"),
        "create",
        "--type", "Task",
        "--props", json.dumps({
            "title": task_title,
            "status": status,
            "assignee": "main",
            "date": datetime.now().strftime("%Y-%m-%d")
        })
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    return result.returncode == 0

def sync_todo_to_ontology():
    """同步 todo-tracker 到 ontology"""
    if not TODO_FILE.exists():
        return
    
    try:
        with open(TODO_FILE, 'r', encoding='utf-8') as f:
            todo_data = json.load(f)
        
        task_title = todo_data.get('title', '未命名任务')
        items = todo_data.get('items', [])
        
        # 检查是否全部完成
        all_completed = all(i.get('status') == 'completed' for i in items)
        
        if all_completed:
            # 更新 ontology
            success = update_task_status(task_title, "done")
            if success:
                print(f"✅ 已更新 ontology: {task_title} → done")
            else:
                print(f"⚠️ 更新 ontology 失败")
    except Exception as e:
        print(f"⚠️ 同步失败：{e}")

if __name__ == "__main__":
    sync_todo_to_ontology()

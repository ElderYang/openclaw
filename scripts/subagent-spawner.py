#!/usr/bin/env python3
"""
子智能体调度器
用于管理和 spawn 专门的子智能体执行特定任务
"""

import json
import sys
from datetime import datetime

# 子智能体配置
SUBAGENTS = {
    "xhs-publisher": {
        "task": "小红书内容创作和发布",
        "label": "xhs-publisher",
        "timeout": 1800,  # 30 分钟
        "memory_dir": "memory/xiaohongshu/"
    },
    "stock-analyst": {
        "task": "股市数据分析和报告生成",
        "label": "stock-analyst",
        "timeout": 300,  # 5 分钟
        "memory_dir": "memory/stock/"
    },
    "content-researcher": {
        "task": "深度内容搜索和整理",
        "label": "content-researcher",
        "timeout": 900,  # 15 分钟
        "memory_dir": "memory/research/"
    }
}

def spawn_subagent(agent_type: str, task: str, mode: str = "run"):
    """
    Spawn 子智能体
    
    Args:
        agent_type: 子智能体类型（xhs-publisher/stock-analyst/content-researcher）
        task: 具体任务描述
        mode: 运行模式（run/session）
    
    Returns:
        dict: 子智能体配置
    """
    if agent_type not in SUBAGENTS:
        raise ValueError(f"未知的子智能体类型：{agent_type}")
    
    config = SUBAGENTS[agent_type]
    
    spawn_config = {
        "task": task,
        "label": config["label"],
        "runtime": "subagent",
        "mode": mode,
        "timeoutSeconds": config["timeout"],
        "cleanup": "delete"  # 完成后清理
    }
    
    print(f"[{datetime.now()}] Spawn 子智能体：{agent_type}")
    print(f"任务：{task}")
    print(f"超时：{config['timeout']}秒")
    print(f"配置：{json.dumps(spawn_config, indent=2, ensure_ascii=False)}")
    
    return spawn_config

def main():
    """命令行调用入口"""
    if len(sys.argv) < 3:
        print("用法：python subagent-spawner.py <agent_type> <task>")
        print("可用 agent_type: xhs-publisher, stock-analyst, content-researcher")
        sys.exit(1)
    
    agent_type = sys.argv[1]
    task = " ".join(sys.argv[2:])
    
    config = spawn_subagent(agent_type, task)
    print("\n✅ 子智能体已 spawn，等待执行完成...")

if __name__ == "__main__":
    main()

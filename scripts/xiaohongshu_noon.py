#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书每日任务 - OpenClaw 实战教程
执行时间：每天中午 12:30
内容：OpenClaw 技能教程 + 配置指南
角色标签：【小红书助手】
"""

import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

# 角色标签（固定前缀）
ROLE_TAG = "【小红书助手】"

def log(message):
    """打印日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {ROLE_TAG} {message}")

def main():
    log("开始执行每日任务 - OpenClaw 实战")
    log("="*60)
    
    # 确定今日主题（按星期轮换）
    weekday = datetime.now().weekday()
    themes = {
        0: "OpenClaw 股市技能",    # 周一
        1: "OpenClaw 邮件技能",    # 周二
        2: "OpenClaw 记忆系统",    # 周三
        3: "OpenClaw 定时任务",    # 周四
        4: "OpenClaw 技能开发",    # 周五
        5: "OpenClaw 配置指南",    # 周六
        6: "OpenClaw 最佳实践",    # 周日
    }
    today_theme = themes.get(weekday, "OpenClaw 教程")
    
    log(f"今日主题：{today_theme}")
    
    # 调用统一发布器
    publisher_script = SCRIPT_DIR / "xiaohongshu_publisher.py"
    
    try:
        result = subprocess.run(
            ["python3", str(publisher_script)],
            capture_output=True,
            text=True,
            timeout=120,
            env={**os.environ, "PYTHONPATH": str(SCRIPT_DIR)}
        )
        
        if result.returncode == 0:
            log("✅ 发布成功")
            log(result.stdout)
        else:
            log(f"❌ 发布失败：{result.stderr}")
    except Exception as e:
        log(f"❌ 执行异常：{e}")
    
    log("="*60)
    log("任务完成")

if __name__ == "__main__":
    main()

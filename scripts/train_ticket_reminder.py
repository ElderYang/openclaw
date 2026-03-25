#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
火车票预约提醒 - 定时任务脚本
每周三和周日早上 9 点添加 macOS 提醒事项
"""

import subprocess
from datetime import datetime, timedelta

def add_macos_reminder(title, notes="", due_date=None, list_name="提醒"):
    """添加 macOS 提醒事项"""
    cmd = ['/opt/homebrew/bin/remindctl', 'add', title]
    
    if list_name:
        cmd.extend(['--list', list_name])
    
    if due_date:
        cmd.extend(['--due', due_date])
    
    if notes:
        cmd.extend(['--notes', notes])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ 提醒事项已添加：{title}")
        return True
    else:
        print(f"❌ 添加失败：{result.stderr}")
        return False

def generate_reminder_title():
    """生成提醒标题"""
    today = datetime.now()
    
    # 判断是周三还是周日
    if today.weekday() == 2:  # 周三
        title = "🚄 预约周末火车票（智行 APP）"
        notes = "周末出行高峰，建议提前预约周五至周日的车票\n\n⏰ 预约建议：\n• 提前 15-30 天预约（铁路提前 15 天放票）\n• 设置多个车次备选\n• 开启候补购票功能"
    elif today.weekday() == 6:  # 周日
        title = "🚄 预约下周火车票（智行 APP）"
        notes = "下周出行需求，建议提前预约周一至周五的商务票\n\n⏰ 预约建议：\n• 提前 15-30 天预约（铁路提前 15 天放票）\n• 设置多个车次备选\n• 开启候补购票功能"
    else:
        title = "🚄 火车票预约"
        notes = "记得在智行火车票 APP 上预约订购火车票"
    
    return title, notes

if __name__ == '__main__':
    today = datetime.now()
    
    # 检查是否是周三或周日
    if today.weekday() not in [2, 6]:  # 不是周三或周日
        print(f"今天不是周三或周日（weekday={today.weekday()}），跳过执行")
        exit(0)
    
    title, notes = generate_reminder_title()
    
    # 设置到期时间为今天 9:00（如果当前时间已过 9 点，则设置为当前时间 +1 小时）
    if today.hour >= 9:
        due = today.replace(hour=today.hour+1, minute=0, second=0)
    else:
        due = today.replace(hour=9, minute=0, second=0)
    
    due_str = due.strftime('%Y-%m-%d %H:%M')
    
    print(f"添加提醒事项：{title}")
    print(f"到期时间：{due_str}")
    print(f"备注：{notes[:50]}...")
    
    # 添加 macOS 提醒事项
    add_macos_reminder(title, notes, due_str, list_name="提醒")
    
    # 记录日志
    with open('/Users/yangbowen/.openclaw/workspace/logs/train_ticket_reminder.log', 'a') as f:
        f.write(f"\n{datetime.now().isoformat()}\nAdded: {title}\nDue: {due_str}\n")

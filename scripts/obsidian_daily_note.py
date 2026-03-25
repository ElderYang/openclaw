#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Obsidian 每日日记自动生成
执行时间：每天早上 7:00
功能：创建当天的日记文件，使用模板填充
"""

from datetime import datetime
import os
from pathlib import Path

# 配置
OBSIDIAN_DIR = Path.home() / "Obsidian" / "日常记录"
TEMPLATE_DIR = Path.home() / "Obsidian" / "templates"

def create_daily_note():
    """创建每日日记"""
    today = datetime.now()
    date_str = today.strftime('%Y-%m-%d')
    weekday_map = {
        'Monday': '星期一',
        'Tuesday': '星期二',
        'Wednesday': '星期三',
        'Thursday': '星期四',
        'Friday': '星期五',
        'Saturday': '星期六',
        'Sunday': '星期日'
    }
    weekday = weekday_map[today.strftime('%A')]
    
    # 检查是否已存在
    note_path = OBSIDIAN_DIR / f"{date_str}.md"
    if note_path.exists():
        print(f"⚠️  {date_str}.md 已存在，跳过创建")
        return
    
    # 读取模板
    template_path = TEMPLATE_DIR / "每日日记模板.md"
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = f"# {date_str} 日记\n\n**日期**: {today.year}年{today.month}月{today.day}日 {weekday}\n\n"
    
    # 替换模板变量
    content = content.replace('{{date:YYYY-MM-DD}}', date_str)
    content = content.replace('{{date:YYYY 年 MM 月 DD 日 dddd}}', f"{today.year}年{today.month}月{today.day}日 {weekday}")
    content = content.replace('{{time:HH:mm}}', today.strftime('%H:%M'))
    
    # 创建文件
    with open(note_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 已创建：{note_path}")

if __name__ == "__main__":
    print("="*60)
    print("📔 Obsidian 每日日记自动生成")
    print("="*60)
    create_daily_note()
    print("="*60)

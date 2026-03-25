#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Obsidian 日记提醒
执行时间：每天晚上 21:00
功能：飞书提醒用户写日记
"""

import json
import requests
from datetime import datetime
from pathlib import Path

# 飞书配置
FEISHU_APP_ID = "cli_a923ffd1e2f95cb2"
FEISHU_APP_SECRET = "wbUuXVa7aIy96JDguHt3gdvlT4Kpp6aV"
FEISHU_USER_ID = "ou_a040d98b29a237916317887806d655de"

def get_tenant_access_token():
    """获取飞书 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {
        "app_id": FEISHU_APP_ID,
        "app_secret": FEISHU_APP_SECRET
    }
    resp = requests.post(url, json=payload, timeout=10)
    return resp.json().get('tenant_access_token', '')

def send_reminder():
    """发送日记提醒"""
    today = datetime.now().strftime('%Y-%m-%d')
    weekday_map = {
        'Monday': '星期一',
        'Tuesday': '星期二',
        'Wednesday': '星期三',
        'Thursday': '星期四',
        'Friday': '星期五',
        'Saturday': '星期六',
        'Sunday': '星期日'
    }
    weekday = weekday_map[datetime.now().strftime('%A')]
    
    # 检查日记是否已写
    note_path = Path.home() / "Obsidian" / "日常记录" / f"{today}.md"
    if note_path.exists():
        print(f"✅ 今天的日记已写，跳过提醒")
        return
    
    # 获取 token
    token = get_tenant_access_token()
    if not token:
        print("❌ 获取飞书 token 失败")
        return
    
    # 构建提醒消息
    card_content = {
        "config": {
            "wide_screen_mode": True
        },
        "header": {
            "title": {
                "content": "📔 写日记时间到啦！",
                "tag": "plain_text"
            },
            "template": "blue"
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "content": f"今天是 {today} {weekday}\n\n忙碌了一天，记得记录今天的点滴哦～",
                    "tag": "lark_md"
                }
            },
            {
                "tag": "div",
                "text": {
                    "content": "**💡 日记模板已准备好**\n\n打开 Obsidian → 日常记录 → 创建今天的日记\n\n或者使用自动创建的日记文件，直接填充内容即可！",
                    "tag": "lark_md"
                }
            },
            {
                "tag": "hr"
            },
            {
                "tag": "div",
                "text": {
                    "content": "坚持写日记，遇见更好的自己！💪",
                    "tag": "lark_md"
                }
            }
        ]
    }
    
    # 发送消息
    url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "receive_id": FEISHU_USER_ID,
        "msg_type": "interactive",
        "content": json.dumps(card_content, ensure_ascii=False)
    }
    
    resp = requests.post(url, headers=headers, json=payload, timeout=10)
    if resp.status_code == 200:
        print(f"✅ 日记提醒已发送")
    else:
        print(f"❌ 发送失败：{resp.text}")

if __name__ == "__main__":
    print("="*60)
    print("📔 Obsidian 日记提醒")
    print("="*60)
    send_reminder()
    print("="*60)

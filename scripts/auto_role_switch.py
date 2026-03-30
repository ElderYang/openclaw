#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动角色切换脚本
在每次回复前调用，根据用户问题自动判断角色并更新 SESSION-STATE.md

触发规则：
- 小红书/发布/笔记/MCP/内容/素材 → 【小红书助手】
- 股市/股票/复盘/早盘/午盘/持仓/ETF → 【股市分析师】
- 其他 → 【个人助手】（默认）

使用方法：
1. 命令行：python3 auto_role_switch.py "用户问题"
2. 模块导入：from auto_role_switch import switch_role; role = switch_role("用户问题")
"""

import sys
import re
from pathlib import Path

SESSION_STATE_FILE = Path.home() / ".openclaw" / "workspace" / "SESSION-STATE.md"

# 角色关键词定义（按优先级排序）
ROLES = {
    "小红书助手": {
        "name": "小红书助手",
        "keywords": ["小红书", "发布", "笔记", "MCP", "内容", "素材", "xhs", "rednote", "封面", "标题", "标签", "话题"],
        "soul_file": "souls/xiaohongshu-assistant.md",
        "tag": "【小红书助手】"
    },
    "股市分析师": {
        "name": "股市分析师",
        "keywords": ["股市", "股票", "复盘", "早报", "持仓", "ETF", "龙虎榜", "涨停", "板块", "资金流向", "A 股", "美股", "行情", "K 线", "大盘"],
        "soul_file": "souls/stock-analyst.md",
        "tag": "【股市分析师】"
    },
}

DEFAULT_ROLE = {
    "name": "个人助手",
    "soul_file": "souls/personal.md",
    "tag": "【个人助手】",
    "keywords": []
}

def switch_role(user_input):
    """根据用户输入判断角色"""
    scores = {}
    
    for role_name, config in ROLES.items():
        score = 0
        for keyword in config["keywords"]:
            if keyword.lower() in user_input.lower():
                score += 1
                # 核心领域词权重 +2
                if keyword in ["小红书", "股市", "股票", "发布", "复盘"]:
                    score += 2
        scores[role_name] = score
    
    # 找出最高分
    best_role = max(scores, key=scores.get) if scores else None
    best_score = scores.get(best_role, 0)
    
    # 阈值判断（>=3 才切换）
    if best_score >= 3:
        return ROLES[best_role]
    else:
        return DEFAULT_ROLE

def update_session_state(role_info):
    """更新 SESSION-STATE.md"""
    if not SESSION_STATE_FILE.exists():
        print(f"⚠️  {SESSION_STATE_FILE} 不存在")
        return False
    
    content = SESSION_STATE_FILE.read_text(encoding='utf-8')
    
    # 更新当前角色部分
    old_pattern = r"\*\*当前角色\*\*: .*?\n\*\*SOUL 文件\*\*: .*?\n\*\*角色标签\*\*: .*?\n\*\*触发关键词\*\*: .*?"
    new_text = f"""**当前角色**: {role_info['name']}  
**SOUL 文件**: `{role_info['soul_file']}`  
**角色标签**: {role_info['tag']}  
**触发关键词**: {', '.join(role_info.get('keywords', ['默认角色']))}"""
    
    new_content = re.sub(old_pattern, new_text, content, flags=re.DOTALL)
    
    if new_content == content:
        print(f"⚠️  角色未变化：{role_info['tag']}")
        return False
    
    SESSION_STATE_FILE.write_text(new_content, encoding='utf-8')
    print(f"✅ 角色已更新：{role_info['tag']}")
    return True

def main():
    if len(sys.argv) < 2:
        print("用法：python3 auto_role_switch.py \"用户问题\"")
        print("示例：python3 auto_role_switch.py \"小红书为什么发布失败\"")
        sys.exit(1)
    
    user_input = " ".join(sys.argv[1:])
    role_info = switch_role(user_input)
    
    print(f"📋 用户输入：{user_input}")
    print(f"🎭 判断角色：{role_info['tag']}")
    
    update_session_state(role_info)
    print(f"\n✅ 角色标签：{role_info['tag']}")

if __name__ == "__main__":
    main()

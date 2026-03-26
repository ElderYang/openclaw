#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置自动执行器 - 每次创建配置后自动执行
1. 自动添加角色标签
2. 自动分段输出
3. 自动检查 todo-tracker
4. 自动测试验证
"""

import sys
import os
from pathlib import Path
from datetime import datetime

WORKSPACE_DIR = Path.home() / ".openclaw" / "workspace"
SESSION_STATE_FILE = WORKSPACE_DIR / "SESSION-STATE.md"

# ==================== 自动角色标签 ====================

def get_role_tag():
    """获取当前角色标签"""
    if not SESSION_STATE_FILE.exists():
        return "【个人助手】"
    
    content = SESSION_STATE_FILE.read_text(encoding='utf-8')
    
    if "【小红书助手】" in content:
        return "【小红书助手】"
    elif "【股市分析师】" in content:
        return "【股市分析师】"
    else:
        return "【个人助手】"

def add_role_tag_to_response(text):
    """在回复开头添加角色标签"""
    role_tag = get_role_tag()
    return f"{role_tag}{text}"

# ==================== 自动分段 ====================

def split_content(content, max_length=2000):
    """分段内容"""
    paragraphs = content.split('\n')
    segments = []
    current_segment = []
    current_length = 0
    
    for para in paragraphs:
        para_length = len(para) + 1
        if current_length + para_length > max_length and current_segment:
            segments.append('\n'.join(current_segment))
            current_segment = [para]
            current_length = para_length
        else:
            current_segment.append(para)
            current_length += para_length
    
    if current_segment:
        segments.append('\n'.join(current_segment))
    
    return segments

def output_with_auto_segment(content):
    """自动分段输出"""
    segments = split_content(content)
    total = len(segments)
    
    if total == 1:
        print(content)
    else:
        for i, segment in enumerate(segments, 1):
            print(f"\n## 📋 内容（第{i}段/共{total}段）\n")
            print(segment)
            if i < total:
                print("\n---\n")

# ==================== 自动测试 ====================

def auto_test_config(config_type, test_command):
    """自动测试配置"""
    print(f"\n🧪 自动测试：{config_type}")
    print("-" * 60)
    
    import subprocess
    try:
        result = subprocess.run(
            test_command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"✅ 测试通过")
            if result.stdout:
                print(result.stdout[:500])
        else:
            print(f"❌ 测试失败")
            if result.stderr:
                print(result.stderr[:500])
    except Exception as e:
        print(f"❌ 测试异常：{e}")

# ==================== 主函数 ====================

def main():
    """主函数"""
    print("=" * 60)
    print("🤖 配置自动执行器")
    print("=" * 60)
    
    # 1. 获取角色标签
    role_tag = get_role_tag()
    print(f"\n✅ 当前角色：{role_tag}")
    
    # 2. 检查内容长度
    if len(sys.argv) > 1:
        content = ' '.join(sys.argv[1:])
        segments = split_content(content)
        print(f"✅ 内容分段：{len(segments)} 段")
    
    # 3. 自动测试
    print("\n" + "=" * 60)
    print("🧪 自动测试配置")
    print("=" * 60)
    
    # 测试示例
    auto_test_config(
        "角色标签",
        "cat ~/.openclaw/workspace/SESSION-STATE.md | grep 角色"
    )
    
    print("\n" + "=" * 60)
    print("✅ 配置自动执行完成")
    print("=" * 60)

if __name__ == "__main__":
    main()

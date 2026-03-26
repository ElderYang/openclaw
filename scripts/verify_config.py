#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置完成后自动验证脚本
每次创建配置后自动执行，确保配置真正生效
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

WORKSPACE_DIR = Path.home() / ".openclaw" / "workspace"

def run_test(name, command, expected_in_output=None):
    """运行测试并检查结果"""
    print(f"\n🧪 测试：{name}")
    print("-" * 60)
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            if expected_in_output:
                if expected_in_output in result.stdout or expected_in_output in result.stderr:
                    print(f"✅ 通过 - 包含'{expected_in_output}'")
                    return True
                else:
                    print(f"❌ 失败 - 未找到'{expected_in_output}'")
                    return False
            else:
                print(f"✅ 通过")
                return True
        else:
            print(f"❌ 失败 - 返回码 {result.returncode}")
            if result.stderr:
                print(result.stderr[:300])
            return False
    except Exception as e:
        print(f"❌ 异常：{e}")
        return False

def main():
    """主验证流程"""
    print("=" * 60)
    print("🔍 配置自动验证")
    print("=" * 60)
    
    tests = [
        # 角色标签
        ("角色标签配置", "cat ~/.openclaw/workspace/SESSION-STATE.md | grep 角色", "角色"),
        ("角色标签脚本", "python3 ~/.openclaw/workspace/scripts/auto_execute_config.py", "角色"),
        
        # 分段功能
        ("分段脚本存在", "ls ~/.openclaw/workspace/scripts/segment_output.py", "segment_output.py"),
        ("分段功能测试", "echo '测试' | python3 ~/.openclaw/workspace/scripts/segment_output.py", "测试"),
        
        # todo-tracker
        ("todo-tracker 存在", "ls ~/.openclaw/workspace/skills/todo-tracker/todo_tracker.py", "todo_tracker.py"),
        
        # Git 提交
        ("Git 提交记录", "cd ~/.openclaw/workspace && git log --oneline -1", "feat"),
    ]
    
    passed = 0
    failed = 0
    
    for name, command, expected in tests:
        if run_test(name, command, expected):
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 测试结果：{passed} 通过，{failed} 失败")
    print("=" * 60)
    
    if failed > 0:
        print("\n⚠️ 有测试失败，请检查配置！")
        sys.exit(1)
    else:
        print("\n✅ 所有测试通过！配置已生效！")
        sys.exit(0)

if __name__ == "__main__":
    main()

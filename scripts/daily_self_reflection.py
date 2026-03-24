#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日自省脚本 - Self-Reflection
执行时间：每天 22:00（每日小结前）
目的：主动反思当天错误，记录到 learnings.md
"""

import json
from datetime import datetime
from pathlib import Path

LEARNINGS_FILE = Path(__file__).parent.parent / "memory" / "learnings.md"
SESSION_STATE = Path(__file__).parent.parent / "SESSION-STATE.md"

def check_git_status():
    """检查是否有未提交的修改"""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(Path(__file__).parent.parent),
            capture_output=True,
            text=True
        )
        uncommitted = [line for line in result.stdout.strip().split('\n') if line and not line.startswith('??')]
        return len(uncommitted) == 0, uncommitted
    except:
        return False, ["git 检查失败"]

def check_errors_in_logs():
    """检查当天日志中的错误"""
    errors = []
    log_dir = Path("/tmp/openclaw")
    today = datetime.now().strftime('%Y-%m-%d')
    
    if log_dir.exists():
        for log_file in log_dir.glob("*.log"):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if '❌' in line or 'ERROR' in line or '失败' in line:
                            if today in line:
                                errors.append(f"{log_file.name}: {line.strip()}")
            except:
                pass
    
    return errors[:5]  # 最多返回 5 条

def main():
    print("="*60)
    print("🤔 每日自省 - Self-Reflection")
    print("="*60)
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 检查 1: Git 状态
    print("【1】检查 Git 状态...")
    git_clean, uncommitted = check_git_status()
    if git_clean:
        print("  ✅ 工作区干净，无未提交修改")
    else:
        print(f"  ⚠️ 发现 {len(uncommitted)} 个未提交文件:")
        for f in uncommitted[:5]:
            print(f"     - {f}")
        print("  💡 建议：执行 git add + commit")
    print()
    
    # 检查 2: 日志错误
    print("【2】检查当天错误日志...")
    errors = check_errors_in_logs()
    if errors:
        print(f"  ⚠️ 发现 {len(errors)} 条错误:")
        for e in errors:
            print(f"     - {e}")
        print("  💡 建议：记录到 learnings.md")
    else:
        print("  ✅ 未发现明显错误")
    print()
    
    # 检查 3: 用户反馈
    print("【3】检查用户反馈...")
    print("  ⚠️ 待实现：分析当天对话，提取用户纠正/批评")
    print()
    
    # 生成反思建议
    print("【4】反思建议")
    if not git_clean or errors:
        print("  📝 今天有需要记录的教训")
        print("  📍 位置：memory/learnings.md")
        print("  🏷️  格式：[LRN-YYYYMMDD-XXX] 标题")
    else:
        print("  ✅ 今天表现良好，继续保持！")
    print()
    
    print("="*60)

if __name__ == "__main__":
    main()

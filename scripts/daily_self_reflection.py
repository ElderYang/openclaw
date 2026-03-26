#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日自省脚本
执行时间：每天 22:00
功能：检查 Self-Improving 系统，生成反思建议
"""

import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path

SELF_IMPROVING_DIR = Path.home() / "self-improving"
WORKSPACE_DIR = Path.home() / ".openclaw" / "workspace"

def log(message):
    """打印日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def check_corrections():
    """检查纠正记录"""
    log("📝 检查纠正记录...")
    corrections_file = SELF_IMPROVING_DIR / "corrections.md"
    
    if not corrections_file.exists():
        log("⚠️ corrections.md 不存在")
        return []
    
    # 读取今天的纠正
    content = corrections_file.read_text(encoding='utf-8')
    today = datetime.now().strftime('%Y-%m-%d')
    
    if today in content:
        log(f"✅ 今天有 {content.count(today)} 条纠正")
        return [today]
    else:
        log("📦 今天没有新纠正")
        return []

def check_memory():
    """检查记忆更新"""
    log("🧠 检查记忆更新...")
    memory_file = SELF_IMPROVING_DIR / "memory.md"
    
    if not memory_file.exists():
        log("⚠️ memory.md 不存在")
        return False
    
    log("✅ memory.md 存在")
    return True

def scan_errors():
    """扫描日志错误"""
    log("🔍 扫描日志错误...")
    log_dir = Path("/tmp/openclaw")
    
    if not log_dir.exists():
        log("⚠️ 日志目录不存在")
        return []
    
    errors = []
    for log_file in log_dir.glob("*.log"):
        try:
            content = log_file.read_text(encoding='utf-8', errors='ignore')
            if "error" in content.lower() or "failed" in content.lower():
                errors.append(str(log_file))
        except:
            pass
    
    if errors:
        log(f"⚠️ 发现 {len(errors)} 个日志文件有错误")
    else:
        log("✅ 未发现明显错误")
    
    return errors

def check_pattern_recognition():
    """检查模式识别"""
    log("🔍 检查模式识别...")
    tracker_file = WORKSPACE_DIR / "notes/areas/proactive-tracker.md"
    
    if not tracker_file.exists():
        log("⚠️ proactive-tracker.md 不存在")
        return []
    
    content = tracker_file.read_text(encoding='utf-8')
    patterns = []
    
    # 检查重复请求
    if "重复请求" in content:
        patterns.append("发现重复请求模式")
    
    # 检查自动化建议
    if "待自动化" in content:
        patterns.append("有待自动化需求")
    
    for pattern in patterns:
        log(f"  - {pattern}")
    
    return patterns

def check_decision_tracking():
    """检查决策追踪"""
    log("📊 检查决策追踪...")
    tracker_file = WORKSPACE_DIR / "notes/areas/proactive-tracker.md"
    
    if not tracker_file.exists():
        log("⚠️ proactive-tracker.md 不存在")
        return []
    
    content = tracker_file.read_text(encoding='utf-8')
    overdue = []
    
    # 检查超 7 天的决策
    if "超过 7 天的决策" in content:
        overdue.append("检查超期决策")
    
    # 检查近期决策
    if "近期决策" in content:
        overdue.append("跟进近期决策")
    
    for item in overdue:
        log(f"  - {item}")
    
    return overdue

def generate_suggestions():
    """生成反思建议"""
    log("💡 生成反思建议...")
    
    suggestions = []
    
    # 检查 proactive-tracker
    tracker_file = WORKSPACE_DIR / "notes/areas/proactive-tracker.md"
    if tracker_file.exists():
        content = tracker_file.read_text(encoding='utf-8')
        if "[ ]" in content:
            pending = content.count("[ ]")
            suggestions.append(f"有 {pending} 个待执行项需要跟进")
    
    # 检查决策追踪
    if "超过 7 天的决策" in open(tracker_file, encoding='utf-8').read():
        suggestions.append("检查是否有超期决策需要跟进")
    
    # 检查模式识别
    suggestions.append("回顾今天的重复请求，是否有可自动化的模式")
    suggestions.append("检查 Self-Improving 纠正，是否有需要系统化的教训")
    
    for suggestion in suggestions:
        log(f"  - {suggestion}")
    
    return suggestions

def update_heartbeat_state():
    """更新心跳状态"""
    log("📊 更新心跳状态...")
    state_file = SELF_IMPROVING_DIR / "heartbeat-state.md"
    
    now = datetime.now()
    state_content = f"""# Self-Improving Heartbeat State

**最后更新**: {now.strftime('%Y-%m-%d %H:%M:%S')}

## 状态追踪

last_heartbeat_started_at: {now.isoformat()}
last_reviewed_change_at: {now.isoformat()}
last_heartbeat_result: 每日自省完成

## 最近行动
- ✅ 检查纠正记录
- ✅ 检查记忆更新
- ✅ 扫描日志错误
- ✅ 生成反思建议
- ✅ 更新心跳状态

## 待处理
- [ ] 每周反思（周六 20:00）
"""
    
    state_file.write_text(state_content, encoding='utf-8')
    log("✅ 心跳状态已更新")

def main():
    """主函数"""
    log("="*60)
    log("🌙 每日自省 | " + now.strftime('%Y-%m-%d %H:%M'))
    log("="*60)
    
    # 1. 检查纠正
    corrections = check_corrections()
    
    # 2. 检查记忆
    memory_ok = check_memory()
    
    # 3. 扫描错误
    errors = scan_errors()
    
    # 4. 模式识别（中期优化）
    patterns = check_pattern_recognition()
    
    # 5. 决策追踪（中期优化）
    decisions = check_decision_tracking()
    
    # 6. 生成建议
    suggestions = generate_suggestions()
    
    # 7. 更新状态
    update_heartbeat_state()
    
    # 8. 输出总结
    log("\n" + "="*60)
    log("📋 今日自省总结")
    log("="*60)
    log(f"纠正记录：{len(corrections)} 条")
    log(f"记忆状态：{'✅' if memory_ok else '❌'}")
    log(f"日志错误：{len(errors)} 个")
    log(f"模式识别：{len(patterns)} 条")
    log(f"决策追踪：{len(decisions)} 条")
    log(f"反思建议：{len(suggestions)} 条")
    log("="*60)
    
    if errors:
        log("\n⚠️ 需要关注的错误日志:")
        for error in errors[:5]:
            log(f"  - {error}")
    
    if patterns:
        log("\n🔍 模式识别:")
        for pattern in patterns:
            log(f"  - {pattern}")
    
    if decisions:
        log("\n📊 决策追踪:")
        for decision in decisions:
            log(f"  - {decision}")
    
    if suggestions:
        log("\n💡 反思建议:")
        for suggestion in suggestions:
            log(f"  - {suggestion}")
    
    log("\n✅ 每日自省完成")
    log("="*60)

if __name__ == "__main__":
    now = datetime.now()
    main()

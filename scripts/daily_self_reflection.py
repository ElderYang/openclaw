#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日自省脚本（增强版）
执行时间：每天 22:00
功能：深度检查 Self-Improving 系统，生成反思报告

增强内容：
1. 扫描当天日志错误（/tmp/openclaw/*.log）
2. 分析任务失败记录（task-tracker.json）
3. 检查用户纠正（SESSION-STATE.md 中的纠正记录）
4. 生成深度反思报告（不只是打卡）
"""

import subprocess
import sys
import os
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

# 导入事件触发反思模块
import event_triggered_reflection

SELF_IMPROVING_DIR = Path.home() / "self-improving"
WORKSPACE_DIR = Path.home() / ".openclaw" / "workspace"
MEMORY_DIR = WORKSPACE_DIR / "memory"
LOG_DIR = Path("/tmp/openclaw")

def log(message, level="INFO"):
    """打印日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    emoji = {"INFO": "ℹ️", "WARN": "⚠️", "ERROR": "❌", "SUCCESS": "✅"}
    print(f"[{timestamp}] [{emoji.get(level, 'ℹ️')}] {message}")

def scan_log_errors():
    """扫描当天日志错误（增强版）"""
    log("🔍 深度扫描日志错误...", "INFO")
    
    if not LOG_DIR.exists():
        log("日志目录不存在", "WARN")
        return {"errors": [], "warnings": [], "summary": "无日志文件"}
    
    today = datetime.now().strftime('%Y-%m-%d')
    errors = []
    warnings = []
    error_counts = defaultdict(int)
    
    for log_file in LOG_DIR.glob("*.log"):
        try:
            content = log_file.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            
            for i, line in enumerate(lines, 1):
                # 检测错误
                if any(kw in line.lower() for kw in ['error', 'failed', 'exception', 'traceback']):
                    if today in line or (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d') in line:
                        errors.append({
                            "file": str(log_file),
                            "line": i,
                            "content": line.strip()[:200],
                            "type": "error"
                        })
                        error_counts[log_file.name] += 1
                
                # 检测警告
                if any(kw in line.lower() for kw in ['warning', 'warn', 'timeout', 'retry']):
                    if today in line:
                        warnings.append({
                            "file": str(log_file),
                            "line": i,
                            "content": line.strip()[:200],
                            "type": "warning"
                        })
        except Exception as e:
            log(f"读取日志失败 {log_file}: {e}", "ERROR")
    
    summary = {
        "total_errors": len(errors),
        "total_warnings": len(warnings),
        "files_with_errors": len(error_counts),
        "most_errors": max(error_counts.items(), key=lambda x: x[1])[0] if error_counts else "无"
    }
    
    log(f"发现 {len(errors)} 个错误，{len(warnings)} 个警告", "WARN" if errors else "SUCCESS")
    return {"errors": errors[:20], "warnings": warnings[:20], "summary": summary}

def analyze_task_failures():
    """分析任务失败记录"""
    log("📊 分析任务失败记录...", "INFO")
    
    tracker_file = WORKSPACE_DIR / "task-tracker.json"
    if not tracker_file.exists():
        log("task-tracker.json 不存在", "WARN")
        return {"failures": [], "patterns": []}
    
    try:
        with open(tracker_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        log("读取 task-tracker.json 失败", "ERROR")
        return {"failures": [], "patterns": []}
    
    failures = []
    patterns = defaultdict(int)
    
    # 分析已完成任务中的失败
    completed = data.get('completed_tasks', [])
    for task in completed:
        if isinstance(task, dict):
            if task.get('status') == 'failed' or task.get('error'):
                failures.append({
                    "task": task.get('name', 'Unknown'),
                    "error": task.get('error', 'Unknown error'),
                    "time": task.get('completed_at', 'Unknown')
                })
                # 提取错误模式
                error_msg = task.get('error', '')
                if 'timeout' in error_msg.lower():
                    patterns['timeout'] += 1
                elif 'connection' in error_msg.lower() or 'network' in error_msg.lower():
                    patterns['network'] += 1
                elif 'permission' in error_msg.lower() or 'access' in error_msg.lower():
                    patterns['permission'] += 1
                elif 'module' in error_msg.lower() or 'import' in error_msg.lower():
                    patterns['dependency'] += 1
    
    # 分析活跃任务
    active = data.get('active_tasks', [])
    for task in active:
        if isinstance(task, dict):
            if task.get('status') == 'failed':
                failures.append({
                    "task": task.get('name', 'Unknown'),
                    "error": task.get('error', 'Unknown error'),
                    "time": "Active"
                })
    
    log(f"发现 {len(failures)} 个失败任务", "WARN" if failures else "SUCCESS")
    return {
        "failures": failures,
        "patterns": dict(patterns),
        "summary": {
            "total_failures": len(failures),
            "top_pattern": max(patterns.items(), key=lambda x: x[1])[0] if patterns else "无"
        }
    }

def check_user_corrections():
    """检查用户纠正（SESSION-STATE.md 和 corrections.md）"""
    log("📝 检查用户纠正...", "INFO")
    
    corrections = []
    
    # 检查 corrections.md
    corrections_file = SELF_IMPROVING_DIR / "corrections.md"
    if corrections_file.exists():
        try:
            content = corrections_file.read_text(encoding='utf-8')
            today = datetime.now().strftime('%Y-%m-%d')
            
            # 提取今天的纠正
            today_pattern = rf'\[({today}.*?)](.*?)(?=\n## \[|$)'
            matches = re.findall(today_pattern, content, re.DOTALL)
            
            for match in matches:
                corrections.append({
                    "time": match[0],
                    "topic": match[1].strip()[:100],
                    "source": "corrections.md"
                })
            
            # 统计本周纠正数量
            week_start = datetime.now() - timedelta(days=datetime.now().weekday())
            week_pattern = rf'\[({week_start.strftime("%Y-%m-%d")}.*?)]'
            week_corrections = len(re.findall(week_pattern, content))
            
            log(f"今天 {len(corrections)} 条纠正，本周 {week_corrections} 条", 
                "WARN" if corrections else "SUCCESS")
        except Exception as e:
            log(f"读取 corrections.md 失败：{e}", "ERROR")
    
    # 检查 SESSION-STATE.md 中的纠正
    session_state_file = WORKSPACE_DIR / "SESSION-STATE.md"
    if session_state_file.exists():
        try:
            content = session_state_file.read_text(encoding='utf-8')
            if "纠正" in content or "纠正记录" in content:
                corrections.append({
                    "time": datetime.now().strftime('%Y-%m-%d %H:%M'),
                    "topic": "SESSION-STATE.md 中有纠正记录",
                    "source": "SESSION-STATE.md"
                })
        except:
            pass
    
    return {
        "corrections": corrections,
        "summary": {
            "today_count": len(corrections),
            "sources": list(set(c['source'] for c in corrections))
        }
    }

def analyze_recurring_issues():
    """分析重复出现的问题"""
    log("🔄 分析重复问题...", "INFO")
    
    issues = defaultdict(list)
    
    # 读取 corrections.md 分析重复主题
    corrections_file = SELF_IMPROVING_DIR / "corrections.md"
    if corrections_file.exists():
        try:
            content = corrections_file.read_text(encoding='utf-8')
            
            # 提取所有主题
            topics = re.findall(r'## \[(.*?)\] (.*?)(?=\n|$)', content)
            for date, topic in topics:
                # 关键词归类
                if "标签" in topic:
                    issues["标签显示"].append(date)
                elif "小红书" in topic:
                    issues["小红书发布"].append(date)
                elif "股市" in topic or "股票" in topic:
                    issues["股市分析"].append(date)
                elif "配置" in topic or "持久化" in topic:
                    issues["配置持久化"].append(date)
                elif "定时任务" in topic or "定时" in topic:
                    issues["定时任务"].append(date)
        except:
            pass
    
    # 找出重复 3 次以上的问题
    recurring = {k: v for k, v in issues.items() if len(v) >= 3}
    
    log(f"发现 {len(recurring)} 个重复问题", "WARN" if recurring else "SUCCESS")
    return {
        "recurring_issues": recurring,
        "summary": {
            "total_categories": len(issues),
            "recurring_count": len(recurring),
            "most_frequent": max(recurring.items(), key=lambda x: len(x[1]))[0] if recurring else "无"
        }
    }

def generate_deep_reflection_report(log_results, task_results, correction_results, recurring_results):
    """生成深度反思报告"""
    log("📄 生成深度反思报告...", "INFO")
    
    today = datetime.now()
    report_file = SELF_IMPROVING_DIR / f"daily-reflection-{today.strftime('%Y%m%d')}.md"
    
    # 构建报告内容
    report = f"""# 每日深度反思报告

**日期**: {today.strftime('%Y-%m-%d')}  
**生成时间**: {today.strftime('%Y-%m-%d %H:%M:%S')}  
**版本**: v2.0 (增强版)

---

## 📊 今日概览

| 指标 | 数值 | 状态 |
|------|------|------|
| 日志错误数 | {log_results['summary'].get('total_errors', 0)} | {'⚠️' if log_results['summary'].get('total_errors', 0) > 0 else '✅'} |
| 任务失败数 | {task_results['summary'].get('total_failures', 0)} | {'⚠️' if task_results['summary'].get('total_failures', 0) > 0 else '✅'} |
| 用户纠正数 | {correction_results['summary'].get('today_count', 0)} | {'⚠️' if correction_results['summary'].get('today_count', 0) > 0 else '✅'} |
| 重复问题数 | {recurring_results['summary'].get('recurring_count', 0)} | {'⚠️' if recurring_results['summary'].get('recurring_count', 0) > 0 else '✅'} |

---

## 🔍 日志错误分析

### 错误统计
- 总错误数：{log_results['summary'].get('total_errors', 0)}
- 总警告数：{log_results['summary'].get('total_warnings', 0)}
- 错误最多文件：{log_results['summary'].get('most_errors', '无')}

### 关键错误
"""
    
    if log_results['errors']:
        for i, error in enumerate(log_results['errors'][:5], 1):
            report += f"\n{i}. **{error['file']}** (行{error['line']})\n   ```\n   {error['content']}\n   ```"
    else:
        report += "\n✅ 未发现明显错误"
    
    report += f"""

---

## 📋 任务失败分析

### 失败统计
- 总失败数：{task_results['summary'].get('total_failures', 0)}
- 主要错误模式：{task_results['summary'].get('top_pattern', '无')}

### 错误模式分布
"""
    
    if task_results['patterns']:
        for pattern, count in task_results['patterns'].items():
            emoji = {"timeout": "⏰", "network": "🌐", "permission": "🔒", "dependency": "📦"}.get(pattern, "📌")
            report += f"\n- {emoji} {pattern}: {count} 次"
    else:
        report += "\n✅ 无明显错误模式"
    
    report += f"""

---

## 📝 用户纠正分析

### 纠正统计
- 今日纠正：{correction_results['summary'].get('today_count', 0)} 条
- 来源：{', '.join(correction_results['summary'].get('sources', []))}

### 今日纠正
"""
    
    if correction_results['corrections']:
        for corr in correction_results['corrections']:
            report += f"\n- **{corr['time']}**: {corr['topic']} ({corr['source']})"
    else:
        report += "\n✅ 今日无用户纠正"
    
    report += f"""

---

## 🔄 重复问题追踪

### 重复问题统计
- 问题类别：{recurring_results['summary'].get('total_categories', 0)} 类
- 重复 3 次以上：{recurring_results['summary'].get('recurring_count', 0)} 类
- 最频繁问题：{recurring_results['summary'].get('most_frequent', '无')}

### 高频问题
"""
    
    if recurring_results['recurring_issues']:
        for issue, dates in recurring_results['recurring_issues'].items():
            report += f"\n- **{issue}**: 出现 {len(dates)} 次 ({', '.join(dates[-3:])})"
    else:
        report += "\n✅ 无重复问题"
    
    report += f"""

---

## 💡 改进建议

### 立即行动
"""
    
    suggestions = []
    if log_results['summary'].get('total_errors', 0) > 5:
        suggestions.append("🔴 优先修复高频日志错误")
    if task_results['summary'].get('total_failures', 0) > 3:
        suggestions.append("🔴 分析任务失败根因")
    if recurring_results['summary'].get('recurring_count', 0) > 0:
        suggestions.append(f"🟡 系统性解决重复问题：{recurring_results['summary'].get('most_frequent', '')}")
    if correction_results['summary'].get('today_count', 0) > 2:
        suggestions.append("🟡 今天纠正较多，建议深度反思")
    
    if suggestions:
        for sug in suggestions:
            report += f"\n- {sug}"
    else:
        report += "\n✅ 系统运行良好，持续保持"
    
    report += f"""

### 长期改进
- [ ] 建立错误自动修复机制
- [ ] 完善任务失败重试策略
- [ ] 优化用户体验减少纠正
- [ ] 定期回顾重复问题

---

## 📈 趋势分析

### 本周对比
- 本周总纠正：待统计（weekly_reflection.py）
- 本周错误趋势：待统计
- 改进措施落实：待检查

---

*报告由 Self-Improving 系统自动生成 (v2.0)*
"""
    
    report_file.write_text(report, encoding='utf-8')
    log(f"报告已保存：{report_file}", "SUCCESS")
    return str(report_file)

def create_daily_memory():
    """创建每日记忆文件（自动填充内容）"""
    log("📝 创建每日记忆文件...", "INFO")
    today = datetime.now()
    today_str = today.strftime('%Y-%m-%d')
    memory_file = MEMORY_DIR / f"{today_str}.md"
    
    if memory_file.exists():
        log(f"今日记忆文件已存在：{memory_file}", "SUCCESS")
        return
    
    # 获取 Git 统计
    try:
        result = subprocess.run(
            ['git', '-C', str(WORKSPACE_DIR), 'log', '--oneline', '--since', today_str],
            capture_output=True, text=True, timeout=10
        )
        git_commits = result.stdout.strip().split('\n') if result.stdout.strip() else []
        git_count = len(git_commits)
    except:
        git_count = 0
        git_commits = []
    
    # 生成记忆文件内容
    git_list = '\n'.join([f"- {c}" for c in git_commits[:5]]) if git_commits else "无提交"
    
    memory_content = f"""# 🦞 {today_str} 记忆日志

**创建时间**: {today.strftime('%Y-%m-%d %H:%M')}  
**来源**: Self-Improving 系统（自动填充）

---

## 🔑 关键事件

### 自动统计

- **Git 提交**: {git_count} 个
- **来源**: 每日自省脚本

### Git 提交
{git_list}

---

## 📊 统计数据

| 指标 | 数值 |
|------|------|
| Git 提交数 | {git_count} |

---

## 💡 关键学习

*待补充（如有纠正会自动记录）*

---

*最后更新：{today.strftime('%Y-%m-%d %H:%M')}*
"""
    
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    memory_file.write_text(memory_content, encoding='utf-8')
    log(f"已创建每日记忆文件：{memory_file}", "SUCCESS")

def update_heartbeat_state():
    """更新心跳状态"""
    log("📊 更新心跳状态...", "INFO")
    state_file = SELF_IMPROVING_DIR / "heartbeat-state.md"
    
    now = datetime.now()
    state_content = f"""# Self-Improving Heartbeat State

**最后更新**: {now.strftime('%Y-%m-%d %H:%M:%S')}

## 状态追踪

last_heartbeat_started_at: {now.isoformat()}
last_reviewed_change_at: {now.isoformat()}
last_heartbeat_result: 每日深度自省完成 (v2.0)

## 最近行动
- ✅ 深度扫描日志错误
- ✅ 分析任务失败记录
- ✅ 检查用户纠正
- ✅ 分析重复问题
- ✅ 生成深度反思报告
- ✅ 创建每日记忆文件
- ✅ 更新心跳状态

## 待处理
- [ ] 每周反思（周六 20:00）
- [ ] 事件触发反思监控
"""
    
    state_file.write_text(state_content, encoding='utf-8')
    log("心跳状态已更新", "SUCCESS")

def main():
    """主函数"""
    now = datetime.now()
    log("="*60, "INFO")
    log(f"🌙 每日深度自省 | {now.strftime('%Y-%m-%d %H:%M')} (v2.0)", "INFO")
    log("="*60, "INFO")
    
    # 0. 事件触发反思（优先执行）
    log("🔔 执行事件触发反思...", "INFO")
    try:
        event_triggered_reflection.trigger_reflection(scan_minutes=60)
        log("事件触发反思完成", "SUCCESS")
    except Exception as e:
        log(f"事件触发反思失败：{e}", "ERROR")
    
    # 1. 深度扫描日志错误
    log_results = scan_log_errors()
    
    # 2. 分析任务失败记录
    task_results = analyze_task_failures()
    
    # 3. 检查用户纠正
    correction_results = check_user_corrections()
    
    # 4. 分析重复问题
    recurring_results = analyze_recurring_issues()
    
    # 5. 生成深度反思报告
    report_file = generate_deep_reflection_report(
        log_results, task_results, correction_results, recurring_results
    )
    
    # 6. 创建每日记忆文件
    create_daily_memory()
    
    # 7. 更新状态
    update_heartbeat_state()
    
    # 8. 输出总结
    log("\n" + "="*60, "INFO")
    log("📋 今日深度自省总结", "INFO")
    log("="*60, "INFO")
    log(f"日志错误：{log_results['summary'].get('total_errors', 0)} 个", 
        "WARN" if log_results['summary'].get('total_errors', 0) > 0 else "SUCCESS")
    log(f"任务失败：{task_results['summary'].get('total_failures', 0)} 个",
        "WARN" if task_results['summary'].get('total_failures', 0) > 0 else "SUCCESS")
    log(f"用户纠正：{correction_results['summary'].get('today_count', 0)} 条",
        "WARN" if correction_results['summary'].get('today_count', 0) > 0 else "SUCCESS")
    log(f"重复问题：{recurring_results['summary'].get('recurring_count', 0)} 类",
        "WARN" if recurring_results['summary'].get('recurring_count', 0) > 0 else "SUCCESS")
    log(f"反思报告：{report_file}", "SUCCESS")
    log("="*60, "INFO")
    log("\n✅ 每日深度自省完成 (v2.0)", "SUCCESS")
    log("="*60, "INFO")

if __name__ == "__main__":
    main()

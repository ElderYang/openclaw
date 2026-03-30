#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
事件触发反思脚本 (Event-Triggered Reflection)

功能：
1. 严重错误检测 - 扫描日志中的关键词（数据准确性/用户反馈错误/API 失败）
2. 重复问题检测 - 相同错误出现 3 次以上触发告警
3. 用户批评检测 - 关键词（"不对"/"错了"/"很难"/"没做"/"流于形式"等）
4. 立即记录到 corrections.md + memory/learnings.md
5. 可选：发送飞书消息通知用户

触发条件（满足任一即执行）：
- 🔴 严重错误：数据准确性问题、用户反馈数据错误
- 🟡 重复问题：相同问题出现 3 次以上
- 🟢 用户要求：用户明确要求"反思一下"
- 📊 重大优化：完成系统性优化后

输出：
- 学习条目：~/self-improving/corrections.md
- 详细报告：~/self-improving/incident-reflection-YYYYMMDD-HHMM.md
- 可选：飞书消息通知

脚本位置：~/.openclaw/workspace/scripts/event_triggered_reflection.py

执行方式：
- 可被其他脚本调用（作为函数 import）
- 可独立运行（扫描最近 1 小时日志）

版本：v1.0
创建时间：2026-03-30
"""

import subprocess
import sys
import os
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

# ============================================================================
# 配置
# ============================================================================

SELF_IMPROVING_DIR = Path.home() / "self-improving"
WORKSPACE_DIR = Path.home() / ".openclaw" / "workspace"
MEMORY_DIR = WORKSPACE_DIR / "memory"
LOG_DIR = Path("/tmp/openclaw")
SESSION_STATE_FILE = WORKSPACE_DIR / "SESSION-STATE.md"

# 严重错误关键词
CRITICAL_ERROR_KEYWORDS = [
    "数据准确性", "数据错误", "accuracy", "data error",
    "API 失败", "API failed", "API error",
    "用户反馈错误", "user reported error",
    "严重错误", "critical error", "fatal",
    "AttributeError", "KeyError", "TypeError",
    "ModuleNotFoundError", "ImportError",
]

# 用户批评分词
USER_CRITICISM_KEYWORDS = [
    "不对", "错了", "错误", "有问题",
    "很难", "太难了", "不好用",
    "没做", "没有做", "忘了", "忘记",
    "流于形式", "空框架", "假的",
    "又忘了", "再次", "反复", "总是",
    "为什么没", "怎么回事", "搞什么",
    "不满意", "失望", "太差了",
]

# 反思触发词
REFLECTION_TRIGGER_KEYWORDS = [
    "反思一下", "反思", "总结一下", "记录一下",
    "记住这个", "别忘了", "持久化",
    "改进", "优化", "修复",
]

# 飞书配置（可选）
FEISHU_ENABLED = False  # 默认关闭，需要时开启
FEISHU_WEBHOOK = ""  # 如有需要可配置


# ============================================================================
# 工具函数
# ============================================================================

def log(message: str, level: str = "INFO"):
    """打印日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    emoji = {
        "INFO": "ℹ️",
        "WARN": "⚠️",
        "ERROR": "❌",
        "SUCCESS": "✅",
        "CRITICAL": "🔴",
        "REFLECTION": "🤔"
    }
    print(f"[{timestamp}] [{emoji.get(level, 'ℹ️')}] {message}")


def ensure_directories():
    """确保必要目录存在"""
    SELF_IMPROVING_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)


def get_recent_logs(minutes: int = 60) -> List[str]:
    """获取最近 N 分钟的日志内容"""
    if not LOG_DIR.exists():
        return []
    
    cutoff_time = datetime.now() - timedelta(minutes=minutes)
    log_lines = []
    
    for log_file in LOG_DIR.glob("*.log"):
        try:
            content = log_file.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            
            for line in lines:
                # 简单的时间戳检查
                if any(cutoff_time.strftime('%Y-%m-%d %H') in line for _ in [1]):
                    log_lines.append(line)
                # 如果没有时间戳，也包含进来
                elif not re.match(r'\d{4}-\d{2}-\d{2}', line):
                    log_lines.append(line)
        except Exception as e:
            log(f"读取日志失败 {log_file}: {e}", "ERROR")
    
    return log_lines


def get_session_state_corrections() -> List[str]:
    """从 SESSION-STATE.md 获取未处理的纠正"""
    if not SESSION_STATE_FILE.exists():
        return []
    
    try:
        content = SESSION_STATE_FILE.read_text(encoding='utf-8')
        corrections = []
        
        # 查找 WAL Protocol 部分
        wal_match = re.search(r'## WAL Protocol.*?(?=##|$)', content, re.DOTALL)
        if wal_match:
            wal_content = wal_match.group(0)
            # 提取纠正项
            correction_lines = re.findall(r'^-\s*(.*?)$', wal_content, re.MULTILINE)
            corrections.extend(correction_lines)
        
        # 查找纠正记录部分
        correction_match = re.search(r'## 纠正记录.*?(?=##|$)', content, re.DOTALL)
        if correction_match:
            correction_content = correction_match.group(0)
            correction_lines = re.findall(r'^-\s*(.*?)$', correction_content, re.MULTILINE)
            corrections.extend(correction_lines)
        
        return corrections
    except Exception as e:
        log(f"读取 SESSION-STATE.md 失败：{e}", "ERROR")
        return []


# ============================================================================
# 检测函数
# ============================================================================

def detect_critical_errors(log_lines: List[str]) -> List[Dict]:
    """检测严重错误"""
    errors = []
    
    for i, line in enumerate(log_lines, 1):
        line_lower = line.lower()
        
        # 检查严重错误关键词
        for keyword in CRITICAL_ERROR_KEYWORDS:
            if keyword.lower() in line_lower:
                errors.append({
                    "line_num": i,
                    "content": line.strip()[:300],
                    "keyword": keyword,
                    "type": "critical_error",
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                break
    
    return errors


def detect_user_criticism(log_lines: List[str]) -> List[Dict]:
    """检测用户批评"""
    criticisms = []
    
    for i, line in enumerate(log_lines, 1):
        # 检查用户批评关键词
        for keyword in USER_CRITICISM_KEYWORDS:
            if keyword in line:
                criticisms.append({
                    "line_num": i,
                    "content": line.strip()[:300],
                    "keyword": keyword,
                    "type": "user_criticism",
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                break
    
    return criticisms


def detect_recurring_issues(corrections_file: Path, threshold: int = 3) -> Dict[str, List[str]]:
    """检测重复问题（出现 threshold 次以上）"""
    if not corrections_file.exists():
        return {}
    
    try:
        content = corrections_file.read_text(encoding='utf-8')
        
        # 提取所有主题
        topics = defaultdict(list)
        matches = re.findall(r'## \[(.*?)\] (.*?)(?=\n|$)', content)
        
        for date, topic in matches:
            # 关键词归类
            if "标签" in topic:
                topics["标签显示问题"].append(date)
            elif "小红书" in topic:
                topics["小红书发布问题"].append(date)
            elif "股市" in topic or "股票" in topic:
                topics["股市分析问题"].append(date)
            elif "配置" in topic or "持久化" in topic:
                topics["配置持久化问题"].append(date)
            elif "定时任务" in topic:
                topics["定时任务问题"].append(date)
            elif "角色" in topic:
                topics["角色切换问题"].append(date)
            elif "任务追踪" in topic or "汇报" in topic:
                topics["任务追踪问题"].append(date)
            elif "MCP" in topic or "发布" in topic:
                topics["MCP 发布问题"].append(date)
            else:
                topics["其他问题"].append(date)
        
        # 过滤出重复问题
        recurring = {k: v for k, v in topics.items() if len(v) >= threshold}
        
        return recurring
    except Exception as e:
        log(f"分析重复问题失败：{e}", "ERROR")
        return {}


def detect_reflection_request(log_lines: List[str]) -> List[Dict]:
    """检测用户要求的反思"""
    requests = []
    
    for i, line in enumerate(log_lines, 1):
        for keyword in REFLECTION_TRIGGER_KEYWORDS:
            if keyword in line:
                requests.append({
                    "line_num": i,
                    "content": line.strip()[:300],
                    "keyword": keyword,
                    "type": "reflection_request",
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                break
    
    return requests


# ============================================================================
# 记录函数
# ============================================================================

def append_to_corrections(incident: Dict, details: str):
    """追加到 corrections.md"""
    corrections_file = SELF_IMPROVING_DIR / "corrections.md"
    
    now = datetime.now()
    timestamp = now.strftime('%Y-%m-%d %H:%M')
    
    # 生成条目
    entry = f"""

---

## [{timestamp}] {incident.get('topic', '事件触发反思')} ⚠️ 新记录

**触发类型**: {incident.get('trigger_type', '未知')}
**严重程度**: {incident.get('severity', '待评估')}
**来源**: 事件触发反思脚本 (event_triggered_reflection.py)

**上下文**: 
{details}

**问题描述**: 
待补充

**根本原因分析**: 
待分析

**改进措施**: 
- [ ] 待制定

**状态**: 待处理

**验证**: 
待验证

---
"""
    
    # 追加到文件
    try:
        if corrections_file.exists():
            content = corrections_file.read_text(encoding='utf-8')
            content += entry
        else:
            content = f"# Corrections Log (最近 50 条纠正记录)\n\n**创建时间**: {now.strftime('%Y-%m-%d')}\n**目的**: 记录用户纠正和自我反思，用于自我提升\n\n---\n{entry}"
        
        corrections_file.write_text(content, encoding='utf-8')
        log(f"已记录到 corrections.md", "SUCCESS")
    except Exception as e:
        log(f"写入 corrections.md 失败：{e}", "ERROR")


def create_incident_reflection_report(
    critical_errors: List[Dict],
    user_criticisms: List[Dict],
    recurring_issues: Dict,
    reflection_requests: List[Dict],
    session_corrections: List[str]
) -> str:
    """创建事件反思详细报告"""
    now = datetime.now()
    report_file = SELF_IMPROVING_DIR / f"incident-reflection-{now.strftime('%Y%m%d-%H%M')}.md"
    
    # 构建报告
    report = f"""# 事件触发反思报告

**生成时间**: {now.strftime('%Y-%m-%d %H:%M:%S')}  
**扫描范围**: 最近 1 小时日志  
**触发类型**: {' | '.join(set([e.get('type', 'unknown') for e in critical_errors + user_criticisms + reflection_requests])) or '定时检查'}

---

## 📊 检测摘要

| 类型 | 数量 | 状态 |
|------|------|------|
| 严重错误 | {len(critical_errors)} | {'🔴' if critical_errors else '✅'} |
| 用户批评 | {len(user_criticisms)} | {'⚠️' if user_criticisms else '✅'} |
| 重复问题 | {len(recurring_issues)} | {'🟡' if recurring_issues else '✅'} |
| 反思请求 | {len(reflection_requests)} | {'📝' if reflection_requests else '✅'} |
| SESSION 纠正 | {len(session_corrections)} | {'📌' if session_corrections else '✅'} |

---

## 🔴 严重错误详情

"""
    
    if critical_errors:
        for i, error in enumerate(critical_errors[:10], 1):
            report += f"""
### {i}. {error.get('keyword', 'Unknown')}
- **时间**: {error.get('timestamp', 'Unknown')}
- **内容**: `{error.get('content', 'N/A')[:200]}`
- **类型**: {error.get('type', 'Unknown')}

"""
    else:
        report += "\n✅ 未检测到严重错误\n"
    
    report += f"""
---

## ⚠️ 用户批评详情

"""
    
    if user_criticisms:
        for i, criticism in enumerate(user_criticisms[:10], 1):
            report += f"""
### {i}. 关键词：{criticism.get('keyword', 'Unknown')}
- **时间**: {criticism.get('timestamp', 'Unknown')}
- **内容**: `{criticism.get('content', 'N/A')[:200]}`

"""
    else:
        report += "\n✅ 未检测到用户批评\n"
    
    report += f"""
---

## 🔄 重复问题追踪

"""
    
    if recurring_issues:
        for issue, dates in recurring_issues.items():
            report += f"\n### {issue}\n- 出现次数：{len(dates)}\n- 最近：{', '.join(dates[-3:])}\n"
    else:
        report += "\n✅ 无重复问题\n"
    
    report += f"""
---

## 📝 反思请求

"""
    
    if reflection_requests:
        for i, req in enumerate(reflection_requests[:10], 1):
            report += f"""
### {i}. {req.get('keyword', 'Unknown')}
- **时间**: {req.get('timestamp', 'Unknown')}
- **内容**: `{req.get('content', 'N/A')[:200]}`

"""
    else:
        report += "\n✅ 无反思请求\n"
    
    report += f"""
---

## 📌 SESSION-STATE.md 纠正

"""
    
    if session_corrections:
        for i, corr in enumerate(session_corrections[:10], 1):
            report += f"\n{i}. {corr[:200]}"
    else:
        report += "\n✅ 无未处理纠正\n"
    
    report += f"""

---

## 💡 建议行动

### 立即行动
"""
    
    suggestions = []
    if critical_errors:
        suggestions.append("🔴 优先修复严重错误（数据准确性/API 失败）")
    if user_criticisms:
        suggestions.append("⚠️ 回应用户批评，制定改进措施")
    if recurring_issues:
        top_issue = max(recurring_issues.items(), key=lambda x: len(x[1]))
        suggestions.append(f"🟡 系统性解决重复问题：{top_issue[0]}（出现{len(top_issue[1])}次）")
    if session_corrections:
        suggestions.append("📌 处理 SESSION-STATE.md 中的纠正记录")
    
    if suggestions:
        for sug in suggestions:
            report += f"\n- {sug}"
    else:
        report += "\n✅ 系统运行良好，持续保持"
    
    report += f"""

### 长期改进
- [ ] 建立错误自动修复机制
- [ ] 完善用户反馈响应流程
- [ ] 定期回顾重复问题
- [ ] 优化日志记录质量

---

## 📈 趋势分析

### 本次扫描统计
- 扫描日志行数：{len(critical_errors) + len(user_criticisms) + len(reflection_requests)}
- 触发反思的事件数：{len(critical_errors) + len(user_criticisms) + len(recurring_issues) + len(reflection_requests)}
- 严重性分布：严重{len(critical_errors)} | 警告{len(user_criticisms)} | 提示{len(reflection_requests)}

### 对比历史
- 上次反思：待统计
- 问题趋势：待分析

---

*报告由 Self-Improving 系统自动生成 (event_triggered_reflection.py v1.0)*
"""
    
    report_file.write_text(report, encoding='utf-8')
    log(f"详细报告已保存：{report_file}", "SUCCESS")
    return str(report_file)


def append_to_learnings(incident_type: str, summary: str):
    """追加到 learnings.md"""
    learnings_file = MEMORY_DIR / "learnings.md"
    
    now = datetime.now()
    learning_id = f"LRN-{now.strftime('%Y%m%d')}-{len(list(SELF_IMPROVING_DIR.glob('incident-reflection-*'))) % 100:03d}"
    
    entry = f"""
## [{learning_id}] {incident_type}

**类别**: 事件触发反思  
**严重程度**: 待评估  
**触发时间**: {now.strftime('%Y-%m-%d %H:%M')}

### 问题描述
{summary}

### 根因分析
待分析

### 正确做法
待制定

### 应用范围
- 待补充

---
"""
    
    try:
        if learnings_file.exists():
            content = learnings_file.read_text(encoding='utf-8')
            # 找到"最后更新"之前插入
            if "## [" in content:
                content = content.replace("## [", f"{entry}\n## [", 1)
            else:
                content += entry
        else:
            content = f"# 🦞 学习日志 (Learnings)\n\n**创建时间**: {now.strftime('%Y-%m-%d')}\n**方法**: self-improving-agent\n**目的**: 记录关键经验教训，避免重复错误\n\n---\n{entry}"
        
        learnings_file.write_text(content, encoding='utf-8')
        log(f"已记录到 learnings.md", "SUCCESS")
    except Exception as e:
        log(f"写入 learnings.md 失败：{e}", "ERROR")


def send_feishu_notification(report_file: str, summary: str):
    """发送飞书消息通知（可选）"""
    if not FEISHU_ENABLED:
        return
    
    try:
        # 这里可以集成飞书 Webhook
        log("飞书通知功能已启用（需配置 Webhook）", "INFO")
        # TODO: 实现飞书消息发送
    except Exception as e:
        log(f"发送飞书通知失败：{e}", "ERROR")


# ============================================================================
# 主函数
# ============================================================================

def trigger_reflection(
    trigger_type: str = "manual",
    topic: str = "手动触发反思",
    details: str = "",
    scan_minutes: int = 60,
    send_notification: bool = False
) -> Dict:
    """
    触发反思（可被其他脚本调用）
    
    参数:
        trigger_type: 触发类型 (manual/critical_error/user_criticism/recurring/reflection_request)
        topic: 反思主题
        details: 详细信息
        scan_minutes: 扫描最近 N 分钟的日志
        send_notification: 是否发送通知
    
    返回:
        Dict 包含反思结果
    """
    log("="*60, "REFLECTION")
    log(f"🤔 事件触发反思 | 类型：{trigger_type} | 主题：{topic}", "REFLECTION")
    log("="*60, "REFLECTION")
    
    ensure_directories()
    
    # 1. 扫描日志
    log(f"📊 扫描最近{scan_minutes}分钟日志...", "INFO")
    log_lines = get_recent_logs(scan_minutes)
    log(f"获取日志 {len(log_lines)} 行", "INFO")
    
    # 2. 检测各类事件
    log("🔍 检测严重错误...", "INFO")
    critical_errors = detect_critical_errors(log_lines)
    log(f"发现 {len(critical_errors)} 个严重错误", "WARN" if critical_errors else "SUCCESS")
    
    log("🔍 检测用户批评...", "INFO")
    user_criticisms = detect_user_criticism(log_lines)
    log(f"发现 {len(user_criticisms)} 条用户批评", "WARN" if user_criticisms else "SUCCESS")
    
    log("🔍 检测重复问题...", "INFO")
    corrections_file = SELF_IMPROVING_DIR / "corrections.md"
    recurring_issues = detect_recurring_issues(corrections_file)
    log(f"发现 {len(recurring_issues)} 类重复问题", "WARN" if recurring_issues else "SUCCESS")
    
    log("🔍 检测反思请求...", "INFO")
    reflection_requests = detect_reflection_request(log_lines)
    log(f"发现 {len(reflection_requests)} 个反思请求", "INFO" if reflection_requests else "SUCCESS")
    
    log("🔍 检查 SESSION-STATE.md 纠正...", "INFO")
    session_corrections = get_session_state_corrections()
    log(f"发现 {len(session_corrections)} 条未处理纠正", "WARN" if session_corrections else "SUCCESS")
    
    # 3. 判断是否需要反思
    should_reflect = (
        len(critical_errors) > 0 or
        len(user_criticisms) > 0 or
        len(recurring_issues) > 0 or
        len(reflection_requests) > 0 or
        len(session_corrections) > 0 or
        trigger_type == "manual"
    )
    
    if not should_reflect:
        log("✅ 无需反思，系统运行良好", "SUCCESS")
        return {"reflected": False, "reason": "no_trigger"}
    
    # 4. 记录到 corrections.md
    incident = {
        "topic": topic,
        "trigger_type": trigger_type,
        "severity": "high" if critical_errors else "medium" if user_criticisms else "low"
    }
    
    full_details = f"""
**触发类型**: {trigger_type}
**主题**: {topic}

**检测到的问题**:
- 严重错误：{len(critical_errors)} 个
- 用户批评：{len(user_criticisms)} 条
- 重复问题：{len(recurring_issues)} 类
- 反思请求：{len(reflection_requests)} 个
- SESSION 纠正：{len(session_corrections)} 条

**原始信息**:
{details or '无额外信息'}
"""
    
    append_to_corrections(incident, full_details)
    
    # 5. 创建详细报告
    report_file = create_incident_reflection_report(
        critical_errors, user_criticisms, recurring_issues,
        reflection_requests, session_corrections
    )
    
    # 6. 记录到 learnings.md
    learning_summary = f"""
触发类型：{trigger_type}
主题：{topic}

检测到的问题:
- 严重错误：{len(critical_errors)} 个
- 用户批评：{len(user_criticisms)} 条
- 重复问题：{len(recurring_issues)} 类
- 反思请求：{len(reflection_requests)} 个
- SESSION 纠正：{len(session_corrections)} 条

详细报告：{report_file}
"""
    append_to_learnings(trigger_type, learning_summary)
    
    # 7. 发送通知（可选）
    if send_notification:
        send_feishu_notification(report_file, learning_summary)
    
    # 8. 输出总结
    log("\n" + "="*60, "REFLECTION")
    log("📋 事件触发反思总结", "REFLECTION")
    log("="*60, "REFLECTION")
    log(f"触发类型：{trigger_type}", "INFO")
    log(f"严重错误：{len(critical_errors)} 个", "WARN" if critical_errors else "SUCCESS")
    log(f"用户批评：{len(user_criticisms)} 条", "WARN" if user_criticisms else "SUCCESS")
    log(f"重复问题：{len(recurring_issues)} 类", "WARN" if recurring_issues else "SUCCESS")
    log(f"反思请求：{len(reflection_requests)} 个", "INFO" if reflection_requests else "SUCCESS")
    log(f"反思报告：{report_file}", "SUCCESS")
    log("="*60, "REFLECTION")
    log("\n✅ 事件触发反思完成 (v1.0)", "SUCCESS")
    log("="*60, "REFLECTION")
    
    return {
        "reflected": True,
        "trigger_type": trigger_type,
        "topic": topic,
        "critical_errors": len(critical_errors),
        "user_criticisms": len(user_criticisms),
        "recurring_issues": len(recurring_issues),
        "reflection_requests": len(reflection_requests),
        "session_corrections": len(session_corrections),
        "report_file": report_file
    }


def main():
    """主函数（独立运行）"""
    result = trigger_reflection(
        trigger_type="manual",
        topic="手动触发反思",
        scan_minutes=60,
        send_notification=False
    )
    
    if result["reflected"]:
        print(f"\n✅ 反思完成！报告已保存到：{result['report_file']}")
        sys.exit(0)
    else:
        print("\n✅ 无需反思，系统运行良好")
        sys.exit(0)


if __name__ == "__main__":
    main()

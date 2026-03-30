#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每周反思脚本 v2.0 - 增强版
执行时间：每周六 20:00
功能：深度反思、模式分析、系统化整理、趋势对比、改进措施检查

增强功能：
1. 问题分类统计 — 按类别统计（数据准确性/配置/API/技能/性能/用户批评）
2. 趋势分析 — 本周 vs 上周对比（改善/恶化）
3. 改进措施落实检查 — 检查上周制定的改进措施是否真正执行
4. 结构化报告 — 生成 Markdown 报告 + 简单图表（ASCII 或表格）
5. 可视化 — 用表格/图表展示问题分布、趋势
"""

import subprocess
import sys
import os
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter

SELF_IMPROVING_DIR = Path.home() / "self-improving"
WORKSPACE_DIR = Path.home() / ".openclaw" / "workspace"

# 问题分类定义
CATEGORIES = {
    '数据准确性': ['数据', '价格', '收盘价', '收盘价', '涨跌幅', ' inaccurate', '错误', '不对', 'wrong'],
    '配置问题': ['配置', '设置', 'config', '持久化', '丢失', '隔夜', 'commit', 'git'],
    'API 问题': ['API', 'api', '接口', 'timeout', '限流', '429', 'rate limit'],
    '技能问题': ['技能', 'skill', '功能', '不会', '不能', '不支持'],
    '性能问题': ['慢', '卡顿', '性能', 'timeout', '超时', '加载'],
    '用户批评': ['批评', '不满意', '失望', '很差', '不好', 'wrong', 'incorrect'],
}

def log(message):
    """打印日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def get_week_start(date=None):
    """获取指定日期所在周的开始日期（周一）"""
    if date is None:
        date = datetime.now()
    return date - timedelta(days=date.weekday())

def get_week_range(date=None):
    """获取指定日期所在周的起止日期"""
    start = get_week_start(date)
    end = start + timedelta(days=6)
    return start, end

def parse_corrections_by_week():
    """按周解析纠正记录"""
    corrections_file = SELF_IMPROVING_DIR / "corrections.md"
    
    if not corrections_file.exists():
        log("⚠️ corrections.md 不存在")
        return {}
    
    content = corrections_file.read_text(encoding='utf-8')
    
    # 按日期解析纠正记录
    weekly_data = {}
    date_pattern = r'\[(\d{4}-\d{2}-\d{2})\s+\d{2}:\d{2}\]'
    current_date = None
    current_text = []
    
    for line in content.split('\n'):
        date_match = re.search(date_pattern, line)
        if date_match:
            # 保存之前的记录
            if current_date and current_text:
                week_start = get_week_start(datetime.strptime(current_date, '%Y-%m-%d'))
                week_key = week_start.strftime('%Y-%m-%d')
                if week_key not in weekly_data:
                    weekly_data[week_key] = []
                weekly_data[week_key].append('\n'.join(current_text))
            
            # 开始新记录
            current_date = date_match.group(1)
            current_text = [line]
        elif current_date:
            current_text.append(line)
    
    # 保存最后一条记录
    if current_date and current_text:
        week_start = get_week_start(datetime.strptime(current_date, '%Y-%m-%d'))
        week_key = week_start.strftime('%Y-%m-%d')
        if week_key not in weekly_data:
            weekly_data[week_key] = []
        weekly_data[week_key].append('\n'.join(current_text))
    
    return weekly_data

def classify_correction(text):
    """对单条纠正进行分类"""
    categories = []
    text_lower = text.lower()
    
    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                categories.append(category)
                break
    
    return categories if categories else ['其他']

def analyze_corrections_detailed():
    """详细分析本周纠正"""
    log("📝 分析本周纠正...")
    
    weekly_data = parse_corrections_by_week()
    now = datetime.now()
    current_week_start = get_week_start(now)
    current_week_key = current_week_start.strftime('%Y-%m-%d')
    last_week_start = current_week_start - timedelta(days=7)
    last_week_key = last_week_start.strftime('%Y-%m-%d')
    
    # 本周数据
    this_week_corrections = weekly_data.get(current_week_key, [])
    last_week_corrections = weekly_data.get(last_week_key, [])
    
    # 分类统计
    this_week_categories = Counter()
    last_week_categories = Counter()
    
    for correction in this_week_corrections:
        cats = classify_correction(correction)
        for cat in cats:
            this_week_categories[cat] += 1
    
    for correction in last_week_corrections:
        cats = classify_correction(correction)
        for cat in cats:
            last_week_categories[cat] += 1
    
    # 提取改进措施
    this_week_actions = extract_action_items(this_week_corrections)
    last_week_actions = extract_action_items(last_week_corrections)
    
    result = {
        'this_week': {
            'count': len(this_week_corrections),
            'categories': dict(this_week_categories),
            'actions': this_week_actions,
        },
        'last_week': {
            'count': len(last_week_corrections),
            'categories': dict(last_week_categories),
            'actions': last_week_actions,
        }
    }
    
    log(f"✅ 本周纠正：{len(this_week_corrections)} 条，上周：{len(last_week_corrections)} 条")
    return result

def extract_action_items(corrections):
    """从纠正记录中提取改进措施"""
    actions = []
    
    for correction in corrections:
        # 查找改进措施部分
        if '**改进措施**:' not in correction and '改进措施' not in correction:
            continue
        
        # 按行处理
        in_action_section = False
        for line in correction.split('\n'):
            line = line.strip()
            
            # 检测改进措施部分开始
            if '改进措施' in line:
                in_action_section = True
                continue
            
            # 检测部分结束（空行或其他标题）
            if in_action_section and (line.startswith('**状态**') or line.startswith('---') or (line == '' and len(actions) > 0)):
                in_action_section = False
                continue
            
            # 提取改进措施项
            if in_action_section and (line.startswith('-') or line.startswith('*')):
                # 清理格式
                action_text = re.sub(r'^[-*]\s*', '', line)
                action_text = action_text.replace('✅', '').replace('❌', '').replace('□', '').strip()
                
                if action_text and len(action_text) > 5 and not action_text.startswith('['):
                    # 检查是否已完成
                    completed = '已' in action_text and ('完成' in action_text or '实施' in action_text or '修正' in action_text)
                    actions.append({
                        'text': action_text,
                        'completed': completed
                    })
    
    return actions

def check_action_implementation(actions):
    """检查改进措施是否真正执行"""
    log("🔍 检查改进措施落实情况...")
    
    implemented = []
    pending = []
    
    for action in actions:
        if action['completed']:
            implemented.append(action)
        else:
            pending.append(action)
    
    # 检查 workspace 中的相关文件
    # 例如：如果措施提到"创建 xxx.py"，检查文件是否存在
    
    for action in pending:
        text = action['text']
        
        # 检查是否提到创建文件
        file_match = re.search(r'创建 [^\s]+\.py', text)
        if file_match:
            filename = file_match.group(0).replace('创建', '')
            filepath = WORKSPACE_DIR / "scripts" / filename
            if filepath.exists():
                action['verified'] = True
                log(f"  ✅ 已验证：{filename}")
            else:
                action['verified'] = False
                log(f"  ⚠️ 未找到：{filename}")
    
    log(f"✅ 已落实：{len(implemented)} 项，待落实：{len(pending)} 项")
    return implemented, pending

def analyze_trends(weekly_data):
    """分析趋势（本周 vs 上周）"""
    log("📊 分析趋势...")
    
    trends = []
    
    # 获取本周和上周数据
    now = datetime.now()
    current_week_key = get_week_start(now).strftime('%Y-%m-%d')
    last_week_key = (get_week_start(now) - timedelta(days=7)).strftime('%Y-%m-%d')
    
    this_week = weekly_data.get('this_week', {})
    last_week = weekly_data.get('last_week', {})
    
    # 纠正数量趋势
    this_count = this_week.get('count', 0)
    last_count = last_week.get('count', 0)
    
    if this_count > last_count and last_count > 0:
        change = ((this_count - last_count) / last_count) * 100
        trends.append({
            'metric': '纠正数量',
            'this': this_count,
            'last': last_count,
            'change': f'+{change:.1f}%',
            'trend': '恶化' if change > 20 else '稳定'
        })
    elif this_count < last_count:
        change = ((last_count - this_count) / last_count) * 100 if last_count > 0 else 0
        trends.append({
            'metric': '纠正数量',
            'this': this_count,
            'last': last_count,
            'change': f'-{change:.1f}%',
            'trend': '改善'
        })
    else:
        trends.append({
            'metric': '纠正数量',
            'this': this_count,
            'last': last_count,
            'change': '0%',
            'trend': '稳定'
        })
    
    # 分类趋势
    this_cats = this_week.get('categories', {})
    last_cats = last_week.get('categories', {})
    
    all_categories = set(this_cats.keys()) | set(last_cats.keys())
    
    for cat in all_categories:
        this_val = this_cats.get(cat, 0)
        last_val = last_cats.get(cat, 0)
        
        if this_val > last_val:
            trend = '增加'
        elif this_val < last_val:
            trend = '减少'
        else:
            trend = '持平'
        
        trends.append({
            'metric': cat,
            'this': this_val,
            'last': last_val,
            'change': f'{this_val - last_val:+d}',
            'trend': trend
        })
    
    log(f"✅ 趋势分析完成：{len(trends)} 项指标")
    return trends

def generate_ascii_bar(value, max_value, width=30):
    """生成 ASCII 条形图"""
    if max_value == 0:
        return ''
    filled = int((value / max_value) * width)
    return '█' * filled + '░' * (width - filled)

def generate_category_chart(categories):
    """生成分类统计的 ASCII 图表"""
    if not categories:
        return "暂无数据"
    
    max_val = max(categories.values()) if categories else 0
    lines = []
    
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        bar = generate_ascii_bar(count, max_val, 20)
        lines.append(f"{cat:12} | {bar} {count}")
    
    return '\n'.join(lines)

def generate_trend_table(trends):
    """生成趋势对比表格"""
    lines = []
    lines.append("| 指标 | 本周 | 上周 | 变化 | 趋势 |")
    lines.append("|------|------|------|------|------|")
    
    for trend in trends:
        trend_icon = '📈' if trend['trend'] == '改善' else ('📉' if trend['trend'] == '恶化' else '➡️')
        lines.append(f"| {trend['metric']} | {trend['this']} | {trend['last']} | {trend['change']} | {trend_icon} {trend['trend']} |")
    
    return '\n'.join(lines)

def generate_report(analysis_result, trends, implemented, pending):
    """生成详细的每周反思报告"""
    log("📄 生成反思报告...")
    
    week_start, week_end = get_week_range()
    report_file = SELF_IMPROVING_DIR / f"weekly-reflection-{datetime.now().strftime('%Y%m%d')}.md"
    
    this_week = analysis_result['this_week']
    last_week = analysis_result['last_week']
    
    report = f"""# 📊 每周反思报告

**周期**: {week_start.strftime('%Y-%m-%d')} ~ {week_end.strftime('%Y-%m-%d')}  
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**报告版本**: v2.0 (增强版)

---

## 📈 核心指标概览

| 指标 | 本周 | 上周 | 变化 | 状态 |
|------|------|------|------|------|
| 纠正总数 | {this_week['count']} | {last_week['count']} | {this_week['count'] - last_week['count']:+d} | {'📈' if this_week['count'] < last_week['count'] else '📉'} |
| 改进措施 | {len(this_week['actions'])} | {len(last_week['actions'])} | {len(this_week['actions']) - len(last_week['actions']):+d} | ➡️ |
| 已落实 | {len(implemented)} | - | - | ✅ |
| 待落实 | {len(pending)} | - | - | ⏳ |

---

## 📊 问题分类统计

### 本周问题分布

```
{generate_category_chart(this_week['categories'])}
```

### 分类对比趋势

{generate_trend_table(trends)}

---

## 🔍 改进措施落实检查

### ✅ 已落实措施 ({len(implemented)} 项)

"""
    
    if implemented:
        for i, action in enumerate(implemented, 1):
            report += f"{i}. {action['text']}\n"
    else:
        report += "暂无已落实措施\n"
    
    report += f"""
### ⏳ 待落实措施 ({len(pending)} 项)

"""
    
    if pending:
        for i, action in enumerate(pending, 1):
            verified = "✅ 已验证" if action.get('verified') else "⚠️ 未验证"
            report += f"{i}. {action['text']} [{verified}]\n"
    else:
        report += "所有措施已落实 ✅\n"
    
    report += f"""
---

## 💡 关键学习与洞察

### 本周主要问题
"""
    
    # 分析主要问题类别
    if this_week['categories']:
        top_category = max(this_week['categories'].items(), key=lambda x: x[1])
        report += f"- **最突出问题**: {top_category[0]} ({top_category[1]} 次)\n"
    
    # 趋势洞察
    improving = [t for t in trends if t['trend'] == '改善']
    worsening = [t for t in trends if t['trend'] == '恶化']
    
    if improving:
        report += f"- **改善领域**: {', '.join([t['metric'] for t in improving])}\n"
    if worsening:
        report += f"- **需关注**: {', '.join([t['metric'] for t in worsening])}\n"
    
    report += f"""
---

## 🎯 下周改进计划

### 优先级 1 - 立即执行
- [ ] 落实待完成的 {len(pending)} 项改进措施
- [ ] 针对 {this_week['categories'].get('配置问题', 0) > 0 and '配置问题' or '主要问题类别'} 制定专项改进

### 优先级 2 - 持续优化
- [ ] 减少重复性错误（相同问题出现 2 次以上）
- [ ] 建立自动化检测机制
- [ ] 完善文档和配置持久化

### 优先级 3 - 长期建设
- [ ] 优化 Self-Improving 系统
- [ ] 建立模式识别机制
- [ ] 提升主动纠错能力

---

## 📊 历史趋势

### 近 4 周纠正数量

"""
    
    # 生成近 4 周的趋势
    weekly_data = parse_corrections_by_week()
    weeks = []
    for i in range(4):
        week_date = datetime.now() - timedelta(weeks=i)
        week_key = get_week_start(week_date).strftime('%Y-%m-%d')
        count = len(weekly_data.get(week_key, []))
        weeks.append((week_date.strftime('%m/%d'), count))
    
    weeks.reverse()  # 按时间顺序
    
    max_count = max([w[1] for w in weeks]) if weeks else 1
    for week_label, count in weeks:
        bar = generate_ascii_bar(count, max_count, 20)
        report += f"{week_label}: {bar} ({count})\n"
    
    report += f"""
---

## 🧠 系统化记忆更新

本周关键学习已同步至 `memory.md`，包括：

1. **新增规则** - 从纠正中提炼的可复用规则
2. **工作习惯** - 需要持续保持的良好实践
3. **待确认模式** - 需要 3 次验证后成为规则

---

## 📬 飞书周报摘要

**标题**: 每周反思 | {week_start.strftime('%m/%d')}-{week_end.strftime('%m/%d')}

**核心数据**:
- 纠正总数：{this_week['count']} 条（上周：{last_week['count']} 条）
- 主要问题：{list(this_week['categories'].keys())[:3] if this_week['categories'] else ['无']}
- 改进措施：已落实 {len(implemented)} 项，待落实 {len(pending)} 项
- 整体趋势：{'📈 改善' if this_week['count'] < last_week['count'] else '📉 需关注'}

**关键行动**:
{chr(10).join([f"- {a['text'][:50]}..." for a in pending[:3]]) if pending else "- 无待办事项"}

---

*报告由 Self-Improving 系统 v2.0 自动生成*
*下次反思时间：{get_week_start(datetime.now() + timedelta(weeks=1)).strftime('%Y-%m-%d')} 20:00*
"""
    
    report_file.write_text(report, encoding='utf-8')
    log(f"✅ 报告已保存到：{report_file}")
    
    return report_file

def update_memory(analysis_result):
    """系统化整理记忆"""
    log("🧠 更新 memory.md...")
    memory_file = SELF_IMPROVING_DIR / "memory.md"
    
    if not memory_file.exists():
        memory_file.parent.mkdir(parents=True, exist_ok=True)
        memory_file.write_text("# 🧠 Self-Improving Memory (HOT Tier)\n\n", encoding='utf-8')
    
    content = memory_file.read_text(encoding='utf-8')
    
    # 提取本周新增规则
    this_week = analysis_result['this_week']
    categories = this_week.get('categories', {})
    actions = this_week.get('actions', [])
    
    # 生成更新内容
    week_start, week_end = get_week_range()
    week_key = f"{week_start.strftime('%Y-%m-%d')} ~ {week_end.strftime('%Y-%m-%d')}"
    
    # 检查是否已存在本周更新（避免重复）
    if f"## 本周更新 ({week_key})" in content:
        log("ℹ️  本周更新已存在，跳过")
        return
    
    update_section = f"""
## 本周更新 ({week_key})

### 问题统计
- 总纠正数：{this_week['count']} 条
- 主要类别：{', '.join([f'{k}({v})' for k, v in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:3]]) if categories else '无'}

### 新增规则
"""
    
    # 从纠正中提取规则
    if categories.get('配置问题', 0) > 0:
        update_section += "- 配置修改后立即 git commit + push\n"
    if categories.get('数据准确性', 0) > 0:
        update_section += "- 所有数据必须来自可靠 API，禁止硬编码\n"
    if categories.get('技能问题', 0) > 0:
        update_section += "- 技能使用前检查配置和依赖\n"
    
    update_section += f"""
### 改进措施 ({len(actions)} 项)
"""
    
    for action in actions[:5]:  # 最多 5 项
        status = "✅" if action['completed'] else "⏳"
        update_section += f"- {status} {action['text'][:50]}...\n"
    
    if not actions:
        update_section += "无新增改进措施\n"
    
    update_section += f"""
### 工作习惯
- 长任务（>2 分钟）每 1 分钟汇报进展
- 完成立即通知，不等待用户询问
- 失败详细说明原因 + 建议方案

---

"""
    
    # 插入到文件开头（在标题之后）
    lines = content.split('\n', 1)
    if len(lines) > 1:
        new_content = lines[0] + '\n' + update_section + lines[1]
    else:
        new_content = update_section + content
    
    memory_file.write_text(new_content, encoding='utf-8')
    log("✅ memory.md 已更新")

def send_feishu_summary(report_file):
    """发送飞书消息（可选功能）"""
    log("📬 准备飞书消息...")
    # 这里可以集成飞书 API
    # 目前仅记录日志
    log("ℹ️  飞书消息功能待实现（需要 API 配置）")

def main():
    """主函数"""
    log("="*60)
    log("🌟 每周反思 v2.0 (增强版) | " + datetime.now().strftime('%Y-%m-%d %H:%M'))
    log("="*60)
    
    # 1. 详细分析纠正
    analysis_result = analyze_corrections_detailed()
    
    # 2. 解析周数据用于趋势分析
    weekly_data = parse_corrections_by_week()
    
    # 3. 分析趋势
    trends = analyze_trends(analysis_result)
    
    # 4. 检查改进措施落实情况
    this_week_actions = analysis_result['this_week']['actions']
    implemented, pending = check_action_implementation(this_week_actions)
    
    # 5. 生成详细报告
    report_file = generate_report(analysis_result, trends, implemented, pending)
    
    # 6. 更新 memory.md
    update_memory(analysis_result)
    
    # 7. 发送飞书消息（可选）
    send_feishu_summary(report_file)
    
    # 8. 输出总结
    log("\n" + "="*60)
    log("📋 本周反思总结")
    log("="*60)
    log(f"纠正总数：本周 {analysis_result['this_week']['count']} 条 vs 上周 {analysis_result['last_week']['count']} 条")
    log(f"问题分类：{analysis_result['this_week']['categories']}")
    log(f"改进措施：已落实 {len(implemented)} 项，待落实 {len(pending)} 项")
    log(f"趋势分析：{len(trends)} 项指标")
    log(f"报告文件：{report_file.name}")
    log("="*60)
    log("\n✅ 每周反思完成 (v2.0)")
    log("="*60)

if __name__ == "__main__":
    main()

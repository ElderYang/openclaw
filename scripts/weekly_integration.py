#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每周整合脚本：将 Self-Improving 的 corrections.md 整合到 learnings.md
执行时间：每周日 19:00（在每周深度反思前）
"""

import os
from datetime import datetime
from pathlib import Path

# ==================== 配置 ====================

SELF_IMPROVING_DIR = Path.home() / 'self-improving'
WORKSPACE_MEMORY = Path('/Users/yangbowen/.openclaw/workspace/memory')

CORRECTIONS_FILE = SELF_IMPROVING_DIR / 'corrections.md'
LEARNINGS_FILE = WORKSPACE_MEMORY / 'learnings.md'
INTEGRATION_LOG = WORKSPACE_MEMORY / 'integration-log.md'

# ==================== 工具函数 ====================

def parse_corrections():
    """解析 corrections.md 文件"""
    if not CORRECTIONS_FILE.exists():
        return []
    
    corrections = []
    with open(CORRECTIONS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
        
        # 简单解析：每个纠正以日期开头
        lines = content.split('\n')
        current_correction = []
        current_date = None
        
        for line in lines:
            if line.startswith('## ') or line.startswith('### '):
                # 保存之前的纠正
                if current_correction and current_date:
                    corrections.append({
                        'date': current_date,
                        'content': '\n'.join(current_correction)
                    })
                current_correction = [line]
                current_date = line.replace('## ', '').replace('### ', '').strip()
            elif current_correction is not None:
                current_correction.append(line)
        
        # 保存最后一个
        if current_correction and current_date:
            corrections.append({
                'date': current_date,
                'content': '\n'.join(current_correction)
            })
    
    return corrections

def get_last_integration_date():
    """获取上次整合日期"""
    if not INTEGRATION_LOG.exists():
        return None
    
    with open(INTEGRATION_LOG, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in reversed(lines):
            if '整合日期:' in line:
                return line.split('整合日期:')[1].strip()
    return None

def format_learning_entry(correction, index):
    """格式化学习条目"""
    today = datetime.now().strftime('%Y%m%d')
    learning_id = f"LRN-{today}-{index:03d}"
    
    # 提取纠正内容的关键信息
    content = correction['content']
    
    # 尝试分类
    category = "通用"
    if any(kw in content for kw in ['数据', '收盘价', '涨跌幅']):
        category = "数据准确性"
    elif any(kw in content for kw in ['配置', '环境', 'Token', 'API']):
        category = "配置管理"
    elif any(kw in content for kw in ['技能', '安装', '删除']):
        category = "技能管理"
    elif any(kw in content for kw in ['性能', '优化', '速度']):
        category = "性能优化"
    
    entry = f"""
## [{learning_id}] 从纠正中学习

**类别**: {category}
**来源**: Self-Improving corrections.md
**原始日期**: {correction['date']}
**整合日期**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

### 纠正内容
{content}

### 经验教训
（从此纠正中提炼的经验）

### 应用范围
（适用的场景）
"""
    return entry

def integrate_corrections():
    """执行整合"""
    print("🔄 开始整合 Self-Improving corrections.md 到 learnings.md...\n")
    
    # 获取纠正
    corrections = parse_corrections()
    if not corrections:
        print("✅ 没有新的纠正记录")
        return 0
    
    # 获取上次整合日期
    last_date = get_last_integration_date()
    
    # 过滤新纠正
    new_corrections = []
    for c in corrections:
        if last_date is None or c['date'] > last_date:
            new_corrections.append(c)
    
    if not new_corrections:
        print(f"✅ 没有新纠正需要整合（上次整合：{last_date}）")
        return 0
    
    print(f"📊 发现 {len(new_corrections)} 条新纠正\n")
    
    # 添加到 learnings.md
    learnings_entries = []
    for i, correction in enumerate(new_corrections, 1):
        entry = format_learning_entry(correction, i)
        learnings_entries.append(entry)
        print(f"  ✅ 处理：{correction['date'][:50]}...")
    
    # 写入 learnings.md
    if LEARNINGS_FILE.exists():
        with open(LEARNINGS_FILE, 'a', encoding='utf-8') as f:
            f.write("\n\n---\n\n")
            f.write(f"## 🔄 整合自 Self-Improving ({datetime.now().strftime('%Y-%m-%d')})\n")
            f.write("\n")
            for entry in learnings_entries:
                f.write(entry)
    else:
        with open(LEARNINGS_FILE, 'w', encoding='utf-8') as f:
            f.write("# 🦞 学习日志 (Learnings)\n\n")
            for entry in learnings_entries:
                f.write(entry)
    
    # 更新整合日志
    with open(INTEGRATION_LOG, 'a', encoding='utf-8') as f:
        f.write(f"\n## 整合记录\n")
        f.write(f"**整合日期**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"**整合数量**: {len(new_corrections)} 条\n")
        f.write(f"**来源文件**: corrections.md\n")
        f.write(f"**目标文件**: learnings.md\n")
        f.write(f"\n### 整合条目\n")
        for i, c in enumerate(new_corrections, 1):
            f.write(f"{i}. {c['date'][:60]}...\n")
        f.write("\n---\n\n")
    
    print(f"\n✅ 整合完成！")
    print(f"   - 新增学习条目：{len(new_corrections)} 条")
    print(f"   - 目标文件：{LEARNINGS_FILE}")
    print(f"   - 整合日志：{INTEGRATION_LOG}")
    
    return len(new_corrections)

def main():
    """主函数"""
    try:
        count = integrate_corrections()
        
        if count > 0:
            print(f"\n📈 下次整合：下周日 19:00")
        else:
            print(f"\n💡 提示：没有新纠正需要整合")
            
    except Exception as e:
        print(f"\n❌ 整合失败：{e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

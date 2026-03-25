#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日 Obsidian 自动整理脚本
功能：
1. 生成当日工作记录
2. 整理聊天记录
3. 更新 API 使用统计
4. 生成周报/月报（到时间自动）
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 添加脚本目录到路径
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

# Obsidian Vault 路径
OBSIDIAN_VAULT = Path('/Users/yangbowen/Documents/Obsidian Vault/OpenClaw')

def ensure_folders():
    """确保目录存在"""
    folders = [
        OBSIDIAN_VAULT / '工作记录',
        OBSIDIAN_VAULT / 'API 配置',
        OBSIDIAN_VAULT / '调度任务',
        OBSIDIAN_VAULT / '聊天记录',
        OBSIDIAN_VAULT / '技术文档',
        OBSIDIAN_VAULT / '模板',
    ]
    for folder in folders:
        folder.mkdir(parents=True, exist_ok=True)
    print(f"✅ 目录检查完成：{OBSIDIAN_VAULT}")

def read_stock_log():
    """读取股市报告日志"""
    log_file = Path('/tmp/openclaw/stock-review.log')
    if not log_file.exists():
        return None
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except:
        return None

def parse_log_stats(log_content):
    """解析日志统计数据"""
    stats = {
        'execution_time': 'N/A',
        'data_completeness': 'N/A',
        'holdings': 'N/A',
        'industry_source': 'N/A',
        'top_sectors': 'N/A',
    }
    
    if not log_content:
        return stats
    
    # 提取执行时间
    import re
    time_match = re.search(r'总执行时间：(\d+\.?\d*)秒', log_content)
    if time_match:
        stats['execution_time'] = f"{time_match.group(1)}秒"
    
    # 提取数据完整度
    completeness_match = re.search(r'数据完整度.*?(\d+)%', log_content)
    if completeness_match:
        stats['data_completeness'] = f"{completeness_match.group(1)}%"
    
    # 提取持仓数据
    holdings_match = re.search(r'持仓数据.*?(\d+)/(\d+)', log_content)
    if holdings_match:
        stats['holdings'] = f"{holdings_match.group(1)}/{holdings_match.group(2)}"
    
    # 提取行业板块数据源
    industry_match = re.search(r'行业板块.*?✅ (.*?) \d+\.?\d*秒', log_content)
    if industry_match:
        stats['industry_source'] = industry_match.group(1)
    
    # 提取领涨板块
    sector_match = re.search(r'市场主线.*?✅ 主线:(.*?)\n', log_content)
    if sector_match:
        stats['top_sectors'] = sector_match.group(1).strip()
    
    return stats

def generate_daily_summary():
    """生成每日工作记录"""
    today = datetime.now()
    date_str = today.strftime('%Y-%m-%d')
    
    print(f"\n📝 生成 {date_str} 工作记录...")
    
    # 读取日志
    log_content = read_stock_log()
    stats = parse_log_stats(log_content)
    
    # 生成笔记内容
    content = f"""# {date_str} 工作记录

**创建时间**:: {today.strftime('%Y-%m-%d %H:%M')}
**标签**:: #OpenClaw #工作记录 #每日总结

---

## 📊 今日工作概览

### 定时任务执行
- **股市早报**：{'✅ 成功' if log_content else '⏰ 待执行'}（7:30）
- **A 股复盘**：{'✅ 成功' if log_content else '⏰ 待执行'}（17:30，工作日）

### 关键指标
| 指标 | 数值 | 状态 |
|------|------|------|
| 执行时间 | {stats['execution_time']} | {'✅' if stats['execution_time'] != 'N/A' and float(stats['execution_time'].replace('秒', '')) < 120 else '⚠️'} |
| 数据完整度 | {stats['data_completeness']} | {'✅' if stats['data_completeness'] != 'N/A' and int(stats['data_completeness'].replace('%', '')) >= 90 else '⚠️'} |
| 持仓数据 | {stats['holdings']} | {'✅' if stats['holdings'] != 'N/A' else '⚠️'} |
| 行业数据源 | {stats['industry_source']} | {'✅' if 'mx-stocks' in stats['industry_source'] or 'QVeris' in stats['industry_source'] else '⚠️'} |

### 市场主线
**领涨板块**：{stats['top_sectors']}

---

## ✅ 完成事项

- [ ] 检查定时任务执行情况
- [ ] 验证数据完整度
- [ ] 查看 API 配额使用
- [ ] 整理聊天记录
- [ ] 更新技术文档

---

## 💡 今日学习

### 技术要点
1. {待填写}
2. {待填写}
3. {待填写}

### 问题与解决
1. **问题**：{待填写}
   **解决**：{待填写}

---

## 📋 明日计划

- [ ] {待填写}
- [ ] {待填写}

---

## 🔗 相关链接
- [[API 配置清单]]
- [[定时任务配置]]
- [[缓存策略设计]]

---

*本记录由 OpenClaw 自动生成*
"""
    
    # 保存文件
    output_file = OBSIDIAN_VAULT / '工作记录' / f'{date_str} 工作记录.md'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 工作记录已保存：{output_file}")
    return output_file

def check_weekly_report():
    """检查并生成周报（每周一 9:00）"""
    today = datetime.now()
    
    # 如果是周一且时间是 9-10 点
    if today.weekday() == 0 and 9 <= today.hour < 10:
        print("\n📊 生成周报...")
        # TODO: 实现周报生成逻辑
        print("⏳ 周报生成功能待实现")

def check_monthly_report():
    """检查并生成月报（每月 1 日 10:00）"""
    today = datetime.now()
    
    # 如果是每月 1 日且时间是 10-11 点
    if today.day == 1 and 10 <= today.hour < 11:
        print("\n📈 生成月报...")
        # TODO: 实现月报生成逻辑
        print("⏳ 月报生成功能待实现")

def main():
    """主函数"""
    print("="*60)
    print("📝 Obsidian 每日自动整理")
    print("="*60)
    print(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 确保目录存在
    ensure_folders()
    
    # 生成每日总结
    generate_daily_summary()
    
    # 检查周报/月报
    check_weekly_report()
    check_monthly_report()
    
    print("\n" + "="*60)
    print("✅ Obsidian 自动整理完成")
    print("="*60)

if __name__ == '__main__':
    main()

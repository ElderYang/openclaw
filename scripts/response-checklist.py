#!/usr/bin/env python3
"""
响应前自动检查脚本
每次回复前必须运行此检查
"""

import json
import os
from datetime import datetime

CHECKLIST = """
## 📋 响应前检查清单

### 1. 任务追踪
- [ ] 是否有后台任务在执行？
- [ ] 是否有任务已完成但未通知？
- [ ] 是否需要汇报进度？

### 2. 反馈规范
- [ ] 长任务是否告知了预计时间？
- [ ] 超过 2 分钟的任务是否汇报了进度？
- [ ] 任务完成是否主动通知了？
- [ ] 任务失败是否说明了原因 + 建议？

### 3. 问题回答
- [ ] 用户的问题是否都回答了？
- [ ] 是否有遗漏的问题？
- [ ] 回答是否清晰完整？

### 4. 身份标识
- [ ] 是否添加了角色标签？
  - 【小红书助手】- 小红书相关
  - 【股市分析师】- 股市相关
  - 【个人助手】- 其他

### 5. 下一步行动
- [ ] 是否告知了下一步做什么？
- [ ] 是否需要用户确认？
- [ ] 是否有待办事项？
"""

def check_active_tasks():
    """检查进行中的任务"""
    tracker_file = os.path.expanduser("~/.openclaw/workspace/task-tracker.json")
    if os.path.exists(tracker_file):
        with open(tracker_file) as f:
            data = json.load(f)
            active = data.get("active_tasks", [])
            if active:
                print(f"⚠️ 发现 {len(active)} 个进行中的任务")
                for task in active:
                    print(f"  - {task.get('name', '未知任务')}: {task.get('status', '未知')}")
            else:
                print("✅ 无进行中的任务")
    else:
        print("⚠️ 任务追踪文件不存在")

def check_time_since_last_response():
    """检查距离上次回复的时间"""
    # TODO: 读取会话历史，检查上次回复时间
    print("⏰ 检查回复间隔...")

def main():
    print("=" * 60)
    print("📋 响应前检查清单")
    print("=" * 60)
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print(CHECKLIST)
    print()
    
    print("=" * 60)
    print("🔍 自动检查")
    print("=" * 60)
    check_active_tasks()
    print()
    
    print("=" * 60)
    print("✅ 检查完成！请确认以上所有项目后再回复")
    print("=" * 60)

if __name__ == "__main__":
    main()

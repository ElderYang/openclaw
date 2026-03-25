#!/bin/bash
# 日常记忆自动保存脚本
# 每天运行一次，自动总结当天的重要对话和任务

set -e

DATE=$(date +%Y-%m-%d)
MEMORY_DIR="$HOME/.openclaw/workspace/memory"
LOG_FILE="/tmp/openclaw/daily-memory.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始创建日常记忆..." >> $LOG_FILE

# 创建今天的记忆文件（如果不存在）
TODAY_FILE="$MEMORY_DIR/$DATE.md"
if [ ! -f "$TODAY_FILE" ]; then
    cat > "$TODAY_FILE" << EOF
# $DATE 学习记录

## 📝 待补充
- [ ] 今天的关键对话
- [ ] 重要决策和纠正
- [ ] 学到的新技能
- [ ] 待办事项

## 🚨 WAL Protocol 记录
（用户纠正、专有名词、偏好、决策等）

---
*最后更新：$(date '+%Y-%m-%d %H:%M')*
EOF
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 创建记忆文件：$TODAY_FILE" >> $LOG_FILE
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ℹ️  记忆文件已存在：$TODAY_FILE" >> $LOG_FILE
fi

# 更新 MEMORY.md 的最后访问时间
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 最后访问：$(date '+%Y-%m-%d %H:%M')" >> "$MEMORY_DIR/last-accessed.txt"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 日常记忆保存完成" >> $LOG_FILE

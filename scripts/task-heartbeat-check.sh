#!/bin/bash
# 任务心跳检查脚本
# 每 30 分钟运行一次，检查是否有未完成的任务

TRACKER_FILE="$HOME/.openclaw/workspace/task-tracker.json"
LOG_FILE="/tmp/openclaw/heartbeat-check.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始检查任务状态..." >> $LOG_FILE

# 检查是否有超时任务
if [ -f "$TRACKER_FILE" ]; then
    # 读取进行中的任务
    ACTIVE_TASKS=$(cat "$TRACKER_FILE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('active_tasks',[])))" 2>/dev/null || echo "0")
    
    if [ "$ACTIVE_TASKS" -gt 0 ]; then
        echo "⚠️ 发现 $ACTIVE_TASKS 个进行中的任务，请检查进度" >> $LOG_FILE
        # 可以通过 message 工具通知用户
    else
        echo "✅ 无进行中的任务" >> $LOG_FILE
    fi
else
    echo "⚠️ 任务追踪文件不存在" >> $LOG_FILE
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 检查完成" >> $LOG_FILE

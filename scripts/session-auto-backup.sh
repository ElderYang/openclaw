#!/bin/bash
# 会话自动备份脚本
# 每天运行一次，备份所有会话文件

set -e

DATE=$(date +%Y%m%d_%H%M%S)
SOURCE="$HOME/.openclaw/agents/main/sessions/"
TARGET="$HOME/.openclaw/backups/sessions/$DATE/"
LOG_FILE="/tmp/openclaw/session-backup.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始备份会话..." >> $LOG_FILE

# 创建备份目录
mkdir -p "$TARGET"

# 复制会话文件
if [ -d "$SOURCE" ]; then
    cp "$SOURCE"*.jsonl "$TARGET" 2>/dev/null || true
    COUNT=$(ls -1 "$TARGET"*.jsonl 2>/dev/null | wc -l)
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 备份完成：$COUNT 个文件" >> $LOG_FILE
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ 源目录不存在：$SOURCE" >> $LOG_FILE
fi

# 清理 30 天前的备份
find "$HOME/.openclaw/backups/sessions/" -type d -mtime +30 -exec rm -rf {} \; 2>/dev/null || true
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 已清理 30 天前的备份" >> $LOG_FILE

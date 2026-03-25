#!/bin/bash

# 添加股市分析定时任务到 crontab
# 使用方法：bash ~/.openclaw/workspace/scripts/setup_cron.sh

echo "📅 配置股市分析定时任务"
echo ""

# 显示当前的 crontab
echo "当前的 crontab 配置："
crontab -l 2>/dev/null || echo "(空)"
echo ""

# 创建新的 crontab 配置
CRON_CONFIG="
# === 股市分析定时任务 ===
# 股市早报（每天 8:15）
15 8 * * * /Users/yangbowen/.openclaw/workspace/scripts/run_stock_analysis.sh morning >> /Users/yangbowen/.openclaw/workspace/logs/cron_morning.log 2>&1

# A 股复盘（周一至周五 17:00）
0 17 * * 1-5 /Users/yangbowen/.openclaw/workspace/scripts/run_stock_analysis.sh afternoon >> /Users/yangbowen/.openclaw/workspace/logs/cron_afternoon.log 2>&1
"

echo "📋 新的定时任务配置："
echo "$CRON_CONFIG"
echo ""

# 提示用户手动添加
echo "⚠️  由于权限限制，请手动执行以下命令添加定时任务："
echo ""
echo "1. 打开 crontab 编辑器："
echo "   crontab -e"
echo ""
echo "2. 粘贴以下内容："
echo "$CRON_CONFIG"
echo ""
echo "3. 保存并退出（vi: :wq）"
echo ""

# 验证命令
echo "✅ 验证配置："
echo "   crontab -l"
echo ""

# 创建日志目录
mkdir -p /Users/yangbowen/.openclaw/workspace/logs
echo "✅ 日志目录已创建：/Users/yangbowen/.openclaw/workspace/logs/"

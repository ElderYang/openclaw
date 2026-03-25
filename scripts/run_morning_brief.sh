#!/bin/bash
# 股市早报包装脚本
# 用法：./run_morning_brief.sh

cd ~/.openclaw/workspace

# 执行 Python 脚本生成报告
python3 scripts/stock_market_analysis_v125.py morning

# 读取生成的报告
REPORT_FILE="reports/morning_brief_$(date +%Y%m%d)_v124.md"

if [ -f "$REPORT_FILE" ]; then
    echo "✅ 报告生成成功：$REPORT_FILE"
    # 可以通过飞书 API 发送报告
    # 这里输出报告内容供 AI 读取
    cat "$REPORT_FILE"
else
    echo "❌ 报告生成失败"
    exit 1
fi

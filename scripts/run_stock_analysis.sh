#!/bin/bash

# A 股市场分析报告定时任务脚本
# 添加到 crontab: crontab -e

# 环境变量
export PATH="/Users/yangbowen/.nvm/versions/node/v24.14.0/bin:/usr/local/bin:/usr/bin:/bin"
export DASHSCOPE_API_KEY="sk-ce9e5828374948b0a5deb0e4d2ab88e5"
export TAVILY_API_KEY="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"

# 脚本路径
SCRIPT_DIR="/Users/yangbowen/.openclaw/workspace/scripts"
LOG_DIR="/Users/yangbowen/.openclaw/workspace/logs"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 获取日期
DATE=$(date +%Y%m%d)
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# 日志函数
log() {
    echo "[$TIMESTAMP] $1" | tee -a "$LOG_DIR/stock_analysis_$DATE.log"
}

# 检查是否是交易日（周一至周五）
is_trading_day() {
    DOW=$(date +%u)
    if [ $DOW -le 5 ]; then
        return 0
    else
        return 1
    fi
}

# 股市早报（每天 8:15）
run_morning_brief() {
    log "========== 开始执行股市早报 =========="
    python3 "$SCRIPT_DIR/stock_market_analysis.py" morning >> "$LOG_DIR/morning_$DATE.log" 2>&1
    log "========== 早报执行完成 =========="
}

# A 股复盘（周一至周五 17:00）
run_afternoon_review() {
    if is_trading_day; then
        log "========== 开始执行 A 股复盘 =========="
        python3 "$SCRIPT_DIR/stock_market_analysis.py" afternoon >> "$LOG_DIR/afternoon_$DATE.log" 2>&1
        log "========== 复盘执行完成 =========="
    else
        log "========== 非交易日，跳过复盘 =========="
    fi
}

# 主函数
case "$1" in
    morning)
        run_morning_brief
        ;;
    afternoon)
        run_afternoon_review
        ;;
    test)
        log "========== 测试模式 =========="
        run_morning_brief
        run_afternoon_review
        log "========== 测试完成 =========="
        ;;
    *)
        echo "Usage: $0 {morning|afternoon|test}"
        exit 1
        ;;
esac

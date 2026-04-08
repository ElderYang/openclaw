#!/bin/bash
# macOS 自动化权限永久授权脚本

echo "🔐 macOS 自动化权限配置"
echo "========================"
echo ""

# 检查是否运行在 Terminal
if [ -z "$TERM_PROGRAM" ]; then
    echo "⚠️  请在 Terminal 或 iTerm2 中运行此脚本"
    exit 1
fi

# 获取 Terminal bundle ID
TERMINAL_BUNDLE="com.apple.Terminal"
if [ "$TERM_PROGRAM" = "iTerm.app" ]; then
    TERMINAL_BUNDLE="com.googlecode.iterm2"
fi

echo "📱 检测到终端：$TERMINAL_BUNDLE"
echo ""

# 重置权限
echo "🔄 正在重置自动化权限..."
tccutil reset AppleEvents $TERMINAL_BUNDLE
tccutil reset AppleEvents org.python.python
tccutil reset Reminders $TERMINAL_BUNDLE

echo ""
echo "✅ 权限已重置！"
echo ""
echo "📋 下一步操作："
echo "1. 运行邮件监控脚本：python3 ~/.openclaw/workspace/scripts/work_email_monitor.py"
echo "2. 当弹出授权对话框时，点击'允许'"
echo "3. 授权后不会再提示"
echo ""
echo "🔍 如果仍需要授权，请手动配置："
echo "   系统设置 → 隐私与安全性 → 自动化 → 提醒事项"
echo "   勾选：Terminal (或 iTerm2)、Python"
echo ""

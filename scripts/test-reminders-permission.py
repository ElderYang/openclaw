#!/usr/bin/env python3
"""测试提醒事项权限"""
import subprocess

script = '''
tell application "Reminders"
    set testReminder to make new reminder at end of reminders of list "提醒" with properties {name:"权限测试 - 自动删除", body:"如果看到此提醒，说明权限正常"}
    delay 1
    delete testReminder
end tell
'''

result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)

if result.returncode == 0:
    print("✅ 权限正常！可以创建和删除提醒")
else:
    print("❌ 权限不足，请在系统设置中授权")
    print(f"错误：{result.stderr}")

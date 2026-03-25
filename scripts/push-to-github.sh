#!/bin/bash
# GitHub 推送脚本
# 使用方法：bash ~/.openclaw/workspace/scripts/push-to-github.sh

cd ~/.openclaw/workspace

echo "🚀 推送到 GitHub: ElderYang/openclaw"

# 设置 Git 用户信息
git config user.name "杨博文"
git config user.email "yangbowen@example.com"

# 设置 GitHub token
export GIT_ASKPASS=echo
echo "https://ghp_DoBrTPZAQhr3aSJx@github.com" > ~/.git-credentials
chmod 600 ~/.git-credentials

# 推送
git push -u origin main

echo ""
echo "✅ 推送完成！"
echo "📍 查看仓库：https://github.com/ElderYang/openclaw"

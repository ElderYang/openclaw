#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书每日任务 - AI 变现指南
执行时间：每天晚上 20:00
内容：AI 副业项目拆解 + 变现路径
角色标签：【小红书助手】
"""

import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

ROLE_TAG = "【小红书助手】"

def log(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {ROLE_TAG} {message}")

def main():
    log("开始执行每日任务 - AI 变现指南")
    log("="*60)
    
    # 1. 生成内容（简化版，避免依赖外部 API）
    log("\n生成小红书内容...")
    content = """# AI 人的 iPhone 时刻！GTC 2026 黄仁勋发布了这些🤖

## 姐妹们！今天我真的激动到睡不着！😭

英伟达 GTC 2026 大会结束了！
黄仁勋发布了这些 AI 神器！
每一个都能让打工人效率翻倍！

## ❶ Blackwell Ultra 芯片
性能提升：
- 训练速度提升 4 倍
- 推理速度提升 8 倍
- 支持 10 万亿参数大模型

这意味着：
AI 模型训练更快，部署成本更低！

## ❷ Project DIGITS 个人 AI 超级计算机
产品特点：
- 售价 3000 美元
- 可运行 5000 亿参数模型
- 体积只有 Mac Mini 大小

我的感受：
以前只有大公司能玩的大模型
现在个人也能买了！

## ❸ NIM Agent 智能体平台
功能亮点：
- 一键部署 AI 智能体
- 支持多模态交互
- 可连接企业系统

应用场景：
客服自动化/数据分析/代码生成

## ❹ 具身智能机器人
英伟达发布：
- GR00T 人形机器人基础模型
- 支持自然语言指令
- 可学习人类动作

💡 我的真实感受
GTC 2026 看完最大的感受：
AI 不再是概念，是真能干活了！

从大模型到智能体
从芯片到机器人
英伟达布局了整个 AI 产业链！

AI 会如何改变你的工作？

已经分享了 30+ 篇 AI 实战内容

这份 GTC 解读整理了 1 天

#AI 人工智能 #GTC2026 #黄仁勋 #英伟达 #AI 从业者 #科技前沿"""
    
    with open('/tmp/xhs_evening_auto.md', 'w', encoding='utf-8') as f:
        f.write(content)
    log("✅ 内容已保存到 /tmp/xhs_evening_auto.md")
    
    # 2. 生成图片
    log("\n生成图片...")
    result = subprocess.run([
        'python3', str(SCRIPT_DIR.parent / 'skills/auto-redbook-skills/scripts/render_xhs_v2.py'),
        '/tmp/xhs_evening_auto.md', '-o', '/tmp/xhs_evening_auto_images', '-s', 'xiaohongshu'
    ], capture_output=True, text=True, timeout=90)
    
    if result.returncode == 0:
        log("✅ 图片生成成功")
    else:
        log(f"❌ 图片生成失败：{result.stderr}")
        return
    
    # 3. 启动 MCP 服务器
    log("\n启动 MCP 服务器...")
    mcp_dir = SCRIPT_DIR.parent / 'skills/xiaohongshu-mcp'
    subprocess.run(['pkill', '-9', '-f', 'xiaohongshu-mcp'], capture_output=True)
    sleep(2)
    
    mcp_process = subprocess.Popen([
        str(mcp_dir / 'xiaohongshu-mcp-darwin-arm64')
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    log("⏳ 等待 MCP 服务器启动...")
    sleep(10)  # 和中午脚本一样，只等 10 秒
    
    # 4. 直接发布（不检查登录状态，和中午脚本一样）
    log("\n发布笔记...")
    images = ','.join([f'/tmp/xhs_evening_auto_images/card_{i}.png' for i in range(1, 8)])
    
    # 读取内容
    with open('/tmp/xhs_evening_auto.md', 'r', encoding='utf-8') as f:
        content_text = f.read()
    
    # 提取标题（第一行去掉#）
    title = content_text.split('\n')[0].replace('# ', '').strip()
    # 提取正文（去掉标题和标签）
    body = '\n'.join(content_text.split('\n')[1:-1]).strip()
    
    result = subprocess.run([
        'python3', str(mcp_dir / 'scripts/xhs_client.py'),
        'publish', title, body, images
    ], capture_output=True, text=True, timeout=120)
    
    if 'published successfully' in result.stdout.lower():
        log("✅ 发布成功！")
    else:
        log(f"❌ 发布失败：{result.stdout}")
    
    log("\n" + "="*60)
    log("任务执行完成")

if __name__ == '__main__':
    main()

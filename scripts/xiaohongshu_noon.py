#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书每日任务 - OpenClaw 实战
执行时间：每天中午 12:30
内容：OpenClaw 技能教程 + 配置指南
角色标签：【小红书助手】
"""

import subprocess
import sys
import requests
import os
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

ROLE_TAG = "【小红书助手】"

def log(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {ROLE_TAG} {message}")

def generate_content():
    """生成小红书内容"""
    log("生成小红书内容...")
    
    # 搜索 OpenClaw 相关素材
    try:
        api_key = os.environ.get('TAVILY_API_KEY', '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')
        url = "https://api.tavily.com/search"
        data = {
            "api_key": api_key,
            "query": "OpenClaw AI 助手 自动化技能 2026",
            "search_depth": "basic",
            "max_results": 5
        }
        resp = requests.post(url, json=data, timeout=15)
        results = resp.json().get('results', [])
        
        # 构建内容
        content = f"""姐妹们！今天分享一个超实用的 AI 工具！🚀

说实话，配置完这个我真的后悔没早知！
OpenClaw 能让 AI 自动帮你干活！
不是聊天机器人，是真正的自动化助手！

❶ OpenClaw 是什么？
- 开源 AI 助手框架
- 53+ 技能（股市/小红书/邮件）
- 本地部署，数据不上传
- 完全免费

❷ 我配置的技能（已实测）
- 股市早报/复盘（自动发布）
- 小红书笔记（自动创作）
- 邮件收发（Gmail/QQ 邮箱）
- Obsidian 日记（自动创建）
- Self-Improving（主动反思）

❸ 配置步骤（3 步搞定）
1. 安装 OpenClaw（npm 安装）
2. 配置 API Keys（10 个服务）
3. 设置定时任务（launchd）

我花了 2 小时搞定！
现在每天早上自动收到股市早报！

💡 我的感受
配置前：AI 就是聊天的
配置后：AI 真的能干活！

你觉得 AI 助手能帮你做什么？
评论区聊聊～

关注我，分享更多 AI 实战🚀
点赞过 500，出详细配置教程！

#AI 人工智能 #OpenClaw #自动化 #AI 助手 #效率工具 #科技
"""
        return content
    except Exception as e:
        log(f"⚠️ 内容生成失败：{e}")
        return None

def generate_images(content):
    """生成小红书图片"""
    log("生成图片...")
    
    # 保存内容为临时文件
    temp_file = Path("/tmp/xhs_noon_content.md")
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(f"# OpenClaw 配置实战｜3 步打造 AI 助手🤖\n\n{content}")
    
    output_dir = Path("/tmp/xhs_noon_images")
    output_dir.mkdir(exist_ok=True)
    
    # 调用渲染脚本
    render_script = SCRIPT_DIR.parent / "skills" / "auto-redbook-skills" / "scripts" / "render_xhs_v2.py"
    try:
        result = subprocess.run(
            ["python3", str(render_script), str(temp_file), "-o", str(output_dir), "-s", "xiaohongshu"],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            images = list(output_dir.glob("card_*.png"))
            log(f"✅ 生成 {len(images)} 张图片")
            return [str(img) for img in images]
        else:
            log(f"⚠️ 图片生成失败：{result.stderr}")
            return []
    except Exception as e:
        log(f"⚠️ 图片生成异常：{e}")
        return []

def publish(content, images):
    """发布小红书笔记"""
    log("发布笔记...")
    
    if not images:
        log("⚠️ 没有图片，无法发布")
        return False
    
    # 启动 MCP 服务器
    mcp_dir = SCRIPT_DIR.parent / "skills" / "xiaohongshu-mcp"
    mcp_script = mcp_dir / "xiaohongshu-mcp-darwin-arm64"
    
    log("启动 MCP 服务器...")
    mcp_process = subprocess.Popen(
        [str(mcp_script)],
        cwd=str(mcp_dir),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    # 等待服务器启动
    import time
    time.sleep(10)
    
    # 构建发布命令
    xhs_client = mcp_dir / "scripts" / "xhs_client.py"
    image_paths = ",".join(images[:7])  # 最多 7 张
    
    title = "OpenClaw 配置实战｜3 步打造 AI 助手🤖"
    
    log(f"发布标题：{title}")
    log(f"图片数量：{len(images)}")
    
    try:
        result = subprocess.run(
            ["python3", str(xhs_client), "publish", title, content, image_paths],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        # 关闭 MCP 服务器
        mcp_process.terminate()
        
        if "success" in result.stdout.lower() or "发布成功" in result.stdout:
            log("✅ 发布成功！")
            return True
        else:
            log(f"⚠️ 发布失败：{result.stdout}")
            log(f"错误：{result.stderr}")
            return False
    except Exception as e:
        mcp_process.terminate()
        log(f"⚠️ 发布异常：{e}")
        return False

def main():
    log("开始执行每日任务 - OpenClaw 实战")
    log("="*60)
    
    # 1. 生成内容
    content = generate_content()
    if not content:
        log("❌ 内容生成失败，终止任务")
        return
    
    # 2. 生成图片
    images = generate_images(content)
    if not images:
        log("❌ 图片生成失败，终止任务")
        return
    
    # 3. 发布笔记
    success = publish(content, images)
    
    if success:
        log("\n✅ 任务完成！笔记已发布")
    else:
        log("\n❌ 任务失败！请检查日志")
    
    log("="*60)

if __name__ == "__main__":
    main()

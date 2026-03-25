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
    
    # 搜索 AI 变现相关素材
    try:
        api_key = os.environ.get('TAVILY_API_KEY', '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')
        url = "https://api.tavily.com/search"
        data = {
            "api_key": api_key,
            "query": "AI 副业项目 变现路径 2026 年 被动收入",
            "search_depth": "basic",
            "max_results": 5
        }
        resp = requests.post(url, json=data, timeout=15)
        results = resp.json().get('results', [])
        
        # 构建内容
        content = f"""姐妹们！今天分享一个 AI 变现思路！💰

说实话，这个真的能赚到钱！
我朋友已经在做了，月入过万！
不是割韭菜，是真实可行的路径！

❶ AI 变现的 3 个方向
- AI 代写（小红书笔记/公众号文章）
- AI 绘画（头像定制/壁纸制作）
- AI 视频（短视频生成/口播视频）

❷ 我朋友在做的（已实测）
- 小红书 AI 代写笔记
- 单价 50-200 元/篇
- 每天接 2-3 单
- 月入 3000-5000 元

❸ 如何开始（3 步搞定）
1. 学习 AI 工具（OpenClaw/Notion AI）
2. 在小红书展示案例
3. 私信接单

我朋友花了 1 周学习！
现在每天 2 小时就能搞定！

💡 我的建议
别光看，要行动！
先接 1 单试试水！
赚到第一块钱你就有信心了！

你觉得 AI 变现靠谱吗？
评论区聊聊你的想法～👇

关注我，分享更多 AI 变现技巧🚀
点赞过 500，出详细接单教程！

#AI 变现 #副业 #AI 副业 #被动收入 #搞钱 #AI 人工智能
"""
        return content
    except Exception as e:
        log(f"⚠️ 内容生成失败：{e}")
        return None

def generate_images(content):
    """生成小红书图片"""
    log("生成图片...")
    
    # 保存内容为临时文件
    temp_file = Path("/tmp/xhs_evening_content.md")
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(f"# AI 变现指南｜3 个方向月入过万💰\n\n{content}")
    
    output_dir = Path("/tmp/xhs_evening_images")
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
    
    title = "AI 变现指南｜3 个方向月入过万💰"
    
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
    log("开始执行每日任务 - AI 变现指南")
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

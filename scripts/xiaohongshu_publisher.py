#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书自动发布器 - 完整版
功能：搜索热点 → 生成内容 → 生成图片 → 发布笔记
"""

import subprocess
import sys
import os
import json
import requests
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
SKILLS_DIR = SCRIPT_DIR.parent / "skills"

# ==================== 搜索热点 ====================

def search_hot_topics(query, count=5):
    """使用 multi-search-engine 搜索热点"""
    print(f"🔍 搜索热点：{query}")
    
    try:
        # 使用 multi-search-engine 技能
        search_script = SKILLS_DIR / "multi-search-engine" / "scripts" / "search.py"
        if search_script.exists():
            result = subprocess.run(
                ["python3", str(search_script), "-q", query, "-c", str(count)],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode == 0:
                # 解析 JSON 输出
                data = json.loads(result.stdout)
                return data.get('results', [])
    except Exception as e:
        print(f"⚠️ multi-search 失败：{e}")
    
    # 降级：使用 Tavily API
    try:
        api_key = os.environ.get('TAVILY_API_KEY', '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')
        url = "https://api.tavily.com/search"
        data = {
            "api_key": api_key,
            "query": query,
            "search_depth": "basic",
            "max_results": count
        }
        resp = requests.post(url, json=data, timeout=15)
        results = resp.json().get('results', [])
        print(f"✅ 找到 {len(results)} 条结果")
        return results
    except Exception as e:
        print(f"❌ Tavily 搜索失败：{e}")
        return []

# ==================== 生成内容 ====================

def generate_content(topic, search_results):
    """生成小红书笔记内容"""
    print(f"📝 生成内容：{topic}")
    
    # 提取关键信息
    titles = [r.get('title', '') for r in search_results[:3]]
    contents = [r.get('content', '') for r in search_results[:3]]
    
    # 生成标题（15-20 字，带 emoji）
    title = f"🤖 {topic}！这 3 个点你必须知道"
    
    # 生成正文（口语化 + emoji + 分段）
    content = f"""# {topic}

姐妹们！今天真的要好好聊聊这个！😭

说实话，我研究了好久才搞明白！
现在第一时间来跟你们分享！

## ❶ 核心要点
{contents[0][:200] if contents else '最新动态值得关注'}

## ❷ 关键信息
{contents[1][:200] if len(contents) > 1 else '行业趋势明显'}

## ❸ 我的感受
真的没想到发展这么快！
普通人也能抓住这波红利！

## 💡 实用建议
- 多关注官方动态
- 学习基础知识
- 动手实践最重要

你们怎么看？
评论区聊聊～

关注我，分享更多干货🚀
"""
    
    return title, content

# ==================== 生成图片 ====================

def generate_images(title, content, output_dir):
    """使用 render_xhs_v2.py 生成图片"""
    print(f"🎨 生成图片...")
    
    # 创建临时 markdown 文件
    md_file = output_dir / "content.md"
    md_file.write_text(f"# {title}\n\n{content}")
    
    # 调用渲染脚本
    render_script = SKILLS_DIR / "auto-redbook-skills" / "scripts" / "render_xhs_v2.py"
    
    try:
        result = subprocess.run(
            ["python3", str(render_script), str(md_file), "-o", str(output_dir), "-s", "xiaohongshu"],
            capture_output=True, text=True, timeout=60,
            cwd=str(SKILLS_DIR / "auto-redbook-skills" / "scripts")
        )
        
        if result.returncode == 0:
            # 查找生成的图片
            images = list(output_dir.glob("*.png")) + list(output_dir.glob("*.jpg"))
            print(f"✅ 生成 {len(images)} 张图片")
            return [str(img) for img in images]
        else:
            print(f"❌ 渲染失败：{result.stderr}")
            return []
    except Exception as e:
        print(f"❌ 图片生成失败：{e}")
        return []

# ==================== 发布笔记 ====================

def publish_note(title, content, images):
    """使用 xhs_client.py 发布笔记"""
    print(f"📤 发布笔记...")
    
    mcp_dir = SKILLS_DIR / "xiaohongshu-mcp"
    xhs_client = mcp_dir / "scripts" / "xhs_client.py"
    
    # 确保 MCP 服务器运行
    try:
        mcp_binary = mcp_dir / "xiaohongshu-mcp-darwin-arm64"
        subprocess.Popen(
            [str(mcp_binary)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=str(mcp_dir)
        )
        import time
        # 等待 MCP 完全启动（需要 6-8 秒）
        print("⏳ 等待 MCP 服务器启动...")
        for i in range(10):
            try:
                resp = requests.get("http://127.0.0.1:18060/api/v1/login/status", timeout=2)
                if resp.status_code == 200:
                    print("✅ MCP 服务器已启动")
                    break
            except:
                pass
            time.sleep(1)
        else:
            print("⚠️ MCP 启动超时，继续尝试发布...")
    except Exception as e:
        print(f"⚠️ MCP 启动失败：{e}")
    
    # 调用发布命令（图片用逗号分隔）
    try:
        images_str = ",".join(images)
        cmd = ["python3", str(xhs_client), "publish", title, content, images_str]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=str(mcp_dir))
        
        if result.returncode == 0:
            print(f"✅ 发布成功！")
            print(result.stdout)
            return True
        else:
            print(f"❌ 发布失败：{result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 发布异常：{e}")
        return False

# ==================== 主函数 ====================

def publish_xiaohongshu(topic, theme="AI 科技", output_dir=None):
    """完整发布流程"""
    if output_dir is None:
        output_dir = SCRIPT_DIR / "xhs_output" / datetime.now().strftime("%Y%m%d_%H%M")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("="*60)
    print(f"📕 小红书自动发布 | {theme}")
    print("="*60)
    
    # 1. 搜索热点
    query = f"{theme} {topic} {datetime.now().strftime('%Y年%m月')}"
    search_results = search_hot_topics(query, count=5)
    
    if not search_results:
        print("⚠️ 未找到热点，使用预设内容")
        search_results = [
            {"title": f"{topic} 最新动态", "content": f"{topic} 备受关注，行业发展迅速"},
            {"title": f"{theme} 趋势分析", "content": f"{theme} 领域持续创新，应用场景广泛"},
        ]
    
    # 2. 生成内容
    title, content = generate_content(topic, search_results)
    print(f"\n✅ 内容生成完成")
    print(f"标题：{title}")
    
    # 3. 生成图片
    images = generate_images(title, content, output_dir)
    
    if not images:
        print("⚠️ 图片生成失败，使用预设图片")
        # TODO: 使用默认图片
    
    # 4. 发布笔记
    success = publish_note(title, content, images)
    
    print("\n" + "="*60)
    if success:
        print("✅ 发布完成！")
    else:
        print("❌ 发布失败")
    print("="*60)
    
    return success

if __name__ == "__main__":
    # 测试执行
    publish_xiaohongshu("AI 大模型", "AI 科技")

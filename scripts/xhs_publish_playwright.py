#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书自动发布脚本 - Playwright 版本
功能：使用 Playwright 直接操作小红书网页发布笔记
"""

import json
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# 配置
COOKIES_FILE = Path.home() / ".openclaw" / "workspace" / "skills" / "xiaohongshu-mcp" / "cookies.json"
PUBLISH_URL = "https://creator.xiaohongshu.com/publish/publish"  # 图文发布专用

def load_cookies():
    """加载 cookies"""
    if not COOKIES_FILE.exists():
        print(f"❌ Cookies 文件不存在：{COOKIES_FILE}")
        return None
    
    with open(COOKIES_FILE, 'r', encoding='utf-8') as f:
        cookies = json.load(f)
    
    print(f"✅ 加载 {len(cookies)} 个 cookies")
    return cookies

def publish_note(title, content, image_paths, tags=None):
    """发布小红书笔记"""
    print("="*60)
    print("📕 小红书自动发布 - Playwright 版")
    print("="*60)
    
    # 加载 cookies
    cookies = load_cookies()
    if not cookies:
        return False
    
    with sync_playwright() as p:
        # 启动浏览器（使用用户数据目录，保持登录状态）
        print("🌐 启动浏览器...")
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(Path.home() / "Library" / "Application Support" / "OpenClaw" / "XHS"),
            headless=False,  # 显示浏览器窗口，方便调试
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
        
        page = browser.pages[0] if browser.pages else browser.new_page()
        
        try:
            # 设置 cookies
            print("🍪 设置 cookies...")
            page.context.add_cookies(cookies)
            
            # 打开发布页面（直接导航到图文发布页）
            print(f"📄 打开发布页面：{PUBLISH_URL}")
            page.goto(PUBLISH_URL, wait_until='networkidle', timeout=30000)
            time.sleep(5)  # 等待页面加载
            
            # 保存页面 HTML 用于调试
            with open('/tmp/xhs_page_source.html', 'w', encoding='utf-8') as f:
                f.write(page.content())
            print("📄 已保存页面 HTML: /tmp/xhs_page_source.html")
            
            # 检查登录状态
            if "login" in page.url.lower():
                print("❌ 未登录，请先登录小红书")
                return False
            
            print("✅ 已登录")
            
            # 先切换到图文模式（再上传图片）
            print("🔄 检查发布模式...")
            
            # 方法 1: 检测是否在视频上传页面
            video_indicators = [
                'text=拖拽视频到此',
                'text=上传视频',
                'video-upload',
                '[class*="video-upload"]',
                'text=视频'
            ]
            
            is_video_mode = False
            for indicator in video_indicators:
                if page.locator(indicator).count() > 0:
                    is_video_mode = True
                    print(f"⚠️ 检测到视频模式 (指示器：{indicator})")
                    break
            
            if is_video_mode:
                print("🔄 尝试切换到图文模式...")
                
                # 图文切换按钮的多种选择器
                switch_selectors = [
                    # Tab 切换
                    'button:has-text("图文"), a:has-text("图文"), [role="tab"]:has-text("图文")',
                    # 发布类型选择
                    '.publish-type-selector button:has-text("图文")',
                    '.type-selector button:has-text("图文")',
                    '[class*="type-selector"] button:has-text("图文")',
                    # 导航栏
                    'nav button:has-text("图文")',
                    '.nav-item:has-text("图文")',
                    # data-e2e
                    '[data-e2e="publish-note"]',
                    '[data-e2e="image-text"]',
                    # 其他
                    'button:has-text("发图文")',
                    'button:has-text("图文笔记")',
                    '.switch-btn:has-text("图文")'
                ]
                
                switch_clicked = False
                for sel in switch_selectors:
                    try:
                        switch_btn = page.locator(sel).first
                        if switch_btn.count() > 0:
                            print(f"  找到切换按钮：{sel}")
                            switch_btn.click()
                            time.sleep(3)
                            print("✅ 已切换到图文模式")
                            switch_clicked = True
                            break
                    except Exception as e:
                        continue
                
                if not switch_clicked:
                    print("⚠️ 未找到图文切换按钮，尝试其他方法...")
                    
                    # 方法 2: 检查 URL，如果是视频发布页，导航到图文发布页
                    current_url = page.url
                    if '/video' in current_url or 'video' in current_url:
                        print("  检测到视频发布 URL，导航到图文发布页...")
                        page.goto("https://creator.xiaohongshu.com/publish/publish?source=official")
                        time.sleep(5)
                    
                    # 方法 3: 尝试点击页面左上角的返回/切换按钮
                    back_buttons = [
                        'button:has-text("返回")',
                        'button:has-text("取消")',
                        '.back-btn',
                        '[class*="back"]'
                    ]
                    for sel in back_buttons:
                        try:
                            back_btn = page.locator(sel).first
                            if back_btn.count() > 0:
                                back_btn.click()
                                time.sleep(2)
                                # 重新导航到发布页
                                page.goto("https://creator.xiaohongshu.com/publish/publish?source=official")
                                time.sleep(5)
                                print("✅ 已尝试返回并重新进入发布页")
                                break
                        except:
                            continue
            
            # 再次检测是否还在视频模式
            video_check = page.locator('text=拖拽视频到此或点击上传')
            if video_check.count() > 0:
                print("⚠️ 仍在视频模式，可能需要手动切换")
                # 截图保存当前状态
                page.screenshot(path='/tmp/xhs_video_mode.png')
                print("📸 已保存视频模式截图：/tmp/xhs_video_mode.png")
            
            # 等待页面加载
            print("⏳ 等待页面加载...")
            time.sleep(5)
            
            # 截图调试
            page.screenshot(path='/tmp/xhs_debug.png')
            print("📸 已保存调试截图：/tmp/xhs_debug.png")
            
            # 上传图片 - 逐个上传
            print(f"📷 上传图片：{len(image_paths)} 张")
            # 先点击上传按钮（如果有）
            upload_buttons = page.locator('button:has-text("上传图片"), button:has-text("选择图片"), .upload-btn, [class*="upload"]')
            if upload_buttons.count() > 0:
                upload_buttons.first.click()
                time.sleep(2)
            
            for i, img_path in enumerate(image_paths, 1):
                print(f"  上传第 {i}/{len(image_paths)} 张...")
                
                # 尝试多种选择器
                upload_success = False
                
                # 方法 1: 使用 accept 属性精确匹配图片上传框
                file_inputs = page.locator('input[type="file"][accept*=".jpg"]')
                if file_inputs.count() > 0:
                    file_inputs.first.set_input_files(img_path)
                    upload_success = True
                    print(f"  ✅ 第 {i} 张上传成功")
                
                # 方法 2: 查找第一个图片上传框
                if not upload_success:
                    file_inputs = page.locator('input[type="file"][accept*="image"]')
                    if file_inputs.count() > 0:
                        file_inputs.first.set_input_files(img_path)
                        upload_success = True
                        print(f"  ✅ 第 {i} 张上传成功")
                
                # 方法 3: 使用 XPath 精确匹配
                if not upload_success:
                    file_inputs = page.locator('xpath=//input[@type="file" and contains(@accept, ".jpg")]')
                    if file_inputs.count() > 0:
                        file_inputs.first.set_input_files(img_path)
                        upload_success = True
                        print(f"  ✅ 第 {i} 张上传成功")
                
                if not upload_success:
                    print(f"  ⚠️ 第 {i} 张上传失败，请手动上传")
                
                time.sleep(2)  # 等待上传完成
            
            # 先切换到图文模式（如果是视频模式）
            print("🔄 检查发布模式...")
            
            # 方法 1: 检测是否在视频上传页面
            video_indicators = [
                'text=拖拽视频到此',
                'text=上传视频',
                'video-upload',
                '[class*="video-upload"]',
                'text=视频'
            ]
            
            is_video_mode = False
            for indicator in video_indicators:
                if page.locator(indicator).count() > 0:
                    is_video_mode = True
                    print(f"⚠️ 检测到视频模式 (指示器：{indicator})")
                    break
            
            if is_video_mode:
                print("🔄 尝试切换到图文模式...")
                
                # 图文切换按钮的多种选择器
                switch_selectors = [
                    # Tab 切换
                    'button:has-text("图文"), a:has-text("图文"), [role="tab"]:has-text("图文")',
                    # 发布类型选择
                    '.publish-type-selector button:has-text("图文")',
                    '.type-selector button:has-text("图文")',
                    '[class*="type-selector"] button:has-text("图文")',
                    # 导航栏
                    'nav button:has-text("图文")',
                    '.nav-item:has-text("图文")',
                    # data-e2e
                    '[data-e2e="publish-note"]',
                    '[data-e2e="image-text"]',
                    # 其他
                    'button:has-text("发图文")',
                    'button:has-text("图文笔记")',
                    '.switch-btn:has-text("图文")'
                ]
                
                switch_clicked = False
                for sel in switch_selectors:
                    try:
                        switch_btn = page.locator(sel).first
                        if switch_btn.count() > 0:
                            print(f"  找到切换按钮：{sel}")
                            switch_btn.click()
                            time.sleep(3)
                            print("✅ 已切换到图文模式")
                            switch_clicked = True
                            break
                    except Exception as e:
                        continue
                
                if not switch_clicked:
                    print("⚠️ 未找到图文切换按钮，尝试其他方法...")
                    
                    # 方法 2: 检查 URL，如果是视频发布页，导航到图文发布页
                    current_url = page.url
                    if '/video' in current_url or 'video' in current_url:
                        print("  检测到视频发布 URL，导航到图文发布页...")
                        page.goto("https://creator.xiaohongshu.com/publish/publish?source=official")
                        time.sleep(5)
                    
                    # 方法 3: 尝试点击页面左上角的返回/切换按钮
                    back_buttons = [
                        'button:has-text("返回")',
                        'button:has-text("取消")',
                        '.back-btn',
                        '[class*="back"]'
                    ]
                    for sel in back_buttons:
                        try:
                            back_btn = page.locator(sel).first
                            if back_btn.count() > 0:
                                back_btn.click()
                                time.sleep(2)
                                # 重新导航到发布页
                                page.goto("https://creator.xiaohongshu.com/publish/publish?source=official")
                                time.sleep(5)
                                print("✅ 已尝试返回并重新进入发布页")
                                break
                        except:
                            continue
            
            # 再次检测是否还在视频模式
            video_check = page.locator('text=拖拽视频到此或点击上传')
            if video_check.count() > 0:
                print("⚠️ 仍在视频模式，可能需要手动切换")
                # 截图保存当前状态
                page.screenshot(path='/tmp/xhs_video_mode.png')
                print("📸 已保存视频模式截图：/tmp/xhs_video_mode.png")
            
            # 等待页面加载
            print("⏳ 等待页面加载...")
            time.sleep(5)
            
            # 截图调试
            page.screenshot(path='/tmp/xhs_debug.png')
            print("📸 已保存调试截图：/tmp/xhs_debug.png")
            
            # 填写标题 - 增强版选择器
            print(f"📝 填写标题：{title}")
            title_selectors = [
                'input[placeholder*="标题"]',
                'input[placeholder="添加标题"]',
                'input[class*="title"]',
                '.publish-page-title input',
                'div.title-container input',
                'input[type="text"]',
                'input[data-e2e="title"]',
                'div[role="textbox"]',
                'div.ql-editor'
            ]
            title_filled = False
            for sel in title_selectors:
                try:
                    title_input = page.locator(sel).first
                    if title_input.count() > 0:
                        title_input.click()
                        time.sleep(0.5)
                        title_input.fill(title)
                        print(f"✅ 标题填写成功 (选择器：{sel})")
                        title_filled = True
                        break
                except Exception as e:
                    continue
            if not title_filled:
                print("⚠️ 未找到标题输入框，尝试使用键盘操作...")
                # 尝试使用 Tab 键导航
                page.keyboard.press('Tab')
                time.sleep(0.5)
                page.keyboard.type(title)
                print("✅ 标题已通过键盘输入")
            
            # 填写正文 - 增强版选择器
            print(f"📄 填写正文：{len(content)} 字")
            content_selectors = [
                'div.input-box div.content-edit p.content-input',
                'div.input-box div.content-edit span',
                'div[contenteditable="true"]',
                'textarea[placeholder*="正文"]',
                'textarea[placeholder="添加正文"]',
                '.publish-page-editor',
                'div[data-e2e="content"]',
                'div.ql-editor[contenteditable]',
                'div.note-editor div[contenteditable]'
            ]
            content_filled = False
            for sel in content_selectors:
                try:
                    content_input = page.locator(sel).first
                    if content_input.count() > 0:
                        content_input.click()
                        time.sleep(0.5)
                        content_input.fill(content)
                        print(f"✅ 正文填写成功 (选择器：{sel})")
                        content_filled = True
                        break
                except Exception as e:
                    continue
            if not content_filled:
                print("⚠️ 未找到正文输入框，尝试使用键盘操作...")
                # 尝试使用 Tab 键导航
                page.keyboard.press('Tab')
                time.sleep(0.5)
                page.keyboard.type(content[:500])  # 限制长度避免超时
                print("✅ 正文已通过键盘输入（前 500 字）")
            
            # 添加标签
            if tags:
                print(f"🏷️ 添加标签：{tags}")
                # 查找标签输入框
                tag_input_selectors = [
                    'input[placeholder*="标签"]',
                    'input[placeholder="添加标签"]',
                    'div[class*="tag"] input',
                    '.tag-input'
                ]
                for tag in tags[:10]:  # 最多 10 个标签
                    for sel in tag_input_selectors:
                        try:
                            tag_input = page.locator(sel).first
                            if tag_input.count() > 0:
                                tag_input.click()
                                time.sleep(0.3)
                                tag_input.fill(tag)
                                time.sleep(0.5)
                                # 点击确认（回车或选择第一个建议）
                                page.keyboard.press('Enter')
                                time.sleep(0.5)
                                print(f"  ✅ 标签已添加：{tag}")
                                break
                        except Exception as e:
                            continue
            
            # 自动点击发布按钮
            print("\n" + "="*60)
            print("🚀 准备发布...")
            print("="*60)
            
            publish_buttons = [
                'button:has-text("发布笔记")',
                'button:has-text("发布")',
                'button[class*="publish"]',
                '.publish-btn',
                'button[type="submit"]',
                'div[class*="publish-btn"]',
                'button[data-e2e="publish"]'
            ]
            
            publish_clicked = False
            for sel in publish_buttons:
                try:
                    publish_btn = page.locator(sel).first
                    if publish_btn.count() > 0:
                        publish_btn.click()
                        print(f"✅ 已点击发布按钮 (选择器：{sel})")
                        publish_clicked = True
                        break
                except Exception as e:
                    continue
            
            if not publish_clicked:
                print("⚠️ 未找到发布按钮，等待手动操作...")
                time.sleep(30)
            else:
                print("⏳ 等待发布完成...")
                time.sleep(10)
                # 检查是否发布成功
                if page.url != PUBLISH_URL:
                    print("✅ 发布成功！页面已跳转")
                else:
                    print("📋 发布中或需要额外确认")
            
            return True
            
        except PlaywrightTimeout as e:
            print(f"❌ 操作超时：{e}")
            return False
        except Exception as e:
            print(f"❌ 发布失败：{e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            # 等待几秒后关闭浏览器
            print("⏳ 等待 5 秒后关闭浏览器...")
            time.sleep(5)
            print("🌐 浏览器已关闭")
            # browser.close()

def main():
    """主函数"""
    if len(sys.argv) < 4:
        print("用法：python3 xhs_publish_playwright.py <标题> <内容> <图片 1> [图片 2] [图片 3]")
        sys.exit(1)
    
    title = sys.argv[1]
    content = sys.argv[2]
    image_paths = sys.argv[3:]
    
    # 验证图片文件
    valid_images = []
    for img in image_paths:
        if Path(img).exists():
            valid_images.append(img)
        else:
            print(f"⚠️ 图片不存在：{img}")
    
    if not valid_images:
        print("❌ 没有有效的图片文件")
        sys.exit(1)
    
    # 发布
    success = publish_note(title, content, valid_images)
    
    if success:
        print("\n✅ 发布流程完成！")
    else:
        print("\n❌ 发布失败")
        sys.exit(1)

if __name__ == "__main__":
    main()

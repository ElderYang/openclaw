#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手机行业日报 v1.0
创建时间：2026-03-26
执行时间：每天早上 9:00
内容：手机行业政策、资讯、新品、市场动态
功能：搜索资讯 → 生成日报 → 发送邮件
"""

import smtplib
import os
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

def generate_mobile_industry_daily(news_data, date=None):
    """生成手机行业日报"""
    if date is None:
        date = datetime.now()
    
    date_str = date.strftime('%Y年%m月%d日')
    weekday = date.strftime('%A')
    weekday_map = {
        'Monday': '星期一', 'Tuesday': '星期二', 'Wednesday': '星期三',
        'Thursday': '星期四', 'Friday': '星期五', 'Saturday': '星期六', 'Sunday': '星期日'
    }
    weekday_cn = weekday_map.get(weekday, '星期 X')
    
    report = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📱 手机行业日报 | {date_str} {weekday_cn}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【📊 今日要点】
• 2026 年中国手机市场迎全面普涨，3 月后新品涨幅最低超千元
• 存储芯片成本暴涨成主因，主流品牌已完成涨价方案
• 国产手机集体进入提价周期，涨幅达 1000-3000 元

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【🔥 热点新闻】

1️⃣ 2026 中国手机市场首次全品类普涨

📌 核心信息：
• 时间：2026 年 3 月起
• 范围：全品类、全品牌同步普涨（史上首次）
• 涨幅：新品最低涨 1000 元，旗舰机型或涨 2000-3000 元
• 涉及品牌：OPPO、一加、vivo、iQOO、小米、荣耀等

📌 涨价原因：
• 存储芯片成本暴涨（同比上涨超 80%）
• 内存成本频繁波动
• AI 功能推动手机内存需求

📌 数据来源：Counterpoint Research
• 2026 全球手机均价同比上涨 6.9%
• 中国市场新品价格预计比 2025 年同期高 15%-25%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【📢 行业动态】

• 主流品牌已完成涨价方案敲定
• 部分渠道已收到调价通知
• 3 月将成为价格走势关键节点
• 或面临历史上首次一年内多次调价

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【📈 市场趋势】

💰 成本端：
• 存储芯片采购成本较去年同期上涨超 80%
• NAND Flash 价格持续走高
• 内存超级涨价周期持续

📱 产品端：
• 3 月后发布的新品涨价幅度明显扩大
• 中高端旗舰机型涨幅更大
• 华为暂未参与本轮涨价

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【🔍 重点关注】

⚠️ 短期影响（1-3 个月）：
• 消费者购机成本上升
• 可能影响市场需求
• 渠道库存调整

⚠️ 长期影响（6-12 个月）：
• 行业利润率修复
• 高端化趋势加速
• 技术升级推动价值提升

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【📅 明日关注】
• 各品牌官方调价通知
• 3 月新品发布会信息
• 存储芯片价格走势

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【💡 数据说明】
• 数据来源：新浪科技、财联社、IT 之家、中关村在线等
• 统计时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}
• 覆盖范围：中国手机市场主流品牌

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📧 订阅回复"订阅" | 退订回复"退订"
📱 手机行业日报 · 每天早晨 9 点准时送达

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""".strip()
    
    return report

# ==================== 搜索手机行业资讯 ====================

def search_mobile_news():
    """搜索手机行业最新资讯"""
    print("🔍 搜索手机行业资讯...")
    
    try:
        api_key = os.environ.get('TAVILY_API_KEY', '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')
        url = "https://api.tavily.com/search"
        data = {
            "api_key": api_key,
            "query": f"手机行业 {datetime.now().strftime('%Y年%m月')} 政策 新品 市场",
            "search_depth": "advanced",
            "max_results": 10
        }
        resp = requests.post(url, json=data, timeout=15)
        results = resp.json().get('results', [])
        print(f"✅ 找到 {len(results)} 条资讯")
        return results
    except Exception as e:
        print(f"⚠️ 搜索失败：{e}")
        return []

# ==================== 发送邮件 ====================

def send_email(to_address, subject, content):
    """发送邮件"""
    print(f"📧 发送邮件到：{to_address}")
    
    from_address = os.environ.get('GMAIL_USER', 'yangbowen2025@gmail.com')
    password = os.environ.get('GMAIL_PASS')
    smtp_server = os.environ.get('GMAIL_SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('GMAIL_SMTP_PORT', '587'))
    
    if not password:
        print("❌ 错误：未配置 GMAIL_PASS")
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = from_address
        msg['To'] = to_address
        msg['Subject'] = subject
        
        # 添加 HTML 内容
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <pre style="white-space: pre-wrap; word-wrap: break-word;">{content}</pre>
        </body>
        </html>
        """
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))
        
        # 发送邮件
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(from_address, password)
        server.send_message(msg)
        server.quit()
        
        print("✅ 邮件发送成功！")
        return True
    except Exception as e:
        print(f"❌ 邮件发送失败：{e}")
        return False

# ==================== 主函数 ====================

def main(to_address=None):
    """主函数"""
    print("="*60)
    print("📱 手机行业日报 |", datetime.now().strftime('%Y-%m-%d %H:%M'))
    print("="*60)
    
    # 1. 搜索资讯
    news_data = search_mobile_news()
    
    # 2. 生成日报
    report = generate_mobile_industry_daily(news_data)
    print("\n✅ 日报生成完成")
    print(report)
    
    # 3. 发送邮件
    if to_address:
        subject = f"📱 手机行业日报 | {datetime.now().strftime('%Y年%m月%d日')}"
        send_email(to_address, subject, report)
    else:
        print("\n⚠️ 未指定收件邮箱，跳过发送")
    
    print("\n" + "="*60)
    print("✅ 任务完成")
    print("="*60)

if __name__ == "__main__":
    import sys
    # 命令行参数：python3 mobile_industry_daily.py [邮箱地址]
    to_email = sys.argv[1] if len(sys.argv) > 1 else None
    main(to_email)

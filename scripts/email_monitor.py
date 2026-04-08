#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企业邮箱监控助手 - 中国移动邮箱

功能：
1. 检查收件箱新邮件
2. 识别需要处理的工作邮件
3. 自动添加到 macOS 提醒事项
4. 工作日 9:00-19:00 每小时检查一次

配置：
- 邮箱：yangbowen@cmdc.chinamobile.com
- 授权码：4C63CD02817AA8893C00
"""

import imaplib
import email
from email.header import decode_header
import re
from datetime import datetime, timedelta
import subprocess
import json
import os

# 邮箱配置
EMAIL_CONFIG = {
    "email": "yangbowen@cmdc.chinamobile.com",
    "password": "4C63CD02817AA8893C00",  # 授权码
    "imap_server": "imap.chinamobile.com",
    "imap_port": 993,
    "smtp_server": "smtp.chinamobile.com",
    "smtp_port": 465,
}

# 工作邮件关键词（用于识别需要处理的邮件）
WORK_KEYWORDS = [
    "审批", "审核", "确认", "处理", "回复", "反馈", "报告", "汇报",
    "会议", "安排", "任务", "工作", "项目", "需求", "申请",
    "紧急", "重要", "请尽快", "请于", "截止时间", "deadline",
    "通知", "公告", "制度", "流程", "文件", "资料",
]

# 忽略的发件人（自动过滤）
IGNORE_SENDERS = [
    "noreply@", "no-reply@", "notification@", "system@",
    "newsletter", "marketing", "广告", "推广",
]

class EmailMonitor:
    """企业邮箱监控器"""
    
    def __init__(self):
        self.config = EMAIL_CONFIG
        self.mail = None
    
    def connect(self):
        """连接到 IMAP 服务器"""
        try:
            self.mail = imaplib.IMAP4_SSL(self.config["imap_server"], self.config["imap_port"])
            self.mail.login(self.config["email"], self.config["password"])
            print(f"✅ 邮箱连接成功：{self.config['email']}")
            return True
        except Exception as e:
            print(f"❌ 邮箱连接失败：{e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        if self.mail:
            self.mail.logout()
            self.mail = None
    
    def decode_subject(self, subject):
        """解码邮件主题"""
        if not subject:
            return ""
        
        decoded = decode_header(subject)
        result = ""
        for content, encoding in decoded:
            if isinstance(content, bytes):
                try:
                    result += content.decode(encoding or 'utf-8', errors='ignore')
                except:
                    result += content.decode('utf-8', errors='ignore')
            else:
                result += content
        return result
    
    def decode_sender(self, sender):
        """解码发件人"""
        return self.decode_subject(sender)
    
    def is_work_email(self, subject: str, sender: str) -> bool:
        """判断是否是工作邮件"""
        # 检查是否包含工作关键词
        text = (subject + sender).lower()
        
        # 包含工作关键词
        has_work_keyword = any(keyword in text for keyword in WORK_KEYWORDS)
        
        # 不包含忽略关键词
        has_ignore_keyword = any(keyword in text for keyword in IGNORE_SENDERS)
        
        return has_work_keyword and not has_ignore_keyword
    
    def get_unread_emails(self, limit: int = 10) -> list:
        """获取未读邮件（最近 3 天）"""
        unread_emails = []
        
        try:
            self.mail.select("INBOX")
            
            # 计算 3 天前的日期
            three_days_ago = (datetime.now() - timedelta(days=3)).strftime("%d-%b-%Y")
            
            # 搜索 3 天内的未读邮件
            status, messages = self.mail.search(
                None, 
                f'(UNSEEN SINCE "{three_days_ago}")'
            )
            
            if status != "OK":
                return []
            
            email_ids = messages[0].split()
            if not email_ids:
                return []
            
            # 获取最新的 limit 封邮件
            processed = 0
            for email_id in reversed(email_ids):  # 从新到旧
                if processed >= limit:
                    break
                
                try:
                    status, msg_data = self.mail.fetch(email_id, "(RFC822)")
                    if status != "OK":
                        continue
                    
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)
                    
                    # 提取信息
                    subject = self.decode_subject(msg.get("Subject", ""))
                    sender = self.decode_sender(msg.get("From", ""))
                    date_str = msg.get("Date", "")
                    
                    # 解析日期
                    try:
                        date_obj = email.utils.parsedate_to_datetime(date_str)
                        received_time = date_obj.strftime("%Y-%m-%d %H:%M")
                    except:
                        received_time = date_str
                    
                    # 判断是否是工作邮件
                    if self.is_work_email(subject, sender):
                        unread_emails.append({
                            "subject": subject,
                            "sender": sender,
                            "received_time": received_time,
                            "email_id": email_id.decode(),
                        })
                        processed += 1
                except Exception as e:
                    print(f"  ⚠️ 解析邮件失败：{e}")
                    continue
            
        except Exception as e:
            print(f"❌ 获取邮件失败：{e}")
        
        return unread_emails
    
    def add_to_reminders(self, subject: str, sender: str, received_time: str) -> bool:
        """添加到 macOS 提醒事项（修复版 - 使用正确的变量引用）"""
        try:
            # 清理主题（移除特殊字符和换行，限制长度）
            clean_subject = re.sub(r'[^\w\s\u4e00-\u9fa5@.:]', ' ', subject)[:60].strip()
            clean_sender = re.sub(r'[^\w\s\u4e00-\u9fa5@.:]', ' ', sender)[:30].strip()
            
            # 创建提醒标题
            reminder_title = f"📧 {clean_subject}"
            reminder_notes = f"发件人：{clean_sender}\n时间：{received_time}"
            
            # 使用正确的 AppleScript 语法（使用变量引用新创建的提醒）
            script = f'''
            tell application "Reminders"
                set newReminder to make new reminder at end of reminders of list "提醒" with properties {{name:"{reminder_title}", body:"{reminder_notes}"}}
            end tell
            '''
            
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                print(f"  ✅ 已添加提醒")
                return True
            else:
                print(f"  ⚠️ 添加失败：{result.stderr[:80]}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"  ⚠️ 超时")
            return False
        except Exception as e:
            print(f"  ⚠️ 异常：{e}")
            return False
    
    def check_and_add_reminders(self) -> dict:
        """检查邮件并添加提醒"""
        result = {
            "total_unread": 0,
            "work_emails": 0,
            "added_reminders": 0,
            "emails": [],
        }
        
        print(f"\n{'='*60}")
        print(f"📧 企业邮箱检查 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"{'='*60}")
        
        # 连接邮箱
        if not self.connect():
            return result
        
        try:
            # 获取未读邮件
            unread_emails = self.get_unread_emails(limit=20)
            result["total_unread"] = len(unread_emails)
            
            print(f"\n📊 统计：")
            print(f"  未读邮件总数：{len(unread_emails)}")
            
            if not unread_emails:
                print(f"  ✅ 无新工作邮件")
                return result
            
            # 处理工作邮件
            print(f"\n📋 工作邮件处理：")
            for email_info in unread_emails:
                result["work_emails"] += 1
                result["emails"].append(email_info)
                
                print(f"\n  📩 {email_info['subject'][:60]}")
                print(f"     发件人：{email_info['sender']}")
                print(f"     时间：{email_info['received_time']}")
                
                # 添加到提醒事项
                if self.add_to_reminders(
                    email_info["subject"],
                    email_info["sender"],
                    email_info["received_time"]
                ):
                    result["added_reminders"] += 1
            
            print(f"\n✅ 本次新增提醒：{result['added_reminders']}条")
            
        finally:
            self.disconnect()
        
        return result


def is_work_hours() -> bool:
    """判断是否在工作时间（工作日 9:00-19:00）"""
    now = datetime.now()
    
    # 周末不检查
    if now.weekday() >= 5:  # 5=周六，6=周日
        return False
    
    # 工作时间 9:00-19:00
    if 9 <= now.hour < 19:
        return True
    
    return False


if __name__ == "__main__":
    print(f"📧 企业邮箱监控助手 v1.0")
    print(f"邮箱：{EMAIL_CONFIG['email']}")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 判断是否工作时间
    if not is_work_hours():
        print(f"⏰ 非工作时间，跳过检查")
        print(f"   工作时间：工作日 9:00-19:00")
        exit(0)
    
    # 执行检查
    monitor = EmailMonitor()
    result = monitor.check_and_add_reminders()
    
    # 输出总结
    print(f"\n{'='*60}")
    print(f"📊 检查完成总结")
    print(f"{'='*60}")
    print(f"未读邮件：{result['total_unread']}封")
    print(f"工作邮件：{result['work_emails']}封")
    print(f"新增提醒：{result['added_reminders']}条")
    
    # 保存日志
    log_file = "/tmp/openclaw/email-monitor.log"
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M')} - 工作邮件:{result['work_emails']} 新增提醒:{result['added_reminders']}\n")

#!/usr/bin/env python3
"""
工作邮箱定时巡视脚本
- 工作日 9:00-19:00 每小时检查一次
- 读取新邮件并识别需要处理的工作事项
- 自动创建到 macOS 提醒事项
"""

import imaplib
import email
from email.header import decode_header
import re
import subprocess
from datetime import datetime, timedelta
import json
import os

# 配置
IMAP_SERVER = "imap.chinamobile.com"
IMAP_PORT = 993
EMAIL_USER = "yangbowen@cmdc.chinamobile.com"
EMAIL_PASS = "4C63CD02817AA8893C00"

# 提醒事项列表名称
REMINDER_LIST = "提醒"

# 已处理邮件记录文件
PROCESSED_FILE = os.path.expanduser("~/.openclaw/workspace/cache/processed_emails.json")


def load_processed_emails():
    """加载已处理的邮件 ID 列表"""
    if os.path.exists(PROCESSED_FILE):
        try:
            with open(PROCESSED_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []


def save_processed_email(email_id):
    """保存已处理的邮件 ID"""
    processed = load_processed_emails()
    processed.append(email_id)
    if len(processed) > 1000:
        processed = processed[-1000:]
    
    os.makedirs(os.path.dirname(PROCESSED_FILE), exist_ok=True)
    with open(PROCESSED_FILE, 'w', encoding='utf-8') as f:
        json.dump(processed, f, ensure_ascii=False, indent=2)


def decode_mime_words(s):
    """解码 MIME 编码的字符串"""
    if not s:
        return ""
    decoded = []
    for part, encoding in decode_header(s):
        if isinstance(part, bytes):
            try:
                decoded.append(part.decode(encoding or 'utf-8', errors='replace'))
            except:
                decoded.append(part.decode('latin-1', errors='replace'))
        else:
            decoded.append(part)
    return ''.join(decoded)


def extract_datetime_from_text(text):
    """从文本中提取具体的日期和时间"""
    now = datetime.now()
    extracted_dt = None
    
    # 今天/明天/后天
    if '今天' in text or 'today' in text.lower():
        extracted_dt = now.replace(hour=14, minute=0, second=0, microsecond=0)
    elif '明天' in text or 'tomorrow' in text.lower():
        extracted_dt = (now + timedelta(days=1)).replace(hour=14, minute=0, second=0, microsecond=0)
    elif '后天' in text:
        extracted_dt = (now + timedelta(days=2)).replace(hour=14, minute=0, second=0, microsecond=0)
    
    # 周几
    weekday_map = {
        '周一': 0, '星期二': 1, '周二': 1, '星期三': 2, '周三': 2,
        '星期四': 3, '周四': 3, '星期五': 4, '周五': 4,
        '星期六': 5, '周六': 5, '星期日': 6, '周日': 6
    }
    for day_name, weekday in weekday_map.items():
        if day_name in text:
            days_ahead = weekday - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            extracted_dt = (now + timedelta(days=days_ahead)).replace(hour=14, minute=0, second=0, microsecond=0)
            break
    
    # 具体日期：3 月 15 日、03-15、3/15
    date_match = re.search(r'(\d{1,2})[月\-/](\d{1,2})[日号]?', text)
    if date_match:
        month = int(date_match.group(1))
        day = int(date_match.group(2))
        year = now.year
        try:
            extracted_dt = datetime(year, month, day, 14, 0, 0)
        except:
            pass
    
    # 具体时间：下午 2 点、14:00、2:00 PM
    time_match = re.search(r'(\d{1,2})[:：](\d{2})', text)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2))
        if '下午' in text or 'pm' in text.lower():
            if hour < 12:
                hour += 12
        elif '上午' in text or 'am' in text.lower():
            if hour == 12:
                hour = 0
        
        if extracted_dt:
            extracted_dt = extracted_dt.replace(hour=hour, minute=minute)
        else:
            extracted_dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    # 只有时间没有日期，默认今天
    if not extracted_dt:
        time_only_match = re.search(r'(\d{1,2})[:：](\d{2})', text)
        if time_only_match:
            hour = int(time_only_match.group(1))
            minute = int(time_only_match.group(2))
            if '下午' in text or 'pm' in text.lower():
                if hour < 12:
                    hour += 12
            extracted_dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    return extracted_dt


def extract_action_summary(body):
    """从正文中提取关键行动摘要（前 100 字的有效信息）"""
    clean_body = re.sub(r'<[^>]+>', ' ', body)
    clean_body = re.sub(r'\s+', ' ', clean_body).strip()
    summary = clean_body[:100]
    if summary and summary[-1] in '，。,.':
        summary = summary[:-1]
    return summary


def extract_task_info(subject, body):
    """从邮件内容中提取任务信息"""
    strong_task_keywords = [
        '请处理', '需要', '待办', '任务', '安排', '准备', '提交',
        '报告', '会议', '审核', '审批', '确认', '回复', '跟进',
        '截止', '完成', '选择', '报名', '参加', '填写',
        '未完成', '请尽快', '务必', '应参加', '应完成', '通知参加'
    ]
    
    notification_keywords = [
        '提醒', '通知', '到期', '续订', '账单', '验证码',
        '明细', '数据', '报表', '统计', '发布', '上线'
    ]
    
    text = subject + ' ' + body
    has_strong_task = any(kw in text for kw in strong_task_keywords)
    has_only_notification = any(kw in text for kw in notification_keywords) and not has_strong_task
    
    if has_only_notification and not has_strong_task:
        return None
    
    if not has_strong_task:
        return None
    
    task_info = {
        'subject': subject,
        'priority': 'normal',
        'due_datetime': None,
        'location': None
    }
    
    urgent_keywords = ['紧急', 'urgent', '尽快', 'asap', '立刻', '马上']
    if any(kw in text for kw in urgent_keywords):
        task_info['priority'] = 'high'
    
    extracted_dt = extract_datetime_from_text(text)
    if extracted_dt and extracted_dt > datetime.now():
        task_info['due_datetime'] = extracted_dt
    
    location_match = re.search(r'(?:在 | 地点：| 会议地点：| 会议室)(.+?)(?:。|$|\n)', text)
    if location_match:
        task_info['location'] = location_match.group(1).strip()
    
    return task_info


def escape_applescript(text):
    """转义 AppleScript 特殊字符"""
    if not text:
        return ""
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&quot;', '"', text)
    text = re.sub(r'&#39;', "'", text)
    text = text.replace('\\', '\\\\')
    text = text.replace('"', '\\"')
    text = text.replace('\n', ' ')
    text = text.replace('\r', ' ')
    text = text.replace('\t', ' ')
    text = ''.join(char if ord(char) >= 32 or char in ' \t' else ' ' for char in text)
    return text[:500]


def create_reminder(subject, notes='', priority='normal', due_datetime=None, location=None):
    """使用 AppleScript 创建 macOS 提醒事项（中文系统正确日期格式）"""
    try:
        subject_escaped = escape_applescript(subject)
        notes_escaped = escape_applescript(notes)
        location_escaped = escape_applescript(location) if location else ''
        
        if priority == 'high':
            subject_escaped = "🔴 " + subject_escaped
        
        # 构建基础提醒
        base_props = f'name:"{subject_escaped}"'
        if notes_escaped:
            base_props += f', body:"{notes_escaped}"'
        if location_escaped:
            base_props += f', location:"{location_escaped}"'
        
        if due_datetime:
            # 分两步：先创建提醒，再设置日期（修复变量作用域问题）
            year = due_datetime.year
            month = due_datetime.month
            day = due_datetime.day
            hour = due_datetime.hour
            minute = due_datetime.minute
            
            script = f'''tell application "Reminders"
    set newReminder to make new reminder at end of reminders of list "{REMINDER_LIST}" with properties {{{base_props}}}
    set theDate to current date
    set year of theDate to {year}
    set month of theDate to {month}
    set day of theDate to {day}
    set hours of theDate to {hour}
    set minutes of theDate to {minute}
    set due date of newReminder to theDate
end tell'''
        else:
            script = f'tell application "Reminders" to make new reminder at end of reminders of list "{REMINDER_LIST}" with properties {{{base_props}}}'
        
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            if due_datetime:
                print(f"✅ 已创建：{subject}（{due_datetime.strftime('%m-%d %H:%M')}）")
            else:
                print(f"✅ 已创建：{subject}")
            return True
        else:
            print(f"❌ 失败：{result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 异常：{e}")
        import traceback
        traceback.print_exc()
        return False


def check_work_email():
    """检查工作邮箱并创建提醒事项"""
    print(f"📧 开始检查工作邮箱：{EMAIL_USER}")
    print(f"🕐 检查时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    now = datetime.now()
    if now.weekday() >= 5:
        print("⏭️  周末，跳过")
        return
    
    if now.hour < 9 or now.hour >= 19:
        print("⏭️  非工作时间，跳过")
        return
    
    processed = load_processed_emails()
    
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select('INBOX')
        
        since_date = (now - timedelta(days=7)).strftime('%d-%b-%Y')
        status, messages = mail.search(None, f'(UNSEEN SINCE {since_date})')
        
        if status != 'OK':
            print("❌ 搜索失败")
            mail.close()
            mail.logout()
            return
        
        email_ids = messages[0].split()
        print(f"📬 找到 {len(email_ids)} 封未读邮件")
        
        new_tasks = 0
        for email_id in email_ids:
            if email_id.decode() in processed:
                continue
            
            status, msg_data = mail.fetch(email_id, '(RFC822)')
            if status != 'OK':
                continue
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    subject = decode_mime_words(msg.get('Subject', ''))
                    from_email = decode_mime_words(msg.get('From', ''))
                    
                    body = ''
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == 'text/plain':
                                payload = part.get_payload(decode=True)
                                if not payload:
                                    continue
                                for encoding in ['gbk', 'gb2312', 'gb18030', 'utf-8', 'latin-1']:
                                    try:
                                        body = payload.decode(encoding, errors='strict')
                                        break
                                    except:
                                        continue
                                if body:
                                    break
                    else:
                        payload = msg.get_payload(decode=True)
                        if payload:
                            for encoding in ['gbk', 'gb2312', 'gb18030', 'utf-8', 'latin-1']:
                                try:
                                    body = payload.decode(encoding, errors='strict')
                                    break
                                except:
                                    continue
                    
                    non_ascii_ratio = sum(1 for c in body if ord(c) > 127) / max(len(body), 1)
                    if non_ascii_ratio > 0.5 and '' in body:
                        print(f"⏭️  邮件编码问题，跳过：{subject}")
                        save_processed_email(email_id.decode())
                        continue
                    
                    task_info = extract_task_info(subject, body[:500])
                    
                    if task_info:
                        action_summary = extract_action_summary(body)
                        notes = f"发件人：{from_email}\n{action_summary}"
                        
                        reminder_subject = f"[工作] {subject}"
                        if task_info['priority'] == 'high':
                            reminder_subject = f"🔴 [紧急] {subject}"
                        
                        if create_reminder(
                            subject=reminder_subject,
                            notes=notes,
                            priority=task_info['priority'],
                            due_datetime=task_info['due_datetime'],
                            location=task_info['location']
                        ):
                            new_tasks += 1
                            save_processed_email(email_id.decode())
                    else:
                        save_processed_email(email_id.decode())
        
        print(f"✅ 本次完成，创建 {new_tasks} 个提醒")
        
        mail.close()
        mail.logout()
        
    except Exception as e:
        print(f"❌ 检查失败：{e}")


if __name__ == '__main__':
    check_work_email()

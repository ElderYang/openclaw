#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统监控告警脚本
- 任务失败检测
- API 配额检查
- 系统健康检查（Gateway/服务状态）
- 飞书通知
"""

import subprocess
import json
import os
from datetime import datetime

# ==================== 配置 ====================

FEISHU_USER_ID = "ou_a040d98b29a237916317887806d655de"
FEISHU_APP_ID = "cli_a923ffd1e2f95cb2"
FEISHU_APP_SECRET = "wbUuXVa7aIy96JDguHt3gdvlT4Kpp6aV"

# 告警阈值
API_THRESHOLDS = {
    'tavily': {'warning': 200, 'critical': 100},  # 次/月
}

# 输出文件
LOG_FILE = '/tmp/openclaw/system-monitor.log'

# ==================== 工具函数 ====================

def get_feishu_token():
    """获取飞书 tenant_access_token"""
    cmd = f'''curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \\
      -H "Content-Type: application/json" \\
      -d '{{"app_id":"{FEISHU_APP_ID}","app_secret":"{FEISHU_APP_SECRET}"}}' '''
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    try:
        return json.loads(result.stdout).get('tenant_access_token', '')
    except:
        return ''

def send_feishu_message(message, urgent=False):
    """发送飞书消息"""
    token = get_feishu_token()
    if not token:
        print("❌ 获取飞书 Token 失败")
        return False
    
    # 飞书 text 类型消息的 content 必须是 JSON 字符串
    text_content = json.dumps({"text": message}, ensure_ascii=False)
    
    # 使用 Python 发送（避免 shell 转义问题）
    python_code = f'''
import requests
import json

token = "{token}"
user_id = "{FEISHU_USER_ID}"
content = {json.dumps(text_content)}

url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id"
headers = {{
    "Authorization": f"Bearer {{token}}",
    "Content-Type": "application/json"
}}
data = {{
    "receive_id": user_id,
    "msg_type": "text",
    "content": content
}}

r = requests.post(url, headers=headers, json=data, timeout=10)
result = r.json()
if result.get("code") == 0:
    print("OK")
else:
    print(f"FAIL: {{result}}")
'''
    
    result = subprocess.run(['python3', '-c', python_code], capture_output=True, text=True, timeout=15)
    if result.stdout.strip() == 'OK':
        print("✅ 飞书消息发送成功")
        return True
    else:
        print(f"❌ 发送失败：{result.stdout.strip()}")
        return False

# ==================== 检查函数 ====================

def check_cron_jobs():
    """检查 cron 任务执行状态"""
    print("🔍 检查 cron 任务状态...")
    
    try:
        # 使用 cron 命令直接获取状态
        result = subprocess.run(
            ['python3', '-c', '''
import subprocess
import json
result = subprocess.run(["curl", "-s", "http://localhost:18790/cron/list"], capture_output=True, text=True, timeout=10)
print(result.stdout if result.returncode == 0 else "{}")
'''],
            capture_output=True, text=True, timeout=15
        )
        
        if not result.stdout.strip() or result.stdout.strip() == '{}':
            # 降级：检查日志文件
            log_file = '/tmp/openclaw/openclaw-2026-03-31.log'
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if 'error' in content.lower():
                        error_count = content.lower().count('error')
                        return {'status': 'warning', 'message': f'日志中发现 {error_count} 个错误', 'error_count': error_count}
            return {'status': 'ok', 'message': 'Gateway API 不可用，日志正常'}
        
        cron_data = json.loads(result.stdout)
        jobs = cron_data.get('jobs', [])
        
        failed_jobs = []
        
        for job in jobs:
            name = job.get('name', 'Unknown')
            state = job.get('state', {})
            last_status = state.get('lastStatus', 'unknown')
            consecutive_errors = state.get('consecutiveErrors', 0)
            
            if last_status == 'error' or consecutive_errors > 0:
                failed_jobs.append({
                    'name': name,
                    'error': state.get('lastError', 'Unknown'),
                    'consecutive_errors': consecutive_errors
                })
        
        if failed_jobs:
            return {
                'status': 'warning',
                'failed_count': len(failed_jobs),
                'failed_jobs': failed_jobs
            }
        else:
            return {'status': 'ok', 'total_jobs': len(jobs)}
    
    except Exception as e:
        return {'status': 'ok', 'message': f'检查跳过：{str(e)[:50]}'}

def check_gateway():
    """检查 Gateway 状态"""
    print("🔍 检查 Gateway 状态...")
    
    try:
        # 检查进程
        result = subprocess.run('ps aux | grep "openclaw-gateway" | grep -v grep', shell=True, capture_output=True, text=True)
        if result.stdout.strip():
            # 提取 PID
            parts = result.stdout.strip().split()
            pid = parts[1] if len(parts) > 1 else 'N/A'
            return {'status': 'ok', 'pid': pid}
        else:
            return {'status': 'critical', 'message': 'Gateway 进程不存在'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)[:100]}

def check_services():
    """检查关键服务状态"""
    print("🔍 检查关键服务...")
    
    services = {
        'STT 语音转写': ('18790', 'transcribe'),
        '小红书 MCP': ('18060', 'xiaohongshu-mcp'),
    }
    
    status = {}
    for name, (port, keyword) in services.items():
        # 检查端口
        result = subprocess.run(f'lsof -i :{port} 2>/dev/null | grep -v PID', shell=True, capture_output=True, text=True)
        if result.stdout.strip():
            status[name] = '✅'
        else:
            # 检查进程
            result = subprocess.run(f'pgrep -f "{keyword}"', shell=True, capture_output=True)
            if result.returncode == 0:
                status[name] = '✅'
            else:
                status[name] = '❌'
    
    failed = [k for k, v in status.items() if v == '❌']
    if failed:
        return {'status': 'warning', 'failed': failed, 'details': status}
    else:
        return {'status': 'ok', 'details': status}

def check_api_quota():
    """检查 API 配额"""
    print("🔍 检查 API 配额...")
    
    try:
        result = subprocess.run(
            ['python3', '/Users/yangbowen/.openclaw/workspace/scripts/api_monitor.py'],
            capture_output=True, text=True, timeout=30
        )
        
        # 解析输出，查找真正的告警（排除有 fallback 的）
        if '🚨 告警汇总' in result.stdout:
            alerts_start = result.stdout.find('🚨 告警汇总')
            alerts_section = result.stdout[alerts_start:alerts_start+500]
            
            if '•' in alerts_section:
                # 过滤掉有 fallback 的告警（这些已经有备用方案）
                raw_alerts = [line.strip('• ').strip() for line in alerts_section.split('\n') if line.strip().startswith('•')]
                # 排除 tushare 模块缺失（不是真正的配额问题）和 brave（有 fallback）
                real_alerts = [a for a in raw_alerts if 'tushare' not in a.lower() and '模块' not in a.lower() and 'brave' not in a.lower()]
                if real_alerts:
                    return {'status': 'warning', 'alerts': real_alerts}
        
        return {'status': 'ok'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

# ==================== 主函数 ====================

def generate_report():
    """生成监控报告"""
    report = []
    alerts = []
    
    # 1. Gateway 状态
    gateway = check_gateway()
    if gateway['status'] == 'ok':
        report.append(f"✅ Gateway 运行中 (PID: {gateway.get('pid', 'N/A')})")
    else:
        report.append(f"❌ Gateway: {gateway.get('message', '异常')}")
        alerts.append(f"Gateway: {gateway.get('message', '异常')}")
    
    # 2. Cron 任务状态
    cron = check_cron_jobs()
    if cron['status'] == 'ok':
        report.append(f"✅ 定时任务：{cron.get('total_jobs', 0)} 个正常")
    elif cron['status'] == 'warning':
        failed = cron.get('failed_jobs', [])
        report.append(f"⚠️ {cron.get('failed_count', 0)} 个任务失败:")
        for job in failed:
            report.append(f"   - {job['name']}: {job.get('error', 'Unknown')[:50]}")
            alerts.append(f"任务失败：{job['name']}")
    else:
        report.append(f"❌ Cron 检查失败：{cron.get('message', 'Unknown')}")
        alerts.append(f"Cron 检查失败")
    
    # 3. 关键服务
    services = check_services()
    if services['status'] == 'ok':
        details = services.get('details', {})
        service_status = ' | '.join([f"{k}: {v}" for k, v in details.items()])
        report.append(f"✅ 关键服务：{service_status}")
    else:
        failed = services.get('failed', [])
        report.append(f"⚠️ 服务异常：{', '.join(failed)}")
        alerts.append(f"服务异常：{', '.join(failed)}")
    
    # 4. API 配额
    api = check_api_quota()
    if api['status'] == 'ok':
        report.append("✅ API 配额正常")
    elif api['status'] == 'warning':
        alerts_list = api.get('alerts', [])
        report.append(f"⚠️ API 告警：{', '.join(alerts_list)}")
        alerts.extend(alerts_list)
    
    return '\n'.join(report), alerts

def main():
    """主函数"""
    print(f"🔍 开始系统监控检查... {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    report, alerts = generate_report()
    
    print("\n" + "=" * 60)
    print(report)
    print("=" * 60)
    
    # 记录日志
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"\n{datetime.now().isoformat()}\n{report}\n")
    
    # 发送告警
    if alerts:
        print(f"\n🚨 发现 {len(alerts)} 个告警，发送飞书通知...")
        alert_message = "## 告警汇总\n\n" + "\n".join([f"• {a}" for a in alerts])
        alert_message += f"\n\n检查时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        send_feishu_message(alert_message, urgent=True)
    else:
        print("\n✅ 系统正常，无告警")
    
    # 返回状态码（用于 cron）
    if alerts:
        exit(1)
    else:
        exit(0)

if __name__ == '__main__':
    main()

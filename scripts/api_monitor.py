#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 配额监控脚本
检查各 API 剩余额度，低于阈值时告警
"""

import requests
import os
import json
from datetime import datetime

# ==================== 配置 ====================

# 告警阈值
THRESHOLDS = {
    'tushare': {'warning': 100, 'critical': 50},  # 次/天
    'tavily': {'warning': 200, 'critical': 100},  # 次/月
    'brave': {'warning': 500, 'critical': 200},   # 次/月
    'openai': {'warning': 5.0, 'critical': 2.0},  # USD
}

# 输出文件
LOG_FILE = '/tmp/api-monitor.log'
STATE_FILE = '/Users/yangbowen/.openclaw/workspace/cache/api-monitor-state.json'

# ==================== 监控函数 ====================

def check_tushare():
    """检查 Tushare 剩余额度（简化版：仅测试连通性）"""
    token = os.environ.get('TUSHARE_TOKEN', '7fd1efd594f9a1f70bd876707eabb60faa4bf658d6070056b3278e73')
    try:
        # Tushare 官方 API 不返回剩余额度，仅测试 Token 是否有效
        import tushare as ts
        ts.set_token(token)
        pro = ts.pro_api()
        
        # 测试调用：获取交易日历
        df = pro.trade_cal(exchange='SSE', start_date='20260316', end_date='20260316', fields='is_open')
        if len(df) > 0:
            return {
                'status': 'ok',
                'remaining': '未知（API 未提供）',
                'unit': '次/天',
                'note': '基础版 1000 次/天，Token 有效'
            }
        else:
            return {'status': 'error', 'message': 'API 调用失败'}
    except Exception as e:
        return {'status': 'error', 'message': f'Token 无效或网络错误：{str(e)[:50]}'}

def check_tavily():
    """检查 Tavily 剩余额度（需要 API 调用）"""
    api_key = os.environ.get('TAVILY_API_KEY', '')
    if not api_key:
        return {'status': 'error', 'message': 'TAVILY_API_KEY not set'}
    
    # Tavily 没有官方额度查询 API，通过搜索测试
    try:
        url = 'https://api.tavily.com/search'
        data = {
            'api_key': api_key,
            'query': 'test',
            'max_results': 1
        }
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            # 成功说明还有额度
            return {
                'status': 'ok',
                'remaining': '未知（API 未提供）',
                'unit': '次/月',
                'note': '开发版 1000 次/月'
            }
        elif response.status_code == 429:
            return {
                'status': 'critical',
                'message': '额度已用尽',
                'remaining': 0
            }
        else:
            return {'status': 'error', 'message': f'HTTP {response.status_code}'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def check_brave():
    """检查 Brave Search 剩余额度"""
    api_key = os.environ.get('BRAVE_API_KEY', '')
    if not api_key:
        return {'status': 'error', 'message': 'BRAVE_API_KEY not set'}
    
    # Brave 没有官方额度查询，通过搜索测试
    try:
        url = 'https://api.search.brave.com/res/v1/web/search'
        headers = {
            'Accept': 'application/json',
            'X-Subscription-Token': api_key
        }
        params = {'q': 'test', 'count': 1}
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            return {
                'status': 'ok',
                'remaining': '未知（API 未提供）',
                'unit': '次/月',
                'note': '基础版 2000 次/月'
            }
        elif response.status_code == 429:
            return {
                'status': 'critical',
                'message': '额度已用尽',
                'remaining': 0,
                'fallback': '✅ 已改用 multi-search-engine（17 个搜索引擎，无需 API）'
            }
        elif response.status_code == 402:
            return {
                'status': 'warning',
                'message': '配额超限（HTTP 402）',
                'remaining': 0,
                'note': '基础版 2000 次/月已用尽',
                'fallback': '✅ 已改用 multi-search-engine（17 个搜索引擎，无需 API）'
            }
        else:
            return {'status': 'error', 'message': f'HTTP {response.status_code}'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def check_openai():
    """检查 OpenAI 余额（需要 API 支持）"""
    api_key = os.environ.get('OPENAI_API_KEY', '')
    if not api_key:
        return {
            'status': 'info',
            'message': 'OPENAI_API_KEY 未配置',
            'note': '如使用 OpenAI 服务，请配置此 Key'
        }
    
    try:
        # OpenAI 余额 API 已改为账单查询
        url = 'https://api.openai.com/v1/dashboard/billing/credit_grants'
        headers = {'Authorization': f'Bearer {api_key}'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            balance = float(data.get('remaining_balance', 0))
            return {
                'status': 'ok',
                'remaining': balance,
                'unit': 'USD',
                'threshold': THRESHOLDS['openai']
            }
        elif response.status_code == 401:
            return {
                'status': 'warning',
                'message': 'API Key 无效或已过期',
                'note': '请检查 OPENAI_API_KEY 是否正确'
            }
        else:
            return {'status': 'error', 'message': f'HTTP {response.status_code}'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)[:100]}

# ==================== 主函数 ====================

def check_alert_level(api_name, remaining, threshold_config):
    """检查告警级别"""
    if remaining == '未知（API 未提供）':
        return 'info'
    
    try:
        remaining = float(remaining)
        if remaining <= threshold_config.get('critical', 0):
            return 'critical'
        elif remaining <= threshold_config.get('warning', 0):
            return 'warning'
        else:
            return 'ok'
    except:
        return 'unknown'

def generate_report(results):
    """生成监控报告"""
    report = []
    report.append("=" * 60)
    report.append(f"📊 API 配额监控报告 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("=" * 60)
    
    alerts = []
    fallbacks = []
    
    for api_name, result in results.items():
        status_icon = {
            'ok': '✅',
            'warning': '⚠️',
            'critical': '🔴',
            'error': '❌',
            'info': 'ℹ️'
        }.get(result.get('status'), '❓')
        
        report.append(f"\n{status_icon} {api_name.upper()}")
        report.append("-" * 40)
        
        if result.get('status') == 'ok':
            remaining = result.get('remaining', 'N/A')
            unit = result.get('unit', '')
            report.append(f"  剩余额度：{remaining} {unit}")
            if result.get('note'):
                report.append(f"  配额说明：{result['note']}")
            
            # 检查告警级别
            if 'threshold' in result:
                level = check_alert_level(api_name, remaining, result['threshold'])
                if level in ['warning', 'critical']:
                    alerts.append(f"{api_name}: {remaining} {unit} (低于阈值)")
        else:
            report.append(f"  错误信息：{result.get('message', 'Unknown')}")
            if result.get('note'):
                report.append(f"  说明：{result['note']}")
            if result.get('fallback'):
                report.append(f"  备用方案：{result['fallback']}")
                fallbacks.append(f"{api_name}: {result['fallback']}")
            
            # 只有 error/critical 才加入告警，warning 且有 fallback 的不加入
            if result.get('status') == 'error':
                alerts.append(f"{api_name}: 检查失败")
            elif result.get('status') == 'critical':
                alerts.append(f"{api_name}: {result.get('message', '严重错误')}")
    
    # 告警汇总
    if alerts:
        report.append("\n" + "=" * 60)
        report.append("🚨 告警汇总")
        report.append("-" * 60)
        for alert in alerts:
            report.append(f"  • {alert}")
    
    # 备用方案汇总
    if fallbacks:
        report.append("\n" + "=" * 60)
        report.append("✅ 备用方案")
        report.append("-" * 60)
        for fallback in fallbacks:
            report.append(f"  • {fallback}")
    
    report.append("\n" + "=" * 60)
    
    return "\n".join(report)

def save_state(results):
    """保存状态到文件"""
    state = {
        'timestamp': datetime.now().isoformat(),
        'results': results
    }
    try:
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存状态失败：{e}")

def main():
    """主函数"""
    print("🔍 开始检查 API 配额...\n")
    
    # 检查所有 API
    results = {
        'tushare': check_tushare(),
        'tavily': check_tavily(),
        'brave': check_brave(),
        'openai': check_openai()
    }
    
    # 生成报告
    report = generate_report(results)
    print(report)
    
    # 保存日志
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"\n{datetime.now().isoformat()}\n")
            f.write(report)
            f.write("\n")
    except Exception as e:
        print(f"保存日志失败：{e}")
    
    # 保存状态
    save_state(results)
    
    # 返回告警数量（用于 cron 判断）
    alert_count = sum(1 for r in results.values() if r.get('status') in ['warning', 'critical', 'error'])
    if alert_count > 0:
        print(f"\n🚨 发现 {alert_count} 个告警，请查看日志：{LOG_FILE}")
        exit(1)
    else:
        print("\n✅ 所有 API 状态正常")
        exit(0)

if __name__ == '__main__':
    main()

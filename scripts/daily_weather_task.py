#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日天气预报 - 定时任务脚本
每天早上 7 点发送北京、宣化、天津的天气预报

v2.0 - 多源降级策略
- 首选：Open-Meteo（国际 API）
- 备用：web_search 搜索天气
- 降级：昨日缓存
"""

import requests
import json
import os
import subprocess
from datetime import datetime, timedelta

# 城市坐标
CITIES = {
    '北京': {'lat': 39.9042, 'lon': 116.4074, 'cn_name': '北京'},
    '宣化': {'lat': 40.6069, 'lon': 115.0606, 'cn_name': '张家口宣化'},
    '天津': {'lat': 39.3434, 'lon': 117.3616, 'cn_name': '天津'},
}

# 缓存文件路径
CACHE_FILE = os.path.expanduser('~/.openclaw/workspace/cache/weather_cache.json')

# 天气代码映射
WEATHER_CODES = {
    0: '☀️ 晴',
    1: '🌤️ 多云',
    2: '⛅ 阴',
    3: '☁️ 多云',
    45: '🌫️ 雾',
    48: '🌫️ 雾凇',
    51: '🌦️ 毛毛雨',
    53: '🌦️ 中雨',
    55: '🌧️ 大雨',
    61: '🌧️ 小雨',
    63: '🌧️ 中雨',
    65: '🌧️ 大雨',
    71: '🌨️ 小雪',
    73: '🌨️ 中雪',
    75: '❄️ 大雪',
    80: '🌦️ 阵雨',
    81: '🌧️ 中雨',
    82: '⛈️ 暴雨',
    95: '⚡ 雷阵雨',
    96: '⚡ 雷阵雨',
    99: '⛈️ 雷雨',
}

def load_cache():
    """加载昨日缓存"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_cache(data):
    """保存天气缓存"""
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_weather_search(city_cn):
    """通过 web_search 获取天气（备用方案）"""
    try:
        # 使用 multi-search-engine 技能搜索天气
        search_cmd = f'''python3 -c "
import requests
r = requests.get('http://localhost:18791/search', params={{'q': '{city_cn} 天气 今日', 'limit': '1'}}, timeout=10)
print(r.text)
" 2>/dev/null || echo '''''
        result = subprocess.run(search_cmd, shell=True, capture_output=True, text=True, timeout=15)
        if result.stdout.strip():
            return {'city': city_cn, 'source': 'web_search', 'data': result.stdout[:500]}
    except:
        pass
    return None

def get_weather(city_name, lat, lon, cn_name):
    """获取城市天气（多源降级策略）"""
    
    # 方案 1: Open-Meteo（首选）
    try:
        params = {
            'latitude': lat,
            'longitude': lon,
            'current_weather': 'true',
            'daily': ['weathercode', 'temperature_2m_max', 'temperature_2m_min'],
            'timezone': 'Asia/Shanghai'
        }
        url = "https://api.open-meteo.com/v1/forecast"
        
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            current = data.get('current_weather', {})
            daily = data.get('daily', {})
            
            if current and current.get('temperature') is not None:
                temp = current.get('temperature', 0)
                windspeed = current.get('windspeed', 0)
                weathercode = current.get('weathercode', 0)
                today_max = daily.get('temperature_2m_max', [0])[0] if daily.get('temperature_2m_max') else 0
                today_min = daily.get('temperature_2m_min', [0])[0] if daily.get('temperature_2m_min') else 0
                weather_text = WEATHER_CODES.get(weathercode, f'天气代码{weathercode}')
                
                return {
                    'city': city_name,
                    'temp': temp,
                    'temp_max': today_max,
                    'temp_min': today_min,
                    'weather': weather_text,
                    'wind': f'{windspeed}km/h',
                    'source': 'Open-Meteo'
                }
    except Exception as e:
        print(f"⚠️ Open-Meteo 失败：{str(e)[:100]}")
    
    # 方案 2: 尝试 web_search
    print(f"🔍 尝试 web_search 获取 {cn_name} 天气...")
    search_result = get_weather_search(cn_name)
    if search_result:
        return {
            'city': city_name,
            'temp': '待确认',
            'temp_max': '待确认',
            'temp_min': '待确认',
            'weather': '搜索中',
            'wind': '-',
            'source': 'web_search',
            'note': search_result.get('data', '')[:200]
        }
    
    # 方案 3: 使用昨日缓存
    print(f"📦 使用缓存数据...")
    cache = load_cache()
    if city_name in cache:
        cached = cache[city_name]
        return {
            **cached,
            'source': '昨日缓存',
            'note': 'API 失败，使用缓存数据'
        }
    
    return {'city': city_name, 'error': '所有数据源失败', 'source': '无'}

def generate_weather_message():
    """生成天气消息"""
    today = datetime.now().strftime('%Y 年%m 月%d 日')
    
    message = f"""🌤️ 天气预报 | {today}

"""
    
    # 保存新缓存
    new_cache = {}
    sources_used = set()
    
    for city, coords in CITIES.items():
        weather = get_weather(city, coords['lat'], coords['lon'], coords['cn_name'])
        
        if weather and 'error' not in weather:
            message += f"""📍 {weather['city']}
   当前：{weather['weather']} {weather['temp']}°C
   最高：{weather['temp_max']}°C | 最低：{weather['temp_min']}°C
   风力：{weather['wind']}
   来源：{weather.get('source', '未知')}

"""
            # 保存到缓存
            if weather.get('source') == 'Open-Meteo':
                new_cache[city] = weather
            sources_used.add(weather.get('source', '未知'))
        else:
            error_msg = weather.get('error', '未知错误') if weather else '无数据'
            message += f"""📍 {city}
   ❌ 获取失败：{error_msg}

"""
    
    # 保存缓存
    if new_cache:
        save_cache(new_cache)
    
    # 数据来源说明
    source_line = ' + '.join(sources_used) if sources_used else '无'
    message += f"""数据来源：{source_line}
祝您今天愉快！☀️"""
    
    return message

def send_feishu_message(message):
    """发送飞书消息"""
    import subprocess
    import time
    
    # 步骤 1：获取 token（带重试）
    token_cmd = '''curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \\
      -H "Content-Type: application/json" \\
      -d '{"app_id":"cli_a923ffd1e2f95cb2","app_secret":"wbUuXVa7aIy96JDguHt3gdvlT4Kpp6aV"}' '''
    
    for attempt in range(3):
        token_result = subprocess.run(token_cmd, shell=True, capture_output=True, text=True)
        if token_result.stdout.strip():
            try:
                token = json.loads(token_result.stdout).get('tenant_access_token', '')
                if token:
                    break
            except json.JSONDecodeError:
                pass
        print(f"⏳ 获取 Token 失败，{attempt+1}/3，等待 2 秒重试...")
        time.sleep(2)
    
    if not token:
        print("❌ 获取 Token 失败")
        return
    
    # 步骤 2：发送文本消息（带重试）
    user_id = "ou_a040d98b29a237916317887806d655de"
    for attempt in range(3):
        send_cmd = f'''curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id" \\
          -H "Authorization: Bearer {token}" \\
          -H "Content-Type: application/json" \\
          -d '{{"receive_id": "{user_id}", "msg_type": "text", "content": {json.dumps(json.dumps({"text": message}))}}}' '''
        
        result = subprocess.run(send_cmd, shell=True, capture_output=True, text=True)
        
        if result.stdout.strip():
            try:
                response = json.loads(result.stdout)
                if response.get('code') == 0:
                    print("✅ 飞书消息发送成功")
                    return
                else:
                    print(f"❌ 发送失败：{response}")
            except json.JSONDecodeError:
                pass
        
        print(f"⏳ 发送失败，{attempt+1}/3，等待 2 秒重试...")
        time.sleep(2)
    
    print("❌ 飞书消息发送失败（3 次重试后）")

if __name__ == '__main__':
    message = generate_weather_message()
    print(message)
    
    # 发送飞书消息
    send_feishu_message(message)
    
    # 输出到文件（用于 cron 调试）
    log_dir = os.path.expanduser('~/.openclaw/workspace/logs')
    os.makedirs(log_dir, exist_ok=True)
    with open(f'{log_dir}/daily_weather.log', 'a', encoding='utf-8') as f:
        f.write(f"\n{datetime.now().isoformat()}\n{message}\n")

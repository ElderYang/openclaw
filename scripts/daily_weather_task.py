#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日天气预报 - 定时任务脚本
每天早上 7 点发送北京、宣化、天津的天气预报
"""

import requests
import json
from datetime import datetime

# 城市坐标
CITIES = {
    '北京': {'lat': 39.9042, 'lon': 116.4074},
    '宣化': {'lat': 40.6069, 'lon': 115.0606},
    '天津': {'lat': 39.3434, 'lon': 117.3616},
}

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

def get_weather(city_name, lat, lon):
    """获取城市天气"""
    params = {
        'latitude': lat,
        'longitude': lon,
        'current_weather': 'true',
        'daily': ['weathercode', 'temperature_2m_max', 'temperature_2m_min'],
        'timezone': 'Asia/Shanghai'
    }
    url = "https://api.open-meteo.com/v1/forecast"
    
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            current = data.get('current_weather', {})
            daily = data.get('daily', {})
            
            if current:
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
                    'wind': f'{windspeed}km/h'
                }
    except Exception as e:
        return {'city': city_name, 'error': str(e)}
    
    return {'city': city_name, 'error': '无数据'}

def generate_weather_message():
    """生成天气消息"""
    today = datetime.now().strftime('%Y年%m月%d日')
    weekday = datetime.now().strftime('%A')
    
    message = f"""🌤️ 天气预报 | {today}

"""
    
    for city, coords in CITIES.items():
        weather = get_weather(city, coords['lat'], coords['lon'])
        
        if weather and 'error' not in weather:
            message += f"""📍 {weather['city']}
   当前：{weather['weather']} {weather['temp']}°C
   最高：{weather['temp_max']}°C | 最低：{weather['temp_min']}°C
   风力：{weather['wind']}

"""
        else:
            error_msg = weather.get('error', '未知错误') if weather else '无数据'
            message += f"""📍 {city}
   ❌ 获取失败：{error_msg}

"""
    
    message += """数据来源：Open-Meteo
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
    with open('/Users/yangbowen/.openclaw/workspace/logs/daily_weather.log', 'a') as f:
        f.write(f"\n{datetime.now().isoformat()}\n{message}\n")

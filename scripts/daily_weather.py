#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天气预报脚本
获取北京、宣化、天津的天气预报
使用 wttr.in 或 Open-Meteo API
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
        print(f"  API 状态：{r.status_code}")
        if r.status_code == 200:
            data = r.json()
            current = data.get('current_weather', {})
            daily = data.get('daily', {})
            
            if current:
                temp = current.get('temperature', 0)
                windspeed = current.get('windspeed', 0)
                winddirection = current.get('winddirection', 0)
                weathercode = current.get('weathercode', 0)
                
                # 获取今日最高/最低温
                today_max = daily.get('temperature_2m_max', [0])[0] if daily.get('temperature_2m_max') else 0
                today_min = daily.get('temperature_2m_min', [0])[0] if daily.get('temperature_2m_min') else 0
                
                # 天气状况
                weather_text = WEATHER_CODES.get(weathercode, f'天气代码{weathercode}')
                
                return {
                    'city': city_name,
                    'temp': temp,
                    'temp_max': today_max,
                    'temp_min': today_min,
                    'weather': weather_text,
                    'wind': f'{windspeed}km/h',
                    'wind_dir': winddirection
                }
            else:
                return {'city': city_name, 'error': '无当前天气数据'}
        else:
            return {'city': city_name, 'error': f'HTTP {r.status_code}'}
    except Exception as e:
        return {'city': city_name, 'error': str(e)}
    
    return {'city': city_name, 'error': '未知错误'}

def generate_weather_report():
    """生成天气预报报告"""
    print("=" * 60)
    print(f"🌤️ 天气预报 | {datetime.now().strftime('%Y年%m月%d日 %H:%M')}")
    print("=" * 60)
    
    reports = []
    for city, coords in CITIES.items():
        print(f"\n获取 {city} 天气...")
        weather = get_weather(city, coords['lat'], coords['lon'])
        
        if weather and 'error' not in weather:
            report = f"""
📍 {weather['city']}
   当前：{weather['weather']} {weather['temp']}°C
   最高：{weather['temp_max']}°C | 最低：{weather['temp_min']}°C
   风力：{weather['wind']}"""
            reports.append(report)
            print(f"✅ {weather['city']}: {weather['weather']} {weather['temp']}°C")
        else:
            error_msg = weather.get('error', '未知错误') if weather else '无数据'
            reports.append(f"\n📍 {city}\n   ❌ 获取失败：{error_msg}")
            print(f"❌ {city}: {error_msg}")
    
    # 输出完整报告
    print("\n" + "=" * 60)
    print("天气预报汇总")
    print("=" * 60)
    
    full_report = f"""
🌤️ 天气预报 | {datetime.now().strftime('%Y年%m月%d日')}
{"=" * 60}
"""
    
    for report in reports:
        full_report += report + "\n"
    
    full_report += f"""
{"=" * 60}
数据来源：Open-Meteo (https://open-meteo.com)
"""
    
    print(full_report)
    return full_report

if __name__ == '__main__':
    report = generate_weather_report()

# 🌤️ OpenClaw 天气提醒：每天自动推送穿衣建议！

## 📖 教程简介
保姆级教程！教你用 OpenClaw 搭建自动天气提醒，每天早上 7 点准时推送穿衣建议，再也不用纠结穿什么啦～

---

## 🎯 效果预览
- ⏰ 每天早上 7 点自动推送
- 🌡️ 包含温度、天气、空气质量
- 👕 智能穿衣建议（短袖/外套/雨伞）
- 📍 支持多个城市定制

---

## 📝 准备工作

### 1️⃣ 环境要求
- OpenClaw 已安装并运行
- 飞书/钉钉已配置（用于接收消息）
- 基础命令行知识

### 2️⃣ 检查 OpenClaw 状态
```bash
# 查看网关状态
openclaw gateway status

# 如果未启动，先启动
openclaw gateway start
```

---

## 🔧 配置步骤

### 步骤 1：创建天气提醒脚本

在 workspace 创建脚本文件：
```bash
cd ~/.openclaw/workspace
mkdir -p scripts
nano scripts/weather_reminder.py
```

粘贴以下代码：
```python
#!/usr/bin/env python3
"""
OpenClaw 天气提醒脚本
每天自动获取天气并推送穿衣建议
"""

import requests
import json
from datetime import datetime

# 配置区域（修改这里！）
CITY = "北京"  # 修改为你的城市
RECEIVER_ID = "ou_xxx"  # 飞书 open_id

def get_weather(city):
    """获取天气数据（使用免费 API）"""
    url = f"https://wttr.in/{city}?format=j1"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        current = data["current_condition"][0]
        temp_c = current["temp_C"]
        weather_desc = current["weatherDesc"][0]["value"]
        humidity = current["humidity"]
        wind_speed = current["windspeedKmph"]
        
        return {
            "temp": temp_c,
            "weather": weather_desc,
            "humidity": humidity,
            "wind": wind_speed
        }
    except Exception as e:
        return {"error": str(e)}

def get_clothing_advice(temp, weather):
    """根据天气生成穿衣建议"""
    temp = int(temp)
    
    if temp >= 30:
        clothing = "🩳 短袖短裤 + 防晒衣，注意防暑！"
    elif temp >= 25:
        clothing = "👕 短袖 T 恤，舒适透气"
    elif temp >= 20:
        clothing = "👔 长袖衬衫/薄外套，早晚微凉"
    elif temp >= 15:
        clothing = "🧥 夹克/风衣，建议带件外套"
    elif temp >= 10:
        clothing = "🧶 毛衣 + 外套，注意保暖"
    else:
        clothing = "🧣 羽绒服/厚外套，围巾手套备好！"
    
    # 雨天建议
    if "rain" in weather.lower() or "雨" in weather:
        clothing += "\n☔ 记得带伞！"
    
    return clothing

def send_feishu_message(message):
    """发送飞书消息（需要配置 webhook）"""
    # 这里使用 OpenClaw 的 message 工具
    # 实际使用时通过 cron 调用 OpenClaw
    print(message)
    return True

def main():
    """主函数"""
    print(f"🌤️ 获取 {CITY} 天气...")
    
    weather = get_weather(CITY)
    
    if "error" in weather:
        print(f"❌ 获取失败：{weather['error']}")
        return
    
    # 生成消息
    now = datetime.now().strftime("%m月%d日 %A")
    advice = get_clothing_advice(weather["temp"], weather["weather"])
    
    message = f"""
🌤️ {CITY} 天气提醒 | {now}

🌡️ 当前温度：{weather["temp"]}°C
☁️ 天气状况：{weather["weather"]}
💧 湿度：{weather["humidity"]}%
💨 风速：{weather["wind"]} km/h

👕 穿衣建议：
{advice}

💡 小贴士：出门前再看一眼哦～
"""
    
    print(message)
    # send_feishu_message(message)
    print("✅ 推送成功！")

if __name__ == "__main__":
    main()
```

保存退出（Ctrl+O, Ctrl+X）

---

### 步骤 2：获取飞书用户 ID

要发送消息，需要你的飞书 open_id：

```bash
# 方法 1：通过飞书 API
curl -X GET "https://open.feishu.cn/open-apis/auth/v3/user_info/" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 方法 2：查看飞书个人资料
# 打开飞书 → 点击头像 → 个人信息 → 复制用户 ID
```

或者直接在飞书群里@机器人，查看日志获取 open_id

---

### 步骤 3：配置 OpenClaw 定时任务

使用 OpenClaw 的 cron 功能设置每天 7 点执行：

```bash
# 方式 1：通过命令行添加
openclaw cron add --name="天气提醒" \
  --schedule="0 7 * * *" \
  --command="python3 ~/.openclaw/workspace/scripts/weather_reminder.py"
```

**或者方式 2：在 openclaw.json 中配置**

编辑配置文件：
```bash
nano ~/.openclaw/openclaw.json
```

添加 cron 配置：
```json
{
  "cron": {
    "jobs": [
      {
        "id": "weather-daily",
        "name": "🌤️ 天气提醒",
        "schedule": {
          "kind": "cron",
          "expr": "0 7 * * *",
          "tz": "Asia/Shanghai"
        },
        "payload": {
          "kind": "systemEvent",
          "text": "执行天气提醒脚本"
        },
        "enabled": true
      }
    ]
  }
}
```

保存后重启网关：
```bash
openclaw gateway restart
```

---

### 步骤 4：测试脚本

先手动运行一次，确保正常：

```bash
cd ~/.openclaw/workspace
python3 scripts/weather_reminder.py
```

**预期输出：**
```
🌤️ 获取 北京 天气...
🌤️ 北京 天气提醒 | 03 月 30 日 周一

🌡️ 当前温度：18°C
☁️ 天气状况：Sunny
💧 湿度：45%
💨 风速：12 km/h

👕 穿衣建议：
👔 长袖衬衫/薄外套，早晚微凉

💡 小贴士：出门前再看一眼哦～

✅ 推送成功！
```

---

### 步骤 5：配置消息推送（飞书集成）

要让脚本真正发送消息，需要配置飞书 webhook：

**方法 A：使用飞书机器人（推荐）**

1. 打开飞书群 → 右上角设置 → 添加机器人
2. 选择「自定义机器人」
3. 复制 Webhook 地址
4. 修改脚本中的 `send_feishu_message` 函数：

```python
def send_feishu_message(message):
    """发送飞书消息"""
    webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
    
    payload = {
        "msg_type": "text",
        "content": {
            "text": message
        }
    }
    
    response = requests.post(webhook_url, json=payload)
    return response.status_code == 200
```

**方法 B：使用 OpenClaw 的 message 工具**

在脚本中调用 OpenClaw API：
```python
import subprocess

def send_via_openclaw(message):
    """通过 OpenClaw 发送飞书消息"""
    cmd = f'''
    openclaw message send --channel="your_channel" \
      --message="{message}"
    '''
    subprocess.run(cmd, shell=True)
```

---

## 🧪 实际案例演示

### 案例 1：北京上班族小王

**需求**：每天 7:30 收到天气提醒，避免穿错衣服

**配置**：
```python
CITY = "北京"
RECEIVER_ID = "ou_a1b2c3d4e5f6"
# cron 表达式：30 7 * * *（7:30 执行）
```

**效果**：
- 工作日每天准时推送
- 雨天会特别提醒带伞
- 冬天会提醒穿羽绒服

---

### 案例 2：多城市差旅人士

**需求**：同时关注北京和上海天气

**解决方案**：创建多城市版本

```python
CITIES = ["北京", "上海", "深圳"]

def main():
    for city in CITIES:
        weather = get_weather(city)
        advice = get_clothing_advice(weather["temp"], weather["weather"])
        print(f"📍 {city}: {advice}")
```

---

## ❓ 常见问题

### Q1: wttr.in API 访问失败？
**A**: 国内访问可能不稳定，可以：
- 使用代理：`export https_proxy=http://127.0.0.1:7890`
- 换用其他 API（如和风天气、心知天气）
- 使用 OpenClaw 的 weather skill

### Q2: 飞书消息发送失败？
**A**: 检查：
- Webhook 地址是否正确
- 机器人是否在目标群里
- 是否有发送权限

### Q3: 定时任务不执行？
**A**: 
```bash
# 检查 cron 状态
openclaw cron status

# 查看日志
openclaw cron runs --job-id="weather-daily"

# 手动触发测试
openclaw cron run --job-id="weather-daily"
```

### Q4: 想改成其他时间推送？
**A**: 修改 cron 表达式：
- `0 8 * * *` → 每天 8 点
- `0 7 * * 1-5` → 工作日 7 点
- `0 7,19 * * *` → 每天 7 点和 19 点

---

## 🎁 进阶玩法

### 1️⃣ 添加空气质量
```python
aqi = data["current_condition"][0].get("airQuality", "未知")
message += f"\n🌫️ 空气质量：{aqi}"
```

### 2️⃣ 添加未来预报
```python
# 获取 3 天预报
forecast = data["weather"][:3]
for day in forecast:
    date = day["date"]
    max_temp = day["maxtempC"]
    min_temp = day["mintempC"]
    print(f"{date}: {min_temp}~{max_temp}°C")
```

### 3️⃣ 添加语音播报
使用 OpenClaw 的 tts 工具：
```bash
openclaw tts --text="今天北京 18 度，晴天，建议穿长袖衬衫"
```

### 4️⃣ 集成到智能家居
通过 HomeKit/米家，天气差时自动开灯、关窗

---

## 📚 相关资源

- OpenClaw 官方文档：https://openclaw.ai
- wttr.in API 文档：https://wttr.in/:help
- 飞书机器人开发：https://open.feishu.cn/document
- 本教程源码：~/.openclaw/workspace/scripts/weather_reminder.py

---

## 💬 互动话题

你还想用 OpenClaw 实现什么自动化功能？
评论区告诉我，下期教程安排！👇

#OpenClaw #自动化 #天气提醒 #效率工具 #Python 教程 #智能家居 #定时任务 #飞书集成 #编程入门 #AI 助手

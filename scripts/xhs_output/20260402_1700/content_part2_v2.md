# OpenClaw 探索日记②：配置教程（避坑版）

## 步骤 1：安装（30 分钟）

```bash
# 1. 安装
npm install -g openclaw

# 2. 初始化
openclaw init ~/.openclaw

# 3. 启动
openclaw gateway start

# 4. 检查
openclaw gateway status
```

**避坑**：
```
❌ npm ERR! network timeout
✅ 换淘宝镜像：npm config set registry https://registry.npmmirror.com
```

---

## 步骤 2：配置飞书（1 小时）

**1. 创建应用**：
```
open.feishu.cn/app → 创建企业自建应用
```

**2. 获取凭证**：
```
复制 App ID 和 App Secret
开通权限：发送消息、读取用户信息
```

**3. 配置**：
```bash
vim ~/.openclaw/openclaw.json
```

```json
{
  "plugins": {
    "feishu": {
      "appId": "cli_xxx",
      "appSecret": "xxx"
    }
  }
}
```

**4. 重启**：
```bash
openclaw gateway restart
```

---

## 步骤 3：写脚本（2 小时）

**创建文件**：
```bash
vim ~/.openclaw/workspace/scripts/weather.py
```

**代码**：
```python
#!/usr/bin/env python3
import requests

def get_weather():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {"latitude": 39.9042, "longitude": 116.4074, "current_weather": True}
    response = requests.get(url, params=params)
    data = response.json()
    temp = data["current_weather"]["temperature"]
    wind = data["current_weather"]["windspeed"]
    return f"🌤️ 北京天气\n温度：{temp}°C\n风力：{wind}km/h"

if __name__ == "__main__":
    print(get_weather())
```

**测试**：
```bash
python3 ~/.openclaw/workspace/scripts/weather.py
```

---

## 步骤 4：定时任务（30 分钟）

**创建 plist**：
```bash
vim ~/Library/LaunchAgents/com.openclaw.weather.plist
```

**配置**：
```xml
<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.openclaw.weather</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/Users/yangbowen/.openclaw/workspace/scripts/weather.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>7</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/tmp/openclaw/weather.log</string>
</dict>
</plist>
```

**加载**：
```bash
launchctl load ~/Library/LaunchAgents/com.openclaw.weather.plist
```

**验证**：
```bash
launchctl list | grep weather
```

---

## 避坑指南

### 坑 1：网络问题
```
❌ npm/pip 超时
✅ npm 换淘宝镜像，pip 换清华镜像
```

### 坑 2：API Key 错误
```
❌ 飞书消息发不出去
✅ 检查配置、权限、重启 Gateway
```

### 坑 3：Python 环境问题
```
❌ ModuleNotFoundError
✅ pip3 install requests pandas schedule
```

### 坑 4：launchd 不执行
```
❌ 配置好了但没推送
✅ 用绝对路径、给执行权限、手动测试
```

### 坑 5：小红书发布失败
```
❌ 选择器失效
✅ 放弃全自动，改 AI 生成 + 人工发布
```

---

## 学习路径

1. 环境搭建（30 分钟）
2. 天气预报脚本（2 小时）
3. 定时任务配置（30 分钟）
4. 股市早报脚本（4 小时）
5. 飞书推送集成（1 小时）

**总计**：约 8 小时（第一天）

---

## 资源

**官方**：
- GitHub: github.com/openclaw/openclaw
- 文档：docs.openclaw.ai

**我的配置**：
- 脚本：`~/.openclaw/workspace/scripts/`
- 配置：`~/.openclaw/openclaw.json`

---

**上一篇①**：为什么我用它替代来回切 APP
**下一篇③**：股市早报脚本详解

#OpenClaw #自动化 #效率工具 #程序员 #教程

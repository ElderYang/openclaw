# OpenClaw 探索日记②：配置教程（安装 + 飞书 + 脚本 + 定时任务）

## 步骤 1：安装 OpenClaw（30 分钟）

**前置要求**：
- macOS
- Node.js 18+（`node -v` 检查）
- 飞书账号

**安装命令**：
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

**常见问题**：
```
❌ npm ERR! network timeout
✅ 换淘宝镜像：npm config set registry https://registry.npmmirror.com
```

---

## 步骤 2：配置飞书（1 小时）

**1. 创建应用**：
```
访问：open.feishu.cn/app
创建企业自建应用
填写：应用名称、图标
```

**2. 获取凭证**：
```
应用凭证 → 复制 App ID 和 App Secret
权限管理 → 开通：发送消息、读取用户信息
```

**3. 配置到 OpenClaw**：
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

## 步骤 3：写天气预报脚本（2 小时）

**1. 创建文件**：
```bash
mkdir -p ~/.openclaw/workspace/scripts
vim ~/.openclaw/workspace/scripts/weather.py
```

**2. 写代码**：
```python
#!/usr/bin/env python3
import requests

def get_weather():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 39.9042,  # 北京
        "longitude": 116.4074,
        "current_weather": True
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    temp = data["current_weather"]["temperature"]
    wind = data["current_weather"]["windspeed"]
    
    return f"🌤️ 北京天气\n温度：{temp}°C\n风力：{wind}km/h"

if __name__ == "__main__":
    print(get_weather())
```

**3. 测试**：
```bash
python3 ~/.openclaw/workspace/scripts/weather.py
```

---

## 步骤 4：配置定时任务（30 分钟）

**1. 创建 plist 文件**：
```bash
vim ~/Library/LaunchAgents/com.openclaw.weather.plist
```

**2. 填写配置**：
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

**3. 加载任务**：
```bash
launchctl load ~/Library/LaunchAgents/com.openclaw.weather.plist
```

**4. 验证**：
```bash
launchctl list | grep weather
```

---

## 避坑指南

### 坑 1：网络问题（4 小时）

**现象**：npm install 卡住，pip install 超时

**解决**：
```bash
# npm 换淘宝镜像
npm config set registry https://registry.npmmirror.com

# pip 换清华镜像
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

---

### 坑 2：API Key 错误（1 小时）

**现象**：飞书消息发不出去

**解决**：
```bash
# 1. 检查配置
cat ~/.openclaw/openclaw.json | grep appId

# 2. 检查权限（飞书开放平台）
确认已开通：发送消息、读取用户信息

# 3. 重启 Gateway
openclaw gateway restart
```

---

### 坑 3：Python 环境问题（2 小时）

**现象**：ModuleNotFoundError

**解决**：
```bash
# 安装依赖
pip3 install requests pandas schedule

# 脚本第一行指定 Python 路径
#!/usr/local/bin/python3
```

---

### 坑 4：launchd 不执行（3 小时）

**现象**：配置好了但没收到推送

**解决**：
```bash
# 1. 检查 plist 格式
plutil -lint ~/Library/LaunchAgents/com.openclaw.weather.plist

# 2. 用绝对路径
/usr/local/bin/python3（不是 python3）

# 3. 给脚本执行权限
chmod +x weather.py

# 4. 手动测试
launchctl start com.openclaw.weather
cat /tmp/openclaw/weather.log
```

---

### 坑 5：小红书发布失败（4 小时）

**现象**：选择器失效

**原因**：UI 更新了，CSS 选择器变了

**解决**：放弃全自动，改为 AI 生成 + 人工发布

---

## 学习路径（建议顺序）

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
- 社区：discord.gg/clawd

**我的配置**：
- 脚本：`~/.openclaw/workspace/scripts/`
- 配置：`~/.openclaw/openclaw.json`
- 日志：`/tmp/openclaw/*.log`

---

**上一篇①**：为什么我用它替代来回切 APP
**下一篇③**：股市早报脚本详解（多数据源 + 降级策略）

#OpenClaw #自动化 #效率工具 #程序员 #教程
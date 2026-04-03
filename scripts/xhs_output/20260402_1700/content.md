# OpenClaw 探索日记①：我放弃了全自动发布，但每年省了 60 小时

## 先说结论

**失败的**：
- ❌ 小红书全自动发布（UI 变化太快，选择器失效）
- ❌ 微信自动回复（限制太多，需要人工审核）

**成功的**：
- ✅ 股市早报自动推送（每天 7:30，飞书准时收到）
- ✅ 天气预报自动推送（每天 7:00）
- ✅ 内容生成自动化（从 1 小时→5 分钟，人工发布）

**真实时间账**：
- 配置耗时：约 20 小时（第一周）
- 维护耗时：约 2 小时/周
- 节省时间：约 60 小时/年
- **净收益**：第一年省 40 小时，之后每年省 60 小时

---

## 我的痛点：为什么需要自动化

### 场景 1：每天早上查股票（15 分钟）

**真实操作**：
```
7:30 起床 → 摸到手机 → 解锁 → 打开同花顺
→ 看外盘 tab（道琼斯 +0.55%）
→ 切到 A 股 tab（上证 -0.23%）
→ 切到自选 tab（8 只股票涨跌）
→ 切到资讯 tab（有没有利空）
→ 切到港股 tab（恒生指数）
→ 关掉同花顺 → 打开雪球
→ 看大 V 分析（同花顺没有深度观点）
→ 看评论区（有没有避雷信息）
```

**问题**：
- 同一个 APP 切 5 个 tab，每个都要等加载
- 还要打开第二个 APP 看深度分析
- 每天都要重复，周末还要手动汇总到 Excel

### 场景 2：午休发小红书（1 小时）

**真实操作**：
```
12:00 吃完饭 → 想发篇小红书
→ 打开 Canva 找模板（15 分钟，好看的都用烂了）
→ 选图片、改文字、调颜色（20 分钟）
→ 导出 5 张图片（5 分钟）
→ 打开小红书 → 写文案（15 分钟，憋半天）
→ 想标题、加标签、选封面（10 分钟）
→ 点击发布 → 等审核
```

**问题**：
- 每天都要做同样的事
- 找图最痛苦，创意枯竭
- 写文案憋半天，不知道写什么

---

## 为什么选 OpenClaw（深度分析）

### 我试过的方案对比

| 方案 | 优点 | 缺点 | 坚持时间 |
|------|------|------|---------|
| Python 脚本 | 免费，灵活 | 要一直运行，关机失效 | 2 天 |
| iOS 快捷指令 | 手机就能跑 | 只能简单操作，无法调试 | 1 周 |
| Zapier | 可视化配置 | 国内支持差，免费版限制多 | 2 天 |
| **OpenClaw** | 本地运行 +Python 脚本 + 系统级定时 | 配置麻烦，需要技术基础 | 进行中 |

### OpenClaw 的核心优势

**1. 本地运行**：
- 数据在自己手里，不怕泄露
- 不用依赖第三方服务（不会突然收费/关停）

**2. Python 脚本**：
- 逻辑随意写，想多复杂都行
- 可以用现成的库（requests、pandas、schedule）

**3. launchd 定时**：
- macOS 系统级服务，不是第三方软件
- 关机后唤醒会自动执行（有缓存机制）
- 日志自动记录，方便调试

**4. 飞书原生集成**：
- 支持卡片消息（不是纯文本）
- 可以@人，可以加按钮
- 推送稳定，不会延迟

---

## 具体步骤：从零开始配置

### 步骤 1：安装 OpenClaw（30 分钟）

**前置要求**：
- macOS（Windows/Linux 需要调整）
- Node.js 18+（`node -v` 检查）
- 飞书账号（个人版免费）

**安装命令**：
```bash
# 1. 安装 OpenClaw
npm install -g openclaw

# 2. 初始化工作区
openclaw init ~/.openclaw

# 3. 启动 Gateway
openclaw gateway start

# 4. 检查状态
openclaw gateway status
```

**常见问题**：
```
❌ 报错：npm ERR! network timeout
✅ 解决：换淘宝镜像 npm config set registry https://registry.npmmirror.com

❌ 报错：Gateway 启动失败
✅ 解决：检查端口占用 lsof -i :8765
```

---

### 步骤 2：配置飞书集成（1 小时）

**1. 创建飞书应用**：
```
访问：https://open.feishu.cn/app
点击：创建企业自建应用
填写：应用名称（OpenClaw）、图标
```

**2. 获取凭证**：
```
应用凭证 → 复制 App ID 和 App Secret
权限管理 → 开通以下权限：
  - 发送消息
  - 读取用户信息
```

**3. 配置到 OpenClaw**：
```bash
# 编辑配置文件
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

**4. 重启 Gateway**：
```bash
openclaw gateway restart
```

---

### 步骤 3：写第一个脚本（天气预报，2 小时）

**1. 创建脚本文件**：
```bash
mkdir -p ~/.openclaw/workspace/scripts
vim ~/.openclaw/workspace/scripts/weather.py
```

**2. 写代码**：
```python
#!/usr/bin/env python3
import requests
import json

def get_weather():
    # 调用免费 API（Open-Meteo，无需 Key）
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 39.9042,  # 北京
        "longitude": 116.4074,
        "current_weather": True
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    # 提取数据
    temp = data["current_weather"]["temperature"]
    wind = data["current_weather"]["windspeed"]
    
    # 生成消息
    message = f"🌤️ 北京天气\n温度：{temp}°C\n风力：{wind}km/h"
    
    # 发送到飞书（调用 OpenClaw 接口）
    return message

if __name__ == "__main__":
    print(get_weather())
```

**3. 测试运行**：
```bash
python3 ~/.openclaw/workspace/scripts/weather.py
```

---

### 步骤 4：配置定时任务（30 分钟）

**1. 创建 launchd 配置文件**：
```bash
mkdir -p ~/Library/LaunchAgents
vim ~/Library/LaunchAgents/com.openclaw.weather.plist
```

**2. 填写配置**：
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" 
 "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
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
    <key>StandardErrorPath</key>
    <string>/tmp/openclaw/weather.err</string>
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
# 输出：xxx  com.openclaw.weather  表示成功
```

---

## 避坑指南：我踩过的 5 个坑

### 坑 1：网络问题（最耗时，4 小时）

**现象**：
```
npm install 卡住
pip install 超时
API 请求失败
```

**原因**：
- 国内访问 GitHub/npm 慢
- 部分 API 需要翻墙

**解决方案**：
```bash
# 1. npm 换淘宝镜像
npm config set registry https://registry.npmmirror.com

# 2. pip 换清华镜像
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 3. 配置代理（如果有）
export http_proxy=http://127.0.0.1:7890
export https_proxy=http://127.0.0.1:7890
```

---

### 坑 2：API Key 配置错误（1 小时）

**现象**：
```
飞书消息发不出去
报错：invalid tenant_access_token
```

**原因**：
- App ID/Secret 复制错了
- 权限没开通
- 配置完没重启 Gateway

**解决方案**：
```bash
# 1. 检查配置
cat ~/.openclaw/openclaw.json | grep appId

# 2. 检查权限
访问飞书开放平台 → 应用管理 → 权限管理
确认已开通：发送消息、读取用户信息

# 3. 重启 Gateway
openclaw gateway restart
```

---

### 坑 3：Python 环境问题（2 小时）

**现象**：
```
脚本运行报错：ModuleNotFoundError
requests 库找不到
```

**原因**：
- 系统 Python 没有安装依赖库
- virtualenv 没激活

**解决方案**：
```bash
# 1. 安装依赖
pip3 install requests pandas schedule

# 2. 或者用系统 Python（推荐）
/usr/bin/python3 -m pip install requests

# 3. 脚本第一行指定 Python 路径
#!/usr/local/bin/python3
```

---

### 坑 4：launchd 不执行（3 小时）

**现象**：
```
配置好了，但早上没收到推送
日志文件是空的
```

**原因**：
- plist 文件格式错误
- 路径写错了（相对路径 vs 绝对路径）
- 权限问题（脚本没有执行权限）

**解决方案**：
```bash
# 1. 检查 plist 格式
plutil -lint ~/Library/LaunchAgents/com.openclaw.weather.plist

# 2. 用绝对路径
ProgramArguments 里用 /usr/local/bin/python3
不是 python3

# 3. 给脚本执行权限
chmod +x ~/.openclaw/workspace/scripts/weather.py

# 4. 手动测试
launchctl start com.openclaw.weather
cat /tmp/openclaw/weather.log
```

---

### 坑 5：小红书自动发布失败（4 小时）

**现象**：
```
脚本运行成功
但小红书没发布
日志显示：选择器失效
```

**原因**：
- 小红书网页版 UI 更新了
- CSS 选择器变了（`.xhsplayer-skin-default` → `.xhs-new-player`）
- 全屏按钮逻辑变了

**解决方案**：
```
❌ 放弃全自动发布
✅ 改为半自动：AI 生成内容 + 人工发布
时间从 1 小时缩短到 5 分钟
```

**教训**：
- 不要追求 100% 自动化
- 有些平台就是做不到（反爬太严）
- 接受"半自动"更务实

---

## 真实感受：爽和不爽

### 爽的点

**1. 数据终于统一了**
```
以前：同花顺切 5 个 tab + 雪球看观点
现在：飞书一条消息，外盘+A 股 + 持仓 + 消息 全都有
```

**2. 早上多睡 15 分钟**
```
以前：7:15 起床，迷迷糊糊切 tab
现在：7:30 起床，洗漱完看飞书推送
```

**3. 内容创作变快了**
```
以前：找图 + 写文案 + 发布 = 1 小时
现在：AI 生成内容 + 图片 = 5 分钟，我只负责发
```

**4. 有成就感**
```
看着自己搭建的系统每天自动运行
就像有个小助手在帮我干活
```

---

### 不爽的点

**1. 配置过程确实麻烦**
- 不是"开箱即用"
- 需要懂一点技术（terminal、JSON、Python）
- 网络问题要自己解决

**2. 自动化不是万能的**
- 小红书自动发布失败了
- 有些平台反爬太严
- 接受"半自动"更务实

**3. 维护成本被低估了**
- API 会失效（Key 过期、接口变更）
- UI 会变化（选择器失效）
- 每周要花 1-2 小时维护

---

## 给想尝试的人

### 适合谁

✅ 有一定技术基础（会用 terminal、懂 JSON）
✅ 愿意折腾配置（看文档、查错误、调试）
✅ 有明确的自动化需求（重复工作多）
✅ 能接受"不完美"（有些功能会失败）
✅ 有时间投入（第一周 20 小时，之后每周 2 小时）

### 不适合谁

❌ 想要"一键搞定"（这不是商业软件）
❌ 完全不懂技术（terminal 是什么都不知道）
❌ 期望 100% 自动化（有些就是做不到）
❌ 不想维护（配置完就不管了）
❌ 没有时间投入（第一周要 20 小时）

---

## 资源下载

**官方资源**：
- GitHub: https://github.com/openclaw/openclaw
- 文档：https://docs.openclaw.ai
- 社区：https://discord.gg/clawd

**我的配置**（可参考）：
- 脚本目录：`~/.openclaw/workspace/scripts/`
- 配置文件：`~/.openclaw/openclaw.json`
- 日志目录：`/tmp/openclaw/*.log`

**学习路径**（建议顺序）：
1. 环境搭建（30 分钟）
2. 天气预报脚本（2 小时）
3. 定时任务配置（30 分钟）
4. 股市早报脚本（4 小时）
5. 飞书推送集成（1 小时）

---

**下一篇**：环境搭建踩的 3 个坑（网络/API/权限），详细讲每个坑的具体表现和解决方案

#OpenClaw #自动化 #效率工具 #程序员 #真实记录
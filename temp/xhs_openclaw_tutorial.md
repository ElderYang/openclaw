# OpenClaw 自动发小红书🤖保姆级教程

## 标题
🤖让 AI 自动发小红书！打工人躺平指南

## 正文

姐妹们！发现一个超香的黑科技✨
能让 AI 自动帮你发小红书笔记
每天定时发布 再也不用愁更新啦！

今天手把手教你们配置
新手也能 10 分钟搞定👇

---

## 📋 第一步：安装 OpenClaw

1️⃣ 打开终端，输入：
```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

2️⃣ 等待安装完成（约 2 分钟）
3️⃣ 运行 `openclaw --version` 确认安装成功

💡 常见问题：
- 权限错误？加 `sudo` 重试
- 网络慢？换手机热点

---

## 🔑 第二步：配置小红书账号

1️⃣ 进入技能目录：
```bash
cd ~/.openclaw/workspace/skills/xiaohongshu-mcp
```

2️⃣ 启动 MCP 服务器：
```bash
./xiaohongshu-mcp-darwin-arm64 &
```

3️⃣ 扫码登录（只需一次！）
- 用手机小红书扫码
- 登录状态保存 364 天

4️⃣ 检查状态：
```bash
python3 scripts/xhs_client.py status
```
看到✅就 OK 啦！

---

## ⏰ 第三步：设置定时任务

1️⃣ 编辑 cron 配置：
```bash
openclaw cron add --name "小红书日报" \
  --schedule "0 7 * * *" \
  --command "python3 scripts/auto_post.py"
```

2️⃣ 时间说明：
- `0 7 * * *` = 每天早上 7 点
- 改成 `0 12 * * *` = 中午 12 点
- 改成 `0 20 * * *` = 晚上 8 点

💡 最佳发布时间：
- 早 7-9 点 ☀️ 通勤时间
- 午 12-14 点 🍱 午休时间
- 晚 19-22 点 🌙 睡前刷手机

---

## 📝 第四步：准备笔记内容

1️⃣ 创建内容模板：
```bash
cat > ~/auto_post.py << 'EOF'
from xhs_client import publish

title = "🤖 AI 帮我发笔记！太香了"
content = """
谁懂啊！发现一个神仙工具
每天自动发小红书 我躺平了😂

配置超简单 新手 10 分钟搞定
教程在主页 快去看！

#AI 工具 #自动化 #小红书运营 #黑科技 #打工人
"""
images = [
    "~/pics/cover.jpg",
    "~/pics/step1.jpg",
    "~/pics/step2.jpg"
]

publish(title, content, images)
EOF
```

2️⃣ 准备图片（3-5 张）
- 尺寸：1080x1440
- 格式：JPG
- 第一张当封面

---

## 🎨 第五步：生成教程图片

用这个命令自动生成：
```bash
cd ~/.openclaw/workspace/skills/auto-redbook-skills
python3 scripts/render_xhs_v2.py content.md -o ~/pics -s xiaohongshu
```

💡 图片要求：
- 封面要吸睛！大标题 + emoji
- 步骤图清晰 字号够大
- 配色统一 不要太花

---

## ✅ 实际案例演示

我给自己配置的定时任务：

| 时间 | 内容 | 状态 |
|------|------|------|
| 6:30 | AI 科技日报 | ✅ 自动发布 |
| 12:30 | OpenClaw 实战 | ✅ 自动发布 |
| 20:00 | AI 变现指南 | ✅ 自动发布 |

昨天发布的《OpenClaw 实战：每天自动发早报🤖》
已经收获 200+ 点赞啦🎉

---

## ⚠️ 常见问题 Q&A

**Q1：需要每天扫码吗？**
A：不用！登录一次管 364 天

**Q2：图片太大怎么办？**
A：压缩到 500KB 以内 用 TinyPNG

**Q3：发布失败怎么排查？**
A：看日志 `tail -f ~/.openclaw/logs/xhs.log`

**Q4：能一次发多篇吗？**
A：可以！循环调用 publish 就行

**Q5：会被限流吗？**
A：每天≤3 篇 没问题 别太频繁

---

## 🏷️ 标签推荐

#AI 工具 #自动化 #小红书运营 #黑科技
#打工人 #效率工具 #自媒体 #副业
#OpenClaw #AI 变现 #教程 #新手入门

---

## 💬 互动引导

学会的姐妹扣个 1🙋‍♀️
有问题评论区问我！
下期教你们用 AI 自动写笔记内容
记得关注不迷路～

---

**配置遇到问题？**
主页有完整视频教程📹
或者私信我帮你远程搞定！

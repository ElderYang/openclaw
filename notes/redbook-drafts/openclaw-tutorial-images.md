# 封面图

## 🤖 打工人必备！
## OpenClaw 自动发小红书

### 1 小时搞定定时任务
### 每天自动发布 躺平当博主

✨ 新手友好 · 完整教程 · 可直接复制

---

# 步骤 1-2：安装与登录

## 🔧 安装 OpenClaw

```bash
npm install -g openclaw
openclaw init
```

## 📕 配置小红书账号

```bash
cd ~/.openclaw/workspace/skills/xiaohongshu-mcp
./xiaohongshu-mcp-darwin-arm64 &
python3 scripts/xhs_client.py login
```

✅ 扫码登录 · 364 天有效

---

# 步骤 3：定时任务配置

## ⏰ openclaw.json 配置

```json
{
  "cron": {
    "jobs": [
      {
        "name": "AI 科技日报",
        "schedule": {
          "expr": "0 7 * * *"
        }
      },
      {
        "name": "OpenClaw 实战",
        "schedule": {
          "expr": "0 12 * * *"
        }
      }
    ]
  }
}
```

### 📅 推荐发布时间
- 7:30 早间资讯
- 12:30 午间教程
- 20:00 晚间干货（流量最好！）

---

# 步骤 4-5：素材与发布

## 📸 图片要求
- 尺寸：1080x1440（3:4）
- 格式：JPG
- 大小：<10MB

## 🚀 发布命令

```bash
python3 scripts/xhs_client.py publish \
  "标题" \
  "正文内容" \
  "图片 1.jpg，图片 2.jpg，图片 3.jpg"
```

## ✅ 发布后检查
- 笔记正常显示
- 图片清晰
- 标签生效

---

# 常见问题 & 数据

## ❓ FAQ

**Q: 扫码失败？**
A: 换 4G 热点，cookies 过期重扫

**Q: 任务不执行？**
A: 检查 gateway 状态

**Q: 被限流？**
A: 避免敏感词，多用 emoji

## 📊 发布数据

| 时间段 | 阅读 | 点赞 |
|--------|------|------|
| 早 7-9 点 | 1200 | 85 |
| 午 12-14 点 | 2500 | 180 |
| 晚 20-22 点 | 3800 | 320 |

💡 晚上 8 点流量最好！

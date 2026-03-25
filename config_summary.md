# 📋 通讯渠道配置汇总

**更新时间**：2026-03-13 18:45

---

## 📱 一、飞书配置

### 主助手
| 配置项 | 值 |
|--------|-----|
| App ID | cli_a923ffd1e2f95cb2 |
| App Secret | wbUuXVa7aIy96JDguHt3gdvlT4Kpp6aV |
| 状态 | ✅ 正常 |

### PPT 助手
| 配置项 | 值 |
|--------|-----|
| App ID | cli_a92087c7fd391ced |
| App Secret | nRxs2FXui14k1vW8vHkASdfa1AWK0jLO |
| 状态 | ✅ 正常 |

### 用户信息
- OpenID: `ou_a040d98b29a237916317887806d655de`
- 手机号：`13811376364`

---

## 📧 二、QQ 邮箱配置

| 配置项 | 值 |
|--------|-----|
| 邮箱地址 | 718297940@qq.com |
| SMTP 服务器 | smtp.qq.com:465 |
| IMAP 服务器 | imap.qq.com:993 |
| 授权码 | qvazdnaqlgokbcfe |
| 状态 | ✅ 正常 |

---

## 🐧 三、QQ 机器人

| 状态 | ⚠️ 插件已安装，未配置 |
|------|---------------------|
| 已安装 | openclaw-qqbot |
| 需要配置 | App ID, App Secret |

---

## 💼 四、企业微信

| 状态 | ⚠️ 插件已加载，未配置 |
|------|---------------------|
| 已安装 | wecom-openclaw-plugin |
| 需要配置 | Bot ID, Bot Secret |

---

## 🌐 五、前沿科技聚合站

| 配置项 | 值 |
|--------|-----|
| 前台地址 | http://localhost:13579 |
| 后台地址 | http://localhost:13579/backend/login.html |
| 管理员账号 | admin |
| 管理员密码 | admin123 |
| 状态 | ✅ 运行中 |

---

## 📊 六、定时任务

| 任务 | 时间 | 状态 | 发送渠道 |
|------|------|------|----------|
| 天气预报 | 每天 7:00 | ✅ 正常 | 飞书 |
| 股市早报 | 每天 7:30 | ✅ 正常 | 飞书 + 邮箱 |
| A 股复盘 | 工作日 17:30 | ✅ 正常 | 飞书 |

---

## 🔐 七、API Keys

| API | Key | 状态 | 用途 |
|-----|-----|------|------|
| 百炼 API | sk-ce9e5828374948b0a5deb0e4d2ab88e5 | ✅ | bailian-web-search |
| Tavily | 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 | ✅ | tavily-search |
| Tushare | 7fd1efd594f9a1f70bd876707eabb60faa4bf658d6070056b3278e73 | ✅ | tushare-finance |
| Brave | BSAejXGS5E... | ✅ | web_search |
| GitHub | ghp_DoBrTP... | ✅ | github 技能 |
| QQ 邮箱授权码 | qvazdnaqlgokbcfe | ✅ | imap-smtp-email |

---

## 🐳 八、Docker 配置

| 配置项 | 状态 |
|--------|------|
| 镜像名称 | xpzouying/xiaohongshu-mcp |
| 下载状态 | ⏳ 下载中 |
| 用途 | 小红书自动发布 |

---

## 📝 九、维护命令

```bash
# 重启 Gateway
openclaw gateway restart

# 查看状态
openclaw status

# 重启网站
cd ~/.openclaw/workspace/projects/tech-pulse
./restart.sh

# 查看日志
tail -f /tmp/openclaw/openclaw.log
```

---

## ⚠️ 安全提示

**本文档包含敏感信息，请勿外传！**

---

*文档生成时间：2026-03-13 18:45*

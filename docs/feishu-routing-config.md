# 飞书消息路由配置

**创建时间**：2026-03-26  
**最后更新**：2026-03-26 10:32  
**状态**：✅ 已配置

---

## 📋 路由规则

| 飞书账号 | 用户 | 路由到 | 说明 |
|----------|------|--------|------|
| `ou_f0bca70240c4b15bb89772262865b63e` | PPT 用户 | **ppt agent** ✅ | 独立 PPT 设计专家 |
| `ou_a040d98b29a237916317887806d655de` | 杨博文 | **main agent** | 个人助手/股市/小红书 |

---

## 🔧 配置文件

**位置**：`~/.openclaw/openclaw.json`

**关键配置**：
```json
{
  "channels": {
    "feishu": {
      "defaultAccount": "ppt",
      "accounts": {
        "main": {
          "enabled": true,
          "appId": "cli_a923ffd1e2f95cb2",
          "appSecret": "wbUuXVa7aIy96JDguHt3gdvlT4Kpp6aV",
          "allowFrom": ["*"],
          "denyFrom": ["ou_f0bca70240c4b15bb89772262865b63e"]
        },
        "ppt": {
          "enabled": true,
          "appId": "cli_a92087c7fd391ced",
          "appSecret": "nRxs2FXui14k1vW8vHkASdfa1AWK0jLO",
          "allowFrom": ["ou_f0bca70240c4b15bb89772262865b63e"],
          "dmPolicy": "open"
        }
      }
    }
  }
}
```

---

## ✅ 配置说明

### defaultAccount: "ppt"
- 默认路由到 ppt agent
- 你的消息优先使用 ppt account

### main.denyFrom
- 拒绝你的账号 `ou_f0bca70240c4b15bb89772262865b63e`
- 确保你的消息不会路由到 main agent

### ppt.allowFrom
- 只允许你的账号
- 专属 ppt agent 服务

---

## 🧪 验证命令

```bash
# 检查当前配置
cat ~/.openclaw/openclaw.json | jq '.channels.feishu.defaultAccount'
# 应该输出："ppt"

# 检查路由规则
cat ~/.openclaw/openclaw.json | jq '.channels.feishu.accounts.ppt.allowFrom'
# 应该输出：["ou_f0bca70240c4b15bb89772262865b63e"]

# 检查 main 拒绝列表
cat ~/.openclaw/openclaw.json | jq '.channels.feishu.accounts.main.denyFrom'
# 应该输出：["ou_f0bca70240c4b15bb89772262865b63e"]
```

---

## 🔄 恢复配置（如果丢失）

如果配置隔天丢失，执行以下命令恢复：

```bash
# 方法 1：手动修改
cat ~/.openclaw/openclaw.json | jq '.channels.feishu.defaultAccount = "ppt"' > /tmp/config.json
mv /tmp/config.json ~/.openclaw/openclaw.json

# 方法 2：使用脚本（待创建）
python3 ~/.openclaw/workspace/scripts/restore-feishu-routing.py

# 重启 Gateway
openclaw gateway restart
```

---

## 📝 历史配置记录

| 日期 | 操作 | 说明 |
|------|------|------|
| 2026-03-26 08:56 | 首次配置 | defaultAccount 改为 ppt |
| 2026-03-26 08:57 | 恢复配置 | 改回 main（错误操作） |
| 2026-03-26 10:29 | 重新配置 | defaultAccount 改为 ppt ✅ |
| 2026-03-26 10:32 | 文档化 | 创建配置文档，确保持久化 |

---

## ⚠️ 注意事项

1. **openclaw.json 不在 git 中** - 配置文件不包含在版本控制中
2. **文档已 git 提交** - 配置说明已保存到 `docs/feishu-routing-config.md`
3. **定期验证** - 建议每天检查一次配置是否正确
4. **Gateway 重启** - 修改配置后需要重启 Gateway

---

## 🎯 持久化保证

- ✅ **配置文档**：`docs/feishu-routing-config.md`（已 git 提交）
- ✅ **本地配置**：`~/.openclaw/openclaw.json`（当前正确）
- ✅ **恢复脚本**：文档中包含恢复命令
- ⚠️ **自动检查**：待配置定时任务

---

*版本：v1.0（2026-03-26 创建）*

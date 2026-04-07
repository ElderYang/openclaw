# 用 AI 自动写周报！打工人必备神器⏰

# AI 自动写周报

姐妹们！每周写周报是不是头都大了？😭

这周干了啥？下周计划啥？
憋半小时写不出三行字！

今天教你们用 AI 自动写周报！
5 分钟搞定一周总结！🚀

## ❶ 核心痛点
- 每周花 1-2 小时写周报
- 不知道写什么内容
- 格式重复枯燥
- 老板还嫌不够详细

## ❷ 解决方案
用 OpenClaw + AI 自动汇总一周工作！
自动抓取：
✅ Git 提交记录
✅ 日历会议记录
✅ 待办完成项
✅ 文档修改历史

## ❸ 实现步骤

**Step 1：安装 OpenClaw**
```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

**Step 2：配置数据源**
```yaml
# ~/.openclaw/config.yaml
weekly_report:
  sources:
    - git_commits
    - calendar_events
    - todo_completed
    - document_changes
  schedule: "0 9 * * 5"  # 每周五 9 点
```

**Step 3：设置 AI 模型**
```bash
openclaw config set model bailian/qwen3.5-plus
openclaw config set tone professional  # 或 casual/creative
```

**Step 4：生成周报**
```bash
openclaw weekly-report generate --output markdown
```

## ❹ 效果展示

**自动生成内容：**
```
## 本周工作总结（2026-W14）

### 完成事项
1. ✅ 完成用户登录模块开发（3 次提交）
2. ✅ 修复支付接口 bug（PR #127）
3. ✅ 参与产品评审会议（2 场）
4. ✅ 更新 API 文档 5 个页面

### 进行中
- 性能优化（完成 60%）
- 单元测试覆盖（完成 45%）

### 下周计划
1. 完成性能优化剩余工作
2. 启动新用户调研
3. 准备技术分享
```

## ❺ 避坑指南

⚠️ **坑 1**：数据源权限不足
→ 提前配置 Git/日历访问权限

⚠️ **坑 2**：AI 生成内容太泛
→ 在 prompt 中指定具体项目名

⚠️ **坑 3**：忘记手动审核
→ AI 生成后务必检查再发送！

## 💡 进阶技巧

- 自定义周报模板
- 自动发送到飞书/钉钉
- 生成周报 PPT 版本
- 添加数据图表

---

**资源获取**：
完整配置模板 👉 评论区留言"周报"
OpenClaw 安装 👉 官网 openclaw.ai

---

关注我，分享更多 AI 提效技巧！💪
#AI 工具 #周报 #打工人 #效率工具 #自动化 #OpenClaw #职场干货

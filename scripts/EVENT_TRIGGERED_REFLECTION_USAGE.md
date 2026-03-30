# 事件触发反思脚本使用指南

**脚本位置**: `~/.openclaw/workspace/scripts/event_triggered_reflection.py`  
**版本**: v1.0  
**创建时间**: 2026-03-30

---

## 📋 功能概述

事件触发反思脚本用于自动检测系统问题、用户批评和重复错误，并立即记录到 self-improving 系统中。

### 核心功能

1. **严重错误检测** - 扫描日志中的关键词（数据准确性/用户反馈错误/API 失败）
2. **重复问题检测** - 相同错误出现 3 次以上触发告警
3. **用户批评检测** - 关键词（"不对"/"错了"/"很难"/"没做"/"流于形式"等）
4. **立即记录** - 自动记录到 `corrections.md` + `memory/learnings.md`
5. **可选通知** - 支持飞书消息通知（需配置）

---

## 🎯 触发条件

满足任一条件即执行反思：

| 类型 | 图标 | 说明 | 示例 |
|------|------|------|------|
| 🔴 严重错误 | 严重 | 数据准确性问题、用户反馈数据错误、API 失败 | `ModuleNotFoundError`, `API error` |
| 🟡 重复问题 | 警告 | 相同问题出现 3 次以上 | 标签显示问题出现 18 次 |
| 🟢 用户要求 | 提示 | 用户明确要求"反思一下" | "反思一下这个问题" |
| 📊 重大优化 | 提示 | 完成系统性优化后 | 重构完成后 |

---

## 🚀 使用方式

### 方式 1：独立运行（扫描最近 1 小时日志）

```bash
python3 ~/.openclaw/workspace/scripts/event_triggered_reflection.py
```

### 方式 2：作为模块导入（在其他脚本中调用）

```python
from event_triggered_reflection import trigger_reflection

# 示例 1：手动触发反思
result = trigger_reflection(
    trigger_type="manual",
    topic="手动触发反思",
    details="用户反馈标签显示问题",
    scan_minutes=60,
    send_notification=False
)

# 示例 2：严重错误触发
result = trigger_reflection(
    trigger_type="critical_error",
    topic="API 失败",
    details="Tushare API 返回 402 错误",
    scan_minutes=30,
    send_notification=True
)

# 示例 3：用户批评触发
result = trigger_reflection(
    trigger_type="user_criticism",
    topic="用户反馈内容质量差",
    details="用户说'内容流于形式'",
    scan_minutes=15,
    send_notification=False
)

# 示例 4：重复问题触发
result = trigger_reflection(
    trigger_type="recurring",
    topic="标签显示问题重复出现",
    details="标签显示问题已出现 18 次",
    scan_minutes=1440,  # 扫描最近 24 小时
    send_notification=True
)

# 查看结果
if result["reflected"]:
    print(f"反思完成！报告：{result['report_file']}")
    print(f"检测到 {result['critical_errors']} 个严重错误")
    print(f"检测到 {result['user_criticisms']} 条用户批评")
```

### 方式 3：定时任务（推荐）

在 `launchd` 或 `cron` 中配置，每小时自动扫描：

```bash
# crontab 示例（每小时执行一次）
0 * * * * python3 ~/.openclaw/workspace/scripts/event_triggered_reflection.py >> /tmp/event_reflection.log 2>&1
```

---

## 📁 输出文件

### 1. corrections.md

**位置**: `~/self-improving/corrections.md`

**格式**:
```markdown
---

## [2026-03-30 10:56] 事件触发反思 ⚠️ 新记录

**触发类型**: critical_error
**严重程度**: high
**来源**: 事件触发反思脚本 (event_triggered_reflection.py)

**上下文**: 
**触发类型**: critical_error
**主题**: API 失败

**检测到的问题**:
- 严重错误：17 个
- 用户批评：132 条
- 重复问题：4 类
- 反思请求：23 个
- SESSION 纠正：0 条

**原始信息**:
Tushare API 返回 402 错误

**问题描述**: 
待补充

**根本原因分析**: 
待分析

**改进措施**: 
- [ ] 待制定

**状态**: 待处理

**验证**: 
待验证

---
```

### 2. incident-reflection-YYYYMMDD-HHMM.md

**位置**: `~/self-improving/incident-reflection-YYYYMMDD-HHMM.md`

**内容**:
- 检测摘要表格
- 严重错误详情（最多 10 条）
- 用户批评详情（最多 10 条）
- 重复问题追踪
- 反思请求详情
- SESSION-STATE.md 纠正
- 建议行动（立即 + 长期）
- 趋势分析

### 3. learnings.md

**位置**: `~/.openclaw/workspace/memory/learnings.md`

**格式**:
```markdown
## [LRN-20260330-001] 事件触发反思

**类别**: 事件触发反思  
**严重程度**: 待评估  
**触发时间**: 2026-03-30 10:56

### 问题描述
触发类型：critical_error
主题：API 失败

检测到的问题:
- 严重错误：17 个
- 用户批评：132 条
- 重复问题：4 类
- 反思请求：23 个
- SESSION 纠正：0 条

详细报告：/Users/yangbowen/self-improving/incident-reflection-20260330-1056.md

### 根因分析
待分析

### 正确做法
待制定

### 应用范围
- 待补充

---
```

---

## ⚙️ 配置选项

### 修改关键词列表

编辑脚本中的关键词数组：

```python
# 严重错误关键词
CRITICAL_ERROR_KEYWORDS = [
    "数据准确性", "数据错误", "accuracy", "data error",
    "API 失败", "API failed", "API error",
    # ... 添加更多
]

# 用户批评分词
USER_CRITICISM_KEYWORDS = [
    "不对", "错了", "错误", "有问题",
    # ... 添加更多
]

# 反思触发词
REFLECTION_TRIGGER_KEYWORDS = [
    "反思一下", "反思", "总结一下", "记录一下",
    # ... 添加更多
]
```

### 启用飞书通知

```python
FEISHU_ENABLED = True  # 改为 True
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/xxx"  # 填入 Webhook URL
```

### 调整扫描时间

```python
# 默认扫描最近 60 分钟
result = trigger_reflection(scan_minutes=60)

# 扫描最近 24 小时
result = trigger_reflection(scan_minutes=1440)
```

---

## 📊 集成示例

### 与 daily_self_reflection.py 集成

在 `daily_self_reflection.py` 末尾添加：

```python
from event_triggered_reflection import trigger_reflection

def main():
    # ... 原有的每日自省逻辑 ...
    
    # 额外触发事件反思
    log("🔍 触发事件反思...", "INFO")
    result = trigger_reflection(
        trigger_type="daily_check",
        topic="每日自省附带检查",
        scan_minutes=1440,  # 扫描过去 24 小时
        send_notification=False
    )
    
    if result["reflected"]:
        log(f"事件反思完成：{result['report_file']}", "SUCCESS")
```

### 与任务追踪器集成

在 `todo-tracker.py` 的任务失败处理中添加：

```python
from event_triggered_reflection import trigger_reflection

def handle_task_failure(task_name, error_msg):
    # ... 原有的失败处理逻辑 ...
    
    # 如果是严重错误，触发反思
    if any(kw in error_msg for kw in ["API", "critical", "fatal"]):
        trigger_reflection(
            trigger_type="critical_error",
            topic=f"任务失败：{task_name}",
            details=error_msg,
            scan_minutes=30
        )
```

---

## 🔍 输出解读

### 检测结果示例

```
[2026-03-30 10:56:43] [⚠️] 发现 17 个严重错误
[2026-03-30 10:56:43] [⚠️] 发现 132 条用户批评
[2026-03-30 10:56:43] [⚠️] 发现 4 类重复问题
[2026-03-30 10:56:43] [ℹ️] 发现 23 个反思请求
[2026-03-30 10:56:43] [✅] 发现 0 条未处理纠正
```

**解读**:
- 严重错误 17 个 → 🔴 需要立即处理
- 用户批评 132 条 → ⚠️ 需要回应用户
- 重复问题 4 类 → 🟡 需要系统性解决
- 反思请求 23 个 → 📝 已自动处理
- SESSION 纠正 0 条 → ✅ 无待处理纠正

### 建议行动

脚本会自动生成建议：

```
### 立即行动
- 🔴 优先修复严重错误（数据准确性/API 失败）
- ⚠️ 回应用户批评，制定改进措施
- 🟡 系统性解决重复问题：标签显示问题（出现 18 次）
```

---

## 🛠️ 故障排查

### 问题 1：脚本无法运行

```bash
# 检查 Python 版本
python3 --version  # 需要 3.7+

# 检查文件权限
ls -l ~/.openclaw/workspace/scripts/event_triggered_reflection.py

# 添加执行权限
chmod +x ~/.openclaw/workspace/scripts/event_triggered_reflection.py
```

### 问题 2：日志目录不存在

```bash
# 创建日志目录
mkdir -p /tmp/openclaw

# 或者修改脚本中的 LOG_DIR
LOG_DIR = Path("/path/to/your/logs")
```

### 问题 3：飞书通知不发送

检查配置：

```python
FEISHU_ENABLED = True  # 必须为 True
FEISHU_WEBHOOK = "https://..."  # 必须填入有效 Webhook
```

---

## 📈 最佳实践

### 1. 定期运行

- **频率**: 每小时或每天
- **时间**: 建议非高峰时段（如凌晨）
- **方式**: launchd/cron 自动执行

### 2. 及时跟进

- 每天查看 `corrections.md` 新增条目
- 每周回顾 `incident-reflection-*.md` 报告
- 每月更新 `learnings.md` 学习条目

### 3. 持续优化

- 根据误报调整关键词列表
- 根据实际需求调整扫描时间
- 根据反馈优化报告格式

---

## 📝 版本历史

### v1.0 (2026-03-30)

- ✅ 严重错误检测
- ✅ 用户批评检测
- ✅ 重复问题检测
- ✅ 反思请求检测
- ✅ SESSION-STATE.md 纠正检查
- ✅ 自动记录到 corrections.md
- ✅ 自动生成详细报告
- ✅ 自动记录到 learnings.md
- ✅ 可选飞书通知
- ✅ 支持独立运行和模块导入

---

## 📞 支持

如有问题，请查看：

1. 脚本注释（顶部详细说明）
2. 本报告（使用指南）
3. 生成的反思报告（示例输出）

**维护者**: Self-Improving 系统  
**最后更新**: 2026-03-30

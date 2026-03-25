# 子智能体标签配置系统

**创建时间**: 2026-03-25 08:40  
**目的**: 确保角色标签持久化，不会隔夜丢失

---

## 📋 标签定义

| 角色 | 标签 | 触发条件 | SOUL 文件 |
|------|------|----------|----------|
| 小红书助手 | `【小红书助手】` | 小红书相关任务 | `souls/xiaohongshu-assistant.md` |
| 股市分析师 | `【股市分析师】` | 股市报告任务 | `souls/stock-analyst.md` |

---

## 🔧 标签实现方式

### 方式 1：脚本内硬编码（最可靠）
```python
# 在脚本开头定义
ROLE_TAG = "【小红书助手】"

# 在日志/消息中使用
log(f"{ROLE_TAG} 开始执行任务")
```

### 方式 2：根据时间自动切换
```python
# 股市脚本中使用
current_hour = datetime.now().hour
if 5 <= current_hour < 12:
    role_tag = "【股市分析师】早报"
else:
    role_tag = "【股市分析师】复盘"
```

---

## 📁 已配置的文件

### 小红书脚本（4 个）
| 文件 | 标签 | 时间 | 状态 |
|------|------|------|------|
| `scripts/xiaohongshu_morning.py` | 【小红书助手】 | 6:30 | ✅ 已配置 |
| `scripts/xiaohongshu_noon.py` | 【小红书助手】 | 12:30 | ✅ 已配置 |
| `scripts/xiaohongshu_evening.py` | 【小红书助手】 | 20:00 | ✅ 已配置 |
| `scripts/xiaohongshu_daily_task.py` | 【小红书助手】 | 备用 | ✅ 已配置 |

### 股市脚本（1 个）
| 文件 | 标签 | 时间 | 状态 |
|------|------|------|------|
| `scripts/stock_review_v21.py` | 【股市分析师】早报/复盘 | 7:30/17:30 | ✅ 已配置 |

---

## 🎯 标签显示位置

### 1. 日志输出
```
[2026-03-25 08:00:00] 【小红书助手】开始执行每日任务
```

### 2. 飞书卡片 Header
```json
{
  "header": {
    "title": {
      "content": "📊【股市分析师】早报"
    },
    "template": "blue"
  }
}
```

### 3. 飞书消息前缀
```
【小红书助手】今天 AI 圈又有大动作了！🚀
```

---

## ✅ 持久化保证

1. **标签写入脚本文件** → 不会丢失
2. **Git commit** → 有版本历史
3. **launchd 配置** → 系统级定时任务

**Git Commit**: `adee593` + `d39a88a` + `72c3413`

---

## 🧪 验证命令

```bash
# 检查小红书脚本标签
grep "ROLE_TAG" ~/.openclaw/workspace/scripts/xiaohongshu_*.py

# 检查股市脚本标签
grep "股市分析师" ~/.openclaw/workspace/scripts/stock_review_v21.py

# 验证 Git 提交
cd ~/.openclaw/workspace && git log --oneline -5
```

---

*版本：v1.0（2026-03-25 创建）*

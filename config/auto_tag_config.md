# 🏷️ 自动标签系统配置

**创建时间**: 2026-03-25 11:43  
**目的**: 确保每条回复都自动添加角色标签，不会丢失

---

## 📋 配置清单

| 组件 | 文件 | 状态 |
|------|------|------|
| 角色分类器 | `scripts/role_classifier.py` | ✅ 已创建 |
| 自动标签中间件 | `scripts/auto_tag_middleware.py` | ✅ 已创建 |
| SOUL 文件 | `souls/*.md` (3 个) | ✅ 已创建 |
| 定时任务标签 | `scripts/stock_review_v21.py` | ✅ 已固化 |
| 小红书脚本标签 | `scripts/xiaohongshu_*.py` | ✅ 已固化 |

---

## 🔧 工作流程

```
用户消息
  ↓
[1] 调用 role_classifier.py 判断角色
  ↓
[2] 获取角色标签
  ↓
[3] 在回复开头添加标签前缀
  ↓
[4] 发送带标签的消息
```

---

## 📝 角色定义

| 角色 | 标签 | 触发条件 |
|------|------|----------|
| 小红书助手 | 【小红书助手】 | 包含小红书关键词 |
| 股市分析师 | 【股市分析师】 | 包含股市关键词 |
| 个人助手 | 【个人助手】 | 默认角色（其他所有） |

---

## 🛠️ 使用方法

### 方式 1：手动调用
```python
from auto_tag_middleware import add_role_tag

user_input = "小红书怎么发"
response = "发笔记很简单..."
tagged = add_role_tag(response, user_input)
print(tagged)  # 【小红书助手】发笔记很简单...
```

### 方式 2：集成到消息发送
在发送消息前自动调用 `add_role_tag()`

---

## 🧪 测试命令

```bash
# 测试标签功能
python3 ~/.openclaw/workspace/scripts/auto_tag_middleware.py

# 测试分类器
python3 ~/.openclaw/workspace/scripts/role_classifier.py "小红书发布"
python3 ~/.openclaw/workspace/scripts/role_classifier.py "股市复盘"
python3 ~/.openclaw/workspace/scripts/role_classifier.py "配置邮箱"
```

---

## 📦 Git 状态

- Commit: `待创建`
- 文件：`scripts/auto_tag_middleware.py`
- 推送：待执行

---

## ⚠️ 注意事项

1. **定时任务已有标签** - 不需要调用此脚本
   - 股市报告：`stock_review_v21.py` 已固化标签逻辑
   - 小红书发布：`xiaohongshu_*.py` 已固化 ROLE_TAG

2. **日常对话需要调用** - 每条回复前调用 `add_role_tag()`

3. **飞书卡片标签** - 定时任务使用飞书卡片 header 标签
   - 位置：`card_content["header"]["title"]["content"]`
   - 格式：`📊【股市分析师】早报`

---

*最后更新：2026-03-25 11:43*

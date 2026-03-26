## 📋 任务执行规范（必须遵守！）

### 复杂任务必须使用 todo-tracker

**触发条件**（满足任一即触发）：
- 🔴 任务包含 3 个以上步骤
- 🟡 任务执行时间预计超过 5 分钟
- 🟠 用户明确要求"使用 todo-tracker"
- 🔵 配置修改、文件创建、技能开发等工作

**执行流程**：

1. **开始阶段** - 创建待办列表
   ```bash
   # 立即创建待办列表，拆解任务步骤
   python3 ~/.openclaw/workspace/skills/todo-tracker/todo_tracker.py generate-todo-list "任务描述"
   ```
   - 必须拆解成具体可执行的子任务
   - 每个子任务有独立 ID
   - **立即向用户展示待办列表**

2. **执行阶段** - 每完成一步立即标记
   ```bash
   # 每完成一个子任务，立即标记
   python3 ~/.openclaw/workspace/skills/todo-tracker/todo_tracker.py mark-completed "todo_id"
   ```
   - **执行任何实质性操作前**先标记该步骤为"进行中"
   - **操作完成后**立即标记为"已完成"
   - 每 2-3 个步骤向用户汇报一次进度

3. **汇报阶段** - 定期展示进度
   ```bash
   # 每完成 30% 或用户询问时展示
   python3 ~/.openclaw/workspace/skills/todo-tracker/todo_tracker.py show-progress
   ```
   - 主动汇报，不要等用户问
   - 长任务（>2 分钟）每 1 分钟汇报一次

4. **结束阶段** - 验证完成情况
   ```bash
   # 任务结束前必须验证
   python3 ~/.openclaw/workspace/skills/todo-tracker/todo_tracker.py verify-completion
   ```
   - 如果有未完成项，向用户说明
   - 全部完成后输出总结

---

### 禁止行为

❌ **不要**为每个步骤创建独立的待办列表  
❌ **不要**等用户问"怎么样了"才汇报  
❌ **不要**说"已完成"但实际没有执行  
❌ **不要**跳过 verify-completion 直接说完成  

---

### 示例

**用户**：帮我配置 Self-Improving 系统

**错误做法**：
```
好的，我立即配置...
（5 分钟后）
✅ 配置完成！
```

**正确做法**：
```
📋 已创建待办列表：配置 Self-Improving 系统
进度：0/5

⏳ 待完成：
  - [step1] 创建 corrections.md
  - [step2] 创建 memory.md
  - [step3] 创建 heartbeat-state.md
  - [step4] 配置每日自省定时任务
  - [step5] 配置每周反思定时任务

---

✅ 已完成：step1 - 创建 corrections.md
进度：1/5

---

✅ 已完成：step2 - 创建 memory.md
进度：2/5

---

📊 当前进度：3/5 已完成
⏳ 待完成：
  - [step4] 配置每日自省定时任务
  - [step5] 配置每周反思定时任务

---

🎉 所有待办项已完成！任务执行完毕。

总结：
- 创建了 3 个文件
- 配置了 2 个定时任务
- Git 提交：abc123
```

---

### 待办数据存储

- **位置**：`~/.openclaw/workspace/todo-current.json`
- **查看方式**：`show-progress` 或直接查看文件
- **清理**：任务完成后自动归档到 MEMORY.md

---

**这个规范必须遵守！让用户看到你的执行过程，而不是只听到口头承诺！**

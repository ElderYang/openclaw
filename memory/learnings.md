# 🦞 学习日志 (Learnings)

**创建时间**: 2026-03-16  
**方法**: self-improving-agent  
**目的**: 记录关键经验教训，避免重复错误

**最后更新**: 2026-03-28 19:00

---

## [LRN-20260325-001] 配置修改必须立即持久化（严重问题！）

**类别**: 工作习惯 / 持久化  
**严重程度**: 🔴 高  
**触发时间**: 2026-03-25 07:56  
**用户反馈**: "你这种隔夜丢失的情况，而且从来不反思，self-improvement 也不主动去用，很难逐步提升"

### 问题描述
1. **隔夜配置丢失**：昨天配置的小红书定时任务、角色标签，今天早上全没了
2. **没有主动反思**：同样的问题反复出现，没有记录到 learnings.md
3. **self-improving 机制闲置**：有 learnings.md 但从不主动使用

### 根因分析
1. ❌ 修改配置后没有 git commit
2. ❌ 以为"配置好了"就完了，没有验证文件持久化
3. ❌ 没有建立"修改→验证→提交"的完整流程
4. ❌ 用户批评后才反思，不是主动反思

### 正确流程（必须遵守！）
```
【配置修改 Checklist】
□ 1. 文件保存到 ~/.openclaw/workspace/
□ 2. 立即验证：ls/cat 确认文件内容
□ 3. Git add + commit（带清晰 message）
□ 4. 安装配置：launchd/cron 等
□ 5. 测试验证：手动执行一次
□ 6. 记录到 learnings.md（self-improving）
□ 7. 远程备份：git push（可选但推荐）
```

### 已持久化的文件（2026-03-25）
- `config/com.openclaw.xiaohongshu-*.plist` (4 个)
- `scripts/xiaohongshu_*.py` (4 个)
- `scripts/stock_review_v21.py` (标签逻辑)
- **Git Commit**: `adee593`

### 预防措施
1. ✅ 每天工作结束前执行 `git status` 检查
2. ✅ 配置修改后立即 commit，不等待
3. ✅ 每周六深度反思时回顾 learnings.md
4. ✅ 用户批评后**立即**记录，不拖延

### 应用范围
- 所有定时任务配置
- 所有脚本修改
- 所有系统配置变更

---

## [LRN-20260316-001] 美股数据必须使用收盘价

**类别**: 数据准确性  
**严重程度**: 🔴 高

### 问题
- 错误使用 Yahoo Finance 盘中数据 (开盘价计算涨跌幅)
- 应该使用 Tushare 的收盘价和官方涨跌幅

### 正确做法
```python
# ✅ 使用 Tushare 获取美股收盘数据
ts.set_token(os.environ.get('TUSHARE_TOKEN'))
df = pro.index_global(ts_code='DJI', start_date=..., end_date=...)
latest = df.iloc[0]
change_pct = float(latest.get('pct_chg', 0))  # 官方涨跌幅
trade_date = latest.get('trade_date', '')
```

### 验证
- 道琼斯：-0.26% ✅ (不是 -0.28%)
- 纳斯达克：-0.93% ✅ (不是 -1.43%)
- 标普 500: -0.61% ✅ (不是 -0.62%)

### 应用范围
- 股市早报
- 复盘报告
- 任何使用美股数据的场景

---

## [LRN-20260316-002] 模板禁止硬编码示例数据

**类别**: 代码质量  
**严重程度**: 🟡 中

### 问题
- 模板中硬编码"富时 A50 涨 0.98%"
- 这是测试时的示例数据

### 正确做法
```python
# ✅ 从实际数据读取
a50 = us_indices.get('富时中国 A50') or {}
a50_pct = a50.get('change_pct', 0)
if a50_pct > 0:
    a50_text = f"富时 A50 涨{a50_pct:.2f}%"
elif a50_pct < 0:
    a50_text = f"富时 A50 跌{abs(a50_pct):.2f}%"
```

### 检查清单
- [ ] 模板中是否有硬编码数字？
- [ ] 示例数据是否已替换？
- [ ] 是否用真实数据测试过？

---

## [LRN-20260316-003] Secrets 使用环境变量管理

**类别**: 安全  
**严重程度**: 🟡 中

### 问题
- Tushare Token 硬编码在 11 个脚本中
- Git 提交时可能泄露

### 正确做法
```bash
# ~/.zshrc
export TUSHARE_TOKEN="your_token"
```

```python
# 脚本中
import os
ts.set_token(os.environ.get('TUSHARE_TOKEN', 'default'))
```

### 检查清单
- [ ] 代码中是否有硬编码的 Key/Token？
- [ ] 是否使用环境变量？
- [ ] 配置文件权限是否为 600？

---

## [LRN-20260316-004] 多源校验是必要的

**类别**: 数据准确性  
**严重程度**: 🔴 高

### 原则
- 绝不依赖单一数据源
- 至少 2 个数据源相互印证
- 数据不一致时标注⚠️

### 实践
```python
# 美股：Tushare + Yahoo Finance
# A 股：AkShare + Tushare + 东方财富
# 富时 A50: Tushare + 东方财富 (网络限制时降级)
```

### 校验规则
1. 双源一致 (误差<0.5%) → ✅ 标注
2. 单源数据 → ⚠️ 标注
3. 数据延迟 → ⚠️ 标注
4. 获取失败 → "待确认"

---

## [LRN-20260316-005] API 配额需要监控

**类别**: 运维  
**严重程度**: 🟡 中

### 问题
- 没有监控，超额了才发现
- 可能影响早报/复盘执行

### 解决方案
- 创建 `api_monitor.py` 脚本
- 每天 10:00 自动检查
- 设置告警阈值

### 告警阈值
| API | 配额 | 警告 | 严重 |
|-----|------|------|------|
| Tushare | 1000 次/天 | <100 | <50 |
| Tavily | 1000 次/月 | <200 | <100 |
| Brave | 2000 次/月 | <500 | <200 |

---

## [LRN-20260316-006] 自动更新应该启用

**类别**: 维护  
**严重程度**: 🟢 低

### 配置
```json
{
  "update": {
    "auto": {
      "enabled": true,
      "schedule": "daily",
      "time": "03:00"
    }
  }
}
```

### 好处
- 自动应用安全补丁
- 保持最新功能
- 减少手动维护

---

## [LRN-20260316-007] 定期清理未使用技能

**类别**: 安全管理  
**严重程度**: 🟡 中

### 问题
- 26 个技能中 5 个未使用
- 2 个高风险技能 (desktop-control, playwright-scraper)

### 实践
- 每月审查技能使用情况
- 删除未使用的高风险技能
- 记录技能依赖关系

---

## [LRN-20260316-008] 用户反馈是最快的质量改进途径

**类别**: 流程  
**严重程度**: 🟢 低 (但重要)

### 案例
- 09:22 用户反馈美股数据错误
- 09:28 修复完成 (6 分钟)
- 09:25 用户反馈模板硬编码
- 09:28 修复完成 (3 分钟)

### 实践
1. 快速响应用户反馈
2. 根本原因分析 (而非临时补丁)
3. 系统性修复
4. 文档化经验教训

---

## [LRN-20260316-009] 百炼 API 配置方法

**类别**: 配置  
**严重程度**: 🟢 低

### 环境变量
```bash
export OPENAI_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
export OPENAI_API_KEY="sk-ce9e5828374948b0a5deb0e4d2ab88e5"
```

### Summarize 配置
```json
{
  "models": {
    "qwen3.5-plus": {
      "id": "openai/qwen3.5-plus",
      "provider": "openai",
      "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
    }
  },
  "defaultModel": "qwen3.5-plus"
}
```

### 优势
- 中文支持优秀
- 成本更低 (约 OpenAI 的 1/3)
- 128K 上下文

---

## [LRN-20260316-010] 配置修改必须备份

**类别**: 运维  
**严重程度**: 🟡 中

### 实践
```bash
# 修改前备份
cp ~/.zshrc ~/.zshrc.backup.20260316
cp ~/.openclaw/openclaw.json ~/.openclaw/backups/
```

### 恢复方法
```bash
cp ~/.zshrc.backup.20260316 ~/.zshrc
```

### 检查清单
- [ ] 修改前是否备份？
- [ ] 备份文件是否有日期？
- [ ] 恢复方法是否文档化？

---

**最后更新**: 2026-03-16 10:55  
**学习条目**: 10 条  
**下次审查**: 2026-03-23

## [LRN-20260325-002] 角色标签必须写入脚本文件

**类别**: 代码持久化  
**严重程度**: 🟡 中  
**触发时间**: 2026-03-25 07:56

### 问题
- 角色标签（【小红书助手】【股市分析师】）隔夜后消失
- 原因：标签逻辑只写在临时测试中，没有保存到脚本

### 正确做法
```python
# ✅ 在脚本开头定义 ROLE_TAG
ROLE_TAG = "【小红书助手】"

# ✅ 在日志/消息中使用
log(f"{ROLE_TAG} 开始执行任务")

# ✅ 在飞书卡片 header 中显示
card_content["header"]["title"]["content"] = f"📊 {role_tag}"
```

### 已保存位置
- `scripts/xiaohongshu_morning.py`: ROLE_TAG = "【小红书助手】"
- `scripts/xiaohongshu_noon.py`: ROLE_TAG = "【小红书助手】"
- `scripts/xiaohongshu_evening.py`: ROLE_TAG = "【小红书助手】"
- `scripts/stock_review_v21.py`: 根据时间自动切换早报/复盘标签

---

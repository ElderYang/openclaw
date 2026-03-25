#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 企业应用方案 - 智能美化版
"""

from smart_ppt_generator import create_smart_ppt

# PPT 内容
slides_content = [
    # 1. 标题页
    {
        'type': 'title',
        'title': 'OpenClaw 企业应用方案',
        'subtitle': '技术架构 · 应用场景 · 部署方案\n中国移动终端公司\n2026 年 3 月'
    },
    
    # 2. 目录
    {
        'type': 'content',
        'title': '📋 目录',
        'items': [
            {'text': 'OpenClaw 技术架构与原理', 'emoji': '🏗️'},
            {'text': 'OpenClaw vs 对话式 AI vs 普通 Agent vs RPA', 'emoji': '⚖️'},
            {'text': '中国移动终端公司应用场景', 'emoji': '🏢'},
            {'text': 'OpenClaw + RPA 协同方案', 'emoji': '🤝'},
            {'text': '为一线创造的价值', 'emoji': '💎'},
            {'text': '内网部署硬件要求（70B+ 大模型）', 'emoji': '💻'},
            {'text': '内网环境限制与风险', 'emoji': '⚠️'},
            {'text': '总结与建议', 'emoji': '📝'},
        ]
    },
    
    # 3. 章节页
    {
        'type': 'section',
        'title': '技术架构与原理'
    },
    
    # 4. 技术架构图
    {
        'type': 'content',
        'title': '🏗️ OpenClaw 技术架构',
        'items': [
            {'text': '用户交互层：飞书/微信/Telegram/网页', 'emoji': '💬'},
            {'text': 'Gateway 网关层：消息路由·会话管理·安全认证', 'emoji': '🔀'},
            {'text': 'Agent 核心层：意图识别·任务规划·工具调用', 'emoji': '🧠'},
            {'text': '技能工具层：文件操作·浏览器控制·API 调用', 'emoji': '🛠️'},
            {'text': '记忆系统：短期记忆·长期记忆·向量检索', 'emoji': '💾'},
        ]
    },
    
    # 5. 技术原理
    {
        'type': 'content',
        'title': '⚙️ 核心设计理念',
        'items': [
            {'text': '本地优先（Local-First）：所有数据存储在本地，保护隐私', 'emoji': '🔒'},
            {'text': '极简内核 + 弹性扩展：核心代码精简，通过 Skills 扩展能力', 'emoji': '🧩'},
            {'text': '多模型兼容：支持百炼、Gemini、GPT、Claude 等主流模型', 'emoji': '🔄'},
            {'text': '', 'emoji': ''},
            {'text': 'Agent 循环：感知 → 思考 → 行动 → 反馈 → 学习', 'emoji': '🔄', 'bold': True},
        ]
    },
    
    # 6. 章节页
    {
        'type': 'section',
        'title': '技术对比'
    },
    
    # 7. 四类技术对比
    {
        'type': 'comparison',
        'title': '⚖️ OpenClaw vs 其他技术',
        'columns': ['对比维度', '对话式 AI', '普通 Agent', 'RPA', 'OpenClaw'],
        'rows': [
            ['核心能力', '文本对话', '简单任务', '规则自动化', '系统级任务'],
            ['上下文理解', '短期对话', '有限', '无', '长期记忆'],
            ['工具调用', '❌', '部分', '固定脚本', '✅ 丰富'],
            ['学习能力', '❌', '弱', '❌', '✅ 自我改进'],
            ['主动性', '被动', '被动', '定时', '主动代理'],
            ['数据隐私', '低', '中', '高', '高'],
        ]
    },
    
    # 8. 章节页
    {
        'type': 'section',
        'title': '应用场景'
    },
    
    # 9. 应用场景 - 业务部门
    {
        'type': 'content',
        'title': '🏢 业务部门应用场景',
        'items': [
            {'text': '市场部：竞品分析·舆情监控·报告生成', 'emoji': '📊'},
            {'text': '产品部：需求分析·竞品对比·文档管理', 'emoji': '📱'},
            {'text': '客服部：智能问答·工单处理·满意度分析', 'emoji': '🎧'},
            {'text': '财务部：发票处理·报表生成·对账核对', 'emoji': '💰'},
        ]
    },
    
    # 10. 应用场景 - 支撑部门
    {
        'type': 'content',
        'title': '🔧 支撑部门应用场景',
        'items': [
            {'text': '供应链：库存监控·供应商管理·采购分析', 'emoji': '📦'},
            {'text': '人力部：简历筛选·培训管理·员工问答', 'emoji': '👥'},
            {'text': 'IT 运维：监控告警·日志分析·自动化运维', 'emoji': '🖥️'},
            {'text': '研发部：代码审查·文档生成·Bug 分析', 'emoji': '💻'},
        ]
    },
    
    # 11. 章节页
    {
        'type': 'section',
        'title': '价值评估'
    },
    
    # 12. 量化价值
    {
        'type': 'comparison',
        'title': '💎 量化价值评估',
        'columns': ['场景', '当前耗时', 'OpenClaw 后', '节省', '年化价值'],
        'rows': [
            ['销售日报', '2 小时/天', '10 分钟/天', '95%', '5 万元'],
            ['竞品分析', '8 小时/周', '1 小时/周', '87%', '15 万元'],
            ['发票录入', '4 小时/天', '30 分钟/天', '85%', '8 万元'],
            ['客服问答', '6 小时/天', '1 小时/天', '83%', '12 万元'],
            ['库存监控', '2 小时/天', '10 分钟/天', '92%', '4 万元'],
            ['合计', '-', '-', '-', '44 万元/年'],
        ]
    },
    
    # 13. 章节页
    {
        'type': 'section',
        'title': '部署方案'
    },
    
    # 14. 硬件要求
    {
        'type': 'content',
        'title': '💻 硬件配置要求（70B+ 大模型）',
        'items': [
            {'text': 'GPU：4x A800 80GB（入门）或 8x H800 80GB（推荐）', 'emoji': '🎮'},
            {'text': 'CPU：2x AMD EPYC 7763 或 4x EPYC 9654', 'emoji': '⚙️'},
            {'text': '内存：512GB-1TB DDR5', 'emoji': '💾'},
            {'text': '存储：2TB NVMe SSD + 10TB+ 数据盘', 'emoji': '🗄️'},
            {'text': '', 'emoji': ''},
            {'text': '成本估算：入门 80 万 | 推荐 200 万 | 替代方案 50 万', 'emoji': '💰', 'bold': True},
        ]
    },
    
    # 15. 风险与缓解
    {
        'type': 'content',
        'title': '⚠️ 内网限制与风险缓解',
        'items': [
            {'text': '网络限制：无法访问外网 API → 使用本地模型', 'emoji': '🌐'},
            {'text': '安全风险：数据泄露 → 沙箱隔离 + 权限控制', 'emoji': '🔒'},
            {'text': '合规风险：数据合规 → 数据脱敏 + 本地部署', 'emoji': '⚖️'},
            {'text': '运维风险：系统依赖 → 冗余部署 + 监控告警', 'emoji': '🔔'},
        ]
    },
    
    # 16. 总结与建议
    {
        'type': 'summary',
        'title': '📝 总结与建议',
        'points': [
            '核心优势：本地优先、系统级执行、丰富生态、灵活扩展',
            '实施建议：试点先行、场景优先、人机协同、安全先行',
            '下一步：需求调研 → 方案设计 → 环境准备 → 试点部署 → 效果评估',
            '推荐试点部门：市场部（竞品分析）、客服部（智能问答）',
        ]
    },
]

# 创建 PPT
output_path = '/Users/yangbowen/Desktop/OpenClaw_企业应用方案_智能美化版.pptx'

create_smart_ppt(
    title='OpenClaw 企业应用方案',
    subtitle='技术架构 · 应用场景 · 部署方案',
    slides_content=slides_content,
    output_path=output_path,
    content_type='tech'  # 自动选择科技蓝主题
)

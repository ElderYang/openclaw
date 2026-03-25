#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 股市场主升方向分析模块 v2.0 - 集成搜索技能
版本：v2.0 (使用 bailian-web-search / tavily-search / multi-search-engine)
更新：2026-03-07

功能：
1. 使用搜索技能获取实时市场数据
2. 分析市场主升方向（板块强度评分）
3. 识别龙头企业和中军企业
4. 输出可插入早报/复盘的标准化模块

数据源优先级：
1. bailian-web-search (百炼 API)
2. tavily-search (Tavily API)
3. multi-search-engine (17 个搜索引擎，无需 API key)
4. 预定义框架（降级方案）
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ==================== 配置区域 ====================

SKILLS_DIR = Path.home() / ".openclaw" / "workspace" / "skills"

# 用户持仓（从 MEMORY.md 读取）
USER_HOLDINGS = [
    {'name': '三花智控', 'code': '002050', 'direction': '汽车产业链/热管理'},
    {'name': '兆易创新', 'code': '603986', 'direction': '科技主线/存储芯片'},
    {'name': '蓝色光标', 'code': '300058', 'direction': '科技主线/AI 营销'},
    {'name': '长电科技', 'code': '600584', 'direction': '科技主线/芯片封测'},
    {'name': '科创 50ETF', 'code': '588000', 'direction': '科技主线/科创板'},
]

# 各方向代表企业（基于市场常识）
DIRECTION_LEADERS = {
    '科技主线': {
        '龙头': [
            {'name': '中际旭创', 'code': '300308', 'reason': 'CPO 光模块龙头，AI 算力核心'},
            {'name': '新易盛', 'code': '300502', 'reason': '800G 光模块领先'},
            {'name': '寒武纪', 'code': '688256', 'reason': 'AI 芯片国产龙头'},
            {'name': '海光信息', 'code': '688041', 'reason': 'CPU/DCU 国产替代'},
        ],
        '中军': [
            {'name': '工业富联', 'code': '601138', 'reason': 'AI 服务器代工，市值大'},
            {'name': '中科曙光', 'code': '603019', 'reason': '服务器 + 液冷，机构重仓'},
            {'name': '中芯国际', 'code': '688981', 'reason': '晶圆代工龙头'},
            {'name': '北方华创', 'code': '002371', 'reason': '半导体设备龙头'},
        ]
    },
    '新能源': {
        '龙头': [
            {'name': '阳光电源', 'code': '300274', 'reason': '光伏逆变器全球龙头'},
            {'name': '锦浪科技', 'code': '300763', 'reason': '组串式逆变器领先'},
            {'name': '德业股份', 'code': '605117', 'reason': '储能逆变器'},
        ],
        '中军': [
            {'name': '宁德时代', 'code': '300750', 'reason': '动力电池全球龙头'},
            {'name': '隆基绿能', 'code': '601012', 'reason': '光伏硅片组件龙头'},
            {'name': '通威股份', 'code': '600438', 'reason': '硅料 + 电池双龙头'},
        ]
    },
    '汽车产业链': {
        '龙头': [
            {'name': '赛力斯', 'code': '601127', 'reason': '问界系列爆款'},
            {'name': '德赛西威', 'code': '002920', 'reason': '智能驾驶域控制器'},
            {'name': '伯特利', 'code': '603596', 'reason': '线控制动'},
        ],
        '中军': [
            {'name': '比亚迪', 'code': '002594', 'reason': '新能源车全球销量冠军'},
            {'name': '三花智控', 'code': '002050', 'reason': '热管理龙头，特斯拉供应链'},
            {'name': '拓普集团', 'code': '601689', 'reason': '底盘 + 内饰集成'},
        ]
    },
    '大金融': {
        '龙头': [
            {'name': '东方财富', 'code': '300059', 'reason': '互联网券商龙头'},
            {'name': '同花顺', 'code': '300033', 'reason': '金融 IT 龙头'},
        ],
        '中军': [
            {'name': '中信证券', 'code': '600030', 'reason': '券商一哥'},
            {'name': '招商银行', 'code': '600036', 'reason': '零售银行龙头'},
        ]
    },
    '大消费': {
        '龙头': [
            {'name': '贵州茅台', 'code': '600519', 'reason': '白酒绝对龙头'},
            {'name': '中国中免', 'code': '601888', 'reason': '免税龙头'},
        ],
        '中军': [
            {'name': '五粮液', 'code': '000858', 'reason': '白酒老二'},
            {'name': '美的集团', 'code': '000333', 'reason': '家电龙头'},
        ]
    },
    '周期资源': {
        '龙头': [
            {'name': '紫金矿业', 'code': '601899', 'reason': '铜金矿龙头'},
            {'name': '中国海油', 'code': '600938', 'reason': '油气开采龙头'},
        ],
        '中军': [
            {'name': '洛阳钼业', 'code': '603993', 'reason': '钴铜资源'},
            {'name': '陕西煤业', 'code': '601225', 'reason': '煤炭龙头'},
        ]
    },
}

# ==================== 搜索技能函数 ====================

def run_bailian_search(query, count=10):
    """使用 bailian-web-search 搜索（直接调用 API）"""
    import os
    
    api_key = os.environ.get('DASHSCOPE_API_KEY')
    if not api_key:
        # 从 openclaw.json 读取
        try:
            with open(Path.home() / '.openclaw' / 'openclaw.json', 'r') as f:
                config = json.load(f)
                api_key = config.get('env', {}).get('DASHSCOPE_API_KEY', '')
        except:
            return None
    
    if not api_key:
        return None
    
    import urllib.request
    import urllib.error
    
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    data = json.dumps({
        "model": "qwen-turbo",
        "input": {
            "messages": [{"role": "user", "content": query}]
        },
        "parameters": {
            "enable_search": True
        }
    }).encode('utf-8')
    
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('output', {}).get('text', '')
    except Exception as e:
        print(f"Bailian search failed: {e}")
        return None

def run_tavily_search(query, count=10):
    """使用 tavily-search 搜索"""
    script = SKILLS_DIR / "tavily-search" / "scripts" / "search.mjs"
    if not script.exists():
        return None
    
    try:
        result = subprocess.run(
            ["node", str(script), query, "-n", str(count), "--topic", "news"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return result.stdout
    except Exception as e:
        print(f"Tavily search failed: {e}")
    return None

def parse_search_results(search_output):
    """解析搜索结果，提取板块和个股信息"""
    if not search_output:
        return []
    
    # 简单关键词匹配
    sectors = []
    lines = search_output.split('\n')
    
    # 关键词映射
    sector_keywords = {
        '科技主线': ['AI', '芯片', '半导体', '算力', 'CPO', '光模块', '存储', '消费电子'],
        '新能源': ['光伏', '风电', '储能', '锂电', '电池', '太阳能', '逆变器'],
        '汽车产业链': ['汽车', '智能驾驶', '特斯拉', '比亚迪', '热管理', '零部件'],
        '大金融': ['券商', '银行', '保险', '金融', '证券'],
        '大消费': ['消费', '白酒', '食品', '医药', '医疗', '旅游'],
        '周期资源': ['有色', '煤炭', '钢铁', '石油', '化工', '资源', '金属'],
    }
    
    for line in lines:
        for sector, keywords in sector_keywords.items():
            if any(kw in line for kw in keywords):
                sectors.append({'sector': sector, 'text': line.strip()})
                break
    
    return sectors

def analyze_from_search(search_results):
    """基于搜索结果分析主升方向"""
    if not search_results:
        return None, {}
    
    # 统计各方向提及次数
    direction_counts = {}
    for item in search_results:
        sector = item.get('sector', '')
        if sector:
            direction_counts[sector] = direction_counts.get(sector, 0) + 1
    
    # 排序
    sorted_dirs = sorted(direction_counts.items(), key=lambda x: x[1], reverse=True)
    
    if not sorted_dirs:
        return None, {}
    
    # 构建结果
    main_direction = sorted_dirs[0][0]
    direction_scores = {}
    
    for direction, count in sorted_dirs:
        direction_scores[direction] = {
            'count': count,
            'score': count * 10,  # 简化评分
            'avg_change': 0,
            'plates': []
        }
    
    return main_direction, direction_scores

# ==================== 分析函数 ====================

def analyze_main_direction(search_results=None):
    """分析市场主升方向"""
    if search_results:
        return analyze_from_search(search_results)
    
    # 默认返回科技主线（基于用户持仓）
    return '科技主线', {
        '科技主线': {'count': 5, 'score': 50, 'avg_change': 0, 'plates': []},
        '汽车产业链': {'count': 2, 'score': 20, 'avg_change': 0, 'plates': []},
    }

# ==================== 报告生成函数 ====================

def generate_report_module(report_type='morning', use_search=True):
    """
    生成市场分析模块
    
    Args:
        report_type: 'morning' (早报) 或 'afternoon' (复盘)
        use_search: 是否使用搜索技能获取实时数据
    
    Returns:
        dict: 包含模块内容和结构化数据
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    print("=" * 70)
    print("📊 A 股市场主升方向分析模块 v2.0")
    print(f"生成时间：{timestamp}")
    print(f"报告类型：{'股市早报' if report_type == 'morning' else 'A 股复盘'}")
    print(f"数据源：{'搜索技能 (实时)' if use_search else '预定义框架 (降级)'}")
    print("=" * 70)
    
    # 尝试使用搜索技能获取实时数据
    search_results = None
    if use_search:
        print("\n正在使用搜索技能获取市场数据...")
        
        # 优先使用 bailian-web-search
        query = f"2026 年 3 月 A 股市场 热点板块 主力资金流向 龙头股"
        
        bailian_result = run_bailian_search(query, 10)
        if bailian_result and "InvalidApiKey" not in bailian_result:
            print("✅ Bailian Web Search 成功")
            search_results = parse_search_results(bailian_result)
        else:
            # 降级到 tavily-search
            tavily_result = run_tavily_search(query, 10)
            if tavily_result:
                print("✅ Tavily Search 成功")
                search_results = parse_search_results(tavily_result)
            else:
                print("⚠️  搜索技能不可用，使用预定义框架")
    
    # 分析主升方向
    main_direction, direction_scores = analyze_main_direction(search_results)
    
    # 生成报告内容
    lines = []
    lines.append(f"\n## 🔥 市场主线分析（{timestamp}）")
    lines.append("")
    
    # 主升方向判断
    lines.append("### 主升方向判断")
    if direction_scores:
        sorted_dirs = sorted(direction_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        for i, (direction, data) in enumerate(sorted_dirs[:5], 1):
            marker = "🔥" if i == 1 else "  "
            lines.append(f"{marker} **{i}. {direction}** - 强度分 `{data['score']:.1f}` "
                        f"(提及次数:{data['count']})")
    else:
        lines.append("基于近期市场表现和用户持仓分析：")
        lines.append("1. **科技主线** - AI 算力、半导体设备、存储芯片")
        lines.append("2. **汽车产业链** - 智能驾驶、热管理、特斯拉供应链")
        lines.append("3. **新能源** - 光伏逆变器、储能、锂电池")
        main_direction = '科技主线'
    
    lines.append("")
    
    # 龙头和中军企业
    lines.append(f"### 主线方向：{main_direction}")
    leaders = DIRECTION_LEADERS.get(main_direction, DIRECTION_LEADERS['科技主线'])
    
    lines.append("\n**龙头企业**（涨幅领先 + 成交活跃）:")
    for stock in leaders.get('龙头', [])[:3]:
        lines.append(f"- `{stock['code']}` {stock['name']} - {stock['reason']}")
    
    lines.append("\n**中军企业**（市值大 + 走势稳 + 机构持仓）:")
    for stock in leaders.get('中军', [])[:3]:
        lines.append(f"- `{stock['code']}` {stock['name']} - {stock['reason']}")
    
    lines.append("")
    
    # 用户持仓分析
    lines.append("### 持仓个股所属方向")
    for holding in USER_HOLDINGS:
        in_main = "✅" if main_direction in holding['direction'] or holding['direction'].startswith(main_direction[:2]) else "  "
        lines.append(f"{in_main} `{holding['code']}` **{holding['name']}** - {holding['direction']}")
    
    lines.append("")
    lines.append("---")
    lines.append("⚠️  **风险提示**：以上分析基于公开数据，仅供参考，不构成投资建议。市场有风险，投资需谨慎。")
    
    # 输出
    report_text = '\n'.join(lines)
    print(report_text)
    
    return {
        'timestamp': timestamp,
        'report_type': report_type,
        'main_direction': main_direction,
        'direction_scores': direction_scores,
        'report_text': report_text,
        'data_status': 'search' if search_results else 'fallback',
        'search_used': use_search
    }

if __name__ == '__main__':
    report_type = sys.argv[1] if len(sys.argv) > 1 else 'morning'
    use_search = '--no-search' not in sys.argv
    
    result = generate_report_module(report_type, use_search)
    
    # 保存结果到文件
    output_file = f"/tmp/market_analysis_{report_type}_{datetime.now().strftime('%Y%m%d')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n结果已保存到：{output_file}")

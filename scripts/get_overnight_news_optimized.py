#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
隔夜新闻获取优化版

优化内容：
1. 增加重试逻辑（最多 3 次）
2. 优化查询关键词（更精准）
3. 增加超时时间（15 秒）
4. 改进错误处理和日志
5. 移除固定模板降级（避免显示过时消息）
"""

import requests
import os
import time
from datetime import datetime, timedelta


def get_overnight_news_optimized(us_indices_data=None):
    """获取隔夜重要消息（Tavily 搜索 + AI 提炼核心内容）- 优化版"""
    print('\n【10】隔夜重要消息', end=' ')
    start = time.time()
    
    news_list = []
    raw_content = []
    
    # Tavily API 配置
    TAVILY_API_KEY = os.environ.get('TAVILY_API_KEY', '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')
    current_date = datetime.now()
    current_month = current_date.strftime('%Y年%m月')
    yesterday = (current_date - timedelta(days=1)).strftime('%m月%d日')
    
    # 优化查询关键词（更精准，聚焦最新）
    search_queries = [
        f'黄金原油 期货价格 {current_month} 最新行情',
        f'美联储 利率决议 {current_month} 最新',
        f'中东局势 地缘政治 {yesterday} 最新进展',
        f'AI 人工智能 科技股 {current_month} 最新动态',
    ]
    
    print(f"(尝试 {len(search_queries)} 个查询)... ", end='')
    
    # 步骤 1: Tavily API 搜索真实新闻（带重试）
    for i, query in enumerate(search_queries, 1):
        max_retries = 3
        retry_delay = 2  # 秒
        
        for attempt in range(max_retries):
            try:
                url = 'https://api.tavily.com/search'
                payload = {
                    'api_key': TAVILY_API_KEY,
                    'query': query,
                    'search_depth': 'basic',
                    'max_results': 3,
                    'days': 3  # 缩短到 3 天，确保最新
                }
                r = requests.post(url, json=payload, timeout=15)  # 增加超时时间
                
                if r.status_code == 200:
                    data = r.json()
                    results = data.get('results', [])
                    if results:
                        for item in results[:2]:
                            title = item.get('title', '')
                            content = item.get('content', '')
                            if title and content:
                                raw_content.append(f"标题：{title}\n内容：{content[:200]}")
                        break  # 成功则跳出重试循环
                else:
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                        
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
            except Exception as e:
                pass
    
    # 步骤 2: AI 提炼核心内容
    if len(raw_content) >= 2:
        try:
            DASHSCOPE_API_KEY = os.environ.get('DASHSCOPE_API_KEY', 'sk-ce9e5828374948b0a5deb0e4d2ab88e5')
            headers = {'Authorization': f'Bearer {DASHSCOPE_API_KEY}', 'Content-Type': 'application/json'}
            
            all_content = '\n\n'.join(raw_content[:5])
            
            refine_payload = {
                'model': 'qwen-plus',
                'input': {
                    'messages': [
                        {'role': 'system', 'content': '你是财经新闻分析师。从提供的新闻内容中提炼 3-4 条核心要点，每条 40 字以内，格式：• 要点内容（影响：XXX）。'},
                        {'role': 'user', 'content': f'请提炼以下财经新闻的核心内容：\n\n{all_content}'}
                    ]
                },
                'parameters': {'temperature': 0.3, 'max_tokens': 500}
            }
            
            r = requests.post(
                'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation',
                headers=headers, json=refine_payload, timeout=15
            )
            
            if r.status_code == 200:
                ai_summary = r.json().get('output', {}).get('text', '')
                lines = [l.strip() for l in ai_summary.split('\n') if l.strip() and len(l) > 10]
                for line in lines[:4]:
                    news_list.append({'title': line[:100], 'snippet': 'Tavily+AI', 'url': ''})
        except Exception as e:
            print(f'(AI 提炼失败)', end=' ')
    
    # 降级 1：直接使用 Tavily 标题（如果 AI 提炼失败）
    if len(news_list) < 3 and len(raw_content) > 0:
        for content in raw_content[:3]:
            title_line = content.split('\n')[0].replace('标题：', '')
            if len(title_line) > 20:
                news_list.append({'title': f'• {title_line[:80]}', 'snippet': 'Tavily', 'url': ''})
    
    # 降级 2：如果完全没有数据，显示提示（不显示固定模板）
    if len(news_list) == 0:
        news_list = [
            {'title': '• 暂无最新隔夜新闻（网络限制，建议查看财联社/华尔街见闻）', 'snippet': '数据获取中', 'url': ''},
        ]
    
    elapsed = time.time() - start
    print(f'✅ {len(news_list)}条 {elapsed:.1f}秒')
    
    return news_list


if __name__ == '__main__':
    # 测试
    print("="*60)
    print("隔夜新闻获取优化版测试")
    print("="*60)
    
    news = get_overnight_news_optimized()
    
    print("\n获取到的新闻：")
    print("-"*60)
    for i, n in enumerate(news, 1):
        print(f"{i}. {n.get('title', 'N/A')[:80]}")
        print(f"   来源：{n.get('snippet', 'N/A')}")
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)

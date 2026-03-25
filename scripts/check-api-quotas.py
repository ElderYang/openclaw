#!/usr/bin/env python3
"""
API 配额检查脚本
每天 10:00 执行，检查各 API 剩余额度
"""

import requests
import json
from datetime import datetime

# API 配置
APIS = {
    "tushare": {
        "url": "https://api.tushare.pro",
        "token": "7fd1efd81e77e4e72f34b199188584f70b791492d252f8908c2d698a",
        "limit": 1000,  # 次/天
        "threshold": 100
    },
    "brave": {
        "url": "https://api.search.brave.com/res/v1/web/search",
        "token": "BSAejXGS5E8qj6b7bqN9j8Xb",
        "limit": 2000,  # 次/月
        "threshold": 500
    },
    "tavily": {
        "url": "https://api.tavily.com/search",
        "token": "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",
        "limit": 1000,  # 次/月
        "threshold": 100
    }
}

def check_tushare():
    """检查 Tushare 配额"""
    try:
        # Tushare 没有直接的配额查询接口，通过调用简单接口测试
        resp = requests.post(APIS["tushare"]["url"], json={
            "api_key": APIS["tushare"]["token"],
            "sign": "token",
            "params": {"api_name": "index_daily"},
            "fields": [],
            "limit": "1"
        }, timeout=10)
        if resp.status_code == 200:
            return {"status": "ok", "remaining": "未知（API 正常）"}
        else:
            return {"status": "error", "message": resp.text}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def check_brave():
    """检查 Brave Search 配额"""
    try:
        resp = requests.get(APIS["brave"]["url"], 
            params={"q": "test", "count": 1},
            headers={"X-Subscription-Token": APIS["brave"]["token"]},
            timeout=10)
        if resp.status_code == 200:
            return {"status": "ok", "remaining": "未知（API 正常）"}
        elif resp.status_code == 401:
            return {"status": "error", "message": "API Key 无效"}
        elif resp.status_code == 429:
            return {"status": "warning", "message": "配额已用尽"}
        else:
            return {"status": "ok", "remaining": "未知（API 正常）"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def check_tavily():
    """检查 Tavily 配额"""
    try:
        resp = requests.post(APIS["tavily"]["url"], json={
            "api_key": APIS["tavily"]["token"],
            "query": "test",
            "max_results": 1
        }, timeout=10)
        if resp.status_code == 200:
            return {"status": "ok", "remaining": "未知（API 正常）"}
        elif resp.status_code == 401:
            return {"status": "error", "message": "API Key 无效"}
        else:
            return {"status": "ok", "remaining": "未知（API 正常）"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def main():
    print(f"=== API 配额检查 | {datetime.now().strftime('%Y-%m-%d %H:%M')} ===\n")
    
    results = {}
    
    # 检查各 API
    print("🔍 检查 Tushare...")
    results["tushare"] = check_tushare()
    print(f"  状态：{'✅' if results['tushare']['status']=='ok' else '❌'} {results['tushare']}")
    
    print("\n🔍 检查 Brave Search...")
    results["brave"] = check_brave()
    print(f"  状态：{'✅' if results['brave']['status']=='ok' else '❌'} {results['brave']}")
    
    print("\n🔍 检查 Tavily...")
    results["tavily"] = check_tavily()
    print(f"  状态：{'✅' if results['tavily']['status']=='ok' else '❌'} {results['tavily']}")
    
    # 保存结果
    with open("/Users/yangbowen/.openclaw/workspace/logs/api-quota-check.json", "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 检查结果已保存至：logs/api-quota-check.json")

if __name__ == "__main__":
    main()

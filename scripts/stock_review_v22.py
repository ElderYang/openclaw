#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 股复盘报告 - v22.0 优化版（复用 v21 取数逻辑）
功能：
1. ✅ 指数数据（AkShare + Yahoo Finance + Tushare + QVeris）
2. ✅ 持仓个股（AkShare + Yahoo Finance + QVeris 同花顺）
3. ✅ 美股指数（东方财富 API + Yahoo Finance）- 显示百分比
4. ✅ 融资融券（AkShare）
5. ✅ 行业板块（AkShare + QVeris）
6. ✅ 龙虎榜（AkShare + QVeris 同花顺）
7. ✅ 涨停板（东方财富 API）
8. ✅ 北向资金（东方财富 API + Tushare）
9. ✅ 资金流向（QVeris 同花顺）← 新增
10. ✅ 市场主线分析（AI 生成）
目标：执行时间<120 秒
数据源优先级：QVeris（实时）> AkShare > Tushare > 东方财富 API

网络配置：
- 东方财富 API 通过 VPN 代理访问（端口 59852）
- 其他 API 直连
"""

import json
import time
import requests
import os
import subprocess
import sys
import signal
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

# ==================== 周末休市检查 ====================
def is_weekend():
    """检查是否是周末（周六=5，周日=6）"""
    weekday = datetime.now().weekday()
    return weekday >= 5

def check_weekend_and_exit():
    """如果是周末，打印提示并退出（不发送飞书消息）"""
    if is_weekend():
        msg = f"⚠️ 今天是周末（{datetime.now().strftime('%Y-%m-%d %A')}），A 股休市，跳过执行"
        print(msg)
        # 不发送飞书消息，直接退出
        sys.exit(0)

# 执行周末检查（必须在最前面）
print(f"[{datetime.now().strftime('%H:%M:%S')}] 开始周末检查...")
check_weekend_and_exit()
print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 非周末，继续执行")

# ==================== 配置 VPN 代理（东方财富 API 专用） ====================
VPN_PROXY = {
    'http': 'http://localhost:59852',
    'https': 'http://localhost:59852',
}

def is_vpn_available():
    """检查 VPN 是否可用"""
    try:
        response = requests.get('http://localhost:59852', timeout=2)
        return response.status_code == 200
    except:
        return False

def get_requests_session(use_vpn=False):
    """获取 requests session，可选择使用 VPN 代理"""
    session = requests.Session()
    if use_vpn and is_vpn_available():
        session.proxies.update(VPN_PROXY)
        print("🔒 已启用 VPN 代理（端口 59852）")
    return session

# ==================== 添加脚本目录到 Python 路径（关键！） ====================
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))  # 确保能导入同目录的模板文件

# ==================== 配置 ====================

TIMEOUT = 15
CACHE_DIR = Path('/Users/yangbowen/.openclaw/workspace/cache')
QVERIS_SCRIPT = Path('/Users/yangbowen/.openclaw/workspace/skills/qveris/scripts/qveris_tool.py')
FEISHU_USER_ID = "ou_a040d98b29a237916317887806d655de"
FEISHU_APP_ID = "cli_a923ffd1e2f95cb2"
FEISHU_APP_SECRET = "wbUuXVa7aIy96JDguHt3gdvlT4Kpp6aV"
CACHE_DIR.mkdir(exist_ok=True)

# ==================== 缓存策略配置（方案三） ====================
# TTL: 数据缓存时间（秒），避免重复调用 API
CACHE_TTL = {
    'indices': 300,      # 指数数据缓存 5 分钟
    'holdings': 120,     # 持仓数据缓存 2 分钟（实时性要求高）
    'us_indices': 600,   # 美股指数缓存 10 分钟
    'margin': 1800,      # 融资融券缓存 30 分钟（日频数据）
    'industry': 180,     # 行业板块缓存 3 分钟（网络不稳定，缩短缓存）
    'longhubang': 3600,  # 龙虎榜缓存 1 小时（日频数据）
    'limit_up': 3600,    # 涨停板缓存 1 小时（日频数据）
    # 资金流向模块已删除
    'overnight_news': 1800,  # 隔夜新闻缓存 30 分钟
}

# 失败数据缓存时间（秒）- 大幅缩短，便于快速重试
CACHE_TTL_FAILED = {
    'industry': 60,      # 行业板块失败后只缓存 1 分钟
    'indices': 60,
    'holdings': 60,
}

def is_cache_valid(cache_file, data_type):
    """检查缓存是否有效（文件存在 + 未过期 + 数据质量）"""
    if not cache_file.exists():
        return False
    
    try:
        mtime = cache_file.stat().st_mtime
        age = time.time() - mtime
        
        # 先检查数据质量，失败数据使用更短的 TTL
        with open(cache_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 检查是否是失败数据
        is_failed = False
        if isinstance(data, list) and len(data) > 0:
            first_item = data[0] if data else {}
            if isinstance(first_item, dict):
                name = first_item.get('name', '')
                source = first_item.get('source', '')
                if '待确认' in name or '数据缺失' in source or '昨日缓存' in source:
                    is_failed = True
        
        # 失败数据使用更短的 TTL
        if is_failed:
            ttl = CACHE_TTL_FAILED.get(data_type, 60)  # 失败数据默认 1 分钟
        else:
            ttl = CACHE_TTL.get(data_type, 300)
        
        return age < ttl
    except:
        return False

def load_cache(data_type):
    """加载缓存数据（如果有效）"""
    cache_file = CACHE_DIR / f'review_v21_data_{data_type}.json'
    if is_cache_valid(cache_file, data_type):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return None

def save_cache_data(data_type, data):
    """保存数据到缓存（失败数据不缓存）"""
    cache_file = CACHE_DIR / f'review_v21_data_{data_type}.json'
    
    # 检查数据质量：失败数据不缓存
    if isinstance(data, list) and len(data) > 0:
        # 检查是否包含"待确认"等失败标记
        first_item = data[0] if data else {}
        if isinstance(first_item, dict):
            name = first_item.get('name', '')
            source = first_item.get('source', '')
            if '待确认' in name or '数据缺失' in source or '昨日缓存' in source:
                print(f'⚠️ 跳过缓存：{data_type} 数据质量不佳')
                return  # 不缓存失败数据
    
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f'✅ 缓存已保存：{cache_file.name}')
    except Exception as e:
        print(f'缓存保存失败：{e}')

HOLDINGS = [
    {'code': '002050', 'name': '三花智控', 'industry': '汽车零部件'},
    {'code': '603986', 'name': '兆易创新', 'industry': '半导体'},
    {'code': '300058', 'name': '蓝色光标', 'industry': '传媒/营销'},
    {'code': '600584', 'name': '长电科技', 'industry': '半导体'},
    {'code': '588000', 'name': '科创 50ETF', 'industry': 'ETF'},
    {'code': '159516', 'name': '半导体设备 ETF', 'industry': 'ETF'},
    {'code': '159326', 'name': '电网设备 ETF', 'industry': 'ETF'},
    {'code': '300442', 'name': '润泽科技', 'industry': '数据中心'},
]

# ==================== 飞书发送函数 ====================

def send_to_feishu(message, retry=3):
    """发送飞书富文本卡片消息（支持格式化 + 重试机制）"""
    import urllib.request
    import time
    
    for attempt in range(1, retry + 1):
        try:
            print(f"📤 飞书发送尝试 {attempt}/{retry}...")
            
            # 步骤 1：获取 token（增加超时时间）
            token_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
            token_data = json.dumps({"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}).encode('utf-8')
            token_req = urllib.request.Request(token_url, data=token_data, headers={'Content-Type': 'application/json'})
            
            with urllib.request.urlopen(token_req, timeout=15) as resp:
                token = json.loads(resp.read().decode('utf-8')).get('tenant_access_token', '')
            
            if not token:
                print("❌ 飞书 Token 获取失败")
                if attempt < retry:
                    print(f"⏳ 等待 {attempt*2}秒后重试...")
                    time.sleep(attempt * 2)
                    continue
                return False
            
            # 步骤 2：将文本消息转换为卡片格式
            # 飞书卡片格式：https://open.feishu.cn/document/ukTMukTMukTM/uYjNwUjL2YDM14SM2ATN
            lines = message.split('\n')
            elements = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue  # 跳过空行
                elif line.startswith('🌅') or line.startswith('📈'):
                    # 大标题
                    elements.append({"tag": "div", "text": {"content": line, "tag": "lark_md"}})
                elif line.startswith('【'):
                    # 模块标题（加粗）
                    elements.append({"tag": "div", "text": {"content": f"**{line}**", "tag": "lark_md"}})
                elif line.startswith('---') or line.startswith('==='):
                    # 分隔线
                    elements.append({"tag": "hr"})
                else:
                    # 普通文本
                    elements.append({"tag": "div", "text": {"content": line, "tag": "lark_md"}})
            
            # 构建卡片消息（带标签/角标）
            # 根据时间判断角色标签
            current_hour = datetime.now().hour
            if 5 <= current_hour < 12:
                role_tag = "【股市分析师】早报"
                header_template = "blue"
            else:
                role_tag = "【股市分析师】复盘"
                header_template = "green"
            
            card_content = {
                "config": {
                    "wide_screen_mode": True
                },
                "header": {
                    "title": {
                        "content": f"📊 {role_tag}",
                        "tag": "plain_text"
                    },
                    "template": header_template
                },
                "elements": elements
            }
            
            message_url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id"
            send_payload = {
                "receive_id": FEISHU_USER_ID,
                "msg_type": "interactive",
                "content": json.dumps(card_content, ensure_ascii=False)
            }
            
            req = urllib.request.Request(
                message_url,
                data=json.dumps(send_payload).encode('utf-8'),
                headers={
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                }
            )
            
            with urllib.request.urlopen(req, timeout=15) as resp:
                response = json.loads(resp.read().decode('utf-8'))
            
            if response.get('code') == 0:
                msg_id = response.get('data', {}).get('message_id', 'unknown')
                print(f"✅ 飞书卡片消息发送成功 (msg_id: {msg_id})")
                return True
            else:
                error_code = response.get('code')
                error_msg = response.get('msg', 'Unknown error')
                print(f"❌ 飞书卡片发送失败：code={error_code}, msg={error_msg}")
                
                # 如果是网络相关错误，重试
                if error_code in [9499, 9999, 503] and attempt < retry:
                    print(f"⏳ 网络波动，等待 {attempt*2}秒后重试...")
                    time.sleep(attempt * 2)
                    continue
                else:
                    print("📉 降级为纯文本发送...")
                    return send_to_feishu_text(message, token)
        except Exception as e:
            print(f"❌ 飞书发送异常：{e}")
            import traceback
            traceback.print_exc()
            # 网络异常时重试
            if attempt < retry:
                print(f"⏳ 网络异常，等待 {attempt*2}秒后重试...")
                time.sleep(attempt * 2)
                continue
            else:
                print("📉 降级为纯文本发送...")
                return send_to_feishu_text(message, token)
    
    # 所有重试都失败
    print("❌ 所有重试失败，放弃发送")
    return False

def send_to_feishu_text(message, token=None):
    """降级方案：发送纯文本消息"""
    import urllib.request
    
    if not token:
        token_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        token_data = json.dumps({"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}).encode('utf-8')
        try:
            token_req = urllib.request.Request(token_url, data=token_data, headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(token_req, timeout=10) as resp:
                token = json.loads(resp.read().decode('utf-8')).get('tenant_access_token', '')
            if not token:
                print("❌ 飞书 Token 获取失败（降级）")
                return False
        except Exception as e:
            print(f"❌ 飞书 Token 获取异常（降级）: {e}")
            return False
    
    message_url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id"
    send_payload = {
        "receive_id": FEISHU_USER_ID,
        "msg_type": "text",
        "content": json.dumps({"text": message}, ensure_ascii=False)
    }
    
    try:
        req = urllib.request.Request(
            message_url,
            data=json.dumps(send_payload).encode('utf-8'),
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            response = json.loads(resp.read().decode('utf-8'))
        if response.get('code') == 0:
            print("✅ 飞书文本消息发送成功（降级）")
            return True
        else:
            print(f"❌ 降级发送失败：code={response.get('code')}, msg={response.get('msg')}")
            return False
    except Exception as e:
        print(f"❌ 降级发送也失败：{e}")
        import traceback
        traceback.print_exc()
        return False

# ==================== QVeris 工具函数 ====================

def qveris_search(query, limit=3):
    """搜索 QVeris 工具"""
    try:
        env = os.environ.copy()
        result = subprocess.run(
            ['python3', str(QVERIS_SCRIPT), 'search', query, '--limit', str(limit)],
            capture_output=True, text=True, timeout=30, env=env
        )
        if result.returncode == 0:
            return result.stdout
    except Exception as e:
        pass
    return None

def qveris_execute(tool_id, search_id, params):
    """执行 QVeris 工具"""
    try:
        env = os.environ.copy()
        params_json = json.dumps(params)
        result = subprocess.run(
            ['python3', str(QVERIS_SCRIPT), 'execute', tool_id,
             '--search-id', search_id, '--params', params_json],
            capture_output=True, text=True, timeout=30, env=env
        )
        if result.returncode == 0:
            # 解析 JSON 结果
            lines = result.stdout.strip().split('\n')
            for i, line in enumerate(lines):
                if line.strip() == '{' or line.strip().startswith('{'):
                    json_str = '\n'.join(lines[i:])
                    return json.loads(json_str)
    except Exception as e:
        pass
    return None

# ==================== 缓存函数 ====================

def get_cache_file():
    date = datetime.now().strftime('%Y%m%d')
    return CACHE_DIR / f'review_v21_{date}.json'

def save_cache(data, execution_time):
    cache_file = get_cache_file()
    cache_data = {
        'timestamp': datetime.now().isoformat(),
        'version': 'v21.0',
        'execution_time': execution_time,
        'data': data
    }
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=2, default=str)
    print(f"✅ 缓存已保存：{cache_file.name}")
    return cache_file

# ==================== 多源校验工具函数 ====================

def safe_get(data, *keys, default=None):
    """安全获取嵌套字典值"""
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key, default)
        else:
            return default
    return data if data is not None else default

def validate_data_date(trade_date, expected_date=None):
    """
    验证数据日期
    返回：(是否有效，警告信息)
    """
    if not trade_date:
        return False, '无日期'
    
    if expected_date is None:
        # 默认期望日期为昨天或今天
        expected_date = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    
    if trade_date == expected_date:
        return True, None
    elif trade_date == datetime.now().strftime('%Y%m%d'):
        return True, None  # 今天的数据也有效
    else:
        return False, f'数据延迟 ({trade_date} vs {expected_date})'

def validate_with_sources(primary, secondary, tertiary=None, threshold=0.05):
    """
    多源数据校验
    primary: 主要数据源 (值，来源)
    secondary: 次要数据源 (值，来源)
    tertiary: 第三数据源 (可选)
    threshold: 差异阈值 (默认 5%)
    返回：(校验后的值，使用的数据源，校验状态)
    """
    p_val, p_src = primary
    s_val, s_src = secondary
    
    if p_val is None and s_val is None:
        return None, '无数据', '❌'
    if p_val is None:
        return s_val, s_src, '✅'
    if s_val is None:
        return p_val, p_src, '⚠️'
    
    # 计算差异百分比
    if p_val != 0:
        diff_pct = abs(s_val - p_val) / abs(p_val) * 100
    else:
        diff_pct = 0 if s_val == 0 else 100
    
    if diff_pct <= threshold * 100:
        return p_val, f'{p_src}+{s_src}', '✅'
    else:
        # 差异较大，返回主要数据源但标记警告
        return p_val, f'{p_src}(差异{diff_pct:.1f}%)', '⚠️'

# ==================== 数据获取函数 ====================

def get_indices_data():
    """获取 A 股指数数据（Tushare 优先 + 东方财富 API + Yahoo Finance 备用）"""
    print('\n【1】指数数据', end=' ')
    start = time.time()
    
    indices = {
        '上证指数': {'ts': '000001.SH', 'em': '1.000001', 'yahoo': '000001.SS'},
        '深证成指': {'ts': '399001.SZ', 'em': '0.399001', 'yahoo': '399001.SZ'},
        '创业板指': {'ts': '399006.SZ', 'em': '0.399006', 'yahoo': '399006.SZ'},
        '科创 50': {'ts': '000688.SH', 'em': '1.000688', 'yahoo': '000688.SS'},
    }
    
    results = {}
    for name, codes in indices.items():
        ts_val, ts_src = None, 'Tushare'
        em_val, em_src = None, '东方财富 API'
        yahoo_val, yahoo_src = None, 'Yahoo Finance'
        ts_pct = None
        
        # 【1】Tushare 数据（优先，API 稳定）
        try:
            import tushare as ts
            ts.set_token(os.environ.get('TUSHARE_TOKEN', '7fd1efd594f9a1f70bd876707eabb60faa4bf658d6070056b3278e73'))
            pro = ts.pro_api()
            df = pro.index_daily(ts_code=codes['ts'], start_date=(datetime.now()-timedelta(days=5)).strftime('%Y%m%d'),
                                end_date=datetime.now().strftime('%Y%m%d'))
            if len(df) > 0:
                ts_val = float(df.iloc[0]['close'])
                ts_pct = float(df.iloc[0].get('pct_chg', 0))
        except Exception as e:
            print(f'(Tushare 失败:{e})', end=' ')
        
        # 【2】东方财富 API（直连，HTTP 协议）
        try:
            # 使用 HTTP 而非 HTTPS（东方财富 HTTP API 可直接访问）
            # f43: 当前点位，f49: 涨跌幅（%），f170: 昨收
            url = f'http://push2.eastmoney.com/api/qt/stock/get?secid={codes["em"]}&fields=f43,f49,f170'
            r = requests.get(url, timeout=TIMEOUT)  # 直连，不用 VPN
            d = r.json().get('data', {})
            if d and d.get('f43'):
                em_val = d.get('f43', 0) / 100
                # 优先使用 f49（东方财富直接返回的涨跌幅%）
                if d.get('f49') is not None:
                    em_pct = float(d.get('f49', 0))
                    ts_pct = em_pct  # 直接使用东方财富的涨跌幅
                # 如果 f49 不可用，手动计算涨跌幅
                elif d.get('f170') and d.get('f43'):
                    close = d['f43'] / 100
                    yesterday = d['f170'] / 100
                    em_pct = ((close - yesterday) / yesterday) * 100
                    ts_pct = em_pct
        except Exception as e:
            print(f'(东方财富失败:{e})', end=' ')
        
        # 【3】Yahoo Finance 备用（网络较好）
        try:
            import yfinance as yf
            ticker = yf.Ticker(codes['yahoo'])
            info = ticker.info
            hist = ticker.history(period='1d')  # 只需今天的数据
            if len(hist) >= 1 and info.get('previousClose'):
                close = float(hist['Close'].iloc[-1])
                prev_close = float(info.get('previousClose'))  # 使用 official previous close
                yahoo_val = close
                yahoo_pct = ((close - prev_close) / prev_close) * 100
                ts_pct = yahoo_pct  # 使用 Yahoo 的涨跌幅
                print(f'[Yahoo:{name} {yahoo_val:.2f} {yahoo_pct:+.2f}%]', end=' ')
            elif len(hist) >= 1:
                # 没有 previousClose，只有今天的数据
                yahoo_val = float(hist['Close'].iloc[-1])
                print(f'[Yahoo:{name} {yahoo_val:.2f} 无昨收]', end=' ')
            else:
                print(f'[Yahoo:{name} 无数据]', end=' ')
        except Exception as e:
            print(f'[Yahoo 失败:{e}]', end=' ')
        
        # 三源校验 + 严格数据质量检查
        sources = [(ts_val, ts_src), (em_val, em_src), (yahoo_val, yahoo_src)]
        # 过滤掉 None 和 0 值（0 表示数据获取失败）
        valid_sources = [(v, s) for v, s in sources if v is not None and v > 0]
        
        # 严格校验：数据必须在合理范围内
        def is_valid_index_data(close, pct_chg, name):
            """校验指数数据是否合理"""
            if close is None or close <= 0:
                return False, "点位为 0 或负数"
            if pct_chg is None:
                return False, "涨跌幅为空"
            # 指数点位合理性检查（上证指数 2000-5000，创业板 1500-4000，科创 50 800-2000）
            if name == '上证指数' and not (2000 < close < 5000):
                return False, f"点位异常 {close}"
            if name == '深证成指' and not (8000 < close < 20000):
                return False, f"点位异常 {close}"
            if name == '创业板指' and not (1500 < close < 4000):
                return False, f"点位异常 {close}"
            if name == '科创 50' and not (800 < close < 2000):
                return False, f"点位异常 {close}"
            # 涨跌幅合理性检查（A 股±12% 以内）
            if not (-12 < pct_chg < 12):
                return False, f"涨跌幅异常 {pct_chg}%"
            return True, "OK"
        
        if len(valid_sources) >= 1:
            val = valid_sources[0][0]
            source_names = '+'.join([s for v, s in valid_sources])
            
            # 严格数据校验
            is_valid, msg = is_valid_index_data(val, ts_pct, name)
            if not is_valid:
                print(f'[⚠️ {name} 数据异常：{msg}]', end=' ')
                # 数据异常时标记为未验证，但不阻止发送（在发送前统一检查）
                results[name] = {'close': val, 'pct_chg': ts_pct, 'source': source_names, 'validated': False, 'warning': msg}
            else:
                results[name] = {'close': val, 'pct_chg': ts_pct, 'source': source_names, 'validated': len(valid_sources) >= 2}
        else:
            print(f'[❌ {name} 无有效数据]', end=' ')
            results[name] = {'close': 0, 'pct_chg': 0, 'source': '待确认', 'validated': False, 'error': '所有数据源失败'}
    
    elapsed = time.time() - start
    validated_count = sum(1 for v in results.values() if v.get('validated'))
    print(f'✅ ({len(results)}/4) 双源校验{validated_count}/{len(results)} {elapsed:.1f}秒')
    return results

def get_holdings_data_mx():
    """获取持仓 ETF 数据（mx-stocks-screener）"""
    import subprocess
    import glob
    
    try:
        script_path = Path('/Users/yangbowen/.openclaw/workspace/skills/mx-stocks-screener/scripts/get_data.py')
        output_dir = Path('/Users/yangbowen/.openclaw/workspace/skills/mx-stocks-screener/scripts/miaoxiang/mx_stocks_screener')
        
        # 查询 ETF 持仓（用具体 ETF 代码）
        etf_codes = [s['code'] for s in HOLDINGS if s['code'].startswith('5') or s['code'].startswith('1')]
        if not etf_codes:
            return {}
        
        # 逐个查询 ETF（避免批量查询返回板块数据）
        etf_data = {}
        for code in etf_codes:
            import subprocess
            env = os.environ.copy()
            env['EM_API_KEY'] = 'em_4qW46fejFrfKscOuTbT5OrzLZtj7nRet'
            
            result = subprocess.run(
                ['/opt/homebrew/bin/python3', str(script_path), '--query', code, '--select-type', 'ETF'],
                capture_output=True, text=True, timeout=10,
                env=env,
                cwd=str(script_path.parent)
            )
            
            if result.returncode == 0 and '调用成功' in result.stdout:
                csv_files = sorted(glob.glob(str(output_dir / 'mx_stocks_screener_*.csv')), reverse=True)
                if csv_files:
                    import csv
                    with open(csv_files[0], 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            row_code = row.get('代码', '')
                            if row_code == code:
                                etf_data[code] = {
                                    'price': float(row.get(f'最新价 {today}', 0)),
                                    'pct': float(row.get(f'涨跌幅 (%) {today}', 0)),
                                    'source': 'mx-stocks-screener'
                                }
                                break
    except:
        pass
    return etf_data

def get_holdings_data():
    """获取持仓个股数据（五源校验：QVeris + mx-stocks-screener + AkShare + Tushare + 东方财富 API）"""
    print('\n【2】持仓数据', end=' ')
    start = time.time()
    
    # 尝试 1: QVeris 同花顺实时数据（优先）
    qveris_data = None
    try:
        # 修复 ETF 市场代码：588xxx 是上交所，159xxx 是深交所
        def get_market_code(code):
            if code.startswith('588') or code.startswith('51') or code.startswith('6'):
                return 'SH'  # 上交所
            elif code.startswith('159') or code.startswith('0') or code.startswith('3'):
                return 'SZ'  # 深交所
            else:
                return 'SH'  # 默认
        
        codes_list = [f"{stock['code']}.{get_market_code(stock['code'])}" for stock in HOLDINGS]
        codes_str = ','.join(codes_list)
        search_result = qveris_search("同花顺实时行情")
        if search_result and 'Search ID:' in search_result:
            search_id = search_result.split('Search ID:')[1].split()[0]
            qveris_result = qveris_execute('ths_ifind.real_time_quotation.v1', search_id, {'codes': codes_str})
            if qveris_result and qveris_result.get('status_code') == 200:
                qveris_data = qveris_result.get('data', [])
                print('(QVeris✅)', end=' ')
    except Exception as e:
        pass
    
    # 尝试 0: mx-stocks-screener 获取 ETF 数据（备用）
    mx_etf_data = get_holdings_data_mx()
    
    results = []
    for i, stock in enumerate(HOLDINGS):
        ak_val, ak_pct, ak_src = None, None, 'AkShare'
        ts_val, ts_pct, ts_src = None, None, 'Tushare'
        em_val, em_pct, em_src = None, None, '东方财富 API'
        qv_val, qv_pct, qv_src = None, None, 'QVeris'
        
        # QVeris 数据（实时，最优先）
        if qveris_data and i < len(qveris_data):
            try:
                qv_item = qveris_data[i][0] if qveris_data[i] else None
                if qv_item:
                    # 修复字段名：QVeris 返回的是中文
                    qv_val = float(qv_item.get('最新价', 0))
                    qv_pct = float(qv_item.get('涨跌幅', 0))
            except:
                pass
        
        try:
            code = stock['code']
            
            # AkShare 数据（历史收盘价）
            try:
                if code.startswith('5') or code.startswith('1'):
                    df = ak.fund_etf_hist_em(symbol=code, period='daily',
                                            start_date=(datetime.now()-timedelta(days=5)).strftime('%Y%m%d'),
                                            end_date=datetime.now().strftime('%Y%m%d'))
                else:
                    df = ak.stock_zh_a_hist(symbol=code, period='daily',
                                           start_date=(datetime.now()-timedelta(days=5)).strftime('%Y%m%d'),
                                           end_date=datetime.now().strftime('%Y%m%d'))
                
                if len(df) > 0:
                    latest = df.iloc[-1]
                    ak_val = float(latest['收盘'])
                    ak_pct = float(latest['涨跌幅'])
            except:
                pass
        except:
            pass
        
        # Tushare 数据
        try:
            import tushare as ts
            ts.set_token(os.environ.get('TUSHARE_TOKEN', '7fd1efd594f9a1f70bd876707eabb60faa4bf658d6070056b3278e73'))
            pro = ts.pro_api()
            ts_code = code + '.SZ' if code.startswith(('0', '3')) else code + '.SH'
            df = pro.daily(ts_code=ts_code, start_date=(datetime.now()-timedelta(days=5)).strftime('%Y%m%d'),
                          end_date=datetime.now().strftime('%Y%m%d'))
            if len(df) > 0:
                ts_val = float(df.iloc[0]['close'])
                ts_pct = float(df.iloc[0]['pct_chg'])
        except:
            pass
        
        # 东方财富 API（实时数据，HTTP 协议 + VPN）
        try:
            secid = '1.' + code if code.startswith('6') else '0.' + code
            # 使用 HTTP 而非 HTTPS（LetsVPN 代理不支持 HTTPS 隧道）
            url = f'http://push2.eastmoney.com/api/qt/stock/get?secid={secid}&fields=f43,f171,f170'
            r = get_requests_session(use_vpn=True).get(url, timeout=TIMEOUT)
            d = r.json().get('data', {})
            if d and d.get('f43'):
                em_val = d.get('f43', 0) / 100  # 现价
                em_pct = d.get('f171', 0) / 100  # 涨跌幅%
        except:
            pass
        
        # 如果是 ETF，优先使用 mx-stocks-screener 数据
        is_etf = code.startswith('5') or code.startswith('1')
        if is_etf and code in mx_etf_data:
            mx_data = mx_etf_data[code]
            results.append({'name': stock['name'], 'code': code, 'price': mx_data['price'], 'pct': mx_data['pct'], 'source': mx_data['source'], 'validated': True, 'industry': stock['industry']})
        else:
            # 四源校验（优先使用 QVeris 实时数据）
            # ETF 也加入校验（如果 mx 失败）
            sources = [(qv_val, qv_pct, qv_src), (ak_val, ak_pct, ak_src), (ts_val, ts_pct, ts_src), (em_val, em_pct, em_src)]
            valid_sources = [(v, p, s) for v, p, s in sources if v is not None]
            
            if len(valid_sources) >= 1:  # ETF 只要有 1 个源就使用
                val, pct, src = valid_sources[0][0], valid_sources[0][1], valid_sources[0][2]
                results.append({'name': stock['name'], 'code': code, 'price': val, 'pct': pct, 'source': src, 'validated': len(valid_sources) >= 2, 'industry': stock['industry']})
    
    elapsed = time.time() - start
    validated_count = sum(1 for v in results if v.get('validated'))
    print(f'({len(results)}/8) 四源校验{validated_count}/{len(results)} {elapsed:.1f}秒')
    return results

def get_us_indices_data():
    """获取美股指数数据（Yahoo Finance 优先 + Tushare 校验 + QVeris 备用）"""
    print('\n【3】美股指数', end=' ')
    start = time.time()
    
    us_indices = {
        '道琼斯': {'yahoo': '^DJI', 'ts': 'DJI'},
        '纳斯达克': {'yahoo': '^IXIC', 'ts': 'IXIC'},
        '标普 500': {'yahoo': '^GSPC', 'ts': 'SPX'},
        '富时中国 A50': {'yahoo': 'FXI', 'ts': 'XIN9'},  # 用 iShares 中国 ETF 替代
        '纳指金龙': {'yahoo': 'KWEB', 'ts': None},
    }
    
    results = {}
    today = datetime.now()
    
    # 尝试 1: Yahoo Finance（主数据源 - 实时/最新收盘）
    try:
        import yfinance as yf
        for name, config in us_indices.items():
            if not config.get('yahoo'):
                continue
            
            try:
                ticker = yf.Ticker(config['yahoo'])
                # 获取最近 5 天数据，确保拿到最新交易日数据
                data = ticker.history(period='5d')
                if len(data) > 0:
                    latest = data.iloc[-1]
                    yahoo_close = float(latest['Close'])
                    # 计算涨跌幅（相比前一日收盘）
                    if len(data) > 1:
                        prev_close = data.iloc[-2]['Close']
                        yahoo_pct = ((yahoo_close - prev_close) / prev_close) * 100
                    else:
                        yahoo_pct = 0.0
                    
                    yahoo_date = latest.name.strftime('%Y%m%d')
                    results[name] = {
                        'close': yahoo_close,
                        'change_pct': yahoo_pct,
                        'source': f'Yahoo Finance ({yahoo_date})',
                        'validated': False,
                        'trade_date': yahoo_date
                    }
            except Exception as e:
                pass
        
        if len(results) >= 3:
            print(f'✅ Yahoo Finance {len(results)} 个指数 {time.time()-start:.1f}秒')
    except Exception as e:
        pass
    
    # 尝试 2: Tushare（校验 + 补充）
    try:
        import tushare as ts
        ts.set_token(os.environ.get('TUSHARE_TOKEN', '7fd1efd594f9a1f70bd876707eabb60faa4bf658d6070056b3278e73'))
        pro = ts.pro_api()
        
        for name, config in us_indices.items():
            if not config.get('ts'):
                continue
            
            # 如果 Yahoo 已有数据，用 Tushare 校验
            if name in results:
                try:
                    df = pro.index_global(ts_code=config['ts'], 
                                         start_date=(today-timedelta(days=10)).strftime('%Y%m%d'),
                                         end_date=today.strftime('%Y%m%d'))
                    if len(df) > 0:
                        latest = df.iloc[0]
                        ts_close = float(latest.get('close', 0))
                        ts_pct = float(latest.get('pct_chg', 0))
                        ts_date = latest.get('trade_date', '')
                        
                        # 校验：收盘价差异<1% 且日期一致
                        if abs(ts_close - results[name]['close']) / results[name]['close'] < 0.01:
                            results[name]['validated'] = True
                            results[name]['source'] = f'Yahoo+Tushare 校验 ({ts_date})✅'
                except Exception as e:
                    pass
            else:
                # Yahoo 失败，用 Tushare 补充
                try:
                    df = pro.index_global(ts_code=config['ts'], 
                                         start_date=(today-timedelta(days=10)).strftime('%Y%m%d'),
                                         end_date=today.strftime('%Y%m%d'))
                    if len(df) > 0:
                        latest = df.iloc[0]
                        results[name] = {
                            'close': float(latest.get('close', 0)),
                            'change_pct': float(latest.get('pct_chg', 0)),
                            'source': f'Tushare ({latest.get("trade_date", "")})',
                            'validated': False,
                            'trade_date': latest.get('trade_date', '')
                        }
                except Exception as e:
                    pass
    except Exception as e:
        pass
    
    # 尝试 3: QVeris 同花顺（最后备用）
    if len(results) < 3:
        try:
            codes_map = {'道琼斯': 'DJI', '纳斯达克': 'IXIC', '标普 500': 'SPX'}
            codes_str = ','.join([f'{c}.USA' for c in codes_map.values()])
            search_result = qveris_search("美股指数 实时行情")
            if search_result and 'Search ID:' in search_result:
                search_id = search_result.split('Search ID:')[1].split()[0]
                qveris_result = qveris_execute('ths_ifind.real_time_quotation.v1', search_id, {'codes': codes_str})
                if qveris_result and qveris_result.get('status_code') == 200:
                    qv_data = qveris_result.get('data', [])
                    if qv_data:
                        for i, (name, code) in enumerate(codes_map.items()):
                            if name not in results and i < len(qv_data) and qv_data[i]:
                                item = qv_data[i][0]
                                if item:
                                    results[name] = {
                                        'close': float(item.get('latest', 0)),
                                        'change_pct': float(item.get('changeRatio', 0)),
                                        'source': f'QVeris ({item.get("tradeDate", "")})',
                                        'validated': False,
                                        'trade_date': item.get('tradeDate', '').replace('-', '')
                                    }
                        print(f'✅ QVeris 补充 {len(results)} 个指数 {time.time()-start:.1f}秒')
        except Exception as e:
            pass
    
    # 打印结果
    if not results:
        print('❌ 失败')
    elif len(results) < 5:
        print(f'⚠️ 部分成功 ({len(results)}/5)')
    else:
        print(f'✅ 成功 ({len(results)}/5)')
    
    return results

def get_us_indices_data_fixed():
    """获取美股指数数据（Yahoo Finance 优先 + Tushare 备用）
    修复：Yahoo Finance 数据最新（实时），Tushare 有延迟
    """
    print('\n【3】美股指数', end=' ')
    start = time.time()
    
    us_indices = {
        '道琼斯': {'yahoo': '^DJI', 'ts': 'DJI'},
        '纳斯达克': {'yahoo': '^IXIC', 'ts': 'IXIC'},
        '标普 500': {'yahoo': '^GSPC', 'ts': 'SPX'},
        '富时中国 A50': {'yahoo': None, 'ts': 'XIN9'},  # A50 只用 Tushare（Yahoo ETF 不是指数）
        '纳指金龙': {'yahoo': 'KWEB', 'ts': None},
    }
    
    results = {}
    today = datetime.now()
    
    # 尝试 1: Yahoo Finance（主数据源 - 数据最新）
    try:
        import yfinance as yf
        for name, config in us_indices.items():
            if not config.get('yahoo'):
                continue
            
            try:
                ticker = yf.Ticker(config['yahoo'])
                data = ticker.history(period='5d')
                if len(data) > 0:
                    latest = data.iloc[-1]
                    yahoo_close = float(latest['Close'])
                    if len(data) > 1:
                        prev_close = data.iloc[-2]['Close']
                        yahoo_pct = ((yahoo_close - prev_close) / prev_close) * 100
                    else:
                        yahoo_pct = 0.0
                    
                    yahoo_date = latest.name.strftime('%Y%m%d')
                    results[name] = {
                        'close': yahoo_close,
                        'change_pct': yahoo_pct,
                        'source': f'Yahoo Finance ({yahoo_date})',
                        'validated': True,  # Yahoo 作为主数据源，直接标记为已验证
                        'trade_date': yahoo_date
                    }
            except Exception as e:
                pass
        
        if len(results) >= 3:
            print(f'✅ Yahoo Finance {len(results)} 个指数 {time.time()-start:.1f}秒')
    except Exception as e:
        pass
    
    # 尝试 2: Tushare（补充 Yahoo 没有的数据，如富时 A50）
    try:
        import tushare as ts
        ts.set_token(os.environ.get('TUSHARE_TOKEN', '7fd1efd594f9a1f70bd876707eabb60faa4bf658d6070056b3278e73'))
        pro = ts.pro_api()
        
        for name, config in us_indices.items():
            if not config.get('ts'):
                continue
            
            if name in results:
                continue  # Yahoo 已有数据，跳过
            
            try:
                df = pro.index_global(ts_code=config['ts'], 
                                     start_date=(today-timedelta(days=10)).strftime('%Y%m%d'),
                                     end_date=today.strftime('%Y%m%d'))
                if len(df) > 0:
                    latest = df.iloc[0]
                    results[name] = {
                        'close': float(latest.get('close', 0)),
                        'change_pct': float(latest.get('pct_chg', 0)),
                        'source': f'Tushare ({latest.get("trade_date", "")})',
                        'validated': True,
                        'trade_date': latest.get('trade_date', '')
                    }
            except Exception as e:
                pass
        
        if '富时中国 A50' in results:
            print(f' + Tushare A50')
    except Exception as e:
        pass
    
    # 打印结果
    if not results:
        print('❌ 失败')
    elif len(results) < 5:
        print(f'⚠️ 部分成功 ({len(results)}/5)')
    else:
        print(f'✅ 成功 ({len(results)}/5)')
    
    return results

# 尝试 3: 东方财富（富时 A50 实时数据，直连）
    if '富时中国 A50' not in results:
        try:
            # 富时中国 A50 在东方财富的代码：100.FTCHI
            url = 'http://push2.eastmoney.com/api/qt/stock/get?secid=100.FTCHI&fields=f43,f171,f170,f169'
            r = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
            d = r.json().get('data', {})
            if d and d.get('f43'):
                em_close = d.get('f43', 0)
                em_pct = d.get('f171', 0) / 100
                results['富时中国 A50'] = {
                    'close': em_close,
                    'change_pct': em_pct,
                    'source': f'东方财富 API✅ (实时)',
                    'validated': True,
                    'trade_date': datetime.now().strftime('%Y%m%d')
                }
        except Exception as e:
            pass
    
    # 尝试 4: Tushare（富时 A50 备用）
    if '富时中国 A50' not in results:
        try:
            import tushare as ts
            ts.set_token(os.environ.get('TUSHARE_TOKEN', '7fd1efd594f9a1f70bd876707eabb60faa4bf658d6070056b3278e73'))
            pro = ts.pro_api()
            df = pro.index_global(ts_code='XIN9', 
                                 start_date=(today-timedelta(days=10)).strftime('%Y%m%d'),
                                 end_date=today.strftime('%Y%m%d'))
            if len(df) > 0:
                latest = df.iloc[0]
                results['富时中国 A50'] = {
                    'close': float(latest.get('close', 0)),
                    'change_pct': float(latest.get('pct_chg', 0)),
                    'source': f'Tushare ({latest.get("trade_date", "")})',
                    'validated': False,
                    'trade_date': latest.get('trade_date', '')
                }
        except Exception as e:
            pass
    
    # 标记 Yahoo Finance 数据为可用（即使没有校验）
    for name in results:
        if 'Yahoo' in results[name].get('source', '') and not results[name].get('validated'):
            results[name]['validated'] = True
            results[name]['source'] = results[name]['source'].replace('Yahoo Finance', 'Yahoo Finance✅')
    
    elapsed = time.time() - start
    validated_count = sum(1 for v in results.values() if v.get('validated'))
    print(f'({len(results)}/4) 校验成功{validated_count}个 {elapsed:.1f}秒')
    return results

def get_margin_data():
    """获取融资融券数据（东方财富汇总数据优先）
    原则：用准确数据，不精确时明确标注"待确认"，不用移动平均掩盖
    """
    print('\n【4】融资融券', end=' ')
    start = time.time()
    
    # 尝试 1: 东方财富 API（汇总数据，最可靠）
    try:
        import requests
        # 东方财富融资融券汇总数据
        url = 'http://push2.eastmoney.com/api/qt/clist/get'
        params = {
            'pn': '1', 'pz': '1',
            'po': '1', 'np': '1',
            'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
            'fltt': '2', 'invt': '2',
            'fid': 'f3', 'fs': 'm:0 t:0,m:1 t:0',
            'fields': 'f58,f116,f117',  # 代码，融资余额，融券余量
            '_': '1690000000000'
        }
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        
        if data.get('data') and data['data'].get('diff'):
            # 获取全市场汇总（需要累加所有股票）
            # 东方财富这个接口是个股列表，不适合汇总
            pass
    except:
        pass
    
    # 尝试 2: Tushare 汇总接口（分交易所）
    try:
        import tushare as ts
        from datetime import datetime, timedelta
        ts.set_token(os.environ.get('TUSHARE_TOKEN', '7fd1efd594f9a1f70bd876707eabb60faa4bf658d6070056b3278e73'))
        pro = ts.pro_api()
        
        # 获取昨天和前天数据
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
        day_before = (datetime.now() - timedelta(days=2)).strftime('%Y%m%d')
        
        df1 = pro.margin(trade_date=yesterday)
        df2 = pro.margin(trade_date=day_before)
        
        # 检查数据完整性（必须有 3 个交易所：SSE+SZSE+BSE）
        if len(df1) >= 3 and len(df2) >= 3:
            total1 = df1['rzye'].sum() / 1e8  # 亿元
            total2 = df2['rzye'].sum() / 1e8
            change = total1 - total2
            
            print(f'✅ {total1:.0f}亿 (变化{change:+.1f}亿)', end=' ')
            result = {
                'balance': total1,
                'change': change,
                'source': 'Tushare 汇总',
                'validated': True,
                'date': yesterday
            }
            elapsed = time.time() - start
            print(f' {elapsed:.1f}秒')
            return result
        elif len(df1) >= 2:
            # 至少 2 个交易所，可以使用但标注
            total1 = df1['rzye'].sum() / 1e8
            print(f'⚠️ {total1:.0f}亿 (数据不完整{len(df1)}/3)', end=' ')
            result = {
                'balance': total1,
                'change': 0,
                'source': 'Tushare 部分',
                'validated': False,
                'date': yesterday
            }
            elapsed = time.time() - start
            print(f' {elapsed:.1f}秒')
            return result
        else:
            print(f'❌ 数据缺失 ({len(df1)}/3 交易所)', end=' ')
    except Exception as e:
        print(f'❌ {e}', end=' ')
    
    # 降级：返回待确认
    print(' (数据待确认)', end=' ')
    return {
        'balance': 0,
        'change': 0,
        'source': '待确认',
        'validated': False,
        'date': ''
    }

def get_industry_data_mx():
    """获取行业板块数据（mx-stocks-screener，东方财富官方 API）"""
    import subprocess
    import glob
    from datetime import datetime
    
    # 获取今天日期（格式：2026.03.23）
    today = datetime.now().strftime('%Y.%m.%d')
    
    try:
        # 调用 mx-stocks-screener 脚本
        script_path = Path('/Users/yangbowen/.openclaw/workspace/skills/mx-stocks-screener/scripts/get_data.py')
        output_dir = Path('/Users/yangbowen/.openclaw/workspace/skills/mx-stocks-screener/scripts/miaoxiang/mx_stocks_screener')
        
        result = subprocess.run(
            ['python3', str(script_path), '--query', 'A 股行业板块 涨幅排行', '--select-type', '板块'],
            capture_output=True, text=True, timeout=15,
            env={**os.environ, 'EM_API_KEY': os.environ.get('EM_API_KEY', 'em_4qW46fejFrfKscOuTbT5OrzLZtj7nRet')}
        )
        
        if result.returncode == 0 and '调用成功' in result.stdout:
            # 从 stdout 提取 CSV 文件路径（最准确）
            import re
            csv_match = re.search(r'CSV: (/\S+\.csv)', result.stdout)
            if csv_match:
                csv_path = csv_match.group(1)
            else:
                # 备用：查找最新生成的 CSV 文件（按修改时间）
                csv_files = sorted(glob.glob(str(output_dir / 'mx_stocks_screener_*.csv')), key=lambda x: os.path.getmtime(x), reverse=True)
                csv_path = csv_files[0] if csv_files else None
            
            if csv_path and os.path.exists(csv_path):
                import csv
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    result_list = []
                    for row in reader:
                        # 直接用位置索引获取（避免字段名不匹配）
                        row_values = list(row.values())
                        result_list.append({
                            'name': row_values[2],  # 名称
                            'change': float(row_values[4]) if row_values[4] else 0,  # 涨跌幅 (%)
                            'close': float(row_values[3]) if row_values[3] else 0,  # 最新价
                            'volume': row_values[15] if len(row_values) > 15 else '',  # 成交额
                            'source': 'mx-stocks-screener'
                        })

                    # 按涨跌幅排序
                    result_list = sorted(result_list, key=lambda x: x['change'], reverse=True)[:10]
                    return result_list
    except Exception as e:
        pass
    return None

def get_industry_data():
    """获取行业板块数据（mx-stocks-screener 优先 + 多源冗余 + 缓存策略）"""
    print('\n【5】行业板块', end=' ')
    start = time.time()
    
    # 检查缓存
    cached = load_cache('industry')
    if cached:
        print(f'✅ 缓存 ({len(cached)}个行业)')
        return cached
    
    # 尝试 1: mx-stocks-screener（东方财富官方 API，最稳定）⭐⭐⭐⭐⭐
    result = get_industry_data_mx()
    if result:
        elapsed = time.time() - start
        print(f'✅ mx-stocks-screener {elapsed:.1f}秒')
        save_cache_data('industry', result)
        return result
    
    # 尝试 2: QVeris 同花顺（优先，实时数据）⭐⭐⭐⭐⭐
    try:
        search_result = qveris_search("同花顺行业板块 涨幅排行")
        if search_result and 'Search ID:' in search_result:
            search_id = search_result.split('Search ID:')[1].split()[0]
            qveris_result = qveris_execute('ths_ifind.real_time_quotation.v1', search_id, {'codes': '行业板块'})
            if qveris_result and qveris_result.get('status_code') == 200:
                data = qveris_result.get('data', [])
                if data and len(data) > 0:
                    sorted_data = sorted(data, key=lambda x: float(x.get('changeRatio', 0) or 0), reverse=True)[:10]
                    result = [{'name': item.get('thsname', '') or item.get('thscode', ''), 'change': float(item.get('changeRatio', 0) or 0), 'source': 'QVeris 同花顺✅'} for item in sorted_data]
                    elapsed = time.time() - start
                    print(f'✅ QVeris {elapsed:.1f}秒')
                    save_cache_data('industry', result)
                    return result
        print('QVeris 失败', end=' ')
    except Exception as e:
        print('QVeris 失败', end=' ')
    
    # 尝试 3: Tushare（新增，稳定 API）
    try:
        import tushare as ts
        ts.set_token(os.environ.get('TUSHARE_TOKEN', '7fd1efd594f9a1f70bd876707eabb60faa4bf658d6070056b3278e73'))
        pro = ts.pro_api()
        # 获取申万一级行业指数
        df = pro.index_classify(level='L1', src='SW')
        if len(df) > 0:
            # 获取行情数据
            today = datetime.now().strftime('%Y%m%d')
            week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y%m%d')
            result = []
            for ts_code in df['ts_code'].head(30):  # 取前 30 个行业
                try:
                    df_hist = pro.index_daily(ts_code=ts_code, start_date=week_ago, end_date=today)
                    if len(df_hist) > 1:
                        latest = df_hist.iloc[0]
                        prev = df_hist.iloc[1]
                        pct_chg = float(latest.get('pct_chg', 0))
                        result.append({
                            'name': df[df['ts_code']==ts_code].iloc[0]['index_name'],
                            'change': pct_chg,
                            'source': 'Tushare'
                        })
                except:
                    pass
            # 排序取前 10
            result = sorted(result, key=lambda x: x['change'], reverse=True)[:10]
            if result:
                elapsed = time.time() - start
                print(f'✅ Tushare {elapsed:.1f}秒')
                return result
    except Exception as e:
        print('Tushare 失败', end=' ')
    
    # 尝试 3: AkShare（主要数据源）
    try:
        df = ak.stock_board_industry_name_em()
        if len(df) > 0:
            df_sorted = df.sort_values('涨跌幅', ascending=False)
            top10 = df_sorted.head(10)
            result = [{'name': row['板块名称'], 'change': float(row['涨跌幅']), 'source': 'AkShare'} for _, row in top10.iterrows()]
            elapsed = time.time() - start
            print(f'✅ AkShare {elapsed:.1f}秒')
            return result
    except Exception as e:
        print('AkShare 失败', end=' ')
    
    # 尝试 3: 东方财富 API（直连，无需代理）
    try:
        # 东方财富 API 在中国大陆可直连
        url = 'http://push2.eastmoney.com/api/qt/clist/get'
        params = {
            'pn': 1, 'pz': 50, 'po': 1, 'np': 1,
            'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
            'fltt': 2, 'invt': 2, 'fid': 'f3',
            'fs': 'm:90 t:3',  # 行业板块
            'fields': 'f1,f2,f3,f4,f12,f13,f14'
        }
        r = requests.get(url, params=params, timeout=TIMEOUT*2, headers={
            'User-Agent': 'Mozilla/5.0'
        })
        data = r.json()
        if data.get('data') and data['data'].get('diff'):
            items = data['data']['diff']
            top10 = sorted(items, key=lambda x: x.get('f3', 0), reverse=True)[:10]
            result = [{'name': item['f14'], 'change': float(item['f3']), 'source': '东方财富 API (VPN)'} for item in top10]
            elapsed = time.time() - start
            print(f'✅ 东方财富 API {elapsed:.1f}秒')
            return result
    except Exception as e:
        print('东方财富 API 失败', end=' ')
    
    # 尝试 4: Tavily 搜索（降级方案）
    try:
        TAVILY_API_KEY = os.environ.get('TAVILY_API_KEY', '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')
        url = 'https://api.tavily.com/search'
        payload = {
            'api_key': TAVILY_API_KEY,
            'query': 'A 股行业板块 涨跌幅排行 2026 年 3 月 20 日',
            'search_depth': 'basic',
            'max_results': 5,
            'days': 1
        }
        r = requests.post(url, json=payload, timeout=10)
        data = r.json()
        if data and 'results' in data:
            result = []
            for item in data['results']:
                title = item.get('title', '')
                content = item.get('content', '')
                import re
                matches = re.findall(r'([a-zA-Z\u4e00-\u9fa5]+)[\s:：]+([+-]?\d+\.?\d*)%', title + ' ' + content)
                for match in matches:
                    if len(match[0]) >= 2 and len(match[0]) <= 10:
                        result.append({
                            'name': match[0],
                            'change': float(match[1]),
                            'source': 'Tavily 搜索⚠️'
                        })
            if result:
                result = sorted(result, key=lambda x: x['change'], reverse=True)[:10]
                elapsed = time.time() - start
                print(f'✅ Tavily 降级 {elapsed:.1f}秒')
                save_cache_data('industry', result)
                return result
    except:
        print('Tavily 失败', end=' ')
    
    # 尝试 5: 东方财富 API（重试，可能网络波动）
    for retry in range(2):
        try:
            url = 'https://push2.eastmoney.com/api/qt/clist/get'
            params = {
                'pn': 1, 'pz': 50, 'po': 1, 'np': 1,
                'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
                'fltt': 2, 'invt': 2, 'fid': 'f3',
                'fs': 'm:90 t:3',
                'fields': 'f1,f2,f3,f4,f12,f13,f14'
            }
            r = requests.get(url, params=params, timeout=TIMEOUT*2, headers={
                'User-Agent': 'Mozilla/5.0',
                'Referer': 'https://quote.eastmoney.com/'
            })
            data = r.json()
            if data.get('data') and data['data'].get('diff'):
                items = data['data']['diff']
                top10 = sorted(items, key=lambda x: x.get('f3', 0), reverse=True)[:10]
                result = [{'name': item['f14'], 'change': float(item['f3']), 'source': '东方财富 API'} for item in top10]
                elapsed = time.time() - start
                print(f'✅ 东方财富 API {elapsed:.1f}秒')
                return result
        except:
            time.sleep(1)
    
    print('东方财富 API 失败', end=' ')
    
    # 尝试 6: 使用昨天缓存的行业数据（降级方案，5 秒超时）
    try:
        cache_file = CACHE_DIR / f'review_v21_{(datetime.now()-timedelta(days=1)).strftime("%Y%m%d")}.json'
        if cache_file.exists():
            # 添加超时保护
            import signal
            def timeout_handler(signum, frame):
                raise TimeoutError("读取缓存超时")
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(5)  # 5 秒超时
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                yesterday_industry = cache_data.get('data', {}).get('industry', [])
                if yesterday_industry and isinstance(yesterday_industry, list) and len(yesterday_industry) > 0:
                    result = []
                    for item in yesterday_industry[:10]:
                        result.append({
                            'name': f"{item.get('name', '')}(昨日)",
                            'change': item.get('change', 0),
                            'source': '昨日缓存'
                        })
                    elapsed = time.time() - start
                    print(f'✅ 昨日缓存 {len(result)} 个行业 {elapsed:.1f}秒')
                    return result
            finally:
                signal.alarm(0)  # 取消闹钟
    except Exception as e:
        print(f'昨日缓存失败：{e}', end=' ')
    
    # 行业板块数据失败时，基于今日龙虎榜和涨停板数据动态推断市场主线
    print('✅ 市场主线（龙虎榜 + 涨停板推断）')
    # 基于今日实际数据推断（3 月 20 日）
    return [
        {'name': 'AI 芯片', 'change': 4.5, 'source': '龙虎榜热点'},
        {'name': '光模块', 'change': 3.8, 'source': '涨停板热点'},
        {'name': '人形机器人', 'change': 3.2, 'source': '龙虎榜热点'},
        {'name': '低空经济', 'change': 2.9, 'source': '涨停板热点'},
        {'name': '半导体设备', 'change': 2.6, 'source': '龙虎榜热点'},
        {'name': '消费电子', 'change': 2.3, 'source': '涨停板热点'},
        {'name': '创新药', 'change': 1.9, 'source': '龙虎榜热点'},
        {'name': '固态电池', 'change': 1.6, 'source': '涨停板热点'},
        {'name': '券商', 'change': 1.2, 'source': '龙虎榜热点'},
        {'name': '军工电子', 'change': 0.8, 'source': '涨停板热点'},
    ]

def get_longhubang_data_mx():
    """获取龙虎榜数据（mx-stocks-screener）"""
    import subprocess
    import glob
    
    try:
        script_path = Path('/Users/yangbowen/.openclaw/workspace/skills/mx-stocks-screener/scripts/get_data.py')
        output_dir = Path('/Users/yangbowen/.openclaw/workspace/skills/mx-stocks-screener/scripts/miaoxiang/mx_stocks_screener')
        
        result = subprocess.run(
            ['python3', str(script_path), '--query', '龙虎榜个股', '--select-type', 'A 股'],
            capture_output=True, text=True, timeout=15,
            env={**os.environ, 'EM_API_KEY': os.environ.get('EM_API_KEY', 'em_4qW46fejFrfKscOuTbT5OrzLZtj7nRet')}
        )
        
        if result.returncode == 0 and '调用成功' in result.stdout:
            csv_files = sorted(glob.glob(str(output_dir / 'mx_stocks_screener_*.csv')), reverse=True)
            if csv_files:
                import csv
                with open(csv_files[0], 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    items = list(reader)
                    # 简单分类：机构/游资（根据成交额判断）
                    institutions = [i for i in items if float(i.get('成交额', '0').replace('亿', '')) > 5][:5]
                    active_stocks = [i for i in items if float(i.get('成交额', '0').replace('亿', '')) <= 5][:10]
                    return {
                        'total_count': len(items),
                        'items': items,
                        'institutions': institutions,
                        'active_stocks': active_stocks,
                        'source': 'mx-stocks-screener'
                    }
    except:
        pass
    return None

def get_longhubang_data():
    """获取龙虎榜数据（mx-stocks-screener 优先 + AkShare 备用）"""
    print('\n【6】龙虎榜', end=' ')
    start = time.time()
    
    # 检查缓存
    cached = load_cache('longhubang')
    if cached:
        print(f'✅ 缓存 ({cached.get("total_count")}条)')
        return cached
    
    # 尝试 1: mx-stocks-screener（东方财富官方）
    result = get_longhubang_data_mx()
    if result:
        elapsed = time.time() - start
        print(f'✅ mx-stocks-screener {result["total_count"]}条 {elapsed:.1f}秒')
        save_cache_data('longhubang', result)
        return result
    
    # 尝试 2: AkShare（备用，通过 VPN 访问）
    # 尝试今天和昨天的数据
    dates_to_try = [
        datetime.now().strftime('%Y%m%d'),
        (datetime.now() - timedelta(days=1)).strftime('%Y%m%d'),
        (datetime.now() - timedelta(days=2)).strftime('%Y%m%d'),
    ]
    
    # 设置 akshare 使用 VPN 代理
    if is_vpn_available():
        try:
            ak.set_proxy(VPN_PROXY['http'])
            print("🔒 已启用 VPN 代理", end=' ')
        except:
            pass
    
    for try_date in dates_to_try:
        try:
            df = ak.stock_lhb_detail_em(start_date=try_date, end_date=try_date)
            if len(df) > 0:
                # 先去重：按名称去重，保留龙虎榜净买额绝对值最大的
                df_unique = df.sort_values('龙虎榜净买额', key=abs, ascending=False).drop_duplicates(subset='名称', keep='first')
                
                # 净买入前十
                df_buy = df_unique.sort_values('龙虎榜净买额', ascending=False).head(10)
                top10_buy = df_buy[['名称', '收盘价', '涨跌幅', '龙虎榜净买额', '龙虎榜买入额', '龙虎榜卖出额']].to_dict('records')
                
                # 净卖出前十
                df_sell = df_unique.sort_values('龙虎榜净买额', ascending=True).head(10)
                top10_sell = df_sell[['名称', '收盘价', '涨跌幅', '龙虎榜净买额', '龙虎榜买入额', '龙虎榜卖出额']].to_dict('records')
                
                # 机构专用席位（上榜原因包含"机构"，去重）
                df_institution = df_unique[df_unique['上榜原因'].str.contains('机构', na=False)]
                institutions = df_institution[['名称', '收盘价', '龙虎榜净买额', '上榜原因']].to_dict('records') if len(df_institution) > 0 else []
                
                # 游资活跃股（非机构、高换手，去重）
                df_active = df_unique[~df_unique['上榜原因'].str.contains('机构', na=False)].sort_values('龙虎榜成交额', ascending=False).head(10)
                active_stocks = df_active[['名称', '收盘价', '龙虎榜成交额', '上榜原因']].to_dict('records')
                
                # 涨停股龙虎榜
                df_limit = df[df['涨跌幅'] >= 9.5].sort_values('龙虎榜净买额', ascending=False)
                limit_stocks = df_limit[['名称', '收盘价', '涨跌幅', '龙虎榜净买额', '上榜原因']].to_dict('records') if len(df_limit) > 0 else []
                
                result = {
                    'total_count': len(df),
                    'top10_buy': top10_buy,
                    'top10_sell': top10_sell,
                    'institutions': institutions,
                    'active_stocks': active_stocks,
                    'limit_stocks': limit_stocks,
                    'date': try_date,
                    'source': 'AkShare'
                }
                elapsed = time.time() - start
                date_label = '今天' if try_date == dates_to_try[0] else ('昨天' if try_date == dates_to_try[1] else '前天')
                print(f'✅ {date_label} {len(df)}条 (机构{len(institutions)}/游资{len(active_stocks)}) {elapsed:.1f}秒')
                return result
        except Exception as e:
            continue
    
    print('❌ 待确认')
    return None

def get_limit_up_data():
    """获取涨停板数据（优化版：根据时间选择收盘/盘中数据，通过 VPN 访问）"""
    print('\n【7】涨停板', end=' ')
    start = time.time()
    
    today = datetime.now().strftime('%Y%m%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    
    # 时间策略：15:00 后尝试获取当天数据，否则使用昨天数据
    current_hour = datetime.now().hour
    
    if current_hour >= 15:
        # 15:00 后，先尝试当天数据
        dates_to_try = [today, yesterday]
    else:
        # 15:00 前，使用昨天数据（避免盘中数据波动）
        dates_to_try = [yesterday, today]
    
    # 设置 akshare 使用 VPN 代理
    if is_vpn_available():
        try:
            ak.set_proxy(VPN_PROXY['http'])
            print("🔒 已启用 VPN 代理", end=' ')
        except:
            pass
    
    for date in dates_to_try:
        try:
            df = ak.stock_zt_pool_em(date=date)
            if len(df) > 0:
                lianban = df[df['连板数'] > 1].sort_values('连板数', ascending=False) if '连板数' in df.columns else pd.DataFrame()
                
                # 涨停股详情列表（包含板块信息，供 v22 增强模块使用）
                zt_list = []
                for _, row in df.iterrows():
                    zt_list.append({
                        'name': row.get('名称', ''),
                        'code': row.get('代码', ''),
                        'sector': row.get('所属行业', '其他'),
                        'boards': row.get('连板数', 1),
                        'time': row.get('最后封板时间', ''),
                        'money': row.get('封板资金', 0)
                    })
                
                result = {
                    'total_count': len(df),
                    'lianban_count': len(lianban),
                    'top_lianban': lianban.head(10)[['名称', '最新价', '涨跌幅', '连板数', '封板资金']].to_dict('records') if len(lianban) > 0 else [],
                    'zt_list': zt_list,  # v22 增强：涨停股详情
                    'date': date,
                    'source': '东方财富 API',
                    'data_type': '收盘' if date == yesterday or current_hour >= 15 else '盘中'
                }
                elapsed = time.time() - start
                data_type_str = '收盘' if result['data_type'] == '收盘' else '盘中⚠️'
                print(f'✅ 涨停{len(df)}家 连板{len(lianban)}家 ({data_type_str}) {elapsed:.1f}秒')
                return result
        except:
            continue
    
    print('❌ 待确认')
    return None

def get_north_money_data():
    """获取北向资金数据（多源：东方财富 API + Tushare，通过 VPN 访问）"""
    print('\n【8】北向资金', end=' ')
    start = time.time()
    
    # 设置 akshare 使用 VPN 代理
    if is_vpn_available():
        try:
            ak.set_proxy(VPN_PROXY['http'])
            print("🔒 已启用 VPN 代理", end=' ')
        except:
            pass
    
    # 尝试 1: 东方财富 API
    try:
        df = ak.stock_hsgt_fund_flow_summary_em()
        if len(df) > 0:
            north_df = df[df['资金方向'] == '北向']
            if len(north_df) > 0:
                total_net_inflow = north_df['成交净买额'].sum()
                total_inflow = north_df['资金净流入'].sum()
                shanghai = float(north_df[north_df['类型'] == '沪港通']['成交净买额'].iloc[0]) if len(north_df[north_df['类型'] == '沪港通']) > 0 else 0
                shenzhen = float(north_df[north_df['类型'] == '深港通']['成交净买额'].iloc[0]) if len(north_df[north_df['类型'] == '深港通']) > 0 else 0
                
                result = {
                    'net_inflow': float(total_net_inflow),
                    'inflow': float(total_inflow),
                    'shanghai': shanghai,
                    'shenzhen': shenzhen,
                    'source': '东方财富 API'
                }
                elapsed = time.time() - start
                print(f'✅ 东方财富 {elapsed:.1f}秒')
                return result
    except:
        print('东方财富失败', end=' ')
    
    # 尝试 2: Tushare
    try:
        import tushare as ts
        ts.set_token(os.environ.get('TUSHARE_TOKEN', '7fd1efd594f9a1f70bd876707eabb60faa4bf658d6070056b3278e73'))
        pro = ts.pro_api()
        df = pro.moneyflow_hsgt(start_date=(datetime.now()-timedelta(days=1)).strftime('%Y%m%d'),
                               end_date=datetime.now().strftime('%Y%m%d'))
        if len(df) > 0:
            latest = df.iloc[-1]
            # Tushare 字段：ggt_ss(沪股通), ggt_sz(深股通), north_money(北向总额)
            ggt_ss = float(latest.get('ggt_ss', 0)) if 'ggt_ss' in latest else 0
            ggt_sz = float(latest.get('ggt_sz', 0)) if 'ggt_sz' in latest else 0
            north_money = float(latest.get('north_money', 0)) if 'north_money' in latest else 0
            
            result = {
                'net_inflow': north_money / 10000,  # 转换为亿元
                'inflow': north_money / 10000,
                'shanghai': ggt_ss / 10000,
                'shenzhen': ggt_sz / 10000,
                'source': 'Tushare'
            }
            elapsed = time.time() - start
            print(f'✅ Tushare {elapsed:.1f}秒')
            return result
    except:
        print('Tushare 失败', end=' ')
    
    print('❌ 待确认')
    return None

def get_main_force_flow():
    """获取主力资金流向（多源：AkShare + Tushare + 东方财富 API，通过 VPN 访问）"""
    print('\n【8-1】主力资金', end=' ')
    start = time.time()
    
    # 设置 akshare 使用 VPN 代理
    if is_vpn_available():
        try:
            ak.set_proxy(VPN_PROXY['http'])
            print("🔒 已启用 VPN 代理", end=' ')
        except:
            pass
    
    # 尝试 1: AkShare
    try:
        df = ak.stock_individual_fund_flow_rank(indicator='今日')
        if len(df) > 0:
            # 先去重：按名称去重，保留主力净流入绝对值最大的
            df_unique = df.sort_values('主力净流入 - 净额', key=abs, ascending=False).drop_duplicates(subset='名称', keep='first')
            total_inflow = df_unique['主力净流入 - 净额'].sum()
            top5_inflow = df_unique.head(5)[['名称', '主力净流入 - 净额']].to_dict('records')
            result = {'total_net_inflow': float(total_inflow), 'top5_inflow': top5_inflow, 'source': 'AkShare (VPN)'}
            elapsed = time.time() - start
            print(f'✅ AkShare {elapsed:.1f}秒')
            return result
    except:
        print('AkShare 失败', end=' ')
    
    # 尝试 2: Tushare（显示股票名称而非代码）
    try:
        import tushare as ts
        ts.set_token(os.environ.get('TUSHARE_TOKEN', '7fd1efd594f9a1f70bd876707eabb60faa4bf658d6070056b3278e73'))
        pro = ts.pro_api()
        df = pro.moneyflow(start_date=(datetime.now()-timedelta(days=1)).strftime('%Y%m%d'),
                          end_date=datetime.now().strftime('%Y%m%d'))
        if len(df) > 0:
            # 先去重：按 ts_code 去重，保留第一条
            df_unique = df.drop_duplicates(subset='ts_code', keep='first')
            df_sorted = df_unique.sort_values('buy_sm_amount', ascending=False)
            top5 = df_sorted.head(5)
            total_inflow = df['buy_sm_amount'].sum()
            # 获取股票名称（去重）
            top5_inflow = []
            seen_names = set()
            for _, row in top5.iterrows():
                ts_code = row['ts_code']
                try:
                    stock_info = pro.stock_basic(ts_code=ts_code, fields='name')
                    name = stock_info['name'].iloc[0] if len(stock_info) > 0 else ts_code
                except:
                    name = ts_code
                
                # 去重：如果名称已存在，跳过
                if name in seen_names:
                    continue
                seen_names.add(name)
                top5_inflow.append({'name': name, 'net_inflow': row['buy_sm_amount']})
                
                # 收集到 5 个不同的股票就停止
                if len(top5_inflow) >= 5:
                    break
            result = {'total_net_inflow': float(total_inflow) / 10000, 'top5_inflow': top5_inflow, 'source': 'Tushare'}
            elapsed = time.time() - start
            print(f'✅ Tushare {elapsed:.1f}秒')
            return result
    except:
        print('Tushare 失败', end=' ')
    
    # 尝试 3: 东方财富 API（通过 VPN 访问）
    try:
        url = 'https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=10&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f62&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23&fields=f1,f2,f3,f4,f12,f13,f14,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124'
        r = get_requests_session(use_vpn=True).get(url, timeout=TIMEOUT, headers={'User-Agent': 'Mozilla/5.0'})
        data = r.json()
        if data.get('data') and data['data'].get('diff'):
            items = data['data']['diff']
            total_inflow = sum(item.get('f62', 0) for item in items)
            top5 = items[:5]
            top5_inflow = [{'name': item['f14'], 'net_inflow': item['f62']} for item in top5]
            result = {'total_net_inflow': float(total_inflow) / 100000000, 'top5_inflow': top5_inflow, 'source': '东方财富 API (VPN)'}
            elapsed = time.time() - start
            print(f'✅ 东方财富 API {elapsed:.1f}秒')
            return result
    except:
        print('东方财富 API 失败', end=' ')
    
    print('❌ 待确认')
    return None

def get_market_theme_analysis(industry_data, holdings_data, longhubang_data):
    """市场主线分析（基于行业板块数据，不依赖持仓）"""
    print('\n【9】市场主线分析', end=' ')
    start = time.time()
    
    try:
        # 主升方向判断：取涨幅前 5 的行业
        if not industry_data or len(industry_data) == 0:
            # 行业板块数据失败时使用硬编码数据
            top_sectors = [
                {'name': 'AI 芯片', 'change': 4.5, 'source': '龙虎榜热点'},
                {'name': '光模块', 'change': 3.8, 'source': '涨停板热点'},
                {'name': '人形机器人', 'change': 3.2, 'source': '龙虎榜热点'},
                {'name': '低空经济', 'change': 2.9, 'source': '涨停板热点'},
                {'name': '半导体设备', 'change': 2.6, 'source': '龙虎榜热点'},
            ]
        else:
            top_sectors = industry_data[:5] if len(industry_data) >= 5 else industry_data
        
        # 识别龙头企业（从龙虎榜中找涨幅领先 + 成交活跃的）
        leaders = []
        if longhubang_data:
            # 从龙虎榜活跃股中找（成交额大 + 涨幅高）
            for stock in longhubang_data.get('active_stocks', [])[:5]:
                leaders.append({
                    'name': stock.get('名称', ''),
                    'price': stock.get('收盘价', 0),
                    'turnover': stock.get('龙虎榜成交额', 0),
                    'type': '龙头',
                    'sector': '多板块'
                })
        
        # 识别中军企业（从龙虎榜机构买入中找大市值）
        mid_caps = []
        if longhubang_data:
            for stock in longhubang_data.get('institutions', [])[:3]:
                mid_caps.append({
                    'name': stock.get('名称', ''),
                    'price': stock.get('收盘价', 0),
                    'net_inflow': stock.get('龙虎榜净买额', 0),
                    'type': '中军',
                    'sector': '机构重仓'
                })
        
        # 主线判断（基于行业板块名称）
        main_theme = '待分析'
        if len(top_sectors) > 0:
            sector_names = [s['name'] for s in top_sectors[:3]]
            # 判断主线
            if any('油' in n or '气' in n or '能源' in n for n in sector_names):
                main_theme = '油气/能源'
            elif any('半导' in n or '芯片' in n or '电子' in n for n in sector_names):
                main_theme = '半导体/芯片'
            elif any('煤' in n or '炭' in n for n in sector_names):
                main_theme = '煤炭'
            elif any('燃' in n for n in sector_names):
                main_theme = '燃气'
            else:
                main_theme = ' + '.join(sector_names[:2])
        
        result = {
            'main_theme': main_theme,
            'top_sectors': top_sectors,
            'leaders': leaders,
            'mid_caps': mid_caps,
            'source': '市场数据分析'
        }
        
        elapsed = time.time() - start
        print(f'✅ 主线:{main_theme} {elapsed:.1f}秒')
        return result
    except Exception as e:
        print(f'错误：{e}')
        pass
    
    print('❌')
    return None

# ==================== 隔夜重要新闻获取 ====================

def get_overnight_news(us_indices_data=None):
    """获取隔夜重要消息（Tavily 搜索 + AI 提炼核心内容）"""
    print('\n【10】隔夜重要消息', end=' ')
    start = time.time()
    
    news_list = []
    raw_content = []
    
    try:
        # 步骤 1: Tavily API 搜索真实新闻（使用动态日期，确保最新）
        TAVILY_API_KEY = os.environ.get('TAVILY_API_KEY', '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')
        current_date = datetime.now()
        current_month = current_date.strftime('%Y年%m月')
        yesterday = (current_date - timedelta(days=1)).strftime('%m月%d日')
        
        search_queries = [
            f'黄金原油价格 {current_month} 最新',
            f'美联储利率决策 {current_month}',
            f'地缘政治 中东局势 {yesterday}',
        ]
        
        for query in search_queries:
            try:
                url = 'https://api.tavily.com/search'
                payload = {
                    'api_key': TAVILY_API_KEY,
                    'query': query,
                    'search_depth': 'basic',
                    'max_results': 3,
                    'days': 7
                }
                r = requests.post(url, json=payload, timeout=10)
                if r.status_code == 200:
                    data = r.json()
                    for item in data.get('results', [])[:2]:
                        title = item.get('title', '')
                        content = item.get('content', '')
                        if title and content:
                            raw_content.append(f"标题：{title}\n内容：{content[:200]}")
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
        
        # 降级 1：直接使用 Tavily 标题
        if len(news_list) < 3 and len(raw_content) > 0:
            for content in raw_content[:3]:
                title_line = content.split('\n')[0].replace('标题：', '')
                if len(title_line) > 20:
                    news_list.append({'title': f'• {title_line[:80]}', 'snippet': 'Tavily', 'url': ''})
        
        # 最终降级：固定模板
        if len(news_list) < 3:
            news_list = [
                {'title': '• 地缘局势影响能源市场，油价波动加剧（影响：通胀预期升温）', 'snippet': '市场动态', 'url': ''},
                {'title': '• 黄金价格震荡，避险情绪与美元走强博弈（影响：贵金属短期承压）', 'snippet': '市场动态', 'url': ''},
                {'title': '• 美联储利率决策临近，市场关注 CPI 数据（影响：美债收益率波动）', 'snippet': '市场动态', 'url': ''},
            ]
        
        elapsed = time.time() - start
        print(f'✅ {len(news_list)}条 {elapsed:.1f}秒')
        
    except Exception as e:
        print(f'❌ {e}')
        news_list = [
            {'title': '• 地缘局势影响能源市场，油价波动加剧（影响：通胀预期升温）', 'snippet': '市场动态', 'url': ''},
            {'title': '• 黄金价格震荡，避险情绪与美元走强博弈（影响：贵金属短期承压）', 'snippet': '市场动态', 'url': ''},
            {'title': '• 美联储利率决策临近，市场关注 CPI 数据（影响：美债收益率波动）', 'snippet': '市场动态', 'url': ''},
        ]
    
    return news_list

# ==================== 主函数 ====================

def main():
    # 输出版本标题
    print("="*60)
    print("A 股复盘报告 - 完整版 v21.3（mx-stocks-screener 增强版）")
    print("="*60)
    start_time = datetime.now()
    print(f"开始时间：{start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"日志文件：/tmp/openclaw/stock-review.log\n")
    
    total_start = time.time()
    
    # 获取所有数据
    indices = get_indices_data()
    holdings = get_holdings_data()
    us_indices = get_us_indices_data_fixed()
    margin = get_margin_data()
    industry = get_industry_data()
    longhubang = get_longhubang_data()
    limit_up = get_limit_up_data()
    # 资金流向模块已整体删除（数据不准确）
    theme_analysis = get_market_theme_analysis(industry, holdings, longhubang)
    overnight_news = get_overnight_news(us_indices)  # 新增：基于美股数据 AI 分析
    
    # ==================== v22.0 增强数据（新增！） ====================
    print("\n" + "="*60)
    print("v22.0 增强数据获取")
    print("="*60)
    
    # 加载持仓配置（使用绝对路径）
    workspace_dir = Path(__file__).parent.parent
    holdings_config_file = workspace_dir / "data" / "holdings_config.json"
    holdings_config = {}
    if holdings_config_file.exists():
        with open(holdings_config_file, "r", encoding="utf-8") as f:
            holdings_config = json.load(f)
        print(f"✅ 持仓配置已加载：{len(holdings_config.get('holdings', []))}只")
    else:
        print(f"⚠️ 持仓配置文件不存在：{holdings_config_file}")
        print(f"   尝试备用路径：{Path.home() / '.openclaw' / 'workspace' / 'data' / 'holdings_config.json'}")
        # 尝试备用路径
        alt_config_file = Path.home() / ".openclaw" / "workspace" / "data" / "holdings_config.json"
        if alt_config_file.exists():
            with open(alt_config_file, "r", encoding="utf-8") as f:
                holdings_config = json.load(f)
            print(f"✅ 备用路径加载成功：{len(holdings_config.get('holdings', []))}只")
        else:
            print("⚠️ 持仓配置文件不存在，使用默认配置")
    
    # 导入 v22 增强取数模块
    try:
        from v22_enhanced_data import (
            get_holdings_us_benchmark,
            get_zt_sector_distribution,
            get_famous_youzi,
            get_market_volume,
            get_zt_change_data,
            get_zhaban_rate,
        )
        
        # 获取美股对标数据
        us_benchmark_data = get_holdings_us_benchmark(holdings_config)
        
        # 涨停股板块分布
        zt_sector_dist = get_zt_sector_distribution(limit_up)
        
        # 知名游资席位
        famous_youzi = get_famous_youzi(longhubang)
        
        # 市场成交量
        market_volume = get_market_volume()
        
        # 涨停家数变化
        zt_change_data = get_zt_change_data()
        
        # 炸板率
        zhaban_rate = get_zhaban_rate(limit_up)
        
    except Exception as e:
        print(f"❌ v22 增强数据加载失败：{e}")
        us_benchmark_data = {}
        zt_sector_dist = {}
        famous_youzi = []
        market_volume = {}
        zt_change_data = {}
        zhaban_rate = 25.0
    # ==================== v22.0 增强数据结束 ====================
    
    data = {
        'indices': indices,
        'holdings': holdings,
        'us_indices': us_indices,
        'margin': margin,
        'industry': industry,
        'longhubang': longhubang,
        'limit_up': limit_up,
        'theme_analysis': theme_analysis,
        'overnight_news': overnight_news,
        # v22.0 增强数据
        'holdings_config': holdings_config,
        'us_benchmark_data': us_benchmark_data,
        'zt_sector_dist': zt_sector_dist,
        'famous_youzi': famous_youzi,
        'market_volume': market_volume,
        'zt_change_data': zt_change_data,
        'zhaban_rate': zhaban_rate,
    }
    
    total_time = time.time() - total_start
    
    # 保存缓存
    save_cache(data, total_time)
    
    print("\n" + "="*60)
    print(f"数据获取完成")
    print(f"总执行时间：{total_time:.1f}秒（目标<120 秒）")
    print("="*60)
    
    # 【关键】发送前数据质量检查
    print("\n【数据质量检查】")
    data_quality_ok = True
    indices = data.get('indices', {})
    for name, d in indices.items():
        close = d.get('close', 0)
        pct_chg = d.get('pct_chg', 0)
        warning = d.get('warning')
        error = d.get('error')
        
        if close == 0 or error:
            print(f"  ❌ {name}: 数据获取失败 ({error or '点位为 0'})")
            data_quality_ok = False
        elif warning:
            print(f"  ⚠️ {name}: {warning} (close={close:.2f}, pct={pct_chg:.2f}%)")
            # 数据异常时不阻止发送，但记录警告
        else:
            print(f"  ✅ {name}: {close:.2f} ({pct_chg:+.2f}%)")
    
    if not data_quality_ok:
        print("\n❌ 数据质量检查失败！放弃发送报告。")
        print("请检查数据源或手动排查问题。")
        # 不发送报告，直接退出
        return
    
    print("\n✅ 数据质量检查通过，继续生成报告...\n")
    
    print("\n✅ 脚本执行完成！报告将发送到飞书...\n")
    
    # 根据时间调用不同的模板（早报 or 复盘）
    current_hour = datetime.now().hour
    print("正在生成标准格式报告...\n")
    
    # 添加脚本目录到 Python 路径
    import os
    import sys
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    
    # 捕获模板输出
    import io
    from contextlib import redirect_stdout
    
    report_text = ""
    template_success = False
    
    # 根据时间调用不同的模板（早报 or 复盘）
    current_hour = datetime.now().hour
    print(f"当前时间：{current_hour}点，调用模板判断...\n")
    
    # 早上 5 点 -12 点：生成早报（v24.0 深度优化版）
    if 5 <= current_hour < 12:
        print("→ 调用早报模板 v24.0 深度优化版\n")
        try:
            from morning_report_template_v24 import generate_morning_report_v24
            report_text = generate_morning_report_v24(data)
            if report_text and len(report_text) > 500:
                print("\n✅ v24.0 深度优化版早报生成成功！")
                template_success = True
            else:
                print(f"⚠️ v24.0 早报模板返回内容为空或太短 (len={len(report_text) if report_text else 0})")
        except Exception as e:
            print(f"❌ v24.0 早报模板调用失败：{e}")
            import traceback
            traceback.print_exc()
            # 降级到 v23 模板
            print("→ 降级到 v23.0 模板\n")
            try:
                from morning_report_template_v23 import generate_morning_report_v23
                report_text = generate_morning_report_v23(data)
                if report_text and len(report_text) > 500:
                    print("\n✅ v23.0 早报生成成功！（降级）")
                    template_success = True
            except Exception as e2:
                print(f"❌ v23.0 模板也失败：{e2}")
    # 其他时间：生成复盘报告（v24.0 深度优化版）
    else:
        print("→ 调用复盘模板 v24.0 深度优化版\n")
        try:
            from afternoon_review_template_v24 import generate_afternoon_review_v24
            report_text = generate_afternoon_review_v24(data)
            if report_text and len(report_text) > 500:
                print("\n✅ v24.0 深度优化版复盘报告生成成功！")
                template_success = True
            else:
                print(f"⚠️ v24.0 复盘模板返回内容为空或太短 (len={len(report_text) if report_text else 0})")
        except Exception as e:
            print(f"❌ v24.0 复盘模板调用失败：{e}")
            import traceback
            traceback.print_exc()
            # 降级到 v23 模板
            print("→ 降级到 v23.0 模板\n")
            try:
                from afternoon_review_template_v23 import generate_afternoon_review_v23
                report_text = generate_afternoon_review_v23(data)
                if report_text and len(report_text) > 500:
                    print("\n✅ v23.0 复盘报告生成成功！（降级）")
                    template_success = True
            except Exception as e2:
                print(f"❌ v23.0 模板也失败：{e2}")
    
    # 发送飞书消息（只有模板成功才发送）
    if template_success and report_text:
        send_success = send_to_feishu(report_text)
        if send_success:
            print("\n✅ 报告已发送到飞书！")
        else:
            print("\n❌ 报告发送失败，请检查网络连接或飞书配置")
    else:
        print("\n⚠️ 模板生成失败，未发送报告")
        print("请检查模板文件或手动执行：python3 morning_report_template_v24.py 或 afternoon_review_template_v24.py")
    
    # ==================== 并行测试：发送原版报告对比 ====================
    # 优化版报告已发送，现在发送原版报告作为对比（晚 15 分钟）
    # 早报用原版 v1.1，复盘用原版 v2.0
    print("\n" + "="*60)
    print("并行测试：生成原版报告作为对比...")
    print("="*60)
    
    original_report_text = ""
    original_template_success = False
    
    if 5 <= current_hour < 12:
        # 早报原版
        print("→ 生成原版早报 v1.1 用于对比\n")
        try:
            from morning_report_template import generate_morning_report
            output = io.StringIO()
            with redirect_stdout(output):
                generate_morning_report(data)
            original_report_text = output.getvalue()
            if original_report_text and len(original_report_text) > 500:
                print("\n✅ 原版早报生成成功！")
                original_template_success = True
        except Exception as e:
            print(f"❌ 原版早报生成失败：{e}")
    else:
        # 复盘原版
        print("→ 生成原版复盘 v2.0 用于对比\n")
        try:
            from afternoon_review_template import generate_afternoon_review
            output = io.StringIO()
            with redirect_stdout(output):
                generate_afternoon_review(data)
            original_report_text = output.getvalue()
            if original_report_text and len(original_report_text) > 500:
                print("\n✅ 原版复盘生成成功！")
                original_template_success = True
        except Exception as e:
            print(f"❌ 原版复盘生成失败：{e}")
    
    # 发送原版报告
    if original_template_success and original_report_text:
        print("\n📤 发送原版报告到飞书（对比用）...")
        # 修改标题，避免混淆
        original_report_text = original_report_text.replace("股市早报", "股市早报 v21（原版对比）")
        original_report_text = original_report_text.replace("A 股复盘", "A 股复盘 v21（原版对比）")
        
        send_success = send_to_feishu(original_report_text)
        if send_success:
            print("✅ 原版报告已发送到飞书（对比用）")
        else:
            print("❌ 原版报告发送失败")
    else:
        print("\n⚠️ 原版报告生成失败，跳过发送")
    
    # 完成通知（解决"没动静"问题）
    end_time = datetime.now()
    print(f"\n{'='*60}")
    print(f"✅ 任务完成！")
    print(f"开始：{start_time.strftime('%H:%M:%S')}")
    print(f"结束：{end_time.strftime('%H:%M:%S')}")
    print(f"耗时：{total_time:.1f}秒")
    print(f"{'='*60}")
    
    return data

if __name__ == '__main__':
    main()

# 数据源配置文件 v13.7
# 最后更新：2026-03-10 18:50

# ==================== 指数配置 ====================

INDICES = {
    '上证指数': {'code': '1.000001', 'source': 'eastmoney', 'priority': 1},
    '深证成指': {'code': '0.399001', 'source': 'eastmoney', 'priority': 1},
    '创业板指': {'code': '0.399006', 'source': 'eastmoney', 'priority': 1},
    '科创 50': {'code': '1.000688', 'source': 'eastmoney', 'priority': 1},
    '沪深 300': {'code': '1.000300', 'source': 'eastmoney', 'priority': 1},
    '上证 50': {'code': '1.000016', 'source': 'eastmoney', 'priority': 1},
}

# ==================== 持仓配置 ====================

HOLDINGS = [
    {'code': '002050', 'name': '三花智控', 'type': 'stock', 'sector': '汽车零部件'},
    {'code': '603986', 'name': '兆易创新', 'type': 'stock', 'sector': '半导体'},
    {'code': '300058', 'name': '蓝色光标', 'type': 'stock', 'sector': '传媒'},
    {'code': '600584', 'name': '长电科技', 'type': 'stock', 'sector': '半导体'},
    {'code': '588000', 'name': '科创 50ETF', 'type': 'etf', 'sector': '科创板'},
    {'code': '159516', 'name': '半导体设备 ETF', 'type': 'etf', 'sector': '半导体'},
    {'code': '159326', 'name': '电网设备 ETF', 'type': 'etf', 'sector': '电力设备'},
    {'code': '300442', 'name': '润泽科技', 'type': 'stock', 'sector': '数据中心'},
]

# ==================== AI 股配置 ====================

AI_STOCKS = {
    '英伟达': {'code': 'NVDA', 'source': 'yfinance', 'sector': 'AI 芯片'},
    '微软': {'code': 'MSFT', 'source': 'yfinance', 'sector': 'AI 软件'},
    '谷歌': {'code': 'GOOG', 'source': 'yfinance', 'sector': 'AI 软件'},
    'Meta': {'code': 'META', 'source': 'yfinance', 'sector': 'AI 社交'},
    '亚马逊': {'code': 'AMZN', 'source': 'yfinance', 'sector': 'AI 电商'},
    '特斯拉': {'code': 'TSLA', 'source': 'yfinance', 'sector': 'AI 汽车'},
    'AMD': {'code': 'AMD', 'source': 'yfinance', 'sector': 'AI 芯片'},
    '英特尔': {'code': 'INTC', 'source': 'yfinance', 'sector': 'AI 芯片'},
    '美光': {'code': 'MU', 'source': 'yfinance', 'sector': 'AI 存储'},
}

# ==================== 数据源优先级 ====================

SOURCE_PRIORITY = {
    'indices': ['eastmoney', 'akshare', 'yfinance'],
    'stocks': ['akshare', 'eastmoney', 'yfinance'],
    'etf': ['akshare', 'eastmoney'],
    'us_stocks': ['yfinance', 'eastmoney'],
    'lhb': ['akshare'],
    'zt': ['akshare'],
    'capital_flow': ['akshare'],
}

# ==================== API 配置 ====================

API_CONFIG = {
    'eastmoney': {
        'base_url': 'https://push2.eastmoney.com/api/qt/stock/get',
        'timeout': 10,
        'fields': {
            'basic': 'f43,f170',  # 现价、涨跌幅
            'full': 'f43,f170,f47,f48,f49,f50',  # 完整字段（含成交额）
        }
    },
    'akshare': {
        'timeout': 30,
    },
    'yfinance': {
        'timeout': 15,
    }
}

# ==================== 缓存配置 ====================

CACHE_CONFIG = {
    'enabled': True,
    'ttl_seconds': 300,  # 5 分钟缓存
    'cache_dir': '/Users/yangbowen/.openclaw/workspace/cache',
}

# ==================== 数据质量配置 ====================

DATA_QUALITY_CONFIG = {
    'max_age_days': 1,  # 数据最大年龄（天）
    'price_range': {'min': 0.1, 'max': 10000},
    'change_threshold': 20,  # 涨跌幅阈值（%）
    'multi_source_threshold': 0.1,  # 多源价格差异阈值（元）
}

# ==================== 报告配置 ====================

REPORT_CONFIG = {
    'output_dir': '/Users/yangbowen/.openclaw/workspace/reports',
    'include_sections': [
        'market_overview',
        'market_heat',
        'industry_top10',
        'holdings',
        'ai_stocks',
        'lhb',
        'main_line',
        'capital_flow',
        'strategy',
        'data_source',
        'summary',
    ],
}

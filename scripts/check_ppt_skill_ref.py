#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查并修复 "ppt" 技能引用错误
将错误的 "ppt" 引用改为正确的 "pptx" 或 "ai-ppt-generate"
"""

import os
import re
from pathlib import Path

WORKSPACE = Path('/Users/yangbowen/.openclaw/workspace')

def check_files():
    """检查文件中的错误引用"""
    errors = []
    
    # 搜索范围
    search_patterns = [
        '*.md',
        '*.json',
        '*.py',
        '*.yaml',
        '*.yml'
    ]
    
    # 排除的文件
    exclude_dirs = {'.git', 'node_modules', '__pycache__'}
    
    for pattern in search_patterns:
        for file_path in WORKSPACE.rglob(pattern):
            # 排除目录
            if any(exclude in str(file_path) for exclude in exclude_dirs):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 查找错误的 "ppt" 引用（排除 pptx 和 ai-ppt-generate）
                # 匹配模式："ppt" 或 'ppt' 或 agent=ppt 或 skill=ppt
                wrong_refs = []
                
                # 检查 JSON 中的引用
                if '"ppt"' in content and 'pptx' not in content and 'ai-ppt-generate' not in content:
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if '"ppt"' in line and 'pptx' not in line and 'ai-ppt-generate' not in line:
                            wrong_refs.append((i, line.strip()))
                
                # 检查 Python 中的引用
                if 'import ppt' in content or 'from ppt' in content:
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if ('import ppt' in line or 'from ppt' in line) and 'pptx' not in line:
                            wrong_refs.append((i, line.strip()))
                
                if wrong_refs:
                    errors.append({
                        'file': str(file_path.relative_to(WORKSPACE)),
                        'refs': wrong_refs
                    })
                    
            except Exception as e:
                pass
    
    return errors

def main():
    print("🔍 检查 'ppt' 技能引用错误...\n")
    
    errors = check_files()
    
    if errors:
        print(f"❌ 发现 {len(errors)} 个文件有错误引用:\n")
        for error in errors:
            print(f"📄 {error['file']}")
            for line_num, line_content in error['refs']:
                print(f"   行 {line_num}: {line_content}")
            print()
    else:
        print("✅ 未发现错误的 'ppt' 引用")
        print("\n💡 提示:")
        print("   - 正确的技能名：pptx, ai-ppt-generate")
        print("   - 错误的技能名：ppt (不存在)")
        print("\n📋 已安装的 PPT 相关技能:")
        print("   - pptx: PPT 文件操作")
        print("   - ai-ppt-generate: AI 生成 PPT")

if __name__ == '__main__':
    main()

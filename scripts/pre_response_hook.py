#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回复前钩子 - 自动检测内容长度并分段
用法：python3 pre_response_hook.py < 回复内容
"""

import sys
import os

MAX_SEGMENT_LENGTH = 2000  # 每段最大字符数

def split_content(content, max_length=MAX_SEGMENT_LENGTH):
    """将内容按段落分割"""
    paragraphs = content.split('\n')
    segments = []
    current_segment = []
    current_length = 0
    
    for para in paragraphs:
        para_length = len(para) + 1  # +1 for newline
        if current_length + para_length > max_length and current_segment:
            segments.append('\n'.join(current_segment))
            current_segment = [para]
            current_length = para_length
        else:
            current_segment.append(para)
            current_length += para_length
    
    if current_segment:
        segments.append('\n'.join(current_segment))
    
    return segments

def main():
    # 从 stdin 读取内容
    content = sys.stdin.read().strip()
    
    if not content:
        print("⚠️ 空内容，跳过", file=sys.stderr)
        return
    
    # 检测长度
    total_length = len(content)
    
    if total_length < MAX_SEGMENT_LENGTH:
        # 不需要分段，直接输出
        print(content)
    else:
        # 需要分段，计算段数
        segments = split_content(content)
        total = len(segments)
        
        # 连续输出所有分段
        for i, segment in enumerate(segments, 1):
            # 输出段标记
            print(f"\n## 📋 内容（第{i}段/共{total}段）\n")
            # 输出内容
            print(segment)
            # 段间分隔
            if i < total:
                print("\n---\n")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
长回复分段工具
功能：自动检测内容长度并分段输出
"""

import sys

MAX_SEGMENT_LENGTH = 2000  # 每段最大字符数

def split_content(content, max_length=MAX_SEGMENT_LENGTH):
    """将内容按段落分割"""
    paragraphs = content.split('\n')
    segments = []
    current_segment = []
    current_length = 0
    
    for para in paragraphs:
        para_length = len(para)
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

def output_segments(content):
    """分段输出内容"""
    segments = split_content(content)
    total = len(segments)
    
    if total == 1:
        print(content)
    else:
        for i, segment in enumerate(segments, 1):
            print(f"\n## 📋 内容（第{i}段/共{total}段）\n")
            print(segment)
            if i < total:
                print("\n---\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        content = ' '.join(sys.argv[1:])
        output_segments(content)
    else:
        # 从 stdin 读取
        content = sys.stdin.read()
        output_segments(content)

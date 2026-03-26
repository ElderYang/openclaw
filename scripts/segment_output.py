#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动分段执行器
功能：在回复前自动检测长度并分段，然后连续输出
使用方式：将内容通过管道传入，或作为参数
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

def output_with_segments(content, title="内容"):
    """分段输出内容，主动连续输出所有分段"""
    segments = split_content(content)
    total = len(segments)
    
    if total == 1:
        # 不需要分段，直接输出
        print(content)
    else:
        # 需要分段，连续输出所有分段
        for i, segment in enumerate(segments, 1):
            # 输出段标记
            print(f"\n## 📋 {title}（第{i}段/共{total}段）\n", file=sys.stderr)
            # 输出内容
            print(segment)
            # 段间分隔
            if i < total:
                print("\n---\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 从命令行参数读取
        content = ' '.join(sys.argv[1:])
        output_with_segments(content)
    else:
        # 从 stdin 读取
        content = sys.stdin.read()
        output_with_segments(content)

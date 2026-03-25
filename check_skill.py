#!/usr/bin/env python3
"""
检查 auto-redbook-skills 技能
"""
import os
import sys
import subprocess

print("="*80)
print("🔍 深度排查 auto-redbook-skills")
print("="*80)
print()

# 1. 检查技能目录
skills_dir = "skills/auto-redbook-skills"
print(f"【1】技能目录：{skills_dir}")
print("-"*80)

result = subprocess.run(['ls', '-la', skills_dir], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print(f"错误：{result.stderr}")

print()

# 2. 检查 clawhub 注册
print("【2】clawhub 注册状态")
print("-"*80)

result = subprocess.run(['clawhub', 'list'], capture_output=True, text=True)
print("已安装技能:")
for line in result.stdout.split('\n'):
    if 'redbook' in line.lower() or 'xiao' in line.lower():
        print(f"  ✅ {line}")

print()

# 3. 检查技能元数据
print("【3】技能元数据")
print("-"*80)

for meta_file in ['SKILL.md', 'manifest.json', 'package.json', 'config.json']:
    filepath = os.path.join(skills_dir, meta_file)
    if os.path.exists(filepath):
        print(f"✅ {meta_file} 存在")
        with open(filepath, 'r') as f:
            content = f.read()
            print(f"   大小：{len(content)} bytes")
            print(f"   内容预览：{content[:200]}")
    else:
        print(f"❌ {meta_file} 不存在")

print()

# 4. 检查 Python 入口
print("【4】Python 入口文件")
print("-"*80)

for entry_file in ['main.py', 'app.py', 'index.py', '__init__.py']:
    filepath = os.path.join(skills_dir, entry_file)
    if os.path.exists(filepath):
        print(f"✅ {entry_file} 存在")
        with open(filepath, 'r') as f:
            content = f.read()
            # 查找函数定义
            import re
            functions = re.findall(r'def\s+(\w+)\s*\(', content)
            if functions:
                print(f"   函数：{functions}")
            # 查找类定义
            classes = re.findall(r'class\s+(\w+)', content)
            if classes:
                print(f"   类：{classes}")
    else:
        print(f"❌ {entry_file} 不存在")

print()
print("="*80)

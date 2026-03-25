#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
印象笔记整理工具
功能：查看笔记统计、整理笔记、清理重复等
"""

import os
from evernote.api.client import EvernoteClient
from evernote.edam.notebook import NotebookStore
from evernote.edam import Type
from evernote.edam import NoteStore

# 配置
DEV_TOKEN = "S=s15:U=11e96c2:E=19d1ee95de7:C=19cfadcd758:P=1cd:A=en-devtoken:V=2:H=892f7ae73aa431f36a1680ac02734a46"
SANDBOX = False  # False = 生产环境（印象笔记中国）

def connect():
    """连接印象笔记"""
    if SANDBOX:
        client = EvernoteClient(token=DEV_TOKEN, sandbox=True)
    else:
        # 印象笔记中国（yinxiang.com）
        client = EvernoteClient(
            token=DEV_TOKEN,
            service_url="https://app.yinxiang.com"
        )
    return client

def get_notebook_stats(client):
    """获取笔记本统计"""
    note_store = client.get_note_store()
    notebooks = note_store.listNotebooks()
    
    print("=" * 60)
    print("📚 笔记本统计")
    print("=" * 60)
    
    total_notes = 0
    for notebook in notebooks:
        # 计算每个笔记本的笔记数
        filter = NoteFilter(notebookGuid=notebook.guid)
        spec = NotesMetadataResultSpec(title=True)
        result = note_store.findNotesMetadata(filter, 0, 1000, spec)
        count = result.totalNotes
        
        print(f"\n📓 {notebook.name}")
        print(f"   笔记数：{count}")
        print(f"   默认：{'✅' if notebook.defaultNotebook else '❌'}")
        print(f"   栈：{notebook.stack or '无'}")
        
        total_notes += count
    
    print("\n" + "=" * 60)
    print(f"📊 总计：{len(notebooks)} 个笔记本，{total_notes} 篇笔记")
    print("=" * 60)
    
    return notebooks

def get_all_notes_metadata(client):
    """获取所有笔记的元数据"""
    note_store = client.get_note_store()
    notebooks = note_store.listNotebooks()
    
    all_notes = []
    for notebook in notebooks:
        filter = NoteFilter(notebookGuid=notebook.guid)
        spec = NotesMetadataResultSpec(title=True, created=True, updated=True, tagGuids=True)
        
        # 分页获取
        start = 0
        count = 50
        while True:
            result = note_store.findNotesMetadata(filter, start, count, spec)
            for note_meta in result.notes:
                all_notes.append({
                    'title': note_meta.title,
                    'created': note_meta.created,
                    'updated': note_meta.updated,
                    'notebook': notebook.name,
                    'notebook_guid': notebook.guid,
                    'guid': note_meta.guid,
                    'tags': note_meta.tagGuids or []
                })
            
            if len(result.notes) < count:
                break
            start += count
    
    return all_notes

def analyze_notes(notes):
    """分析笔记"""
    print("\n" + "=" * 60)
    print("📈 笔记分析")
    print("=" * 60)
    
    # 按创建年份统计
    from datetime import datetime
    year_stats = {}
    for note in notes:
        year = datetime.fromtimestamp(note['created'] / 1000).year
        year_stats[year] = year_stats.get(year, 0) + 1
    
    print("\n📅 按年份统计:")
    for year in sorted(year_stats.keys()):
        print(f"   {year}年：{year_stats[year]} 篇")
    
    # 按笔记本统计
    notebook_stats = {}
    for note in notes:
        nb = note['notebook']
        notebook_stats[nb] = notebook_stats.get(nb, 0) + 1
    
    print("\n📓 按笔记本统计（Top 10）:")
    sorted_nbs = sorted(notebook_stats.items(), key=lambda x: x[1], reverse=True)[:10]
    for nb, count in sorted_nbs:
        print(f"   {nb}: {count} 篇")
    
    # 最近更新的笔记
    print("\n🕒 最近更新的笔记（Top 10）:")
    sorted_notes = sorted(notes, key=lambda x: x['updated'], reverse=True)[:10]
    for note in sorted_notes:
        date = datetime.fromtimestamp(note['updated'] / 1000).strftime('%Y-%m-%d')
        print(f"   [{date}] {note['title'][:40]}")

def main():
    print("🚀 连接印象笔记...")
    try:
        client = connect()
        user_store = client.get_user_store()
        user = user_store.getUser()
        print(f"✅ 连接成功！用户：{user.username}")
        print()
        
        # 获取笔记本统计
        notebooks = get_notebook_stats(client)
        
        # 获取所有笔记
        print("\n📝 获取所有笔记元数据...")
        notes = get_all_notes_metadata(client)
        print(f"✅ 获取到 {len(notes)} 篇笔记")
        
        # 分析笔记
        analyze_notes(notes)
        
        # 保存分析结果
        import json
        from datetime import datetime
        output_file = f"/Users/yangbowen/.openclaw/workspace/logs/evernote_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(notes, f, ensure_ascii=False, indent=2)
        print(f"\n💾 分析结果已保存到：{output_file}")
        
    except Exception as e:
        print(f"❌ 错误：{e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
印象笔记整理工具 - 简化版
使用 evernote SDK 连接印象笔记
"""

import sys
import json
from datetime import datetime

# 尝试导入
try:
    from evernote.api.client import EvernoteClient
    print("✅ SDK 导入成功")
except Exception as e:
    print(f"❌ SDK 导入失败：{e}")
    print("请运行：pip3 install evernote3 --break-system-packages")
    sys.exit(1)

# 配置
DEV_TOKEN = "S=s15:U=11e96c2:E=19d1ee95de7:C=19cfadcd758:P=1cd:A=en-devtoken:V=2:H=892f7ae73aa431f36a1680ac02734a46"

def main():
    print("🚀 连接印象笔记...")
    
    try:
        # 连接印象笔记中国
        client = EvernoteClient(
            token=DEV_TOKEN,
            service_url="https://app.yinxiang.com"
        )
        
        # 获取用户信息
        user_store = client.get_user_store()
        user = user_store.getUser()
        print(f"✅ 连接成功！用户：{user.username}")
        print(f"   邮箱：{user.email}")
        print()
        
        # 获取笔记本列表
        note_store = client.get_note_store()
        notebooks = note_store.listNotebooks()
        
        print("=" * 60)
        print("📚 笔记本统计")
        print("=" * 60)
        
        total_notes = 0
        notebook_info = []
        
        for notebook in notebooks:
            # 计算每个笔记本的笔记数
            note_filter = type('NoteFilter', (), {'notebookGuid': notebook.guid})()
            
            # 简单获取笔记列表
            notes_metadata = note_store.findNotesMetadata(
                type('NoteFilter', (), {'notebookGuid': notebook.guid})(),
                0, 1000,
                type('NotesMetadataResultSpec', (), {'title': True})()
            )
            
            count = notes_metadata.totalNotes if hasattr(notes_metadata, 'totalNotes') else len(notes_metadata.notes)
            
            print(f"\n📓 {notebook.name}")
            print(f"   笔记数：{count}")
            print(f"   默认：{'✅' if notebook.defaultNotebook else '❌'}")
            print(f"   栈：{notebook.stack or '无'}")
            
            notebook_info.append({
                'name': notebook.name,
                'guid': notebook.guid,
                'note_count': count,
                'default': notebook.defaultNotebook,
                'stack': notebook.stack
            })
            
            total_notes += count
        
        print("\n" + "=" * 60)
        print(f"📊 总计：{len(notebooks)} 个笔记本，{total_notes} 篇笔记")
        print("=" * 60)
        
        # 保存结果
        output_file = f"/Users/yangbowen/.openclaw/workspace/logs/evernote_notebooks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'user': user.username,
                'total_notebooks': len(notebooks),
                'total_notes': total_notes,
                'notebooks': notebook_info
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 结果已保存到：{output_file}")
        
    except Exception as e:
        print(f"❌ 错误：{e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

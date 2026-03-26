#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书路由配置恢复脚本
用途：当配置隔天丢失时，一键恢复到正确状态
执行：python3 ~/.openclaw/workspace/scripts/restore-feishu-routing.py
"""

import json
import os
import subprocess
from pathlib import Path

def restore_routing():
    """恢复飞书路由配置"""
    print("="*60)
    print("🔄 恢复飞书路由配置")
    print("="*60)
    
    config_path = Path.home() / ".openclaw" / "openclaw.json"
    
    if not config_path.exists():
        print(f"❌ 配置文件不存在：{config_path}")
        return False
    
    # 读取配置
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 修改路由配置
    print("\n📝 修改配置...")
    config['channels']['feishu']['defaultAccount'] = 'ppt'
    config['channels']['feishu']['accounts']['main']['denyFrom'] = ['ou_f0bca70240c4b15bb89772262865b63e']
    config['channels']['feishu']['accounts']['ppt']['allowFrom'] = ['ou_f0bca70240c4b15bb89772262865b63e']
    
    # 保存配置
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("✅ 配置已保存到：", config_path)
    
    # 重启 Gateway
    print("\n🔄 重启 Gateway...")
    result = subprocess.run(['openclaw', 'gateway', 'restart'], capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Gateway 重启成功")
    else:
        print("⚠️ Gateway 重启失败，请手动执行：openclaw gateway restart")
    
    # 验证配置
    print("\n🧪 验证配置...")
    with open(config_path, 'r', encoding='utf-8') as f:
        new_config = json.load(f)
    
    default = new_config['channels']['feishu'].get('defaultAccount')
    if default == 'ppt':
        print("✅ defaultAccount = ppt ✓")
    else:
        print(f"❌ defaultAccount = {default} ✗")
    
    print("\n" + "="*60)
    print("✅ 配置恢复完成！")
    print("="*60)
    print("\n📋 路由规则：")
    print("  - ou_f0bca70240c4b15bb89772262865b63e → ppt agent")
    print("  - ou_a040d98b29a237916317887806d655de → main agent")
    print("\n💡 提示：发送一条新消息验证路由是否正确")
    
    return True

if __name__ == "__main__":
    restore_routing()

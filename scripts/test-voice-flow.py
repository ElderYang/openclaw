#!/usr/bin/env python3
"""
语音消息处理完整流程测试脚本
用法：python3 test-voice-flow.py
"""

import json
import requests
import subprocess
import sys
from pathlib import Path

# ========== 配置 ==========
FEISHU_APP_ID = 'cli_a923ffd1e2f95cb2'
FEISHU_APP_SECRET = 'wbUuXVa7aIy96JDguHt3gdvlT4Kpp6aV'
FEISHU_USER_ID = 'ou_a040d98b29a237916317887806d655de'
STT_SERVICE_URL = "http://127.0.0.1:18790/transcribe"

def test_stt_service():
    """测试 STT 服务"""
    print("\n【1】测试 STT 服务...")
    
    # 检查服务是否运行
    try:
        resp = requests.options(STT_SERVICE_URL, timeout=5)
        if resp.status_code == 204:
            print("   ✅ STT 服务正常运行")
            return True
        else:
            print(f"   ❌ STT 服务异常：{resp.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ STT 服务无法连接：{e}")
        return False

def test_tts():
    """测试 TTS（macOS say）"""
    print("\n【2】测试 TTS...")
    
    try:
        # 生成测试语音
        test_file = '/tmp/voice_test.aiff'
        subprocess.run(['say', '-v', 'Ting-Ting', '-o', test_file, '测试语音'], 
                      capture_output=True, check=True)
        
        # 转换为 MP3
        mp3_file = '/tmp/voice_test.mp3'
        subprocess.run(['ffmpeg', '-i', test_file, '-y', '-acodec', 'libmp3lame', '-ab', '64k', mp3_file],
                      capture_output=True, check=True)
        
        # 清理
        subprocess.run(['rm', '-f', test_file, mp3_file], capture_output=True)
        
        print("   ✅ TTS 正常")
        return True
    except Exception as e:
        print(f"   ❌ TTS 异常：{e}")
        return False

def test_feishu_token():
    """测试飞书 Token 获取"""
    print("\n【3】测试飞书 Token...")
    
    try:
        token_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        resp = requests.post(token_url, json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET})
        token = resp.json().get('tenant_access_token', '')
        
        if token:
            print(f"   ✅ Token 获取成功：{token[:20]}...")
            return token
        else:
            print(f"   ❌ Token 获取失败：{resp.json()}")
            return None
    except Exception as e:
        print(f"   ❌ Token 获取异常：{e}")
        return None

def test_feishu_upload(token):
    """测试飞书文件上传"""
    print("\n【4】测试飞书文件上传...")
    
    try:
        # 创建测试文件
        test_file = '/tmp/upload_test.mp3'
        subprocess.run(['say', '-v', 'Ting-Ting', '-o', '/tmp/test.aiff', '测试'], capture_output=True)
        subprocess.run(['ffmpeg', '-i', '/tmp/test.aiff', '-y', '-acodec', 'libmp3lame', '-ab', '64k', test_file],
                      capture_output=True)
        
        # 上传
        file_url = "https://open.feishu.cn/open-apis/im/v1/files"
        with open(test_file, 'rb') as f:
            files = {'file': ('test.opus', f, 'audio/ogg')}
            data = {'file_type': 'opus'}
            resp = requests.post(file_url, headers={'Authorization': f'Bearer {token}'}, files=files, data=data)
        
        # 清理
        subprocess.run(['rm', '-f', test_file, '/tmp/test.aiff'], capture_output=True)
        
        if resp.status_code == 200:
            file_key = resp.json().get('data', {}).get('file_key', '')
            if file_key:
                print(f"   ✅ 文件上传成功：{file_key}")
                return True
        
        print(f"   ❌ 文件上传失败：{resp.json()}")
        return False
    except Exception as e:
        print(f"   ❌ 文件上传异常：{e}")
        return False

def test_feishu_voice_send(token):
    """测试飞书语音消息发送"""
    print("\n【5】测试飞书语音消息发送...")
    
    try:
        # 生成测试语音
        test_file = '/tmp/voice_send_test.mp3'
        subprocess.run(['say', '-v', 'Ting-Ting', '-o', '/tmp/test.aiff', '这是测试语音消息'], capture_output=True)
        subprocess.run(['ffmpeg', '-i', '/tmp/test.aiff', '-y', '-acodec', 'libmp3lame', '-ab', '64k', test_file],
                      capture_output=True)
        
        # 上传
        file_url = "https://open.feishu.cn/open-apis/im/v1/files"
        with open(test_file, 'rb') as f:
            files = {'file': ('test.opus', f, 'audio/ogg')}
            data = {'file_type': 'opus'}
            upload_resp = requests.post(file_url, headers={'Authorization': f'Bearer {token}'}, files=files, data=data)
        
        file_key = upload_resp.json().get('data', {}).get('file_key', '')
        
        # 发送
        message_url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id"
        content = json.dumps({"file_key": file_key, "duration": 5})
        payload = {
            "receive_id": FEISHU_USER_ID,
            "msg_type": "audio",
            "content": content
        }
        
        send_resp = requests.post(message_url, json=payload, headers={'Authorization': f'Bearer {token}'})
        
        # 清理
        subprocess.run(['rm', '-f', test_file, '/tmp/test.aiff'], capture_output=True)
        
        if send_resp.json().get('code') == 0:
            print("   ✅ 语音消息发送成功")
            return True
        else:
            print(f"   ❌ 语音消息发送失败：{send_resp.json()}")
            return False
    except Exception as e:
        print(f"   ❌ 语音消息发送异常：{e}")
        return False

def main():
    """主测试流程"""
    print("="*60)
    print("🎙️ 语音消息处理流程测试")
    print("="*60)
    
    results = []
    
    # 1. STT 服务
    results.append(("STT 服务", test_stt_service()))
    
    # 2. TTS
    results.append(("TTS", test_tts()))
    
    # 3. 飞书 Token
    token = test_feishu_token()
    results.append(("飞书 Token", token is not None))
    
    if token:
        # 4. 飞书上传
        results.append(("飞书上传", test_feishu_upload(token)))
        
        # 5. 飞书语音发送
        results.append(("飞书语音发送", test_feishu_voice_send(token)))
    
    # 输出总结
    print("\n" + "="*60)
    print("📊 测试结果总结")
    print("="*60)
    
    all_passed = True
    for name, passed in results:
        status = "✅" if passed else "❌"
        print(f"{status} {name}")
        if not passed:
            all_passed = False
    
    print("="*60)
    if all_passed:
        print("✅ 所有测试通过！语音功能正常")
        return 0
    else:
        print("❌ 部分测试失败，请检查配置")
        return 1

if __name__ == '__main__':
    sys.exit(main())

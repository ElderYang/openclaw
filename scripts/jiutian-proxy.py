#!/usr/bin/env python3
"""
九天大模型 OpenAI 兼容代理服务器
将 OpenAI API 格式转换为九天大模型的 JSON-RPC 2.0 格式
"""

from flask import Flask, request, jsonify, Response
import requests
import json
import uuid
import sys

app = Flask(__name__)

# 九天大模型配置
JIUTIAN_BASE_URL = "https://jiutian.10086.cn/largemodel/moma/api/v1"
JIUTIAN_API_KEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhcGlfa2V5IjoiNjljZjgwMTIwOWFkYzU5ZTQ0Mjc0Yjk5IiwiZXhwIjoxODU1NDQzNjIzMDcyODEsInRpbWVzdGFtcCI6MTc3NTIwNjQ4MX0.jh9LWQHbvBpkK67A5IdmJqyC3ENcqOeglo6eztFaF0c"
ROUTER_CONFIG_ID = "693bb7a496b16a338f70b576"

def convert_to_jsonrpc(messages, stream=False):
    """将 OpenAI 消息格式转换为九天大模型 JSON-RPC 2.0 格式"""
    # 合并所有用户消息
    full_text = ""
    for msg in messages:
        role = msg.get('role', 'user')
        content = msg.get('content', '')
        if isinstance(content, list):
            # 处理多模态内容
            for part in content:
                if part.get('type') == 'text':
                    full_text += part.get('text', '') + "\n"
        else:
            full_text += f"[{role}] {content}\n"
    
    return {
        "id": str(uuid.uuid4()),
        "jsonrpc": "2.0",
        "method": "message/send",
        "params": {
            "id": str(uuid.uuid4()),
            "message": {
                "messageId": str(uuid.uuid4()),
                "parts": [
                    {
                        "kind": "text",
                        "text": full_text.strip()
                    }
                ]
            },
            "routerConfigId": ROUTER_CONFIG_ID
        }
    }

def parse_stream_response(response_text):
    """解析九天大模型的 SSE 流式响应"""
    for line in response_text.split('\n'):
        if line.startswith('data:'):
            try:
                data = json.loads(line[5:])
                yield data
            except:
                continue

@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "service": "jiutian-proxy",
        "version": "1.0.0"
    })

@app.route('/v1/models', methods=['GET'])
def list_models():
    """返回模型列表（OpenAI 兼容格式）"""
    return jsonify({
        "object": "list",
        "data": [
            {
                "id": "moma-stream",
                "object": "model",
                "created": 1775206481,
                "owned_by": "jiutian",
                "permission": [],
                "root": "moma-stream",
                "parent": None
            }
        ]
    })

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    """聊天补全接口（OpenAI 兼容格式）"""
    try:
        data = request.json
        messages = data.get('messages', [])
        stream = data.get('stream', False)
        max_tokens = data.get('max_tokens', 4096)
        
        # 转换为九天大模型格式
        jsonrpc_payload = convert_to_jsonrpc(messages, stream)
        
        headers = {
            "Authorization": f"Bearer {JIUTIAN_API_KEY}",
            "Content-Type": "application/json"
        }
        
        url = f"{JIUTIAN_BASE_URL}/moma/message/stream"
        
        # 调用九天大模型 API
        response = requests.post(
            url,
            headers=headers,
            json=jsonrpc_payload,
            timeout=120,
            stream=True
        )
        
        if response.status_code != 200:
            return jsonify({
                "error": {
                    "message": f"九天大模型 API 错误：{response.status_code}",
                    "type": "api_error",
                    "code": response.status_code
                }
            }), response.status_code
        
        if stream:
            # 流式响应
            def generate():
                chunk_id = str(uuid.uuid4())
                for line in response.iter_lines():
                    if line and line.startswith(b'data:'):
                        try:
                            data = json.loads(line[5:].decode('utf-8'))
                            
                            # 解析九天大模型的响应
                            if 'result' in data:
                                result = data['result']
                                
                                # 检查是否有内容
                                if result.get('artifact'):
                                    parts = result['artifact'].get('parts', [])
                                    content = ""
                                    for part in parts:
                                        if part.get('kind') == 'text':
                                            content += part.get('text', '')
                                    
                                    if content:
                                        openai_chunk = {
                                            "id": chunk_id,
                                            "object": "chat.completion.chunk",
                                            "created": 1775206481,
                                            "model": "moma-stream",
                                            "choices": [
                                                {
                                                    "index": 0,
                                                    "delta": {
                                                        "content": content
                                                    },
                                                    "finish_reason": None
                                                }
                                            ]
                                        }
                                        yield f"data: {json.dumps(openai_chunk)}\n\n"
                                
                                # 检查是否结束
                                if result.get('status', {}).get('state') == 'completed':
                                    openai_chunk = {
                                        "id": chunk_id,
                                        "object": "chat.completion.chunk",
                                        "created": 1775206481,
                                        "model": "moma-stream",
                                        "choices": [
                                            {
                                                "index": 0,
                                                "delta": {},
                                                "finish_reason": "stop"
                                            }
                                        ]
                                    }
                                    yield f"data: {json.dumps(openai_chunk)}\n\n"
                                    yield "data: [DONE]\n\n"
                                    break
                                    
                        except Exception as e:
                            print(f"解析错误：{e}", file=sys.stderr)
                            continue
            
            return Response(generate(), mimetype='text/event-stream')
        else:
            # 非流式响应 - 等待完整响应
            full_content = ""
            for line in response.iter_lines():
                if line and line.startswith(b'data:'):
                    try:
                        data = json.loads(line[5:].decode('utf-8'))
                        if 'result' in data:
                            result = data['result']
                            if result.get('artifact'):
                                parts = result['artifact'].get('parts', [])
                                for part in parts:
                                    if part.get('kind') == 'text':
                                        full_content += part.get('text', '')
                    except:
                        continue
            
            return jsonify({
                "id": str(uuid.uuid4()),
                "object": "chat.completion",
                "created": 1775206481,
                "model": "moma-stream",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": full_content
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
            })
            
    except Exception as e:
        print(f"错误：{e}", file=sys.stderr)
        return jsonify({
            "error": {
                "message": str(e),
                "type": "server_error",
                "code": 500
            }
        }), 500

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='九天大模型 OpenAI 兼容代理')
    parser.add_argument('--port', type=int, default=5000, help='监听端口 (默认：5000)')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='监听地址 (默认：127.0.0.1)')
    parser.add_argument('--debug', action='store_true', help='调试模式')
    
    args = parser.parse_args()
    
    print(f"🚀 启动九天大模型代理服务器...")
    print(f"   监听地址：http://{args.host}:{args.port}")
    print(f"   健康检查：http://{args.host}:{args.port}/health")
    print(f"   API 端点：http://{args.host}:{args.port}/v1/chat/completions")
    print(f"\n在 OpenClaw 中配置:")
    print(f'''
  "models": {{
    "providers": {{
      "jiutian-moma": {{
        "baseUrl": "http://{args.host}:{args.port}",
        "apiKey": "jiutian-proxy",
        "api": "openai-completions",
        "models": [
          {{
            "id": "moma-stream",
            "name": "九天大模型 (流式)",
            "contextWindow": 32000,
            "maxTokens": 4096
          }}
        ]
      }}
    }}
  }}
''')
    
    app.run(host=args.host, port=args.port, debug=args.debug, threaded=True)

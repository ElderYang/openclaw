#!/bin/bash
# 语音消息处理服务启动脚本
# 用法：./start-voice-services.sh

set -e

echo "🎙️ 启动语音消息处理服务..."

# 1. 检查并启动 STT 服务
echo "1. 检查 STT 服务..."
if ps aux | grep -q "[t]ranscribe-server.py"; then
    echo "   ✅ STT 服务已运行"
else
    echo "   ⚠️  启动 STT 服务..."
    cd /Users/yangbowen/.openclaw/workspace/voice-input
    nohup /opt/homebrew/bin/python3 transcribe-server.py > /tmp/openclaw/transcribe.log 2>&1 &
    sleep 3
    
    if curl -s http://127.0.0.1:18790/transcribe -X OPTIONS > /dev/null 2>&1; then
        echo "   ✅ STT 服务已启动"
    else
        echo "   ❌ STT 服务启动失败"
        exit 1
    fi
fi

# 2. 检查必要工具
echo "2. 检查必要工具..."
for cmd in say ffmpeg; do
    if which $cmd > /dev/null 2>&1; then
        echo "   ✅ $cmd 已安装"
    else
        echo "   ❌ $cmd 未安装"
        exit 1
    fi
done

# 3. 测试 TTS
echo "3. 测试 TTS..."
if say -v Ting-Ting "测试" -o /tmp/voice_test.aiff 2>/dev/null; then
    echo "   ✅ TTS 正常"
    rm -f /tmp/voice_test.aiff
else
    echo "   ❌ TTS 异常"
    exit 1
fi

# 4. 检查飞书配置
echo "4. 检查飞书配置..."
if [ -f /Users/yangbowen/.openclaw/openclaw.json ]; then
    echo "   ✅ 配置文件存在"
else
    echo "   ❌ 配置文件不存在"
    exit 1
fi

echo ""
echo "✅ 所有语音服务已就绪！"
echo ""
echo "📋 快速测试命令:"
echo "   # 测试 STT"
echo "   curl -X POST http://127.0.0.1:18790/transcribe -H 'Content-Type: audio/ogg' --data-binary @test.ogg"
echo ""
echo "   # 测试 TTS"
echo "   say -v Ting-Ting '你好' -o test.aiff && ffmpeg -i test.aiff test.mp3"
echo ""
echo "   # 查看日志"
echo "   tail -f /tmp/openclaw/transcribe.log"

# MLX-Audio TTS 部署指南

**性能**: 1.34秒 vs Docker CPU 的 39秒（**29倍加速**！）

---

## 🎉 测试验证

### 实际性能测试

```bash
# MLX-Audio GPU 版本
curl -X POST 'http://localhost:7861/api/tts' \
  -G --data-urlencode 'text=你好世界' \
  --data 'speed=1.0' --data 'speaker=Vivian' \
  -o test.wav

结果:
✅ HTTP 200 OK
⏱️  生成耗时: 1.34秒
📊 文件大小: 71KB (73004 bytes)
📊 音频格式: WAVE audio, 16 bit, mono 24000 Hz
🚀 实时率: 1.13x (超过实时！)
```

**对比 Docker CPU 版本（39 秒）**:
- **加速比: 29x**
- **超时设置可以从 90 秒降到 10 秒**
- **用户体验: 从"等待很久"到"几乎即时"**

---

## 📦 完整部署步骤

### 步骤 1: 停止 Docker 版本（可选）

如果你想完全替换 Docker 版本:

```bash
cd ~/docker/qwen3-tts
docker compose down
```

或者保留 Docker 作为备份，使用不同端口运行 MLX 版本。

### 步骤 2: 使用现有虚拟环境

MLX 服务器已经准备就绪:

```bash
cd ~/docker/qwen3-tts
source mlx-test-venv/bin/activate

# 检查依赖（应该都已安装）
pip list | grep -E "(mlx|fastapi|uvicorn|soundfile)"
```

### 步骤 3: 启动 MLX 服务器

#### 方式 A: 前台运行（用于测试）

```bash
cd ~/docker/qwen3-tts
source mlx-test-venv/bin/activate
python mlx-server.py
```

#### 方式 B: 后台运行（推荐）

```bash
cd ~/docker/qwen3-tts
source mlx-test-venv/bin/activate
nohup python mlx-server.py > /tmp/mlx-server.log 2>&1 &
echo $! > /tmp/mlx-server.pid
```

检查运行状态:
```bash
tail -f /tmp/mlx-server.log
curl http://localhost:7861/health
```

停止服务器:
```bash
kill $(cat /tmp/mlx-server.pid)
rm /tmp/mlx-server.pid
```

### 步骤 4: 测试 MLX 服务器

```bash
# 健康检查
curl http://localhost:7861/health | python3 -m json.tool

# TTS 测试
curl -X POST 'http://localhost:7861/api/tts' \
  -G --data-urlencode 'text=测试文本' \
  --data 'speed=1.0' --data 'speaker=Vivian' \
  -o /tmp/test.wav

# 播放测试
afplay /tmp/test.wav
```

### 步骤 5: 修改 Home Assistant 集成

在 Home Assistant 服务器上修改配置:

```bash
ssh root@192.168.20.76

# 编辑 TTS 配置
vi /config/custom_components/qwen3_tts/tts.py
```

**修改内容**:

1. **修改默认端口**（第 25 行左右）:
```python
# 原来:
DEFAULT_BASE_URL = "http://192.168.20.99:7860"

# 修改为:
DEFAULT_BASE_URL = "http://192.168.20.99:7861"
```

2. **减少超时时间**（第 130 行左右）:
```python
# 原来:
async with asyncio.timeout(90):

# 修改为:
async with asyncio.timeout(10):  # MLX 版本更快，10 秒足够
```

保存文件后重启 Home Assistant:
```bash
ha core restart
```

### 步骤 6: 在 HA 中测试

打开 Home Assistant → 开发者工具 → 动作

```yaml
service: tts.speak
target:
  entity_id: tts.qwen3_tts
data:
  media_player_entity_id: media_player.客厅小爱音箱
  message: "你好世界"
```

**预期结果**:
- 之前: 39-66 秒（可能超时）
- 现在: **1-3 秒**（接近即时）

---

## 🔧 开机自启动配置

### 方式 A: launchd (macOS 推荐)

创建 `~/Library/LaunchAgents/com.qwen3tts.mlx.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.qwen3tts.mlx</string>

    <key>ProgramArguments</key>
    <array>
        <string>/Users/nichomelab/docker/qwen3-tts/mlx-test-venv/bin/python</string>
        <string>/Users/nichomelab/docker/qwen3-tts/mlx-server.py</string>
    </array>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>

    <key>StandardOutPath</key>
    <string>/tmp/qwen3-tts-mlx.log</string>

    <key>StandardErrorPath</key>
    <string>/tmp/qwen3-tts-mlx-error.log</string>

    <key>WorkingDirectory</key>
    <string>/Users/nichomelab/docker/qwen3-tts</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
</dict>
</plist>
```

加载服务:
```bash
launchctl load ~/Library/LaunchAgents/com.qwen3tts.mlx.plist
launchctl start com.qwen3tts.mlx
```

查看状态:
```bash
launchctl list | grep qwen3tts
tail -f /tmp/qwen3-tts-mlx.log
```

卸载服务:
```bash
launchctl unload ~/Library/LaunchAgents/com.qwen3tts.mlx.plist
```

### 方式 B: 简单的 shell 脚本

创建 `~/docker/qwen3-tts/start-mlx-server.sh`:

```bash
#!/bin/bash
cd /Users/nichomelab/docker/qwen3-tts
source mlx-test-venv/bin/activate
python mlx-server.py > /tmp/mlx-server.log 2>&1 &
echo $! > /tmp/mlx-server.pid
echo "MLX TTS Server started with PID $(cat /tmp/mlx-server.pid)"
```

给予执行权限:
```bash
chmod +x ~/docker/qwen3-tts/start-mlx-server.sh
```

使用:
```bash
~/docker/qwen3-tts/start-mlx-server.sh
```

---

## 📊 性能监控

### 查看服务器日志

```bash
tail -f /tmp/mlx-server.log
```

日志示例:
```
2026-01-26 09:10:25,219 - INFO - 📝 TTS 请求: 你好世界 (speaker=Vivian, speed=1.0, language=Chinese)
2026-01-26 09:10:26,560 - INFO - ✅ 语音生成完成，耗时: 1.34s (音频时长: 1.52s, 实时率: 1.13x)
```

### HTTP 响应头

MLX 服务器在响应头中包含性能指标:

```bash
curl -I -X POST 'http://localhost:7861/api/tts?text=test&speaker=Vivian&speed=1.0'
```

响应头包含:
```
X-Generation-Time: 1.34
X-Audio-Duration: 1.52
X-Realtime-Factor: 1.13
```

---

## 🔍 故障排查

### 问题 1: 端口冲突

**症状**: `Address already in use`

**解决方案**:
```bash
# 检查端口占用
lsof -i :7861

# 方式 A: 杀死旧进程
kill $(lsof -t -i:7861)

# 方式 B: 修改端口
# 编辑 mlx-server.py，将 port=7861 改为其他端口
```

### 问题 2: 模型加载失败

**症状**: `Model not loaded`

**解决方案**:
```bash
# 检查虚拟环境
source mlx-test-venv/bin/activate
python -c "from mlx_audio.tts import load; print('OK')"

# 清除缓存重新下载
rm -rf ~/.cache/huggingface/hub/models--Qwen--Qwen3-TTS*
```

### 问题 3: GPU 不可用

**症状**: `metal_gpu: false`

**检查 GPU**:
```bash
source mlx-test-venv/bin/activate
python -c "import mlx.core as mx; print(f'Metal GPU: {mx.metal.is_available()}')"
```

如果返回 False，说明不在 Apple Silicon Mac 上。

### 问题 4: Home Assistant 无法连接

**检查网络连通性**:
```bash
# 在 HA 服务器上测试
ssh root@192.168.20.76
curl http://192.168.20.99:7861/health
```

**检查防火墙**:
```bash
# Mac 上检查防火墙
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
```

---

## 📈 性能对比总结

| 指标 | Docker CPU | MLX GPU | 改进 |
|-----|-----------|---------|-----|
| 短文本 (4字) | 39秒 | **1.34秒** | **29x** ⚡ |
| 中等文本 (13字) | ~50秒 | **3.42秒** | **15x** ⚡ |
| 长文本 (35字) | 66秒 | **6.96秒** | **9.5x** ⚡ |
| 超时设置 | 90秒 | **10秒** | 大幅减少 ✅ |
| 实时率 | 0.1x | **1.13x** | 超过实时 🚀 |
| GPU 使用 | ❌ | ✅ Metal | 完全激活 |
| 用户体验 | 慢 | **接近即时** | 极大提升 🎉 |

---

## ✅ 推荐配置

### 最佳实践

1. **使用 launchd 开机自启**: 稳定可靠
2. **保留 Docker 作为备份**: 两个端口同时运行（7860 和 7861）
3. **监控日志**: 定期检查 `/tmp/mlx-server.log`
4. **定期更新**: `pip install --upgrade mlx mlx-audio`

### HA 集成配置

```yaml
# configuration.yaml（可选，使用 UI 配置更方便）
tts:
  - platform: qwen3_tts
    base_url: "http://192.168.20.99:7861"
    timeout: 10
```

---

## 📚 相关文档

- [MLX-Audio 成功报告](./mlx-audio-success-report.md) - 详细测试数据
- [HA TTS 故障排查](./ha-tts-troubleshooting.md) - 之前的问题诊断
- [Qwen3-TTS MPS 尝试报告](./qwen3-tts-mps-gpu-attempt.md) - 为什么 PyTorch MPS 失败

---

**部署时间**: 2026-01-26
**状态**: ✅ 生产就绪
**推荐程度**: ⭐⭐⭐⭐⭐ 强烈推荐立即部署

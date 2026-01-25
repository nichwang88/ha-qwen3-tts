# Qwen3 TTS Integration

![Qwen3 TTS Logo](https://raw.githubusercontent.com/nichwang88/ha-qwen3-tts/main/assets/logo.png)

阿里巴巴千问 TTS（Qwen3-TTS）的 Home Assistant 集成，提供高质量本地语音合成服务。

## 特性

- 🎯 **完全本地化** - 无需联网，保护隐私
- 🌍 **多语言支持** - 中文、英文、日语、韩语等 10 种语言
- 🎭 **声音克隆** - 支持自定义音色样本
- ⚡ **超低延迟** - 端到端延迟低至 97ms
- 🎚️ **可调语速** - 0.5-2.0 倍速自由调节
- 🔧 **UI 配置** - 通过界面轻松配置，无需 YAML

## 快速开始

### 1. 部署 Qwen3 TTS 服务器

如果还没有运行 Qwen3 TTS 服务器，请先部署：

```bash
# 使用 Docker 快速部署
docker run -d \
  --name qwen3-tts \
  --gpus all \
  -p 7860:7860 \
  -v ~/qwen3-models:/root/.cache/huggingface \
  your-qwen3-tts-image
```

或参考完整部署指南：[Qwen3 TTS 部署文档](https://github.com/nichwang88/qwen3-tts-docker)

### 2. 安装集成

通过 HACS 或手动安装本集成。

### 3. 配置集成

1. 进入 **设置** → **设备与服务**
2. 点击 **+ 添加集成**
3. 搜索 "**Qwen3 TTS**"
4. 输入服务器地址和端口
5. 完成配置

### 4. 使用 TTS

```yaml
service: tts.speak
target:
  entity_id: tts.qwen3_tts
data:
  media_player_entity_id: media_player.living_room
  message: "你好，欢迎回家！"
```

## 使用示例

### 欢迎回家自动化

```yaml
automation:
  - alias: "欢迎回家"
    trigger:
      - platform: state
        entity_id: person.xiaoming
        to: "home"
    action:
      - service: tts.speak
        target:
          entity_id: tts.qwen3_tts
        data:
          media_player_entity_id: media_player.living_room
          message: "欢迎回家！"
```

### 门铃通知

```yaml
automation:
  - alias: "门铃通知"
    trigger:
      - platform: state
        entity_id: binary_sensor.doorbell
        to: "on"
    action:
      - service: tts.speak
        target:
          entity_id: tts.qwen3_tts
        data:
          media_player_entity_id: media_player.living_room
          message: "有人按门铃"
          options:
            speed: 1.2
```

### 使用自定义音色

先上传音色样本：

```bash
curl -X POST "http://YOUR_SERVER:7860/api/upload_speaker?name=xiaoming" \
  -F "file=@voice_sample.wav"
```

然后在 Home Assistant 中使用：

```yaml
service: tts.speak
target:
  entity_id: tts.qwen3_tts
data:
  media_player_entity_id: media_player.living_room
  message: "小明，你好！"
  options:
    speaker: "xiaoming"
```

## 配置选项

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `host` | Qwen3 TTS 服务器地址 | `localhost` |
| `port` | 服务器端口 | `7860` |
| `speed` | 默认语速（0.5-2.0） | `1.0` |

## 支持的语言

- 中文 (zh)
- 英文 (en)
- 日语 (ja)
- 韩语 (ko)
- 德语 (de)
- 法语 (fr)
- 俄语 (ru)
- 葡萄牙语 (pt)
- 西班牙语 (es)
- 意大利语 (it)

## 常见问题

### 无法连接到服务器

确认 Qwen3 TTS 服务器正在运行：

```bash
curl http://YOUR_SERVER:7860/health
```

### 没有声音

1. 检查 media_player 状态和音量
2. 查看 Home Assistant 日志
3. 验证网络连通性

## 相关链接

- [详细文档](https://github.com/nichwang88/ha-qwen3-tts)
- [问题反馈](https://github.com/nichwang88/ha-qwen3-tts/issues)
- [Qwen3-TTS 官方](https://github.com/QwenLM/Qwen3-TTS)

## 许可证

MIT License - 详见 [LICENSE](https://github.com/nichwang88/ha-qwen3-tts/blob/main/LICENSE)

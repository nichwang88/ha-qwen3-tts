# Qwen3 TTS for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/nichwang88/ha-qwen3-tts.svg)](https://github.com/nichwang88/ha-qwen3-tts/releases)
[![License](https://img.shields.io/github/license/nichwang88/ha-qwen3-tts.svg)](LICENSE)

阿里巴巴千问 TTS（Qwen3-TTS）的 Home Assistant 自定义集成，支持高质量多语言语音合成和声音克隆。

[English](#english) | [中文](#中文)

---

## 中文

### 功能特性

- ✅ **完全本地化** - 所有语音合成在本地完成，无需联网
- ✅ **UI 配置流程** - 通过 Home Assistant UI 轻松配置，无需编辑 YAML
- ✅ **多语言支持** - 支持中文、英文、日语、韩语等 10 种语言
- ✅ **声音克隆** - 支持使用自定义音色样本
- ✅ **可调语速** - 支持 0.5-2.0 倍速调节
- ✅ **自动发现音色** - 自动列出服务器上的可用音色
- ✅ **HACS 支持** - 通过 HACS 一键安装和更新

### 系统要求

1. **Qwen3 TTS 服务器** 已运行（参见[部署指南](#部署-qwen3-tts-服务器)）
2. **Home Assistant** 2024.1.0 或更高版本

### 安装方法

#### 方法 1: HACS 安装（推荐）

1. 确保已安装 [HACS](https://hacs.xyz/)
2. 在 HACS 中点击 `Integrations`
3. 点击右上角菜单，选择 `Custom repositories`
4. 添加仓库 URL: `https://github.com/nichwang88/ha-qwen3-tts`
5. 类别选择 `Integration`
6. 点击 `Add`
7. 在 HACS 中搜索 "Qwen3 TTS"
8. 点击 `Download`
9. 重启 Home Assistant

#### 方法 2: 手动安装

1. 下载 [最新版本](https://github.com/nichwang88/ha-qwen3-tts/releases)
2. 将 `custom_components/qwen3_tts` 文件夹复制到 Home Assistant 的 `config/custom_components/` 目录
3. 重启 Home Assistant

### 配置集成

1. 进入 **设置** → **设备与服务**
2. 点击右下角 **+ 添加集成**
3. 搜索 "**Qwen3 TTS**"
4. 输入配置信息：
   - **主机地址**: Qwen3 TTS 服务器的 IP 地址（例如：`192.168.1.100` 或 `localhost`）
   - **端口**: 服务器端口
     - MLX-Audio 版本（推荐）: `7861`
     - Docker 版本: `7860`
   - **默认语速**: 0.5-2.0（默认：`1.0`）
5. 点击 **提交**

配置成功后，会创建一个 `tts.qwen3_tts` 实体。

### 使用示例

#### 基础语音播报

```yaml
service: tts.speak
target:
  entity_id: tts.qwen3_tts
data:
  media_player_entity_id: media_player.living_room
  message: "你好，欢迎回家！"
```

#### 调整语速

```yaml
service: tts.speak
target:
  entity_id: tts.qwen3_tts
data:
  media_player_entity_id: media_player.living_room
  message: "这是一条紧急通知"
  options:
    speed: 1.5  # 1.5 倍速
```

#### 使用自定义音色

```yaml
service: tts.speak
target:
  entity_id: tts.qwen3_tts
data:
  media_player_entity_id: media_player.living_room
  message: "小明，你好"
  options:
    speaker: "xiaoming"  # 需要先上传音色样本
```

#### 自动化示例

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
          message: "欢迎回家，小明！"
          options:
            speed: 1.0

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
          message: "有人按门铃，请查看门口。"
          options:
            speed: 1.2

  - alias: "天气播报"
    trigger:
      - platform: time
        at: "07:00:00"
    condition:
      - condition: state
        entity_id: person.xiaoming
        state: "home"
    action:
      - service: tts.speak
        target:
          entity_id: tts.qwen3_tts
        data:
          media_player_entity_id: media_player.bedroom
          message: >
            早上好！今天{{ states('weather.home') }}，
            温度{{ state_attr('weather.home', 'temperature') }}度。
            祝你有美好的一天！
```

### 部署 Qwen3 TTS 服务器

如果还没有部署 Qwen3 TTS 服务器，请按以下步骤操作：

#### 使用 MLX-Audio（Apple Silicon 推荐，29 倍加速！）

**性能对比**:
- Docker CPU 版本: 短文本 39 秒，长文本 66 秒
- MLX-Audio GPU 版本: **短文本 1.34 秒，长文本 6.96 秒**（**29 倍加速**！）

**系统要求**: Apple Silicon Mac (M1/M2/M3/M4)

1. 安装依赖：
   ```bash
   python3.10 -m venv mlx-venv
   source mlx-venv/bin/activate
   pip install mlx mlx-audio fastapi uvicorn soundfile numpy aiofiles python-multipart
   ```

2. 下载服务器代码：
   ```bash
   git clone https://github.com/nichwang88/ha-qwen3-tts.git
   cd ha-qwen3-tts
   ```

3. 启动服务（端口 7861）：
   ```bash
   python mlx-server.py
   ```

4. 验证服务：
   ```bash
   curl http://localhost:7861/health
   # 应该显示: "metal_gpu": true
   ```

**配置开机自启**（可选）:
创建 `~/Library/LaunchAgents/com.qwen3tts.mlx.plist`，参见 [MLX 部署指南](https://github.com/nichwang88/ha-qwen3-tts/blob/main/docs/MLX_DEPLOYMENT.md)

#### 使用 Docker（通用方案）

**性能**: 短文本 ~39 秒，长文本 ~66 秒（CPU only）

1. 下载部署文件：
   ```bash
   git clone https://github.com/nichwang88/qwen3-tts-docker.git
   cd qwen3-tts-docker
   ```

2. 启动服务（端口 7860）：
   ```bash
   docker compose up -d
   ```

3. 等待模型下载（首次启动需要 5-15 分钟）

4. 验证服务：
   ```bash
   curl http://localhost:7860/health
   ```

详细部署指南请参考：[Qwen3 TTS 部署文档](https://github.com/nichwang88/qwen3-tts-docker)

### 上传自定义音色

通过 API 上传音频样本作为音色：

```bash
curl -X POST "http://YOUR_SERVER_IP:7860/api/upload_speaker?name=xiaoming" \
  -F "file=@/path/to/voice_sample.wav"
```

**音频要求**：
- 格式：WAV/MP3/FLAC
- 时长：3-10 秒
- 质量：清晰人声，无背景噪音

上传后，可在 Home Assistant 中使用 `speaker: "xiaoming"` 调用。

### 故障排除

#### 集成无法添加

**问题**：提示"无法连接到 Qwen3 TTS 服务器"

**解决方案**：
1. 确认 Qwen3 TTS 服务器正在运行：
   ```bash
   curl http://YOUR_SERVER_IP:7860/health
   ```
2. 检查防火墙设置，确保端口 7860 可访问
3. 验证 Home Assistant 可以访问服务器（网络连通性）

#### TTS 播报无声音

**问题**：服务调用成功但没有声音

**检查清单**：
1. 确认 `media_player` 实体可用且音量不为 0
2. 检查 Home Assistant 日志：**设置** → **系统** → **日志**
3. 测试 media player：
   ```yaml
   service: media_player.play_media
   target:
     entity_id: media_player.living_room
   data:
     media_content_type: music
     media_content_id: "http://YOUR_SERVER_IP:7860/api/tts?text=测试"
   ```

#### 音色不可用

**问题**：使用 `speaker` 选项时失败

**解决方案**：
1. 检查音色是否已上传：
   ```bash
   curl http://YOUR_SERVER_IP:7860/api/list_speakers
   ```
2. 重新上传音色样本
3. 确认音色名称拼写正确

### 开发和贡献

欢迎贡献代码、报告问题或提出功能建议！

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

### 相关链接

- [Qwen3-TTS 官方仓库](https://github.com/QwenLM/Qwen3-TTS)
- [Home Assistant 官方文档](https://www.home-assistant.io/)
- [HACS 官方网站](https://hacs.xyz/)

---

## English

### Features

- ✅ **Fully Local** - All speech synthesis is done locally, no internet required
- ✅ **UI Configuration Flow** - Easy setup through Home Assistant UI, no YAML editing needed
- ✅ **Multi-language Support** - Supports 10 languages including Chinese, English, Japanese, Korean
- ✅ **Voice Cloning** - Support for custom voice samples
- ✅ **Adjustable Speed** - 0.5-2.0x speed control
- ✅ **Auto Speaker Discovery** - Automatically lists available speakers from server
- ✅ **HACS Support** - One-click installation and updates via HACS

### Requirements

1. **Qwen3 TTS Server** running (see [Deployment Guide](#deploy-qwen3-tts-server))
2. **Home Assistant** 2024.1.0 or later

### Installation

#### Method 1: HACS (Recommended)

1. Ensure [HACS](https://hacs.xyz/) is installed
2. In HACS, click `Integrations`
3. Click the menu in the top right, select `Custom repositories`
4. Add repository URL: `https://github.com/nichwang88/ha-qwen3-tts`
5. Category: `Integration`
6. Click `Add`
7. Search for "Qwen3 TTS" in HACS
8. Click `Download`
9. Restart Home Assistant

#### Method 2: Manual Installation

1. Download the [latest release](https://github.com/nichwang88/ha-qwen3-tts/releases)
2. Copy `custom_components/qwen3_tts` folder to your Home Assistant `config/custom_components/` directory
3. Restart Home Assistant

### Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration** in the bottom right
3. Search for "**Qwen3 TTS**"
4. Enter configuration:
   - **Host**: IP address of Qwen3 TTS server (e.g., `192.168.1.100` or `localhost`)
   - **Port**: Server port (default: `7860`)
   - **Default Speed**: 0.5-2.0 (default: `1.0`)
5. Click **Submit**

After successful configuration, a `tts.qwen3_tts` entity will be created.

### Usage Examples

#### Basic TTS

```yaml
service: tts.speak
target:
  entity_id: tts.qwen3_tts
data:
  media_player_entity_id: media_player.living_room
  message: "Hello, welcome home!"
```

#### Adjust Speed

```yaml
service: tts.speak
target:
  entity_id: tts.qwen3_tts
data:
  media_player_entity_id: media_player.living_room
  message: "This is an urgent notification"
  options:
    speed: 1.5  # 1.5x speed
```

#### Use Custom Voice

```yaml
service: tts.speak
target:
  entity_id: tts.qwen3_tts
data:
  media_player_entity_id: media_player.living_room
  message: "Hello, John"
  options:
    speaker: "john"  # Must upload voice sample first
```

### Deploy Qwen3 TTS Server

If you haven't deployed the Qwen3 TTS server yet:

#### Using Docker (Recommended)

1. Download deployment files:
   ```bash
   git clone https://github.com/nichwang88/qwen3-tts-docker.git
   cd qwen3-tts-docker
   ```

2. Start service:
   ```bash
   docker compose up -d
   ```

3. Wait for model download (5-15 minutes on first start)

4. Verify service:
   ```bash
   curl http://localhost:7860/health
   ```

For detailed deployment guide, see: [Qwen3 TTS Deployment Docs](https://github.com/nichwang88/qwen3-tts-docker)

### Upload Custom Voice

Upload audio sample as voice via API:

```bash
curl -X POST "http://YOUR_SERVER_IP:7860/api/upload_speaker?name=john" \
  -F "file=@/path/to/voice_sample.wav"
```

**Audio Requirements**:
- Format: WAV/MP3/FLAC
- Duration: 3-10 seconds
- Quality: Clear voice, no background noise

After upload, use `speaker: "john"` in Home Assistant.

### Troubleshooting

#### Cannot Add Integration

**Issue**: "Cannot connect to Qwen3 TTS server"

**Solution**:
1. Verify Qwen3 TTS server is running:
   ```bash
   curl http://YOUR_SERVER_IP:7860/health
   ```
2. Check firewall settings for port 7860
3. Verify network connectivity from Home Assistant to server

#### No Sound from TTS

**Issue**: Service call succeeds but no audio

**Checklist**:
1. Verify `media_player` entity is available and volume is not 0
2. Check Home Assistant logs: **Settings** → **System** → **Logs**
3. Test media player directly

#### Speaker Not Available

**Issue**: Fails when using `speaker` option

**Solution**:
1. List available speakers:
   ```bash
   curl http://YOUR_SERVER_IP:7860/api/list_speakers
   ```
2. Re-upload voice sample
3. Verify speaker name spelling

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

### Links

- [Qwen3-TTS Official Repository](https://github.com/QwenLM/Qwen3-TTS)
- [Home Assistant Documentation](https://www.home-assistant.io/)
- [HACS Official Website](https://hacs.xyz/)

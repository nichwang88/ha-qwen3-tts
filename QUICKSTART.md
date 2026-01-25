# 快速开始指南

5 分钟快速部署 Qwen3 TTS Home Assistant 集成。

## 前置条件

✅ Qwen3 TTS 服务器已运行（参见 `~/docker/qwen3-tts/`）
✅ Home Assistant 2024.1.0+ 已安装
✅ 可选：已安装 HACS

---

## 方案 A: 通过 HACS 安装（推荐）

### 1. 准备发布到 GitHub

```bash
cd ~/github/ha-qwen3-tts

# 运行部署脚本（替换为你的 GitHub 用户名）
./deploy.sh YOUR_GITHUB_USERNAME
```

### 2. 创建 GitHub 仓库

1. 访问 https://github.com/new
2. Repository name: `ha-qwen3-tts`
3. Description: `Qwen3 TTS integration for Home Assistant`
4. 选择 **Public**
5. 点击 **Create repository**

### 3. 推送代码

```bash
# 添加远程仓库（替换 YOUR_GITHUB_USERNAME）
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/ha-qwen3-tts.git

# 推送代码和标签
git push -u origin main
git push origin v1.0.0
```

### 4. 创建 GitHub Release

1. 访问仓库的 Releases 页面
2. 点击 **Create a new release**
3. 选择标签 `v1.0.0`
4. Title: `Version 1.0.0`
5. Description: 复制标签消息
6. 点击 **Publish release**

### 5. 在 HACS 中安装

1. 打开 Home Assistant
2. HACS → Integrations → ⋮ → Custom repositories
3. 添加仓库:
   - Repository: `https://github.com/YOUR_GITHUB_USERNAME/ha-qwen3-tts`
   - Category: `Integration`
4. 搜索 "Qwen3 TTS"
5. 点击 Download
6. 重启 Home Assistant

---

## 方案 B: 手动安装（本地测试）

### 1. 复制文件到 Home Assistant

```bash
# 假设 HA 配置目录是 /config
cp -r ~/github/ha-qwen3-tts/custom_components/qwen3_tts \
      /config/custom_components/
```

### 2. 重启 Home Assistant

```bash
ha core restart
```

---

## 配置集成

### 1. 添加集成

1. 设置 → 设备与服务 → + 添加集成
2. 搜索 "Qwen3 TTS"
3. 填写配置:
   - **主机**: Qwen3 TTS 服务器 IP（如 `192.168.1.100` 或 `localhost`）
   - **端口**: `7860`
   - **默认语速**: `1.0`
4. 点击 **提交**

### 2. 验证安装

检查是否出现 `tts.qwen3_tts` 实体：

1. 设置 → 设备与服务 → Qwen3 TTS
2. 查看实体列表

---

## 测试 TTS

### 开发者工具测试

1. 开发者工具 → 服务
2. 服务: `tts.speak`
3. 目标: `tts.qwen3_tts`
4. 服务数据:

```yaml
media_player_entity_id: media_player.living_room
message: "你好，这是测试"
```

5. 点击 **调用服务**

应该听到语音播报！

---

## 创建自动化

### 示例 1: 欢迎回家

```yaml
automation:
  - alias: "欢迎回家"
    trigger:
      - platform: state
        entity_id: person.你的名字
        to: "home"
    action:
      - service: tts.speak
        target:
          entity_id: tts.qwen3_tts
        data:
          media_player_entity_id: media_player.living_room
          message: "欢迎回家！"
```

### 示例 2: 门铃通知

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

---

## 故障排除

### 问题: 无法添加集成

**检查**:
```bash
# 验证 Qwen3 TTS 服务器运行
curl http://YOUR_SERVER_IP:7860/health
```

**预期响应**:
```json
{"status":"healthy","model_loaded":true}
```

### 问题: 没有声音

**检查**:
1. media_player 实体状态
2. 音量设置
3. Home Assistant 日志

### 问题: HACS 找不到集成

**确认**:
1. GitHub 仓库是 Public
2. 已创建 Release
3. 刷新 HACS

---

## 下一步

✅ 探索更多功能:
- 声音克隆（上传音色样本）
- 多语言支持（10 种语言）
- 语速调节（0.5-2.0 倍）

✅ 查看完整文档:
- [README.md](README.md) - 完整功能介绍
- [INSTALLATION.md](INSTALLATION.md) - 详细安装指南
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - GitHub 部署教程

---

**快速开始完成！** 🎉

现在你可以在 Home Assistant 中使用高质量的 Qwen3 TTS 了！

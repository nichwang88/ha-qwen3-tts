# Release v1.3.2 - Voice Selection UI Support

## 🎉 主要特性

### ✨ UI 音色选择支持

现在可以直接在 Home Assistant UI 中选择音色了！无需手动编辑配置文件。

**在以下位置可以选择音色**:
- 开发者工具 → 服务 → `tts.qwen3_tts_say`
- 自动化编辑器中的 TTS 动作
- 集成配置选项

**支持的音色** (取决于 TTS 服务器配置):
- Vivian (温暖友好的女声)
- Chelsie (活泼明亮的女声)
- Ethan (稳重自信的男声)
- Serena (优雅柔和的女声)
- Aria (专业清晰的女声)
- Ryan (友好亲切的男声)
- Aiden (年轻活力的男声)

## 🐛 修复内容

### 音色选择器无法显示

**问题**: v1.3.1 及之前版本在 Home Assistant UI 中无法显示音色下拉选择器

**原因**: 集成缺少 Home Assistant 要求的 `async_get_supported_voices()` 方法

**修复**:
- ✅ 实现了 `async_get_supported_voices()` 方法
- ✅ 添加了音色缓存机制提升性能
- ✅ 首次 TTS 请求时自动获取音色列表

## 📋 技术改进

### 代码变更

**新增**:
```python
@callback
def async_get_supported_voices(self, language: str) -> list[str] | None:
    """Return a list of supported voices for a language."""
    voices = self._supported_voices_cache.get(language)
    return voices
```

**优化**:
- 实现了音色缓存，避免重复请求 TTS 服务器
- 延迟加载机制，不阻塞 HA 启动流程
- 支持多语言独立缓存

### 文件变更

- `custom_components/qwen3_tts/tts.py` (+18 lines)
  - 新增 `callback` 导入
  - 新增 `_supported_voices_cache` 缓存字典
  - 新增 `async_get_supported_voices()` 方法
  - 在 `async_get_tts_audio()` 中自动填充缓存
- `custom_components/qwen3_tts/manifest.json`
  - 版本号更新: 1.3.1 → 1.3.2
- `CHANGELOG.md` (新增)
  - 记录所有版本的变更历史

## 📦 安装/更新

### 通过 HACS 更新 (推荐)

1. 打开 HACS → 集成
2. 找到 "Qwen3 TTS"
3. 点击更新到 v1.3.2
4. 重启 Home Assistant

### 手动更新

```bash
cd /config/custom_components/
rm -rf qwen3_tts
wget https://github.com/nichwang88/ha-qwen3-tts/archive/refs/tags/v1.3.2.tar.gz
tar -xzf v1.3.2.tar.gz
mv ha-qwen3-tts-1.3.2/custom_components/qwen3_tts ./
rm -rf ha-qwen3-tts-1.3.2 v1.3.2.tar.gz
```

重启 Home Assistant Core。

## 🧪 测试验证

### 验证音色选择器

1. 前往 **开发者工具 → 服务**
2. 选择服务: `tts.qwen3_tts_say`
3. 在 "speaker" 字段应该看到下拉选择器
4. 选择一个音色并测试

### 示例配置

```yaml
service: tts.qwen3_tts_say
data:
  entity_id: media_player.living_room
  message: "你好，这是 Serena 的声音"
  # 现在可以从 UI 选择器中选择音色
```

## 📚 参考文档

- [安装指南](INSTALLATION.md)
- [快速开始](QUICKSTART.md)
- [部署指南](DEPLOYMENT_GUIDE.md)
- [完整变更日志](CHANGELOG.md)

## 🙏 贡献

感谢所有使用和反馈的用户！

如果遇到问题，请在 [Issues](https://github.com/nichwang88/ha-qwen3-tts/issues) 中报告。

## 📝 完整变更日志

查看 [CHANGELOG.md](CHANGELOG.md) 获取所有版本的详细变更历史。

---

**发布日期**: 2026-02-01
**兼容版本**: Home Assistant 2024.1.0+
**集成版本**: v1.3.2

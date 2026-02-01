# Changelog

All notable changes to this project will be documented in this file.

## [1.3.2] - 2026-02-01

### Fixed
- **Voice Selection UI Support**: Added `async_get_supported_voices()` method to enable voice selection in Home Assistant UI
  - Home Assistant UI can now properly display voice/speaker selection dropdown
  - Implemented voice caching mechanism to improve performance
  - Voices are automatically cached on first TTS request for each language

### Technical Details
- Added `callback` import from `homeassistant.helpers`
- Added `_supported_voices_cache` dictionary to store voices per language
- Implemented `async_get_supported_voices(language: str)` method required by HA's `TextToSpeechEntity`
- Voice list is populated automatically on first TTS request to avoid blocking HA startup

### Changed
- Voice list is now accessible through the standard Home Assistant TTS entity interface
- Improved compatibility with Home Assistant 2024.1.0+

## [1.3.1] - 2026-01-27

### Fixed
- 修复超时配置实时更新问题

## [1.3.0] - 2026-01-26

### Added
- 添加可配置的超时时间设置 (10-300 seconds range)
- Dynamic timeout calculation based on text length

## [1.2.1] - 2026-01-26

### Fixed
- Options flow configuration errors

## [1.2.0] - 2026-01-26

### Added
- Options flow for runtime configuration changes
- Ability to modify host, port, speed, and speaker settings without restart

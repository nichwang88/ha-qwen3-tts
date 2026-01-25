# GitHub 仓库部署指南

如何将 Qwen3 TTS 集成发布到 GitHub 并通过 HACS 分发。

## 准备工作

### 1. 创建 GitHub 仓库

1. 登录 [GitHub](https://github.com)
2. 点击右上角 **+** → **New repository**
3. 填写仓库信息:
   - **Repository name**: `ha-qwen3-tts`
   - **Description**: `Qwen3 TTS integration for Home Assistant`
   - **Public** (必须是公开仓库才能在 HACS 中使用)
   - 不要勾选 "Initialize this repository with a README"
4. 点击 **Create repository**

### 2. 替换占位符

在发布前，需要替换以下文件中的占位符：

#### manifest.json
```json
"codeowners": ["@nichwang88"],  // 改为你的 GitHub 用户名
"documentation": "https://github.com/nichwang88/ha-qwen3-tts",  // 改为实际仓库 URL
"issue_tracker": "https://github.com/nichwang88/ha-qwen3-tts/issues",  // 改为实际 URL
```

#### README.md
全局替换:
- `nichwang88` → 你的 GitHub 用户名
- `Your Name` → 你的名字（在 LICENSE 中）

快速替换命令：
```bash
cd ~/github/ha-qwen3-tts

# macOS
find . -type f \( -name "*.md" -o -name "*.json" \) -exec sed -i '' 's/nichwang88/YOUR_GITHUB_USERNAME/g' {} +

# Linux
find . -type f \( -name "*.md" -o -name "*.json" \) -exec sed -i 's/nichwang88/YOUR_GITHUB_USERNAME/g' {} +
```

## 推送到 GitHub

### 1. 初始化 Git 仓库

```bash
cd ~/github/ha-qwen3-tts

# 初始化 Git
git init

# 添加远程仓库
git remote add origin https://github.com/YOUR_USERNAME/ha-qwen3-tts.git

# 检查文件
git status
```

### 2. 创建首次提交

```bash
# 添加所有文件
git add .

# 创建提交
git commit -m "Initial commit: Qwen3 TTS integration for Home Assistant

Features:
- Config flow UI for easy setup
- Support for 10 languages
- Voice cloning support
- Adjustable speed control
- Auto speaker discovery
- HACS compatible
"

# 推送到 GitHub
git branch -M main
git push -u origin main
```

### 3. 创建 Release

创建发布版本以便 HACS 使用：

```bash
# 创建标签
git tag -a v1.0.0 -m "Version 1.0.0

Initial release:
- Basic TTS functionality
- Config flow setup
- Multi-language support
- Voice cloning
- Speed control
- HACS integration
"

# 推送标签
git push origin v1.0.0
```

或通过 GitHub Web UI:

1. 进入仓库页面
2. 点击 **Releases** → **Create a new release**
3. 填写:
   - **Tag version**: `v1.0.0`
   - **Release title**: `Version 1.0.0`
   - **Description**: 复制上面的更新日志
4. 点击 **Publish release**

## 提交到 HACS

### 方法 1: 提交到 HACS 默认仓库（推荐）

1. Fork [HACS 默认仓库](https://github.com/hacs/default)

2. 编辑 `integration` 文件，添加:
   ```json
   {
     "name": "Qwen3 TTS",
     "domain": "qwen3_tts",
     "owner": "nichwang88"
   }
   ```

3. 创建 Pull Request

4. 等待 HACS 团队审核（通常 1-2 周）

### 方法 2: 用户自定义仓库（立即可用）

用户可以直接添加你的仓库：

1. 在 HACS 中点击 **Integrations**
2. 点击 **⋮** → **Custom repositories**
3. 添加:
   - **Repository**: `https://github.com/nichwang88/ha-qwen3-tts`
   - **Category**: `Integration`

## 文件结构检查

确保仓库结构正确：

```
ha-qwen3-tts/
├── .github/
│   └── workflows/
│       └── validate.yaml          # CI/CD 验证
├── custom_components/
│   └── qwen3_tts/
│       ├── __init__.py            # 集成入口
│       ├── manifest.json          # 集成元数据
│       ├── config_flow.py         # 配置流程
│       ├── const.py               # 常量定义
│       ├── strings.json           # UI 字符串
│       ├── tts.py                 # TTS 平台实现
│       └── translations/
│           ├── en.json            # 英文翻译
│           └── zh-Hans.json       # 中文翻译
├── .gitignore                     # Git 忽略文件
├── hacs.json                      # HACS 元数据
├── info.md                        # HACS 信息页面
├── LICENSE                        # MIT 许可证
├── README.md                      # 主文档
├── INSTALLATION.md                # 安装指南
└── DEPLOYMENT_GUIDE.md            # 本文件
```

## 验证集成

### GitHub Actions 自动验证

推送后，GitHub Actions 会自动运行验证：

1. 进入仓库的 **Actions** 标签
2. 查看 **Validate** 工作流
3. 确保所有检查都通过 ✅

### 本地验证

使用 Home Assistant 官方工具验证：

```bash
# 安装验证工具
pip install homeassistant

# 运行 hassfest
python -m homeassistant.scripts.hassfest --requirements --action validate

# HACS 验证
docker run --rm -v $(pwd):/github/workspace ghcr.io/hacs/action:main
```

## 更新集成

### 1. 修改代码

```bash
# 创建功能分支
git checkout -b feature/new-feature

# 修改代码
# ...

# 提交更改
git add .
git commit -m "Add new feature: xxx"

# 推送分支
git push origin feature/new-feature
```

### 2. 创建 Pull Request

在 GitHub 上创建 PR 并合并到 main 分支。

### 3. 发布新版本

```bash
# 切换到 main 分支
git checkout main
git pull origin main

# 更新版本号
# 编辑 custom_components/qwen3_tts/manifest.json
# "version": "1.0.1"

# 提交版本更新
git add custom_components/qwen3_tts/manifest.json
git commit -m "Bump version to 1.0.1"
git push origin main

# 创建新标签
git tag -a v1.0.1 -m "Version 1.0.1

Changes:
- Fix: xxx
- Feature: xxx
"
git push origin v1.0.1
```

### 4. 创建 GitHub Release

1. 进入 **Releases** → **Draft a new release**
2. 选择标签 `v1.0.1`
3. 填写更新日志
4. 发布

HACS 会自动检测新版本并通知用户更新。

## 最佳实践

### 版本号规范

使用语义化版本 (Semantic Versioning):

- **主版本号** (MAJOR): 不兼容的 API 修改
- **次版本号** (MINOR): 向后兼容的功能新增
- **修订号** (PATCH): 向后兼容的问题修正

示例:
- `1.0.0` - 初始版本
- `1.0.1` - Bug 修复
- `1.1.0` - 新功能
- `2.0.0` - 重大更新（不兼容旧版本）

### Commit 消息规范

使用清晰的提交消息：

```bash
# 功能
git commit -m "feat: add voice cloning support"

# 修复
git commit -m "fix: resolve connection timeout issue"

# 文档
git commit -m "docs: update installation guide"

# 性能
git commit -m "perf: optimize TTS request caching"

# 重构
git commit -m "refactor: simplify config flow logic"
```

### Issue 和 PR 模板

创建 `.github/ISSUE_TEMPLATE/bug_report.md`:

```markdown
---
name: Bug report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''
---

**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
What you expected to happen.

**Environment:**
 - Home Assistant version: [e.g. 2024.1.0]
 - Integration version: [e.g. 1.0.0]
 - Qwen3 TTS server version: [e.g. 1.0.0]

**Logs:**
```
Paste relevant logs here
```

**Additional context**
Any other context about the problem.
```

## 维护和支持

### 监控 Issues

定期检查和回复用户问题：

1. 启用 GitHub Notifications
2. 及时回复 Issues
3. 标记和分类问题（bug, enhancement, question）
4. 关闭已解决的问题

### 社区贡献

欢迎社区贡献：

1. 创建 `CONTRIBUTING.md` 指南
2. 设置 PR 模板
3. 运行 CI/CD 检查
4. Code review 并合并优质 PR

## 推广集成

### 社区分享

在以下平台分享你的集成：

- **Home Assistant 社区论坛**: https://community.home-assistant.io/
- **Reddit**: r/homeassistant
- **Home Assistant 中文社区**: https://bbs.hassbian.com/
- **GitHub Awesome Lists**: awesome-home-assistant

### 示例帖子

```markdown
# 介绍 Qwen3 TTS - 本地高质量中文语音合成

我开发了一个 Home Assistant 集成，连接阿里巴巴开源的 Qwen3 TTS 模型。

特性:
- 完全本地化，无需联网
- 支持中英日韩等 10 种语言
- 可以克隆自定义音色
- 通过 HACS 一键安装

GitHub: https://github.com/nichwang88/ha-qwen3-tts
欢迎试用和反馈！
```

## 故障排除

### HACS 验证失败

检查 `hacs.json` 格式:
```bash
cat hacs.json | jq .
```

### GitHub Actions 失败

查看 Actions 日志，常见问题：

1. **Hassfest 失败**: 检查 `manifest.json` 格式
2. **HACS 验证失败**: 检查 `hacs.json` 和文件结构
3. **权限错误**: 检查 repository settings → Actions → Permissions

### 用户无法安装

确保：
1. 仓库是公开的
2. 至少有一个 Release 标签
3. `hacs.json` 存在
4. 文件结构正确

## 检查清单

发布前检查：

- [ ] 所有占位符已替换
- [ ] `manifest.json` 版本号正确
- [ ] README.md 链接正确
- [ ] LICENSE 文件已添加
- [ ] 创建了至少一个 Release
- [ ] GitHub Actions 验证通过
- [ ] 本地测试安装成功
- [ ] 文档完整（README, INSTALLATION）

## 参考资料

- [HACS 官方文档](https://hacs.xyz/)
- [Home Assistant 开发者文档](https://developers.home-assistant.io/)
- [集成质量规范](https://developers.home-assistant.io/docs/creating_integration_quality_scale/)
- [语义化版本](https://semver.org/)

---

**祝发布顺利！** 🚀

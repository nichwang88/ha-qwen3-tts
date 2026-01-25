#!/bin/bash
# Qwen3 TTS HA Integration - 快速部署脚本
# 使用方法: ./deploy.sh [github_username]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查参数
if [ -z "$1" ]; then
    echo -e "${RED}错误: 请提供 GitHub 用户名${NC}"
    echo "使用方法: ./deploy.sh YOUR_GITHUB_USERNAME"
    exit 1
fi

GITHUB_USER="$1"
echo -e "${GREEN}=== Qwen3 TTS HA Integration 部署脚本 ===${NC}"
echo -e "GitHub 用户名: ${YELLOW}$GITHUB_USER${NC}"
echo ""

# 步骤 1: 替换占位符
echo -e "${YELLOW}[1/5] 替换占位符...${NC}"

# macOS 和 Linux 兼容的 sed 命令
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    find . -type f \( -name "*.md" -o -name "*.json" \) \
        -not -path "./.git/*" \
        -exec sed -i '' "s/yourusername/$GITHUB_USER/g" {} +
else
    # Linux
    find . -type f \( -name "*.md" -o -name "*.json" \) \
        -not -path "./.git/*" \
        -exec sed -i "s/yourusername/$GITHUB_USER/g" {} +
fi

echo -e "${GREEN}✓ 占位符替换完成${NC}"

# 步骤 2: 验证文件
echo -e "\n${YELLOW}[2/5] 验证必需文件...${NC}"

REQUIRED_FILES=(
    "custom_components/qwen3_tts/__init__.py"
    "custom_components/qwen3_tts/manifest.json"
    "custom_components/qwen3_tts/config_flow.py"
    "custom_components/qwen3_tts/tts.py"
    "hacs.json"
    "README.md"
    "LICENSE"
)

ALL_EXIST=true
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file ${RED}(缺失)${NC}"
        ALL_EXIST=false
    fi
done

if [ "$ALL_EXIST" = false ]; then
    echo -e "\n${RED}错误: 某些必需文件缺失，请检查${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 所有必需文件存在${NC}"

# 步骤 3: 初始化 Git
echo -e "\n${YELLOW}[3/5] 初始化 Git 仓库...${NC}"

if [ ! -d ".git" ]; then
    git init
    echo -e "${GREEN}✓ Git 仓库已初始化${NC}"
else
    echo -e "${YELLOW}ℹ Git 仓库已存在，跳过${NC}"
fi

# 步骤 4: 创建提交
echo -e "\n${YELLOW}[4/5] 创建 Git 提交...${NC}"

git add .
git commit -m "Initial commit: Qwen3 TTS integration for Home Assistant

Features:
- Config flow UI for easy setup
- Support for 10 languages (zh, en, ja, ko, de, fr, ru, pt, es, it)
- Voice cloning support
- Adjustable speed control (0.5-2.0x)
- Auto speaker discovery
- HACS compatible

Ready for deployment and testing.
" || echo -e "${YELLOW}ℹ 无新更改需要提交${NC}"

git branch -M main

echo -e "${GREEN}✓ 提交创建完成${NC}"

# 步骤 5: 创建标签
echo -e "\n${YELLOW}[5/5] 创建版本标签...${NC}"

if git rev-parse v1.0.0 >/dev/null 2>&1; then
    echo -e "${YELLOW}ℹ 标签 v1.0.0 已存在，跳过${NC}"
else
    git tag -a v1.0.0 -m "Version 1.0.0

Initial release of Qwen3 TTS Home Assistant integration.

Features:
- UI configuration flow
- Multi-language TTS support
- Voice cloning capability
- Speed control
- HACS integration
- Complete documentation

Installation:
- Via HACS custom repository
- Manual installation supported

For detailed installation guide, see INSTALLATION.md
"
    echo -e "${GREEN}✓ 标签 v1.0.0 已创建${NC}"
fi

# 完成
echo -e "\n${GREEN}=== 部署准备完成！ ===${NC}"
echo ""
echo -e "${YELLOW}下一步操作:${NC}"
echo ""
echo "1. 在 GitHub 创建新仓库:"
echo -e "   ${YELLOW}https://github.com/new${NC}"
echo "   - Repository name: ${YELLOW}ha-qwen3-tts${NC}"
echo "   - Description: ${YELLOW}Qwen3 TTS integration for Home Assistant${NC}"
echo "   - Public repository"
echo ""

echo "2. 添加远程仓库并推送:"
echo -e "   ${YELLOW}git remote add origin https://github.com/$GITHUB_USER/ha-qwen3-tts.git${NC}"
echo -e "   ${YELLOW}git push -u origin main${NC}"
echo -e "   ${YELLOW}git push origin v1.0.0${NC}"
echo ""

echo "3. 在 GitHub 创建 Release:"
echo -e "   访问: ${YELLOW}https://github.com/$GITHUB_USER/ha-qwen3-tts/releases/new${NC}"
echo "   - Tag: v1.0.0"
echo "   - Title: Version 1.0.0"
echo "   - 复制上面的标签消息作为描述"
echo ""

echo "4. 用户安装方式:"
echo "   - HACS → Integrations → ⋮ → Custom repositories"
echo -e "   - 添加: ${YELLOW}https://github.com/$GITHUB_USER/ha-qwen3-tts${NC}"
echo "   - Category: Integration"
echo ""

echo -e "${GREEN}更多详细信息请查看 DEPLOYMENT_GUIDE.md${NC}"

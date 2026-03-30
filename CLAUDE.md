# Game Asset Design

## Skills

- [game-asset](skills/game-asset/SKILL.md) — 游戏素材设计与提取。生成角色、图标、UI、卡牌、精灵图、瓦片等 2D 游戏素材，支持从设计图中提取和分离素材。

## 项目结构

- `game_asset_tools/` — Python 后处理工具库（16 个命令）
- `skills/game-asset.md` — Claude Code Skill 文件
- `projects/` — 项目配置（风格、尺寸、需求清单）
- `output/` — 素材输出目录
- `templates/` — 卡牌模板、字体

## 快速开始

```bash
# 安装依赖
pip3 install -r requirements.txt

# 验证工具可用
python3 -m game_asset_tools --help
```

然后在 Claude Code 中使用 `/game-asset` 调用技能。

## 依赖的 MCP 工具

- `gemini-image` — AI 图像生成与编辑（必需）
- `imgbb` — 图片上传分享（可选）

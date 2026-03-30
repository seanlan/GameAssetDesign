# Game Asset Design

## Skills

- [game-asset](skills/game-asset/SKILL.md) — 游戏素材设计与提取。生成角色、图标、UI、卡牌、精灵图、瓦片等 2D 游戏素材，支持从设计图中提取和分离素材。

## Commands

| 命令 | 说明 |
|------|------|
| `/game-asset:init` | 初始化项目配置 |
| `/game-asset:generate` | AI 生成新素材 |
| `/game-asset:analyze` | 分析设计图，识别元素 |
| `/game-asset:extract` | 裁切 + AI精修 + 去背景 |
| `/game-asset:manage` | 打开素材管理面板 |
| `/game-asset:refine` | 精修素材 |
| `/game-asset:version` | 版本管理 |
| `/game-asset:export` | 引擎导出 |
| `/game-asset:atlas` | 纹理图集打包 |

## 项目结构

- `commands/` — 9 个独立命令文件
- `skills/game-asset/` — Skill 路由入口
- `game_asset_tools/` — Python 后处理工具库（16 个命令）
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

然后在 Claude Code 中使用命令，如 `/game-asset:init`。

## 依赖的 MCP 工具

- `gemini-image` — AI 图像生成与编辑（必需）
- `imgbb` — 图片上传分享（可选）

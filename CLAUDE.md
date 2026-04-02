# Game Asset Design

## Skills

- [game-asset](skills/game-asset/SKILL.md) — 游戏素材设计与提取。生成角色、图标、UI、卡牌、精灵图、瓦片等 2D 游戏素材，支持从设计图中提取和分离素材。

## Commands

| 命令 | 说明 |
|------|------|
| `/game-asset:init` | 初始化项目配置（风格、引擎、参考图） |
| `/game-asset:generate` | AI 生成新素材 |
| `/game-asset:analyze` | 分析设计图，识别元素 |
| `/game-asset:extract` | 裁切 + AI精修 + 去背景 |
| `/game-asset:manage` | 打开素材管理面板 |
| `/game-asset:serve` | 启动 Web 管理服务 |
| `/game-asset:refine` | 精修素材 |
| `/game-asset:version` | 版本管理 |
| `/game-asset:export` | 引擎导出 |
| `/game-asset:atlas` | 纹理图集打包 |

## 项目结构

- `skills/game-asset/` — Skill 定义 + 知识库（5 个 CSV 数据文件）
- `commands/` — 10 个独立命令文件
- `game_asset_tools/` — Python 后处理工具库（20 个命令）
- `server/` — FastAPI 后端
- `web/` — React 前端
- `templates/` — 卡牌模板、字体
- `output/` — 素材输出目录

## 快速开始

```bash
pip3 install -r requirements.txt
python3 -m game_asset_tools --help
```

## 依赖的 MCP 工具

- `gemini-image` — AI 图像生成与编辑（必需）
- `grsai-nanobanana` — 高质量风格化生成（推荐）
- `imgbb` — 图片上传分享（可选）

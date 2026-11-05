# Personal Skills

TreasureGooldove 的个人技能与插件集合，直接整理自 GitHub 上游源码。每项可独立安装。

| 插件 | 上游 | 技能数 |
| --- | --- | --- |
| excalidraw-diagram | [coleam00/excalidraw-diagram-skill](https://github.com/coleam00/excalidraw-diagram-skill) | 1 |
| ui-ux-pro-max | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | 1 |
| find-skills | [vercel-labs/skills](https://github.com/vercel-labs/skills) | 1 |
| superpowers-zh | [jnMetaCode/superpowers-zh](https://github.com/jnMetaCode/superpowers-zh) | 21 |
| project-preflight | 本仓库原创：创建项目前检查更新 | 1 |

## Codex / ChatGPT 桌面插件市场

    codex plugin marketplace add TreasureGooldove/personal-skills

随后在支持本地插件市场的客户端打开插件目录，选择 TreasureGooldove Personal Skills，按需安装。私有仓库需要 GitHub 访问权限。

## Claude Code

    /plugin marketplace add TreasureGooldove/personal-skills

然后从此市场选择需要的插件。

## 作为普通 Skills 安装

    npx skills add TreasureGooldove/personal-skills

安装器支持私有仓库时，请先配置相应 GitHub 访问权限。

## 来源与打包说明

- 上游提交固定在 upstream-lock.json；不是自动追踪最新版本。
- MIT 项目许可证保留在各插件目录的 LICENSE 中。
- Excalidraw 上游当前没有明确 LICENSE；本仓库仅用于私人收藏，不为其声明额外授权。
- 上游说明保留在各插件的 UPSTREAM_README.md。
- UI/UX Pro Max 仅调整 SKILL.md 中插件内脚本路径，使其适配本仓库 skills/ 布局，保留数据、脚本和参考资料。
- Superpowers 中文版保留全部 21 个技能；本集合仅打包技能，不包含上游各平台的会话启动 hooks。
- 此仓库整理现有第三方作品，原作者与上游项目保留各自权利。

## 创建新项目前检查更新

安装并启用 project-preflight 插件后，在创建新项目、初始化仓库或生成脚手架前使用此技能。
仅收藏仓库或安装其他四个插件不会自动启用本检查；根目录 AGENTS.md 的作用范围也仅限加载它的会话。

在本仓库根目录手动检查：

    python plugins/project-preflight/skills/project-preflight/scripts/check_updates.py

要求 Python 3、Git、GitHub CLI（gh）及访问私有集合仓库的登录状态。
检查个人集合和四个上游，以打包提交为基线列出新增提交、部分变更文件及比较链接。
不修改文件，不自动升级。安装副本无法识别集合版本时报告“本地版本未知”；可用 --collection-base <提交SHA> 指定基线。
--json 输出结构化结果。检查发生错误时退出码为 1；成功检查（包括发现更新）退出码为 0。

上游更新时，同时维护根目录 upstream-lock.json 与技能 references/upstream-lock.json。
上游提交可能仅涉及不被打包的文件；是否升级应结合 diff 判断。

检查脚本的离线测试：

    python -m unittest discover -s tests -p test_check_updates.py
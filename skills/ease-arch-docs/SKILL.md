---
name: ease-arch-docs
description: "/ease:arch-docs — 生成或更新基于现有代码、配置、IaC 与批准记录的当前状态架构文档"
user-invocable: true
---

# /ease:arch-docs

先读取本技能目录的 `../ease-resources/runtime.md`，再读取
`../ease-resources/commands/arch-docs.md`，执行其中完整流程。
资源根为本技能目录的 `../ease-resources/`；所有 commands/、references/、templates/
绝对定位到该资源根。用户项目路径始终相对当前项目工作目录。
从用户消息中取得 `/ease:arch-docs`（或 `/ease-arch-docs`）之后的参数。

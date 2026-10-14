---
name: ease-analyze-code
description: "/ease:analyze-code — 分析源代码，提炼领域模型、业务用例与业务规则，初始化项目领域信息（适用于存量系统）"
user-invocable: true
---

# /ease:analyze-code

先读取本技能目录的 `../ease-resources/runtime.md`，再读取
`../ease-resources/commands/analyze-code.md`，执行其中完整流程。
资源根为本技能目录的 `../ease-resources/`；所有 commands/、references/、templates/
前缀的定位按 runtime.md 执行；领域内局部模板相对该领域目录，不能一律指向资源根。
用户项目路径始终相对当前项目工作目录。
从用户消息中取得 `/ease:analyze-code`（或 `/ease-analyze-code`）之后的参数。

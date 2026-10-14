---
name: ease-constitution
description: "/ease:constitution — 使用 ease-spec 技能初始化项目的 constitution 文档，支持用户补充项目内部规则和冲突点澄清"
user-invocable: true
---

# /ease:constitution

先读取本技能目录的 `../ease-resources/runtime.md`，再读取
`../ease-resources/commands/constitution.md`，执行其中完整流程。
资源根为本技能目录的 `../ease-resources/`；所有 commands/、references/、templates/
前缀的定位按 runtime.md 执行；领域内局部模板相对该领域目录，不能一律指向资源根。
用户项目路径始终相对当前项目工作目录。
从用户消息中取得 `/ease:constitution`（或 `/ease-constitution`）之后的参数。

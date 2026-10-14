---
name: ease-starter
description: "/ease:starter — 【一键三阶段】针对一份需求文档，自动编排并完整执行 flow-1（分析）→ flow-2（设计）→ flow-3（实现），内置阶段门控、BRD/TRD 路径分支、断点续跑与异步执行"
user-invocable: true
---

# /ease:starter

先读取本技能目录的 `../ease-resources/runtime.md`，再读取
`../ease-resources/commands/starter.md`，执行其中完整流程。
资源根为本技能目录的 `../ease-resources/`；所有 commands/、references/、templates/
绝对定位到该资源根。用户项目路径始终相对当前项目工作目录。
从用户消息中取得 `/ease:starter`（或 `/ease-starter`）之后的参数。

# Ease 三流程对齐审计

审计日期：2026-10-14。对照 `../ease-cc-plugins/plugins/ease` 当前工作树，
另读取 `ease-tools` 中主流程依赖的两个领域技能，不修改源仓库。

## 结论

三流程的命令正文、阶段合同、门禁、模板及已选领域资源已完成逐文件对齐。
这证明转换内容没有遗漏；不等同于模型在 DSH 中已经完整执行并交付一轮需求。
原生异步、外部工具、平台脚本差异仍按以下边界处理。

| 路线/阶段 | 对齐内容 | 结果 |
|---|---|---|
| starter | 路由、身份传播、resume/from-phase、阶段调用、门禁 | 完整正文保留 |
| BRD Flow 1 | 业务分析、领域对齐、DDR、测试 basis、候选证据 | 完整正文保留 |
| TRD Flow 1 | 风险分级、NFR、方案、权威 tasks、进入 Flow 3 | 完整正文保留；不强制经过 Flow 2 |
| Flow 2 | 上游消费者准入、架构/详细设计、测试选择、框架/TDD、任务 | 完整正文保留 |
| Flow 3 | BRD/TRD 双源准入、RED/GREEN/REFACTOR、故障分流、只读交付验收 | 完整正文保留；补齐调试依赖 |
| ease-spec | 全部 gates/、reference/、模板与脚本 | 完整资源核对；脚本仅做已记录适配 |
| 资源 | 16 个领域目录、共享模板及命令声明的 skills | 存在性与内容核对通过 |

## 发现并修复

1. **强制调试依赖遗漏**：Flow 3 明确要求多次失败后调用 systematic-debugging。
   之前只记录外部引用会让异常分支无法继续。本轮内化该技能及完整参考资料。
2. **技术验证依赖遗漏**：ease-spec、架构、编码资料引用的 ease-poc 位于 ease-tools，
   现已内化。没有把整个 ease-tools 命令族无差别迁移进来。
3. **非 Git 项目根定位错误**：common 与 create-new-feature 原先从脚本安装位置
   推断业务根，DSH 用户级安装后可能指向技能目录。本轮改为当前业务目录，Git
   项目仍用 git rev-parse；Bash 已实际验证，PowerShell 做相同适配但未执行验证。
4. **模板缺失导致空文件**：原脚本只找项目 .specify/.ease 模板，初始项目没有这些
   文件。现保留项目覆盖优先级，缺失时回退到内化的 ease-spec 模板。
5. **auto-integrate 查找外部源目录**：新增基于脚本自身位置的 ease-spec 定位。
6. **入口路径约定冲突**：移除“所有 references/templates 一律相对资源根”的
   过度描述，明确领域资料的局部路径与共享路径的区别。
7. **验收独立性表述不足**：同会话只能分生产遍和只读验收遍；必须冻结产物、
   主动反证及集合对账，不得以生产者自检替代源门禁的第二遍。
8. **缺少持续对齐证据**：新增 source-manifest.json（源文件 SHA-256）与
   audit_alignment.py；依赖删除、上游变化或正文漂移可自动发现。

## 验证证据

- `python3 scripts/audit_alignment.py`：9 个命令、199 个参考文件、14 个共享模板，0 错误。
- `python3 -m unittest discover -s tests -v`：8 项通过。包含人为删除交付 gate 后
  必须失败的负例；临时非 Git 业务目录实际执行 create-new-feature/setup-plan；
  验证包内模板回退和项目模板优先。
- `node tests/runtime-smoke.mjs`：实际 DSH 发现、九个冒号入口、参数保留与事件触发。
- 脚本适配只修改精确定位的片段，匹配次数不符就中止转换，避免悄悄丢失上游逻辑。

## 仍存在的差异与限制

- `--async` / 云端任务接口没有适配，明确停止，不能宣称和 Claude 完全等价。
- Claude frontmatter 的权限/model/scripts/handoffs 不在 DSH 自动执行。
  Flow 2 的前置检查在正文已有对应步骤；handoff 清单在会话内依据 ease-spec 执行。
- 外部 git-commit/git-branch-sync 等可选工具未迁移；superpowers 的 TDD 名称
  映射到包内 TDD，完成前验证用真实测试证据和 ease-qa/阶段门禁落实。
- 历史 contracts/schemas 等引用保留；引用报告是提示清单，不是全量链接有效性证明。
  缺少强制门禁资源时仍需阻断，不能虚构 PASS。
- 未验证 Windows PowerShell、完整业务流程模型行为或 Web 冒号自动补全。

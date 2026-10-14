# Ease 的 DSH 运行约定

此文件适用于包内全部命令。先读取本文件，再读取当前命令；这里对 DSH 的适配
优先于保留的源指令中 Claude 专属运行方式，业务流程、产物与质量门禁保持源合同。

## 命令和参数

支持 `/ease:starter`、`/ease:flow-1-analyze-brd`、`/ease:flow-1-analyze-trd`、
`/ease:flow-2-design`、`/ease:flow-3-implement`，以及 constitution、bootstrap-system、
analyze-code、arch-docs 四个预处理命令。冒号入口由随包提供的 DSH alias 插件加载；
原生备用名称使用 `ease-` 前缀，例如 `/ease-starter`。

`$ARGUMENTS`、`{ARGS}`、`$USER_INPUT` 表示用户消息中命令之后的参数，DSH 不会
替换这些模板变量。读取消息并解析参数，不把占位符作为实际路径或 shell 输入。
嵌套执行阶段时传递该阶段所需的路径与选项，不能沿用未解析的整段 starter 输入。

## 路径与参考资料

资源根是入口 SKILL.md 同级的 `../ease-resources/`，不依赖源仓库或安装位置。
`commands/` 指向资源根中的命令，`references/<技能名>/` 指向内化的领域资料，
资源根的 `templates/` 是共享模板。领域文档中原有的裸 `templates/`、`reference/`、
`references/` 路径相对该领域技能目录（Markdown 链接相对所在文档）。
`ease-spec/...` 等领域前缀展开为资源根的 `references/ease-spec/...`。
命令内 constitution 的 plan/spec/tasks 模板取自 `references/ease-spec/templates/`。

`memory/`、`docs/`、`.eases/`、源代码路径相对用户项目；源文中的 `/memory/`、
`/docs/` 也表示项目路径，不得写操作系统根目录。执行资源脚本时使用技能资源的
绝对路径，保持 cwd 为用户项目。不要 cd 到安装目录生成项目产物。

读取领域技能即读取其 SKILL.md，不依赖 Claude 的 Skill 工具或自动技能发现。
读取 `commands/<命令>.md` 完成阶段交接，不把 `/ease:xxx` 当作 shell 命令执行。
脚本仅做显式的 DSH 安装位置适配：非 Git 项目使用当前目录，项目模板优先，
缺失时使用包内模板。运行前确认当前目录就是业务项目，不能从安装目录启动业务流程。

## 流程与能力边界

- BRD：Flow 1 → Flow 2 → Flow 3；TRD：Flow 1 内含方案与任务 → Flow 3，
  不强制经过 Flow 2。使用源阶段合同判定门禁、身份编号和权威产物。
- starter 保留 `--resume`、`--path`、`--from-phase`；不把源代码示例中的自动
  提交/push 当作用户授权。只在用户明确要求交付到远端时执行相应操作。
- `--async` 或明确云端执行请求：当前交付包没有云端适配器，说明不支持并停止，
  不调用 ease:async-task、不静默改为同步。普通文档中的 async 字样不是请求。
- `--worktree` 使用内化的 ease-spec worktree 合同与脚本；在用户项目运行。
  当前移植保留这些脚本，不承诺所有平台都已完成端到端验证。
- 源 frontmatter 的工具授权、model、scripts、handoffs 不产生 DSH 运行时行为。
  按实际可用工具执行；子代理不可用时允许在当前会话分角色执行，但必须结束生产遍、
  冻结待审对象，再单独进行只读验收遍；不能把生产者自检当作独立验收或跳过反证与集合对账。
- Flow 3 的强制故障分流使用包内 `references/systematic-debugging/SKILL.md`；
  技术可行性验证使用 `references/ease-poc/SKILL.md`。调试文档中的
  `superpowers:test-driven-development` 使用包内 TDD 资料；
  `superpowers:verification-before-completion` 表示完成前执行并读取真实测试/构建证据，
  使用 ease-qa 和阶段门禁验证，不假定外部 superpowers 插件存在。
- 其他 ease-tools、历史 contracts-unified/schemas 等未提供的引用不代表
  已安装功能。需要时检查可用能力；若是强制门禁缺少的资源，应报告缺口并停止，
  不编造 PASS。可选提交/评审工具可用本会话中的常规操作替代。

`conversion-report.json` 记录仍需评估的源外部引用；不要一次性加载全部参考资料。

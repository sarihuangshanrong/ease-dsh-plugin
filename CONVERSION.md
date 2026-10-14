# 转换映射与机制核实

## 命令映射

| 用户入口 | DSH 技能名 | 共享指令 |
|---|---|---|
| /ease:starter | ease-starter | commands/starter.md |
| /ease:flow-1-analyze-brd | ease-flow-1-analyze-brd | commands/flow-1-analyze-brd.md |
| /ease:flow-1-analyze-trd | ease-flow-1-analyze-trd | commands/flow-1-analyze-trd.md |
| /ease:flow-2-design | ease-flow-2-design | commands/flow-2-design.md |
| /ease:flow-3-implement | ease-flow-3-implement | commands/flow-3-implement.md |
| /ease:constitution | ease-constitution | commands/constitution.md |
| /ease:bootstrap-system | ease-bootstrap-system | commands/bootstrap-system.md |
| /ease:analyze-code | ease-analyze-code | commands/analyze-code.md |
| /ease:arch-docs | ease-arch-docs | commands/arch-docs.md |

共享指令和全部领域参考位于 `skills/ease-resources`。该目录没有根 SKILL.md，
DSH 不将它注册为命令；只发现九个入口。这是多入口、共享资源的完整分发包。

## 转换规则

- 命令 frontmatter 完整剥离，description 用于入口，argument-hint 和 skills
  依赖变成正文信息。必需依赖缺失则转换失败。handoffs 不作为原生能力保留。
- 内化 16 个领域目录，保留脚本及可执行权限，领域 SKILL.md 的 frontmatter
  整块删除，防止删除顶层键后遗留嵌套 YAML。
- 明确的 `plugins/ease/skills/` → `references/`、`plugins/ease/templates/`
  → `templates/`、`plugins/ease/commands/` → `commands/`，相对资源根。
- 不再全局替换裸 `templates/`：它常指 ease-testing 或 ease-spec 自己的模板，
  原转换器会误指向共享模板。正文中的局部路径按运行约定解释。
- 源脚本通过 script_adapters.py 做有限安装位置适配：非 Git 项目根、模板回退、
  auto-integrate 自定位。所有替换检查预期匹配数，上游变化时中止并要求重新核查。
- 外部引用保留并输出 occurrence 报告；报告不等于完整 Markdown 链接检查。
- 命令与参考正文中的 Claude 专属行为由 `entry/runtime.md` 明确降级；
  历史源文字保留便于跟进上游，不能把原样复制视为语义等价迁移。

## 调研证据（2026-10-14）

Claude 官方文档说明 commands 已合并到 skills，旧 commands/*.md 仍可使用；
plugin 是分发和命名空间层，移植时需拆开“指令内容”和“运行机制”。
参见 [Skills](https://code.claude.com/docs/en/skills) 与
[Plugin manifest](https://code.claude.com/docs/en/plugins-reference)。

本地 DSH 源码基线 `99f6f02fecdb7dff40c3fbc9470f5907c29f74ca`：

- `packages/skill/skill/src/index.ts`：`isSkillName` 只接受连字符名称；
  `renderSkillContent` 给出资源基目录，正文不执行参数替换。
- `packages/skill/skill-filesystem/src/index.ts`：扫描根的直接子目录 SKILL.md
  或扁平 Markdown；不递归发现领域参考。支持自定义 provider 和 customSkillDirs。
- `packages/skill/tool-skill/src/index.ts`：`SKILL_GESTURE` 不含冒号；原生
  pre-step 校验 user-invocable 后注入技能内容。本项目适配器沿用这些公共接口。
- 源码也支持 `whenToUse`、metadata 和 bundled 根；此前项目说明“仅识别四个键”
  不是完整字段清单。本项目入口只使用 name、description、user-invocable。
- `examples/web-cordis/cordis.yml` 展示 `--patch` 的 insert overlay 格式。

Ease 源基线 `dd6e874ef3ea29ebb9d45eccfcf61fdc2ebc6d7e`，读取本地工作树转换。
本机实际安装 DSH 包验证了名称限制、发现、技能加载、事件注册及参数保留。

## 未宣称完成的验证

没有调用模型执行一轮 BRD/TRD 业务开发，没有做 Windows PowerShell 执行验证、
Web UI 自动补全适配、云端异步提交或 Skills API 托管上传。38 处外部引用是当前
快照的 occurrence 数，重新转换时可能变化。

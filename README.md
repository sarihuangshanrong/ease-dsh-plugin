# ease-dsh-plugin

把 Claude Code 的 Ease SDD 流程迁移到 DeepSeek Harness，保留用户入口：

```text
/ease:starter docs/brd/用户注册.md
/ease:flow-1-analyze-brd docs/brd/用户注册.md
/ease:flow-1-analyze-trd docs/trd/性能优化.md
/ease:flow-2-design <阶段1产物>
/ease:flow-3-implement <权威设计与任务目录>
```

另提供 `/ease:constitution`、`/ease:bootstrap-system`、`/ease:analyze-code`、
`/ease:arch-docs`。BRD 走 1→2→3；TRD 在阶段1完成方案与任务后进入阶段3。

## 快速使用：保留冒号命令

当前 DSH 只允许小写字母、数字和连字符组成技能名，不原生识别 `ease:starter`。
本项目提供 DSH pre-step 插件，把明确的冒号命令加载为底层 `ease-starter` 技能，
保留用户原始参数。无需修改 DSH 源码或持久化 profile 配置。

在本仓库目录执行：

```bash
python3 scripts/convert.py --src ../ease-cc-plugins
node scripts/prepare-runtime.mjs
```

第二条命令输出 overlay 的绝对路径。然后在**你的业务项目目录**启动 DSH，例如：

```bash
dsh --profile web --patch /absolute/path/ease-dsh-plugin/.runtime/ease.patch.yml
```

使用其他已安装 profile 时替换 `web`。默认从 `${DSH_HOME:-~/.dsh}/profiles`
查找 DSH 模块；如果安装布局不同：

```bash
node scripts/prepare-runtime.mjs --modules /path/containing/node_modules
```

overlay 使用绝对路径，移动仓库或升级 DSH 后重新生成。overlay 新增独立的
Ease 文件系统 provider，指向仓库 `skills/`，无需复制安装。冒号入口支持消息开头
的明确命令；不会把引用文档、代码块或助手消息当作调用。当前没有增加 Web UI 的
冒号命令自动补全，手动输入可触发。

## 目录与转换

```text
entry/runtime.md                  手写 DSH 运行约定的真源
runtime/aliases.mjs                冒号命令适配插件
scripts/convert.py                可重复转换器
scripts/prepare-runtime.mjs       生成 profile overlay
skills/ease-starter/SKILL.md       原生合法技能入口
skills/ease-flow-*/SKILL.md        四个阶段入口
skills/ease-*/SKILL.md             四个预处理入口
skills/ease-resources/            全部入口共用的命令、16 个领域资料与模板
skills/ease-manifest.json         命令映射和转换清单
```

这是一套整体交付包；入口和 `ease-resources` 必须相邻，不能只复制某个入口目录。
生成内容不要手工修改：修改转换器或 `entry/runtime.md` 后重新转换。
转换前检查必需输入，先暂存完整产物再替换受管理目录，保留无关目录。
原 `ease-flow` 合并入口已退出本仓库产物。旧安装目录不会被自动删除。

## 复制安装与打包

只需要 DSH 原生命名（如 `/ease-starter`）时可复制安装：

```bash
/absolute/path/ease-dsh-plugin/scripts/install.sh project  # 当前业务项目
/absolute/path/ease-dsh-plugin/scripts/install.sh user     # 用户技能目录
```

复制安装本身不启用冒号入口；冒号入口需使用上面的 overlay。

```bash
./scripts/pack.sh  # dist/ease-dsh-plugin.zip
```

ZIP 包含运行适配器、入口、资源与安装脚本，解压后运行 `prepare-runtime.mjs`。
这是仓库分发包，**不是** Skills API 的单技能上传包。托管单技能分发尚未适配。

## 验证

```bash
python3 scripts/audit_alignment.py --src ../ease-cc-plugins
python3 -m unittest discover -s tests -v
node scripts/prepare-runtime.mjs
node tests/runtime-smoke.mjs
```

测试覆盖重复转换、缺失输入保留旧产物、安装更新、嵌套 frontmatter 清理、模板路径、
真实 DSH 技能发现及 Cordis pre-step 冒号调用。另验证源文件完整性、缺失门禁检测、
非 Git 业务目录与模板回退。完整审计说明见 [ALIGNMENT.md](ALIGNMENT.md)。运行时测试需要已安装 DSH；
可通过 `EASE_DSH_MODULE_ROOT` 指定含 node_modules 的目录。

## 当前边界

- `--async` 云端适配未迁移；命令必须报告不支持并停止，不得静默改为同步。
- `--worktree` 保留源合同和脚本；尚未在 DSH 中做业务需求到代码的完整实测。
- 源库仍有 尚未迁移的 ease-tools、历史 contracts/schemas 等外部或失效引用。
  见 `skills/ease-resources/conversion-report.json`，不可把缺失资源算作门禁通过。
- Claude 的工具授权、model、scripts、handoffs 不作为 DSH 元数据执行。
- 验证基线：本机 DSH CLI `0.1.1-rc.2`；测试不调用付费模型、不修改业务仓库。

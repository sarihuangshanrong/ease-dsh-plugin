# 架构证据、决策与交付契约（2.2）

新生成使用 `content_schema_version=2.2.0`。旧 2.0/2.1 文档仍可执行机械兼容检查，但报告 `overall_result=pending`，不是新的语义交付证书。partial 只升级本次目标，不强制迁移无关文档。

## 快照与校验

先用 `scripts/check_architecture_drift.py --snapshot-only --mode worktree` 捕获源码、配置、测试、ADR 等输入。默认扫描 Git 跟踪及未忽略新增文件，排除 `.eases/`、生成的 `docs/system/`；采用被排除目录中的批准设计时应先将适用约束提取为有批准来源的 ADR，不把过程输出当 observed。`--mode commit --head <sha>` 支持固定提交；涉及 ADR/索引解析的 commit 检查要求 checkout 与目标一致，避免混读。

metadata 增加：

- `snapshot`：脚本输出原样保存。发布时每个本次目标的 `last_generation.per_doc.<file>` 保存 snapshot_id，以及 sources 闭包实际文件的 source_hashes；未发布的其他文档保持旧值。漂移优先比较 source_hashes，旧文档才按 commit diff，避免已记录的未提交实现被重复报过期。
- `document_dependencies.<file>`：`partitions`、正文引用的 `claims`、**传递闭包** `sources`（仓库相对文件/目录，含共享库、全局 ADR）。
- `indexes.<partition>.depends_on`：派生分区依赖。partial 仅加载目标闭包，未更新消费者继续 stale。
- 每个 claim：稳定 id、state、confidence、evidence；派生项 derived_from 引用存在且无环。证据 location 必须是快照中的真实 `path:line`。
- `decision_realization` 项使用 adr_id、constraint_id、realization_status，引用对应决策 claim 和实际执行点；无批准决策明确记录 coverage gap。

运行 `validate_arch_docs.py --strict --repo-root . --docs-dir docs/system --mode full`（partial 加 --documents）。退出码 1 表示机械失败，2 表示机械通过但语义待审，0 才是严格模式完整通过。第一次输出 semantic_result.binding，独立只读 review 使用该 binding 生成报告后，以 `--semantic-review <report>` 重跑。

语义报告含 `binding`、`reviewer`、`result`、`checks[]`、`coverage[]`。每个 check 含 id、result、evidence、counterexample_search；必检 ID：claim-support、coverage-denominator、causal-consistency、decision-realization、mermaid-render。coverage 每行含 object_id 和 view_ids，覆盖 deployable、写入/信任边界、批准约束；缺口不得冒充验证完成。核对全文关键结论与 claim，优先回查高风险结论并补充可复现抽样；检查反例而不是复述生成文本。Mermaid 必须实际解析/渲染，失败回退文本图并记录证据。

冻结输入后完成结构、证据与语义验证；通过后再发布目标文档及 per-doc 基线。临时版本存 `.eases/<change>/arch-docs/.tmp/`，保留旧发布版本直到整批通过；采用同文件系统原子替换与可恢复发布清单，失败不得提前推进基线。共享索引改变时按依赖源标记其他消费者 stale。

## ADR 双维度

- Status 仅表示批准生命周期，Accepted 必须有批准人、时间、来源；已有授权可引用，不重复索要。
- realization 独立为 realized/partial/conflict/not_observed/unknown；实现代码不自动将 Proposed 改为 Accepted。
- Accepted 的 decision/rationale/scope/constraints 不原位改写；变更创建替代 ADR。实施证据允许追加并绑定快照，不能修改原决策内容。
- `docs/adr/NNN-title.md` 使用 `json adr` 块（参见架构设计 reference）。旧 ADR 无结构块只报告 coverage gap，不自动判合规。
- 多子系统使用全局 ADR ID，约束显式 scope 和 effective。尚未生效的约束不因 not_observed 阻断；生效的 partial/conflict/unknown 需要处理后才能严格交付。

`scripts/check_architecture_drift.py --base <baseline> --mode worktree --assessment <assessment.json> --policy warn|block` 只读输出文档影响和独立 decision_findings；无 metadata 仍检查 ADR。源码/暂存/新增/删除/重命名、仅 ADR 修改均采集。文档按各自基线和传递来源判断；未能覆盖影响时返回 unknown，由 Agent 补充语义传播判断，不宣称无漂移。

assessment：`{snapshot_id, decisions:[{adr_id,constraint_id,adr_hash,status,reason,evidence:[{path,hash}]}]}`。必须逐项对照真实实现；有未知不要写 realized。生成者不能通过伪造报告代替独立交付检查。

文档过期、实现违反决策、决策记录冲突、证据不足分别处理。刷新文档只能清除对应 stale_docs，**不得清除 decision_findings**。关闭决策冲突需要同一约束的新实现证据或正式替代 ADR。

## 接入三流程与测试

Flow 2 写入批准 ADR及长期 TC；Flow 3 在最终门禁前补充实现证据、执行漂移检查。普通文档过期可提醒，适用且生效的 ADR 冲突/缺证据在交付检查中阻断；没有 ADR 时不能据此豁免设计一致性检查。

测试设计读取新鲜的关键路径、不变量、故障传播和质量场景，按 `ease-test-case-design/references/durable-test-assets.md` 生成长期 TC 与任务 obligations。arch-docs 不修改测试预期。运行结果是落实证据的一种，单元 Mock 通过不证明真实事务、隔离和恢复机制成立。

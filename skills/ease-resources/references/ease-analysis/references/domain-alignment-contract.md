# 领域对齐契约（Domain Alignment Contract）

本文定义领域事实的持久化基线、DDR、阶段证据、TRD 领域影响守门和 Git 漂移验收。路径、连接键和阈值同时受 `ease-spec/reference/stage-contract.md` 约束。

## 1. 单一事实源

- `docs/domains/${DOMAIN_ID}/usecases/**/{usecase,rules}.md`：当前业务事实。
- `docs/domains/${DOMAIN_ID}/domain-alignment.json`：领域元素状态与需求来源的持久化基线。
- `.eases/${CHANGE_ID}/flow-1-analyze/delta-analysis.md`：单次增量需求的变动说明，不替代持久化基线。
- `.eases/${CHANGE_ID}/flow-2-design/alignment/domain-design-matrix.json`：UC/BR 到设计的阶段证据。
- `.eases/${CHANGE_ID}/flow-3-implement/checklists/domain-implementation-alignment.json`：UC/BR 到代码和测试的实现证据。
- `docs/domains/${DOMAIN_ID}/decisions/`：重要业务语义变化的 DDR 历史。

领域正文只描述业务事实；设计、代码和测试路径放入阶段证据，避免技术重构反复污染业务文档。

## 2. Manifest 最小模型

Manifest 使用 JSON，以保证离线环境可由 Python 标准库读取。结构必须符合 `schemas/domain-alignment.schema.json`。

每个元素至少包含：

- `id`：稳定的 `UC-XXX` 或 `BR-XXX-name` 连接键。
- `kind`：`usecase` 或 `business-rule`。
- `status`：`active`、`deprecated` 或 `superseded`。
- `delta`：`NEW`、`MOD`、`UNCHANGED` 或 `NONE`。
- `source_refs`：需求文档章节、访谈结论或代码证据；活动元素不得为空。
- `decision_required` / `decision_refs`：是否必须记录 DDR 及其相对领域目录的路径。

删除、拆分或替换既有元素时，保留旧 ID 并标记 `deprecated`/`superseded`，禁止静默删除导致下游引用断链。

## 3. 阶段门禁

### Flow 1：领域基线

- Manifest 存在且结构合法。
- UC/BR ID 格式合规且全局唯一。
- 所有活动 UC/BR 均有需求来源。
- `[Δ-NEW]`、`[Δ-MOD]` 元素 100% 进入 Manifest。
- 全新领域也生成初始 baseline，不因缺少 `delta-analysis.md` 跳过。
- 领域边界、Actor/Goal/主流程、聚合不变量/生命周期、核心规则或统一语言正式含义变化时必须创建并索引 DDR。

### Flow 2：设计覆盖

- 生成 `domain-design-matrix.json`。
- 所有本次 `NEW`/`MOD` UC/BR 均至少有一个 `design_refs`，覆盖率必须为 100%。
- 全量设计要点可追溯率继续遵循 stage-contract 的 ≥80% 阈值。
- 澄清若改变 Actor、Goal、主流程、业务规则、统一语言或领域边界，必须 Stop-the-Line，返回 Flow 1 更新领域事实；Flow 2 不得静默修改 UC/BR。

### Flow 3：实现证据

- 生成 `domain-implementation-alignment.json`。
- 每个本次 `NEW`/`MOD` UC/BR 至少有一个 `code_refs` 和一个 `test_refs`。
- 所有证据 ID 必须存在于 Manifest，不允许孤儿引用。
- `drift_status.status=blocking` 或存在未解决漂移时，不得完成 Flow 3。

### TRD Domain Impact Guard

- `.eases/trd/${CHANGE_ID}/flow-1-analyze-trd/validation/domain-impact.json` 为强制工件。
- `impact=none` 保持原 TRD Flow 1 → Flow 3 路径。
- `potential`/`confirmed` 停止 TRD 并转 BRD Flow 1。

### Git 漂移与语义裁决

- `detect_domain_drift.py` 用真实 Git diff 与 Flow 3 `code_refs`/`test_refs` 计算受影响 UC/BR。
- 变更源码中出现的 `UC-*`/`BR-*` 标识也会纳入检测；未知标识或未登记文件在 CI 阻断，防止新增实现绕开证据表。
- 本地提交使用 `warn`，不改变一键 commit/push；CI 使用 `block`。
- 语义裁决只能是 `no-semantic-change`、`aligned-domain-change` 或 `semantic-drift`，且必须覆盖精确提交范围与全部受影响元素。
- 裁决在提交后生成并作为流水线/审批工件输入，以避免让绑定 head SHA 的文件自引用同一 commit。
- 高风险变化必须有 `human_approval`；`semantic-drift` 必须返回 Flow 1。

## 4. 校验器

```bash
python3 references/ease-analysis/scripts/validate_domain_alignment.py \
  --manifest "docs/domains/${DOMAIN_ID}/domain-alignment.json" \
  --phase flow-1

python3 references/ease-analysis/scripts/validate_domain_alignment.py \
  --manifest "docs/domains/${DOMAIN_ID}/domain-alignment.json" \
  --phase flow-2 \
  --matrix ".eases/${CHANGE_ID}/flow-2-design/alignment/domain-design-matrix.json"

python3 references/ease-analysis/scripts/validate_domain_alignment.py \
  --manifest "docs/domains/${DOMAIN_ID}/domain-alignment.json" \
  --phase flow-3 \
  --matrix ".eases/${CHANGE_ID}/flow-2-design/alignment/domain-design-matrix.json" \
  --implementation ".eases/${CHANGE_ID}/flow-3-implement/checklists/domain-implementation-alignment.json"
```

校验器只执行确定性检查；业务语义冲突仍须由需求分析和人工确认裁决。

严格只读组合验收入口：

```bash
python3 references/ease-analysis/scripts/accept_domain_alignment.py \
  --repo-root . --change "${CHANGE_ID}" --domain "${DOMAIN_ID}" --level ci \
  --base "${MERGE_BASE}" --head HEAD \
  --semantic-review ".eases/${CHANGE_ID}/domain-semantic-review.json"
```

CI 细则见 `references/domain-alignment-ci.md`。

## 5. 兼容策略

历史领域采用 touch-to-verify：未触达领域可保持 `legacy-unverified`；某个领域首次被新需求修改时生成 Manifest 并建立 baseline。不得要求一次性补写全部历史证据。

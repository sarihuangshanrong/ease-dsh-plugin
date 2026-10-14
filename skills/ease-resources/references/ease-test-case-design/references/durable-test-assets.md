# 长期 TC 与任务验证契约

本文件是 TC 身份、长期路径、任务选择、迁移和执行证据的唯一权威。适用于 BRD 三流程、TRD 直连实现、generate-tests 及任务中发现的长期回归案例。`docs/qa/` 是质量资产入口，不创建 `docs/testing/`。

## 1. 归属与权限

- 领域 TC：`docs/domains/${DOMAIN_ID}/testcases/[三位编号]-[subdomain]/[三位编号]-[case].md`。
- 跨域 TC：`docs/qa/testcases/cross-domain/[三位编号]-[scenario]/[三位编号]-[case].md`。
- 架构/NFR/技术 TC：`docs/qa/testcases/architecture/[三位编号]-[capability]/[三位编号]-[case].md`。
- 各案例只有一个权威定义；`docs/qa/README.md` 和领域 `testcases/README.md` 是导航，不复制案例正文。
- Flow 2 的测试设计角色可以维护上述 TC 文件；UC/BR 仍由 Flow 1 拥有，不能借 TC 修改业务语义。TRD 不伪造 DOMAIN_ID。
- Flow 3 可补充测试代码关联、缺陷回归 TC 草案；预期结果变化必须回到对应需求/决策 owner。arch-docs 不得覆盖 TC。
- 临时诊断、日志、覆盖率、一次性执行记录留在 `.eases/`；有持续验证价值的目标提升为长期 TC。测试代码留在项目原有测试目录。

## 2. 身份与定义

使用 `templates/durable-test-case.md`：一个文件一个案例，包含唯一的 `json tc` fenced block 作为机器字段；可补充说明，Given/When/Then 不维护第二份副本。

新 ID：领域 `TC-D001-0001`、跨域 `TC-X-0001`、架构 `TC-A-0001`。领域号来自 DOMAIN_ID；四位案例流水号仅为稳定 ID，文件/目录仍使用三位编号。原有合法且唯一 ID 保留。全库检查唯一性，并行分支合并时重分配未发布的冲突 ID；已发布 ID 不复用。

- `revision` 从 1 递增，内容变化必须递增；任务清单另锁定整个文件 SHA256。
- `status=draft|active|deprecated`；active 表示案例获准使用，不代表测试通过。
- `basis[]` 引用 UC/BR、契约、批准 ADR/NFR 的 `{id,path}`。现状观察仅帮助定位风险，不能自动成为正确性依据。
- `architecture_refs[]` 可引用不变量、关键路径、故障传播等稳定 ID。
- `level=unit|integration|contract|system|static|manual|performance`，描述执行所需 environment、数据、准备/清理。单 TC 可映射多个参数化测试方法。
- 同一验证目标变化保留 ID、增加 revision；拆分/合并或独立新目标使用新 ID，并以 `supersedes[]` 记录历史。退役保留文件。
- 草案在工作分支可审查；设计验收后 active。取消任务不将草案提升到主分支正式基线。

## 3. 任务选择与三流程

BRD 选择清单：`.eases/${CHANGE_ID}/flow-2-design/test-cases/test-selection.json`。
TRD 选择清单：`.eases/trd/${CHANGE_ID}/flow-1-analyze-trd/validation/test-selection.json`。
执行记录：`${IMPLEMENTATION_ARTIFACT_DIR}/testing/test-execution.json` 和 `execution-snapshot.json`。

1. Flow 1 识别 UC/BR/技术目标变化及已有 TC 影响，不批量重建案例库。
2. 测试设计前检查本次 API/数据/依赖/ADR 新鲜度；过期部分定向回查，记录 unknown；不得直接信任旧接口清单。
3. Flow 2 或 TRD 验证设计阶段加载已有 TC，按新增/修改/涉及选择复用、改版、新建；ADR、不变量、故障路径和 NFR 都进入验证义务集合。
4. 生成快照和 test-selection（见下方 schema）。设计验收只读校验，案例必须 active；验收后 TC 内容变化使准入失效。
5. Flow 3 消费 TC 定义表达 RED，GREEN 后补覆盖。最终生成独立 execution-snapshot，结果绑定 TC revision/hash、当前快照、环境及证据 hash。
6. 交付时需求/ADR 源 hash 变化必须重做选择；实现代码变化允许产生新执行快照，不能重写历史设计快照冒充已重新验收。
7. 必须执行的案例缺失、blocked、skipped、转交均不是 PASS。人工案例必须有执行人、步骤与可定位记录；静态检查可承担不可用运行测试证明的依赖约束。

选择清单 schema（所有路径仓库相对）：

```json
{
  "schema_version": "1.0",
  "change_id": "001-order-change",
  "snapshot": {"mode": "worktree", "head": "<commit>", "scopes": ["."], "files": {}, "id": "<computed>"},
  "obligations": [{"id": "BR-001-idempotency", "source": "docs/domains/001-order/usecases/001-submit/rules.md", "source_hash": "<sha256>", "tc_ids": ["TC-D001-0001"]}],
  "cases": [{"id": "TC-D001-0001", "revision": 1, "path": "docs/domains/001-order/testcases/001-submit/001-duplicate.md", "hash": "<sha256>", "reason": "事务边界变化，验证重复投递", "required": true}]
}
```

执行记录 schema：

```json
{
  "change_id": "001-order-change",
  "snapshot_id": "<execution-snapshot.id>",
  "results": [{"id": "TC-D001-0001", "revision": 1, "case_hash": "<sha256>", "result": "pass", "method": "tests/order_test.py#test_duplicate", "environment": "local isolated database", "evidence": [{"path": ".eases/001-order-change/flow-3-implement/testing/evidence/run.log", "hash": "<sha256>"}]}]
}
```

机械校验命令（插件目录为工具路径，不是用户项目路径）：

```bash
python3 <ease>/skills/ease-arch-documentation/scripts/check_architecture_drift.py --repo-root . --snapshot-only > <task-dir>/snapshot.json
python3 <ease>/skills/ease-test-case-design/scripts/manage_test_assets.py --repo-root . --selection <selection.json> --admission
python3 <ease>/skills/ease-test-case-design/scripts/manage_test_assets.py --repo-root . --selection <selection.json> --execution <test-execution.json> --execution-snapshot <execution-snapshot.json>
```

报告的 pass 表示引用、快照和执行记录结构一致，独立交付 review 仍须打开证据确认实际执行及有效断言，不能仅因报告存在认定成功。

## 4. 架构测试覆盖

- `invariants` → 正常、违规、绕过路径；唯一键/事务等真实组件语义必须有集成验证，Mock 分支不等于机制验证。
- `critical_paths` → 跨组件成功链和关键状态；`failure_propagations` → 故障注入、隔离、恢复。
- `quality_scenarios` → 指定条件和批准阈值；无阈值不得凭经验编造。
- Accepted ADR 中本次生效约束 → 运行、静态或人工验证。

独立验收比较“本次变更 UC/BR、接口、适用架构风险全集”和 obligations，不能让生成者通过少列分母达到100%。高风险义务全部关联 TC；缺口保留未通过，确不适用则由阶段门禁记录依据，不伪造 TC。业务语义变化回 Flow 1，技术决策变化回架构设计。

## 5. 兼容迁移

`manage_test_assets.py --inventory-legacy` 只读列出旧 `.eases/**/test-case-document.md`、hash 和 TC ID。Agent 根据 UC/BR 与预期行为做语义归属、去重、冲突裁决，将确定案例写入长期目录，并在任务 `migration/tc-mapping.json` 记录 `{old_path,old_id,new_path,new_id,reason}`。不自动合并矛盾预期，不删除旧证据。

消费者优先 test-selection；存在但无效时必须失败，不能退回旧文件。无 selection 的旧任务可只读消费原 `test-case-document.md` 并提示迁移。新任务的同名文件只允许作为从已选 TC 生成的可读投影（保留原 §1–§5 以支持接口报告），不是可编辑权威；不得把投影与长期 TC 双向同步。生成测试、Flow 3 和接口报告都使用同一选择集合。

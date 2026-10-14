<!-- Converted from ease command: bootstrap-system. Read ../runtime.md first. -->

参数提示：`<system-brief-path-or-text> [--design-only] [--worktree=auto|required|reuse|off]`

领域参考（按需读取）：`references/ease-system-bootstrap/SKILL.md`、`references/ease-analysis/SKILL.md`、`references/ease-architecture-design/SKILL.md`、`references/ease-framework-code/SKILL.md`、`references/ease-code-implement/SKILL.md`、`references/ease-testing/SKILL.md`、`references/test-driven-development/SKILL.md`、`references/ease-arch-documentation/SKILL.md`

[Always respond in 中文]

# 绿地系统启动（/ease:bootstrap-system）

你是绿地系统启动编排者。你的任务是把“只有产品意图的空仓库”建设为“拥有已批准目标架构、可运行 Walking Skeleton 和 observed 架构基线的仓库”，然后把后续业务交付交还给现有 BRD/TRD 三流程。

## 边界

- 本命令是一次性预处理，不是 BRD/TRD 的第三条 Track。
- 不修改现有 Flow 1/2/3 的 `DOMAIN_ID`、`CHANGE_ID`、`TRACK`、阶段目录或门禁。
- `docs/architecture/target/` 表示 `approved_intent`；`docs/system/` 只表示从实现提取的 `observed` 事实。
- `--design-only` 在 B2 通过后停止，不生成源代码或 `docs/system/`。
- B3 只实现系统地基，禁止实现业务用例、领域规则、真实生产迁移、真实外部写入或 Secret。

完整路径、工件与门禁以 `ease-system-bootstrap/references/bootstrap-contract.md` 为唯一权威。

## 参数

```text
/ease:bootstrap-system docs/product/system-brief.md
/ease:bootstrap-system "建设统一支付接入平台……"
/ease:bootstrap-system docs/product/system-brief.md --design-only
```

`--worktree` 语义与现有 Ease worktree 合同一致，默认 `auto`。`BOOTSTRAP_ID` 使用三位编号，例如 `001-payment-platform`；分支准入可使用 `change-id=bootstrap-${BOOTSTRAP_ID}`，但过程产物必须写入 `.eases/bootstrap/${BOOTSTRAP_ID}/`。

## 执行前路由

运行：

```bash
references/ease-system-bootstrap/scripts/resolve-architecture-baseline.sh --root .
```

- `empty`：允许开始新 Bootstrap。
- `target_only`：只允许续跑匹配的 Bootstrap，或停止并建议使用普通 `/ease:starter`。
- `observed_missing`：停止，执行 `/ease:arch-docs` 建立存量基线。
- `observed_only` / `hybrid`：停止；该系统已进入存量/演进状态，应使用原三流程。

不得为了继续 Bootstrap 而删除或忽略已有代码和 `docs/system/`。

## B0 → B1 → B2 → B3 → B4

### B0：治理与身份准入

1. 检查 `memory/constitution.md`；不存在则停止并提示先执行 `/ease:constitution`。
2. 从输入锁定系统目标、范围、利益相关者、约束和成功指标。
3. 生成/复用 `BOOTSTRAP_ID`，完成 worktree 准入。
4. 创建 `.eases/bootstrap/${BOOTSTRAP_ID}/context.json` 和 B0 检查清单。

### B1：领域与系统范围

使用 `ease-analysis` 提取业务能力、领域边界、上下文关系、关键场景和统一语言。草稿先写 `.eases/bootstrap/${BOOTSTRAP_ID}/`；经确认的领域事实才进入 `docs/domains/`。

生产者只能提交 `READY_FOR_ADMISSION`。以独立只读第二遍核验范围、来源和相互关系，写入 `checklists/b1-domain-scope.md`；FAIL 时回流 B1。

### B2：目标架构

使用 `ease-architecture-design`，为每项重大决策比较至少两个方案，明确组件/接口/数据/事务/信任/部署边界、错误语义、NFR、验证与回退。

设计草稿写入 `.eases/bootstrap/${BOOTSTRAP_ID}/target-architecture/`。消费者门禁通过后，才提升到 `docs/architecture/target/` 并写入：

```json
{"status":"accepted","bootstrap_id":"${BOOTSTRAP_ID}","evidence_state":"approved_intent"}
```

若指定 `--design-only`，输出未实现声明和下一步命令后停止，不调用 `ease-framework-code`、`ease-code-implement` 或 `/ease:arch-docs`。

### B3：Walking Skeleton

1. 使用 `ease-framework-code` 根据已批准目标架构生成地基骨架与测试骨架。
2. 在修改源代码前使用 `test-driven-development` 建立失败测试。
3. 使用 `ease-code-implement` 只实现构建、入口、配置、健康检查、可观测性、测试和 CI 接缝。
4. 运行构建、目标测试、smoke 和配置验证；命令、退出码与结果写入 `checklists/b3-walking-skeleton.md`。

任何业务逻辑请求必须转为后续 BRD `/ease:starter`，不得在 B3 顺手实现。

### B4：observed 基线与实现对账

只有 B3 已产生可扫描代码/配置/IaC/测试后，才执行 `/ease:arch-docs` 生成 `docs/system/`。

对 `docs/architecture/target/` 的重大声明逐项生成 `docs/architecture/realization-matrix.json`，状态只允许：`realized`、`partial`、`conflict`、`not_observed`。未解释的 `conflict` 阻断完成；其余缺口必须有后续 BRD/TRD owner。

## 完成条件

- B0–B4 消费者门禁全部 PASS；
- 目标与 observed 文档没有事实混写；
- Walking Skeleton 可构建、可测试、可启动或完成等价 smoke 验证；
- 没有业务逻辑和真实 Secret；
- 输出下一个正常 `/ease:starter <第一项业务需求>` 命令。

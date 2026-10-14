# E2E 执行增强（按需读取）

Ease 三流程、需求/长期 TC、任务及门禁是唯一主流程。E2E 只提供生成、运行和取证能力，不引入第四阶段、第二套业务预期或独立完成状态。仅已接入服务的相关工作，或明确安排的接入 TRD，读取本文件；未接入提醒不读取。

## 1. 已接入：按变更范围复用

| 阶段 | 行为与现有产物 |
|---|---|
| BRD Flow 1 | 在 UC/BR 影响分析中识别关键旅程和既有 E2E 场景影响，不改测试预期、不生成部署文件。 |
| BRD Flow 2 | 在现有测试设计中复用或更新长期 TC，把相关系统级场景纳入 test-selection；在现有测试设计/manifest 中记录 TC→runner 方法、真实/Mock 边界、数据准备清理、业务断言、执行命令与前置条件，无需独立 e2e-plan。 |
| TRD Flow 1 | 在 solution-design/validation 完成同样的选择和执行设计，保持直接进入 Flow 3，不要求 Flow 2 或 DOMAIN_ID。 |
| Flow 3 | 复用现有 runner；增量行为先建立相关回归基线，再随实现验证本次选中场景，交付前归档当前运行结果。只补当前需求必要的案例，不全量重建接入。 |

自动启用不等于全量执行。无相关行为影响时在现有测试范围说明中简述依据，不新增 E2E 测试。高风险验证义务不得因少选案例而消失。旧任务按长期 TC 契约兼容原案例来源，不强制全库迁移。

已接入但目录为空、配置不完整、平台不可用时，记录具体缺口；不得回退成未接入或自动重建环境。未选为交付条件的接入缺口仅作为待办；已选必需案例 blocked/skipped 不算 PASS，不能为了放行静默取消选择。继续不依赖该环境的工作，交付结论如实保留阻塞。

## 2. 按操作选择能力

| 本次操作 | 必读输入与执行边界 |
|---|---|
| 仅运行已有案例 | 项目运行入口/配置、本次选择集合；保留现有技术栈与模式，不调用文件生成或重新 onboarding。 |
| 新增/修改 Java 后端案例 | 已批准 TC、现有模式；按 `e2e-technical-rules.md` Java 节核对请求、断言和报告。可用时定向读取 `e2e-test-authoring-java` 对应章节。 |
| 新增/修改 Go 后端案例 | 已批准 TC、现有 runner；必读技术规则 Go 节，核对 body/Content-Type。可用时定向读取 `e2e-test-authoring-go`。 |
| 新增/修改 UI 案例或配置 | 已批准 TC、现有 UI runner；必读技术规则 UI 节。可用时读取 `e2e-ui-e2e` 对应章节，不调用后端 file-gen。 |
| 修改契约/部署/打包/依赖/沙箱配置 | 必读技术规则环境节及实际语言节，检查受影响配置；可用时读取 `e2e-file-gen-java` / `e2e-file-gen-go` 与 onboarding 沙箱自检的相关章节。不重跑完整接入。 |
| 正式实施首次接入 TRD | 在 Ease 已批准任务范围内选择 runner，按需使用 onboarding 信息收集、file-gen、authoring、沙箱自检能力；其内部步骤不是新的 Ease 阶段。 |

修改测试时必须读取相关技术规则，不能用“已有 runner”跳过协议和平台限制。外部技能不是强制安装依赖；缺失时使用随插件分发的技术规则和项目可验证配置。仍不足以确定协议、平台或依赖时，将具体缺口留在当前设计/任务中，暂停依赖它的修改，继续独立工作；不猜测、不自动安装、不宣称生成成功。禁止依赖开发者机器的绝对路径。非本参考支持的 runner 使用项目正式文档，不强套 Java/Go/UI 规则。

## 3. 信息来源与兼容

1. 正确行为由 Ease 需求、批准设计及长期 TC 决定；代码用于核对协议、字段和现状，冲突回 owner，不降低断言。
2. 执行事实优先从现有 runner、构建/沙箱配置、项目文档和已有 `.e2e-onboarding-context.md` 取得；context 是线索，过期内容须与当前配置对账，不复制为新的业务权威。
3. 本次范围、命令、TC 映射和结果进入 Ease 既有设计、manifest、tasks、testing 产物，不新增相同内容的 E2E 计划或状态机。
4. 纯运行不强制创建 `.e2e-onboarding-context.md` / `.e2e-progress.json`。实际调用的生成工具依赖它们时，复用并仅补齐本次所需事实、更新所执行步骤与产物；不重复问已有信息，不将所有步骤重置重跑。
5. progress 的 done 仅表示接入步骤完成，不能替代 Ease 准入或交付结论。

## 4. 模式到 Ease 证据的映射

遵循 `../../ease-test-case-design/references/durable-test-assets.md`，继续使用既有 TC ID、level 和 test-selection/test-execution/execution-snapshot schema。

| 模式 | TC 到执行目标的映射（写入现有 method/manifest） | 保留的原始证据 |
|---|---|---|
| Java Gradle/JUnit（E） | 测试类#方法，参数化执行记录须覆盖本次选中目标 | JUnit XML、逐例平台报告、构建身份与退出状态 |
| Java executor（A/C） | 请求文件#案例标识 | 请求案例结果、实际 assertion_results、退出状态；C 的外部断言证据一起归档 |
| 自定义 runner（B） | 现有入口#场景标识 | 实际断言、场景结果及退出状态，不能仅凭 JAR 执行成功 |
| Go curl | run.sh#场景标识 | 请求/业务断言结果、report.json 与退出状态 |
| UI | spec 路径#测试标题/稳定标识 | UI results、必要 trace/截图、UI 容器退出状态 |
| 日志轮询（D） | runner 路径#验证目标标识 | 本次日志范围、成功/失败匹配、轮询超时设置与实际退出状态；不强制 JUnit 或 JSON 报告 |

- 统一判断“必选目标实际得到验证”，不是强制所有 runner 发现框架测试方法。JUnit/executor/UI 等应发现所选案例；模式 D 无框架案例也可以有效验证，但必须映射到 TC，不能没有验证目标或有效断言。
- 模式 D 按本次 run ID、隔离日志或起始偏移排除历史成功记录；失败匹配和超时均不能判通过。探活 TC 可以验证就绪，不能据此声称业务链路完成。
- 使用现有 `test-execution.json` 的 id/revision/case_hash/method/environment/evidence 字段记录结果；额外命令、run ID、构建/镜像标识写入其引用的运行记录，不擅自扩展 schema。证据归档到 `${IMPLEMENTATION_ARTIFACT_DIR}/testing/` 并绑定当前 execution-snapshot 和 hash。
- 保留原平台报告路径和格式；Ease 归档是在原产物基础上建立关联，不改写平台协议。临时证据过期前取回，UI 与后端分别采集；不能只留下临时链接。
- 逐项核对必选目标与实际结果，不能拿总状态、历史构建或重试成功覆盖首次失败。启动失败、未执行任何有效验证、缺少所需证据都不是业务 RED 或 PASS。

## 5. 验收边界

服务级沙箱必须声明 Mock 边界，不能冒充真实跨系统验证。HTTP 200、code=0 或 UI 请求发出只能证明对应的有限目标，不能替代 TC 要求的业务结果。保留 Ease 的单元/集成 TDD、覆盖率、L2 断言、D-Gate 和适用变异要求；不把单元 I/O 隔离规则解释为 E2E 禁止真实网络。

由 F2-TST-01（TRD 为 T1-DES-01）验收本次范围、断言、数据准备/隔离/清理及执行条件；F3-TST-01/F3-TRC-01 验收必选目标的真实执行与版本证据。不新增独立 E2E 门禁。只读 review 不修改测试或补写产物；缺设计回对应阶段，代码或配置问题回实现。未接入分支按 `e2e-integration.md` 直接结束。

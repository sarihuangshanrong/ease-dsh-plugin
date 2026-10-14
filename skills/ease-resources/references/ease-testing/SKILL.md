# Ease Testing

## Overview

Test generation and quality improvement skill focused on TDD methodology and MC/DC (Modified Condition/Decision Coverage) principles. Generates high-quality unit and integration tests across languages (Java, Go, Python, TypeScript) with proper dependency handling.

## Role Contract

- **主角色 — 测试开发工程师（QA/SDET）**：把已确认的需求和测试案例转化为可靠、可重复的自动化测试，并提供覆盖率与缺陷证据。
- **允许**：创建或修改测试代码、测试夹具与测试专用配置；运行测试和覆盖率；隔离不稳定依赖；报告生产缺陷。
- **禁止**：修改生产代码、降低正确断言来迎合当前实现、把覆盖率数字替代行为验证，或自行决定需求含义。
- **TDD 协作**：本技能负责表达和验证预期行为；生产实现由处于实现模式的 `ease-coding` 负责。测试暴露生产缺陷时，保留失败证据并移交实现，修复后再重新验证。
- **上游与移交**：优先使用 `ease-test-case-design` 的案例文档；需求歧义返回 `ease-analysis`，架构可测性问题返回 `ease-architecture`。

## When to Use

**Use when:**
- User needs to generate or improve tests for existing code
- Code has unclear behavior or high regression risk
- Tests are missing, flaky, or have low coverage
- User wants to follow TDD methodology or MC/DC coverage
- Refactoring requires test verification
- Code has non-deterministic behavior (time, randomness, external dependencies)

**Do NOT use:**
- User wants to write implementation code → Use `ease-coding`
- User wants architecture design → Use `ease-architecture`
- User wants to analyze code structure → Use `ease-analysis`
- User wants code review → Use `code-review`

## Quick Reference

| You want to... | First step | Then go to... |
|----------------|-----------|---------------|
| Generate code from existing test-case doc | Read `test-case-document.md` first | `flows/generate-test-code.md` (Step 0) |
| Add unit tests for a single file | Detect language/framework | `flows/generate-test-code.md` + `references/testing-<lang>.md` |
| Improve coverage to target | Run baseline coverage first | `flows/generate-test-code.md` (round-based strategy) |
| Write integration tests | Verify local dependencies available | `/ease-tools:generate-tests` (--integration/--all) |
| Fix flaky tests | Identify non-determinism sources | `references/testing-<lang>.md` (deterministic section) |
| Standardize test structure | Use Mustache templates | `templates/README.md` + `templates/*` |

## 长期 TC 接入（新任务）

执行前读取 `ease-test-case-design/references/durable-test-assets.md`（相对 `references/`）。领域 TC 保存在 `docs/domains/${DOMAIN_ID}/testcases/`，跨域/架构 TC 在 `docs/qa/testcases/`；不创建 docs/testing。任务只保存 test-selection 和执行证据。

新任务优先读取 BRD `flow-2-design/test-cases/test-selection.json` 或 TRD `flow-1-analyze-trd/validation/test-selection.json`，按 path/revision/hash 加载长期 TC；存在但无效不得回退。下文 `test-case-document.md` 对新任务仅指从所选 TC 生成的只读可读投影，旧任务无 selection 时才兼容旧权威案例文件。接口报告与测试方法必须引用同一集合，不能重新从代码推导并丢弃它。


## Non-negotiables

### Upstream Test-Case Document → Test Code (MUST Check FIRST)

Before deriving test cases from code (white-box), **MUST first check** whether an upstream
requirement-driven test-case document exists:

- **Path**: `.eases/${CHANGE_ID}/flow-2-design/test-cases/test-case-document.md` (produced by `ease-test-case-design` in Phase 2 / flow-2-design §4.5)
- **If it exists**: it is the **primary source** of WHAT to test. Each case (`TC-XXX-NNN`) carries UC/BR traceability, the chosen black-box technique, Given-When-Then, concrete test data, and a 单元/集成 level. Generate test methods FROM these cases and keep the traceability into code (see `flows/generate-test-code.md` Step 0).
- **If it does not exist**: fall back to pure white-box derivation from code.

**CRITICAL**: When the document exists, do NOT silently re-derive cases from code and discard it.
The requirement→case→code traceability chain breaks here if you ignore upstream cases.

### Test Type → Dependency Strategy (MUST Follow)

| Test Type | Purpose | Dependency Handling |
|-----------|---------|---------------------|
| **Unit Tests** | Verify pure business logic and branches (MC/DC) | **MUST isolate** I/O dependencies (DB/Redis/MQ/network/time) via Mock/Fake. Goal: fast, deterministic, repeatable. |
| **Integration Tests** | Verify real component interaction (database, HTTP, messaging) | **PREFER** reproducible local dependencies (TestContainers/embedded/docker-compose) with explicit fallback strategy when unavailable. |

**CRITICAL: Never say "resource layer should never be mocked outright"** - this misleads in unit test context. Instead:
- "Resource layer in integration tests: use real dependencies when possible"
- "Resource layer in unit tests: MUST isolate all I/O"

### Deterministic Requirements (FIRST)

**ALL unit tests MUST be:**
- **F**ast: milliseconds, run frequently
- **I**ndependent: no dependencies between tests, parallel-safe
- **R**epeatable: same result in any environment
- **S**elf-validating: clear pass/fail, no manual inspection
- **T**imely: written before or with production code

**FORBIDDEN in unit tests:**
- `sleep()` / `setTimeout()` - use injected clock
- `Math.random()` - use seeded generator
- Real network calls - Mock all I/O
- Global state - pass parameters

### 确定性隔离硬禁令（D1–D9）

FIRST 是原则，下面 D1–D9 是**可逐条核对的具体禁令**（与下方 Assertion Value Ladder 并列：一个管"测得稳"，一个管"测得对"）。每条标注是否已由 lint 机械化（🔒）或需 D-Gate 人工核对（🧍）。

> **总纲自检**：每个测试必须能作为该类**唯一被执行的测试**而通过——不依赖兄弟测试、共享状态、真实时钟、环境默认值。

| ID | 禁令 | 自检口令 | 检查 |
|----|------|---------|------|
| **D1** 顺序无关 | 禁 `@Order`/`@TestMethodOrder`/等价排序；不得假设任何其他测试已/未执行 | 删掉本测试外的所有测试，它还能通过吗？ | 🔒 C1 |
| **D2** 无共享可变状态 | 禁 static 可变字段承载测试数据；被测静态/单例须 `@BeforeEach` 显式重置并注释；`mockStatic`/`mockConstruction` 须 try-with-resources 或 `@AfterEach` `close()` | 静态/单例是否每测前归零？mockStatic 是否必 close？ | 🧍 D-Gate |
| **D3** 无真实时间 | 禁 `now()`/`currentTimeMillis()`/`nanoTime()`；时间经注入 `Clock.fixed` 或常量；断言不得含运行时时间表达式 | 断言的时间值是 SUT 算出的固定值，还是 `now()` 求值？ | 🔒 C3 + 🧍 |
| **D4** 无无序集合顺序依赖 | `HashMap`/`HashSet` 遍历不得直接与有序集合比较；需顺序改 `LinkedHashMap`/`TreeMap` 或显式排序后断言 | 遍历顺序若变化，断言会失败吗？ | 🧍 D-Gate |
| **D5** 无 sleep 式同步 | 禁 `Thread.sleep`/`setTimeout`；改 `CountDownLatch`/`Awaitility`/同步 Executor/回调；超时不得依赖机器性能 | 等异步用确定性原语吗？超时机器无关吗？ | 🔒 C4 |
| **D6** 无非确定输入 | 断言数据禁来自 `Random`/`UUID.randomUUID()`/自增序列；确需随机固定 seed 并注释 | 断言数据确定吗？随机 seed 了吗？ | 🔒 C5 + 🧍 |
| **D7** 无共享外部资源 | 端口/临时文件/目录由框架分配（`@TempDir`/随机端口）；DB 测试自带准备与清理，不依赖既有数据或固定自增 ID | 外部资源框架分配了吗？DB 自包含吗？ | 🧍 D-Gate |
| **D8** 无环境隐式依赖 | 时区/Locale/编码/行分隔符/文件系统大小写须显式指定，禁系统默认 | TZ/Locale/编码显式了吗？ | 🧍 D-Gate |
| **D9** 无 `@BeforeAll`/`@AfterAll` 可变状态 | 类级钩子只允许创建**不可变** fixture | 类级钩子有可变操作吗？ | 🧍 D-Gate |

**为何 D2/D4/D7/D8/D9 不进 lint**：需作用域/数据流分析（如"`mockStatic` 是否在 try 块内""遍历顺序是否真影响断言"），正则扫描器误报率高——交给 `flows/generate-test-code.md` §7.3.6 的 **D-Gate** 人工门禁。

### Assertion Value (MUST Follow — ranks ABOVE coverage)

> Coverage proves a line was *executed*. An assertion proves the *behavior was verified*. A test
> that executes code but asserts nothing meaningful is a **false positive**: it inflates coverage,
> passes forever, and never catches a bug. Coverage is the means; assertion value is the end.

**The Assertion Value Ladder (every unit test MUST reach Level ≥ 2):**

| Level | Name | What it verifies | Bug-catching power |
|-------|------|------------------|--------------------|
| L0 | **No-op** | nothing (`assertDoesNotThrow`, no assert) | ❌ none — forbidden as the *only* assertion |
| L1 | **Existence** | "something came back" (`isNotNull`, `hasSize(>0)`) | ⚠️ weak — never the *only* assertion |
| L2 | **Exact value / state** | the returned value or post-state equals the expected business value | ✅ catches wrong-value bugs |
| L3 | **Semantic + boundary** | exact value AT the business boundary, plus error code/message on the failing side | ✅✅ catches off-by-one & contract drift |
| L4 | **Interaction contract** | the right collaborator was called the right number of times with the right args (`argThat` exact match), AND no unexpected interactions | ✅✅✅ catches missing/duplicated side effects |

**Every test MUST have at least one assertion at L2 or above tied to the case's business rule (BR-XXX).**
Existence-only tests (`assertThat(result).isNotNull();` and nothing else) are **rejected**.
An auxiliary L1 assertion may remain when the same test also contains an effective L2–L4 assertion
that verifies the associated business rule. The gate evaluates each test's **highest effective
assertion level**; it does not require deleting useful null/shape diagnostics.

**Assertion anti-patterns (FORBIDDEN as the test's primary verification):**
- Asserting only non-null / non-empty / "no exception"
- Asserting on a value the test itself hard-coded into the mock (tautology — see `test-driven-development/testing-anti-patterns.md`)
- `verify(mock).method(any())` when the *arguments* are the business behavior under test → use `argThat` with exact field matching
- Snapshot/`toString()` equality as a substitute for asserting the specific fields that encode the rule
- One assertion covering many behaviors ("assert soup") → split, or use grouped assertions (`assertAll` / `assertThat(obj).extracting(...)`)

**Strengthening rule**: if you wrote an L1 assertion, ask "what *value/state/interaction* does BR-XXX
actually promise?" and add the L2–L4 assertion that pins it down. See the **Assertion Strength Gate**
in `flows/generate-test-code.md` §6.5 and §7.

### Coverage Targets

**Default targets (when project has no config):**
- Line coverage: ≥ 80%
- Branch coverage: ≥ 70%
- Method coverage: ≥ 85%

**Priority: Read project config first** (jaCoCo/jest/pytest config). User-overridable.

> **Coverage is a goal, and assertion value is a separate release gate.** Standard coverage tools
> prove execution but cannot attribute every covered line to a specific assertion. Therefore push
> line ≥ 80 / branch ≥ 70 / method ≥ 85 (or project config), while mapping every required business
> branch to at least one BR-linked L2+ test. Never write a test whose only purpose is to color a
> line green.

**For unreachable code:** Either improve code testability OR allow documented exemption - never write fragile tests just for coverage.

### Project Type Detection (MUST Execute First)

| Language | Signature File | Reference |
|----------|----------------|-----------|
| Java | `pom.xml` or `build.gradle` | `references/testing-java.md` |
| Go | `go.mod` | `references/testing-go.md` |
| Python | `requirements.txt` or `pyproject.toml` | `references/testing-python.md` |
| TypeScript | `package.json` + `tsconfig.json` | `references/testing-typescript.md` |

**Detection priority:** User-specified file extension → Java → TypeScript → Go → Python

## Common Mistakes

| Mistake | Symptom | Fix |
|---------|---------|-----|
| Writing integration tests as unit tests | Slow, environment-dependent, flaky | Unit tests MUST isolate I/O; integration tests use reproducible dependencies (containers) |
| Chasing coverage without confidence | High coverage but regressions still happen | Meet the coverage target and independently require BR-linked L2+ assertions |
| Tests depend on execution order/time | Passes locally, fails in CI | No sleep/random; fixed clock/seeds; isolate external dependencies |
| Over-mocking | Tests drift from real behavior | Mock only boundaries (I/O, external services); core logic uses real objects |
| Weak assertions (L0/L1) | Only `isNotNull`/`assertDoesNotThrow`; coverage green but bugs slip through | Reach Assertion Value Level ≥ 2: assert exact value/state, boundary, and interaction (`argThat`) tied to BR-XXX. See Assertion Value Ladder above |
| Tautological assertions | Asserting the value the test hard-coded into the mock | Assert the *transformation/decision* the SUT performs, not the mock's canned return |
| Assert soup | One test verifies many behaviors with mixed assertions | One behavior per test; use `assertAll`/`extracting` for grouped fields of the same behavior |

## See Also

- `flows/generate-test-code.md` - Complete generation workflow
- `references/testing-java.md` - Java test patterns (JUnit 5 + Mockito + AssertJ)
- `references/testing-go.md` - Go test patterns (testing + testify)
- `references/testing-python.md` - Python test patterns (pytest + pytest-mock)
- `references/testing-typescript.md` - TypeScript test patterns (Jest)
- `templates/README.md` - Mustache templates for consistent test structure
- `/ease-tools:generate-tests` - Command interface with --unit/--integration/--all flags

## Testability Checklist

| Check | Requirement | Refactoring if not met |
|-------|-------------|------------------------|
| Single responsibility | Class/function does one thing | Extract methods/classes |
| Dependency injection | Dependencies via constructor | Use DI container |
| Interface segregation | Depend on interfaces not implementations | Extract interfaces |
| No global state | Avoid singletons/global variables | Pass parameters |
| Pure functions preferred | Same input → same output | Separate side effects |

<!-- Converted from ease command: analyze-code. Read ../runtime.md first. -->

参数提示：`[file_path]`

领域参考（按需读取）：`references/ease-analysis/SKILL.md`

你是一位资深的**逆向工程专家（Reverse Engineering Expert）**，擅长从存量代码中提取业务知识和领域模型。你的核心能力包括：多语言代码分析（Java、Go、Python）、从代码结构逆向推导领域边界、识别隐性业务规则与技术债务、代码到用例的映射与文档化。你采用语言感知的分析策略，按项目特性调整方法，识别多个独立的业务 Domain，拒绝"大一统"思维，为存量系统建立领域知识基线。

> **异步任务检测（优先执行）**
>
> 在执行任何操作前，首先检测用户输入是否包含异步触发标记：
>
> **检测条件**（满足任一即触发）：
> - 输入包含 `[@ease]` 标记
> - 输入包含 `--async` 标记
> - 输入包含 `async` 关键词
>
> **触发逻辑**：
> ```bash
> # 检测用户输入 $ARGUMENTS 或完整会话输入
> if echo "$USER_INPUT" | grep -qE "\[@ease\]|\[async\]|async"; then
>     # 构造完整的原始命令（包含命令前缀和参数）
>     ORIGINAL_COMMAND="/ease:analyze-code $USER_INPUT"
>     # 调用 async-task 技能，将完整原始命令提交到云端
>     使用 Skill 工具调用 "ease:async-task"，参数为 "$ORIGINAL_COMMAND"
>     # 结束当前命令执行，不再继续后续流程
> fi
> ```
>
> **异步触发示例**：
> - `/ease:analyze-code [@ease] 分析 src/main/java 目录下的代码`
> - `/ease:analyze-code --async 分析整个项目`
> - `/ease:analyze-code async 分析 user 模块代码`
>
> **重要**：触发异步任务时，必须将完整的原始命令（包括 `/ease:analyze-code` 前缀）传递给 async-task，以便云端处理时能正确识别来源命令。
>
> **注意**：由命令转发的异步任务会跳过质量检查和澄清流程，直接提交到云端。

依据 **ease-analysis** 技能的指引，针对源代码：`$ARGUMENTS` 开展系统化分析，产出领域模型（Domain Model）、业务用例（Use Case）与业务规则（Business Rule）。

> 💡 **适用场景**：本命令专为**存量系统**设计，在没有 `/docs` 和需求文档的情况下，通过代码分析初始化项目领域信息，与 `flow-1-analyze-brd` 命令形成闭环。

## 使用方法

### 分析指定的源代码文件/目录

```bash
/ease:analyze-code [file_path]
```

> ℹ️ **说明**：本命令仅执行代码分析和领域提取，**不执行 ease-spec 生命周期**。如需执行完整生命周期，请使用 `flow-1-analyze-brd` 命令。

## 核心原则（不可协商）

> ⚠️ **强制要求**：以下原则必须严格执行，不可跳过或简化。

### 1. 多 Domain 划分原则

**禁止将整个项目视为单一 Domain。** 必须基于代码结构识别并划分多个独立的业务 Domain。

- 分析代码的核心模块结构
- 识别不同的业务领域边界
- 每个业务模块作为独立的 Domain
- 每个 Domain 独立输出到 `docs/domains/[编号]-[domain-name]/`

### 2. 语言感知分析原则

**必须先检测项目语言，然后使用对应的语言分析指南。**

支持的语言及对应指南：
- **Java**: `references/code-analysis-java.md`
- **Go**: `references/code-analysis-go.md`
- **Python**: `references/code-analysis-python.md`

## 纲要

触发消息中 `/ease.analyze-code` 之后的文本即为源代码路径。即使下方出现字面量 `{ARGS}`，也假定在本会话中始终可获取该路径。除非用户命令为空，不要要求用户重复描述。

给定该源代码路径，执行以下步骤：

1. **语言检测（不可跳过）**
   - 检测项目使用的编程语言
   - 加载对应的语言分析指南
   - 如果是混合语言项目，按主要语言处理

2. **环境检查与初始化（不可跳过）**
   - 检查 `docs/domains/` 目录是否存在，如不存在则创建
   - 检查 `.eases/reverse-engineering/` 是否存在，如不存在则创建
   - 新执行生成 `RUN_ID=[YYYYMMDDHHMMSS]-[scope-slug]`；续跑必须显式复用已有 `--run-id`

3. **核心模块识别（不可跳过）**
   - 分析项目目录结构
   - 识别业务模块边界
   - **划分多个独立的 Domain（禁止单一 Domain）**
   - 为每个 Domain 生成功能标识（module_name）

4. **生成功能标识与编号**
   - 使用有意义的名词或名词短语，反映业务领域
   - 格式：kebab-case，如 `user-management`, `payment-processing`, `inventory-control`
   - **扫描 `docs/domains/` 目录，获取下一个 domain 编号（三位数字）**
   - **每个识别出的 Domain 都需要独立编号**

5. **创建输出目录（带编号）**
   - 主目录：`docs/domains/[编号]-[module_name]/`（领域模块目录）
   - 子目录结构：
     - `artifacts/` - 生成的工件（API设计、数据模型等）
     - `usecases/` - 业务用例文档（按子领域组织，**每个子领域和用例都带编号**）
     - `diagrams/` - 架构图与关系图（可选）

6. **执行分析流程**
   - 领域模型分析
   - 业务用例提取（拆解到 usecases 目录，**带编号**）
   - 业务规则识别
   - 生成标准化输出

## 语言检测规则

### 检测逻辑

```bash
# 语言检测伪代码
detect_project_language() {
    target_path="$1"
    
    # Java 项目特征
    if [ -f "$target_path/pom.xml" ] || [ -f "$target_path/build.gradle" ] || \
       [ -d "$target_path/src/main/java" ] || \
       find "$target_path" -name "*.java" -type f | head -1 | grep -q .; then
        echo "java"
        return
    fi
    
    # Go 项目特征
    if [ -f "$target_path/go.mod" ] || \
       find "$target_path" -name "*.go" -type f | head -1 | grep -q .; then
        echo "go"
        return
    fi
    
    # Python 项目特征
    if [ -f "$target_path/requirements.txt" ] || [ -f "$target_path/pyproject.toml" ] || \
       [ -f "$target_path/setup.py" ] || [ -f "$target_path/Pipfile" ] || \
       find "$target_path" -name "*.py" -type f | head -1 | grep -q .; then
        echo "python"
        return
    fi
    
    # 默认：未知语言
    echo "unknown"
}
```

### 语言分析指南映射

| 检测结果 | 分析指南 | 关键分析点 |
|---------|---------|-----------|
| java | `references/code-analysis-java.md` | 包结构、Spring 注解、JPA 实体 |
| go | `references/code-analysis-go.md` | 目录结构、接口定义、gRPC proto |
| python | `references/code-analysis-python.md` | Django App、FastAPI Router、Pydantic 模型 |
| unknown | 通用分析 | 目录结构、文件命名、代码注释 |

### 使用方式

1. 执行语言检测
2. 读取对应的语言分析指南
3. 按照指南中的规则进行代码分析
4. 严格遵循指南中的 Domain 划分策略

## 编号规则（不可协商）

> ⚠️ **重要**：所有目录和文件都必须带有三位递增编号，以提高可视化和排序效果。

### 编号生成规则

1. **新增 domain 时**：

   - 扫描 `docs/domains/` 目录下现有的 `[编号]-*` 目录
   - 取最大编号 + 1 作为新编号
   - 格式：三位数字，如 001, 002, 003
   - 示例：现有 `001-user-management`，新增 `002-payment-processing`
2. **新增 subdomain 时**：

   - 扫描 `docs/domains/[编号]-[module_name]/usecases/` 目录下现有的 `[编号]-*` 目录
   - 取最大编号 + 1 作为新编号
   - 示例：现有 `001-authentication`，新增 `002-registration`
3. **新增 subdomain 时**：

   - 扫描 `docs/domains/[编号]-[module_name]/usecases/` 目录下现有的 `[编号]-*` 目录
   - 取最大编号 + 1 作为新编号
   - 示例：现有 `001-authentication`，新增 `002-registration`
   - 每个子领域目录固定包含 `usecase.md` 和 `rules.md` 两个文件

### 编号检测伪代码

```bash
# 获取 domain 的下一个编号
get_next_domain_number() {
    max_num=$(ls -d docs/domains/[0-9][0-9][0-9]-* 2>/dev/null | \
              sed 's/.*\/\([0-9]\{3\}\)-.*/\1/' | \
              sort -rn | head -1)
    if [ -z "$max_num" ]; then
        echo "001"
    else
        printf "%03d" $((10#$max_num + 1))
    fi
}

# 获取 subdomain 的下一个编号
get_next_subdomain_number() {
    domain_dir="$1"
    max_num=$(ls -d "$domain_dir/usecases/"[0-9][0-9][0-9]-* 2>/dev/null | \
              sed 's/.*\/\([0-9]\{3\}\)-.*/\1/' | \
              sort -rn | head -1)
    if [ -z "$max_num" ]; then
        echo "001"
    else
        printf "%03d" $((10#$max_num + 1))
    fi
}
```

## 实施步骤

你必须严格按照以下步骤执行分析任务：

### 步骤 1：语言检测与指南加载（不可跳过）

```bash
# 使用 TodoWrite 创建任务跟踪
TodoWrite:
  todos: [
    {content: "检测项目语言并加载分析指南", status: "pending"},
    {content: "创建 docs/domains 目录", status: "pending"},
    {content: "分析项目结构识别核心模块", status: "pending"},
    {content: "划分多个独立的 Domain", status: "pending"},
    {content: "扫描现有编号并生成新编号", status: "pending"},
    {content: "为每个 Domain 创建带编号的输出目录", status: "pending"},
    {content: "执行领域模型分析", status: "pending"},
    {content: "生成详细工作计划（包含所有 Domain、Subdomain 和用例任务）", status: "pending"},
    {content: "检查工作计划并识别断点续做位置", status: "pending"},
    {content: "按工作计划提取业务用例到带编号的 usecases 目录", status: "pending"},
    {content: "实时更新工作计划状态", status: "pending"},
    {content: "识别业务规则", status: "pending"},
    {content: "生成分析报告", status: "pending"},
    {content: "验证工作计划完成度", status: "pending"}
  ]
```

#### 1.1 检测项目语言

```bash
# 检测项目语言
LANG=$(detect_project_language "$ARGUMENTS")
echo "检测到项目语言: $LANG"

# 根据语言加载对应的分析指南
case $LANG in
    java)
        GUIDE="references/code-analysis-java.md"
        echo "使用 Java 分析指南"
        ;;
    go)
        GUIDE="references/code-analysis-go.md"
        echo "使用 Go 分析指南"
        ;;
    python)
        GUIDE="references/code-analysis-python.md"
        echo "使用 Python 分析指南"
        ;;
    *)
        GUIDE="通用分析"
        echo "使用通用分析规则"
        ;;
esac
```

#### 1.2 创建必要目录

```bash
# 创建目录结构
mkdir -p docs/domains
```

### 步骤 2：核心模块识别与 Domain 划分（不可协商）

> ⚠️ **强制要求**：必须识别并划分多个独立的 Domain，禁止将整个项目视为单一 Domain。

#### 2.1 分析项目结构

根据检测到的语言，按照对应指南分析项目结构：

**Java 项目**：
- 分析包结构（package structure）
- 识别业务模块（如 `com.example.user`, `com.example.order`）
- 每个顶层业务包作为一个 Domain

**Go 项目**：
- 分析目录结构
- 识别 `internal/` 或 `services/` 下的业务子目录
- 每个业务子目录作为一个 Domain

**Python 项目**：
- 分析 Django App 或 FastAPI Router
- 识别 `apps/` 下的应用或 `api/` 下的路由模块
- 每个应用/模块作为一个 Domain

#### 2.2 Domain 划分输出

```markdown
## 识别的 Domain 列表

### Domain 1: user-management
- 路径: [源码路径]
- 核心实体: User, UserProfile, Role
- 主要服务: UserService, AuthService

### Domain 2: order-management
- 路径: [源码路径]
- 核心实体: Order, OrderItem, Payment
- 主要服务: OrderService, PaymentService

### Domain 3: ...
```

### 步骤 3：扫描编号并创建目录

1. **扫描现有编号**：
   - 扫描 `docs/domains/` 获取当前最大 domain 编号
   - 例如：现有 `001-user-management`，则新编号从 `002` 开始
2. **为每个识别的 Domain 创建目录**：
   ```bash
   # 为每个 Domain 创建目录
   for domain in $DOMAINS; do
       DOMAIN_NUM=$(get_next_domain_number)
       mkdir -p "docs/domains/${DOMAIN_NUM}-${domain}"/{artifacts,usecases,diagrams}
   done
   ```

### 步骤 4：领域模型分析

按照 ease-analysis 技能的 `flows/extract-domains.md` 流程，**对每个 Domain 独立执行**：

1. **阶段 1：Language & Global Understanding**
   - 提取并统一业务术语（Ubiquitous Language）
   - 识别核心域、支撑域与通用域

2. **阶段 2：Strategic Design**
   - 定义限界上下文（Bounded Contexts）
   - 创建上下文映射（Context Mapping）

3. **阶段 3：Tactical Design**
   - 识别聚合根与聚合
   - 建模实体与值对象
   - 定义关系与领域事件

4. **阶段 4：Output Generation**
   - 使用模板 `templates/system-domains-template.md` 生成文档
   - 原始报告输出到 `.eases/reverse-engineering/${RUN_ID}/domains/[编号]-[module_name]/analysis-report.md`
   - 审核确认后的领域事实更新到 `docs/domains/[编号]-[module_name]/domain-overview.md`、`usecases/` 与 `artifacts/`
   - 验证模型的完整性与一致性

### 步骤 4.5：生成详细工作计划（不可跳过）

> ⚠️ **重要**：在完成领域模型分析并识别所有 Subdomain 后，必须生成一份严格详细的工作计划，确保后续用例拆解能完整执行，并支持断点续做。

#### 4.5.1 工作计划生成时机

在以下条件满足后立即生成工作计划：
- ✅ 所有 Domain 的领域模型分析已完成
- ✅ 所有 Subdomain 已识别并编号
- ✅ 每个 Subdomain 需要生成的用例已初步识别

#### 4.5.2 工作计划文件位置

**全局工作计划**：`.eases/reverse-engineering/${RUN_ID}/workplan.md`

**Domain 级工作计划**（可选）：`.eases/reverse-engineering/${RUN_ID}/domains/[编号]-[module_name]/workplan.md`

#### 4.5.3 工作计划格式规范

工作计划必须使用以下严格的 Markdown 格式：

```markdown
# 代码分析工作计划 (Code Analysis Work Plan)

## 元数据 (Metadata)

- **生成时间**: [YYYY-MM-DD HH:mm:ss]
- **项目语言**: [java/go/python/unknown]
- **源代码路径**: [原始路径]
- **总 Domain 数**: [数量]
- **总 Subdomain 数**: [数量]
- **总用例任务数**: [数量]
- **执行状态**: [pending/in_progress/completed]
- **最后更新时间**: [YYYY-MM-DD HH:mm:ss]

## 执行进度概览 (Progress Overview)

- **已完成 Domain**: [数量] / [总数]
- **已完成 Subdomain**: [数量] / [总数]
- **已完成用例**: [数量] / [总数]
- **总体完成度**: [百分比]%

## Domain 任务列表 (Domain Tasks)

### Domain 1: [编号]-[module_name]

- **状态**: [pending/in_progress/completed]
- **路径**: [源码路径]
- **核心实体**: [实体列表]
- **Subdomain 数量**: [数量]
- **用例任务数量**: [数量]
- **开始时间**: [时间戳或空]
- **完成时间**: [时间戳或空]

#### Subdomain 1: [编号]-[subdomain-name]

- **状态**: [pending/in_progress/completed]
- **目录路径**: `docs/domains/[编号]-[module_name]/usecases/[编号]-[subdomain-name]/`
- **用例任务列表**:
  - [ ] **任务 UC-001**: [用例名称]
    - 状态: [pending/in_progress/completed]
    - 文件: `usecase.md` (需包含此用例)
    - 规则文件: `rules.md` (需包含相关规则)
    - 依赖: [依赖的其他用例或规则]
    - 开始时间: [时间戳或空]
    - 完成时间: [时间戳或空]
  - [ ] **任务 UC-002**: [用例名称]
    - 状态: [pending/in_progress/completed]
    - 文件: `usecase.md`
    - 规则文件: `rules.md`
    - 依赖: [依赖]
    - 开始时间: [时间戳或空]
    - 完成时间: [时间戳或空]

#### Subdomain 2: [编号]-[subdomain-name]

[同上格式]

### Domain 2: [编号]-[module_name]

[同上格式]

## 任务依赖关系 (Task Dependencies)

### 依赖图

```
Domain 1 → Subdomain 1 → UC-001
Domain 1 → Subdomain 1 → UC-002 (依赖 UC-001)
Domain 1 → Subdomain 2 → UC-003
Domain 2 → Subdomain 1 → UC-004
```

### 关键路径

1. Domain 1 → Subdomain 1 → UC-001 → UC-002
2. Domain 1 → Subdomain 2 → UC-003
3. Domain 2 → Subdomain 1 → UC-004

## 执行检查点 (Checkpoints)

### 检查点 1: 领域模型完成
- [ ] 所有 Domain 的领域模型分析已完成
- [ ] 所有 Subdomain 已识别
- [ ] 工作计划已生成

### 检查点 2: 用例提取进行中
- [ ] 开始执行用例提取
- [ ] 每完成一个 Subdomain 更新状态

### 检查点 3: 用例提取完成
- [ ] 所有 Subdomain 的 usecase.md 已生成
- [ ] 所有 Subdomain 的 rules.md 已生成
- [ ] 所有用例任务状态为 completed

## 断点续做说明 (Resume Instructions)

### 如何从断点继续

1. **检查工作计划状态**：
   ```bash
   # 读取工作计划
   cat ".eases/reverse-engineering/${RUN_ID}/workplan.md"
   ```

2. **识别未完成任务**：
   - 查找状态为 `pending` 或 `in_progress` 的任务
   - 检查文件是否存在但未完成

3. **继续执行**：
   - 从第一个 `pending` 状态的任务开始
   - 按依赖关系顺序执行
   - 每完成一个任务立即更新工作计划状态

### 状态更新规则

- **pending**: 任务尚未开始
- **in_progress**: 任务正在执行中（设置开始时间）
- **completed**: 任务已完成（设置完成时间，验证文件存在）

## 验证清单 (Validation Checklist)

### 每个 Subdomain 完成后验证

- [ ] `usecase.md` 文件存在且内容完整
- [ ] `rules.md` 文件存在且内容完整
- [ ] 用例文档中仅引用规则 ID，不复制规则细节
- [ ] 所有引用的规则 ID 在 rules.md 中存在
- [ ] 用例流程至少包含 3 个操作步骤
- [ ] 业务规则已按类型分类（Constraints、Computations、Inferences、Action Enablers）

### 所有任务完成后验证

- [ ] 所有 Domain 的用例提取已完成
- [ ] 所有文件格式符合模板要求
- [ ] 所有编号正确且连续
- [ ] 工作计划中所有任务状态为 completed
```

#### 4.5.4 工作计划生成步骤

1. **收集所有 Domain 和 Subdomain 信息**
   - 遍历所有已创建的 Domain 目录
   - 从领域模型分析结果中提取 Subdomain 列表
   - 从代码分析中初步识别每个 Subdomain 的用例

2. **构建任务列表**
   - 为每个 Subdomain 创建任务项
   - 为每个用例创建子任务项
   - 识别任务依赖关系

3. **生成工作计划文件**
   - 使用上述格式规范生成 `.eases/reverse-engineering/${RUN_ID}/workplan.md`
   - 所有任务初始状态设置为 `pending`
   - 记录生成时间和元数据

4. **验证工作计划完整性**
   - 确保所有 Domain 都已包含
   - 确保所有 Subdomain 都已包含
   - 确保所有初步识别的用例都已包含
   - 确保编号正确且连续

### 步骤 4.6：检查工作计划并断点续做（不可跳过）

> ⚠️ **重要**：在执行用例提取前，必须先检查工作计划，支持从断点继续执行。

#### 4.6.1 工作计划检查

1. **检查工作计划是否存在**
   ```bash
   if [ -f ".eases/reverse-engineering/${RUN_ID}/workplan.md" ]; then
       echo "发现现有工作计划，检查断点续做"
       # 读取工作计划
       # 识别未完成任务
   else
       echo "未发现工作计划，需要先执行步骤 4.5 生成工作计划"
       # 提示用户或自动生成
   fi
   ```

2. **识别执行状态**
   - 读取工作计划文件
   - 查找所有状态为 `pending` 或 `in_progress` 的任务
   - 检查对应文件是否存在但未完成
   - 确定断点位置

3. **验证文件完整性**
   - 对于状态为 `completed` 的任务，验证文件是否存在
   - 如果文件不存在但状态为 `completed`，将状态重置为 `pending`
   - 如果文件存在但状态为 `pending`，检查内容是否完整

#### 4.6.2 断点续做策略

1. **确定起始点**
   - 找到第一个状态为 `pending` 的 Domain
   - 在该 Domain 中找到第一个状态为 `pending` 的 Subdomain
   - 在该 Subdomain 中找到第一个状态为 `pending` 的用例任务

2. **按依赖关系执行**
   - 检查任务依赖关系
   - 确保依赖的任务已完成
   - 按顺序执行未完成的任务

3. **更新工作计划**
   - 每开始一个任务，将状态更新为 `in_progress`，记录开始时间
   - 每完成一个任务，将状态更新为 `completed`，记录完成时间
   - 实时更新总体进度概览

### 步骤 5：业务用例提取（带编号拆解到 usecases 目录）

> ⚠️ **重要**：
> 1. usecases 必须从 ease-analysis 技能的 `flows/extract-usecases.md` 流程产出，**所有子领域和用例文件都必须带三位编号**。
> 2. **必须严格按照工作计划执行**，每完成一个任务立即更新工作计划状态。
> 3. **支持断点续做**，从工作计划中识别未完成任务并继续执行。

#### 5.1 执行前准备

1. **读取工作计划**
   ```bash
   # 读取全局工作计划
   WORKPLAN=".eases/reverse-engineering/${RUN_ID}/workplan.md"
   if [ ! -f "$WORKPLAN" ]; then
       echo "错误：工作计划不存在，请先执行步骤 4.5 生成工作计划"
       exit 1
   fi
   ```

2. **识别待执行任务**
   - 从工作计划中提取所有状态为 `pending` 或 `in_progress` 的任务
   - 按 Domain → Subdomain → UseCase 的顺序组织
   - 检查依赖关系，确保依赖任务已完成

3. **初始化执行上下文**
   - 记录当前执行时间
   - 准备状态更新机制

#### 5.2 按工作计划执行用例提取

**对每个 Domain 按工作计划独立执行**：

1. **检查 Domain 状态**
   - 如果 Domain 状态为 `completed`，跳过该 Domain
   - 如果 Domain 状态为 `pending`，更新为 `in_progress`

2. **对每个 Subdomain 执行**：
   
   a) **检查 Subdomain 状态**
      - 如果 Subdomain 状态为 `completed`，验证文件存在后跳过
      - 如果 Subdomain 状态为 `pending`，更新为 `in_progress`，记录开始时间
   
   b) **创建 Subdomain 目录**
      - 扫描 `docs/domains/[编号]-[module_name]/usecases/` 获取下一个 subdomain 编号
      - 创建目录：`docs/domains/[编号]-[module_name]/usecases/[编号]-[subdomain-name]/`
   
   c) **执行用例提取流程**
      - 按照 ease-analysis 的 `flows/extract-usecases.md` 流程执行
      - **严格按照工作计划中的用例任务列表执行**
      - 对每个用例任务：
         - 检查任务状态，如果为 `completed` 且文件存在，跳过
         - 如果为 `pending`，更新为 `in_progress`，记录开始时间
         - 执行用例分析，生成用例内容
         - 识别相关业务规则
         - 更新任务状态为 `completed`，记录完成时间
   
   d) **生成 Subdomain 文档**
      - 生成 `usecase.md`：包含该 Subdomain 下的所有用例（按工作计划中的用例列表）
      - 生成 `rules.md`：包含该 Subdomain 下的所有业务规则
      - 确保用例文档中仅引用规则 ID，规则详细信息在 rules.md 中
   
   e) **更新 Subdomain 状态**
      - 验证 `usecase.md` 和 `rules.md` 文件存在且内容完整
      - 更新工作计划中该 Subdomain 的状态为 `completed`
      - 记录完成时间

3. **更新 Domain 状态**
   - 检查该 Domain 下所有 Subdomain 是否已完成
   - 如果全部完成，更新 Domain 状态为 `completed`，记录完成时间

#### 5.3 实时更新工作计划

**每完成一个任务后立即更新工作计划**：

1. **更新任务状态**
   - 将任务状态从 `pending` 或 `in_progress` 更新为 `completed`
   - 记录完成时间戳

2. **更新进度概览**
   - 重新计算已完成 Domain 数量
   - 重新计算已完成 Subdomain 数量
   - 重新计算已完成用例数量
   - 更新总体完成度百分比

3. **更新最后更新时间**
   - 更新元数据中的"最后更新时间"字段

#### 5.4 执行验证

**每个 Subdomain 完成后执行验证**：

- [ ] `usecase.md` 文件存在且内容完整
- [ ] `rules.md` 文件存在且内容完整
- [ ] 用例文档中仅引用规则 ID，不复制规则细节
- [ ] 所有引用的规则 ID 在 rules.md 中存在
- [ ] 用例流程至少包含 3 个操作步骤
- [ ] 业务规则已按类型分类
- [ ] 工作计划状态已更新

**所有任务完成后执行最终验证**：

- [ ] 所有 Domain 的用例提取已完成
- [ ] 所有文件格式符合模板要求
- [ ] 所有编号正确且连续
- [ ] 工作计划中所有任务状态为 `completed`
- [ ] 工作计划中的进度概览显示 100% 完成

#### usecases 目录结构示例

> ⚠️ **重要**：每个子领域目录固定包含 `usecase.md` 和 `rules.md` 两个文件，与 `flow-1-analyze-brd.md` 保持一致。

```
docs/domains/001-user-management/usecases/
├── 001-authentication/                    # 子领域1：认证（编号 001）
│   ├── usecase.md                         # 用例文档：认证相关用例（登录、登出、刷新令牌等）
│   └── rules.md                           # 用例规则：认证业务规则、约束、成功标准
├── 002-registration/                      # 子领域2：注册（编号 002）
│   ├── usecase.md                         # 用例文档：注册相关用例（邮箱注册、验证、完善资料等）
│   └── rules.md                           # 用例规则：注册业务规则、约束、成功标准
└── 003-password-management/               # 子领域3：密码管理（编号 003）
    ├── usecase.md                         # 用例文档：密码管理相关用例（重置密码、修改密码等）
    └── rules.md                           # 用例规则：密码管理业务规则、约束、成功标准
```

### 步骤 6：生成标准化输出

**为每个 Domain 独立生成**以下文档：

#### 6.1 原始分析报告 (`.eases/reverse-engineering/${RUN_ID}/domains/${DOMAIN_ID}/analysis-report.md`)

```markdown
# Code Analysis Report: [Module Name]

## Executive Summary
[简要总结分析结果]

## Source Code Overview
[源代码结构概述]

## Domain Model

### Core Domains
[核心域描述]

### Bounded Contexts
[限界上下文列表]

### Entities and Relationships
[实体关系图描述]

## Business Use Cases

### Primary Use Cases
1. [用例1：名称、描述、参与者]
2. [用例2：...]

### Secondary Use Cases
1. [次要用例列表]

## Business Rules

### Functional Rules
1. [规则1：条件-行动]
2. [规则2：...]

### Non-functional Rules
1. [性能规则]
2. [安全规则]
3. [合规规则]

## Technical Insights
[从代码中发现的技术细节]

## Assumptions and Constraints
[假设和限制]

## Appendices

### Glossary
[术语表]

### Code References
[关键代码引用]
```

#### 6.2 工件文件 (artifacts/)

- `api-design.md` - API设计规范（从代码中提取）
- `data-model.md` - 数据模型描述（从代码中提取）
- `db-schema.sql` - 数据库模式定义（如适用）

**格式要求：** 所有工件文件必须使用Markdown或SQL格式，禁止使用JSON、YAML等其他文件格式。

### 步骤 7：完成与验证

#### 7.1 工作计划最终验证

1. **验证工作计划完整性**
   - 检查工作计划中所有任务状态是否为 `completed`
   - 验证所有标记为 `completed` 的任务对应的文件确实存在
   - 检查进度概览是否显示 100% 完成

2. **验证文件完整性**
   - 遍历所有 Domain 目录
   - 验证每个 Subdomain 的 `usecase.md` 和 `rules.md` 文件存在
   - 检查文件内容是否符合模板要求

3. **验证编号连续性**
   - 检查所有 Domain 编号是否连续
   - 检查所有 Subdomain 编号是否连续
   - 检查所有用例编号是否连续

#### 7.2 生成最终报告

1. **更新工作计划元数据**
   - 将执行状态更新为 `completed`
   - 更新最后完成时间
   - 记录最终统计信息

2. **生成执行摘要**
   - 统计总 Domain 数
   - 统计总 Subdomain 数
   - 统计总用例数
   - 统计总业务规则数
   - 记录执行总时长（如果有时间戳）

#### 7.3 完成与汇报

1. 将任务清单全部标记为已完成
2. 向用户汇报分析结果与生成文档路径，包括：
   - **工作计划位置**：`.eases/reverse-engineering/${RUN_ID}/workplan.md`
   - **检测到的项目语言**
   - **识别的 Domain 数量及名称**
   - **每个 Domain 的 Subdomain 数量**
   - **每个 Domain 的用例数量**
   - **总体完成度**
3. 提示用户：
   - 如果执行中断，下次执行时会自动从断点继续
   - 可以查看工作计划了解详细进度
   - 后续可使用 `flow-1-analyze-brd` 命令执行 Phase 1 的 ease-spec 生命周期

## 输出位置

长期领域事实与逆向分析过程必须分层存放：

> ⚠️ **注意**：每个识别的 Domain 都会生成独立的目录结构。

```
docs/
└── domains/                                     # 领域模块根目录（不可协商）
    ├── 001-user-management/                     # Domain 1: 用户管理
    │   ├── domain-overview.md                   # 审核确认后的当前领域概览
    │   ├── artifacts/                           # 生成的工件
    │   │   ├── api-design.md                    # API设计规范（Markdown格式）
    │   │   ├── data-model.md                    # 数据模型描述
    │   │   └── db-schema.sql                    # 数据库模式定义（如适用）
    │   ├── diagrams/                            # 架构图与关系图（可选）
    │   └── usecases/                            # 用例文档
    │       ├── 001-authentication/              # 子领域1：认证
    │       │   ├── usecase.md                   # 用例文档（固定文件名）
    │       │   └── rules.md                     # 规则文档（固定文件名）
    │       └── 002-registration/                # 子领域2：注册
    │           ├── usecase.md
    │           └── rules.md
    ├── 002-order-management/                    # Domain 2: 订单管理
    │   ├── domain-overview.md
    │   ├── artifacts/
    │   └── usecases/
    │       ├── 001-order-creation/
    │       │   ├── usecase.md
    │       │   └── rules.md
    │       └── 002-order-fulfillment/
    │           ├── usecase.md
    │           └── rules.md
    └── 003-payment-processing/                  # Domain 3: 支付处理
        ├── domain-overview.md
        ├── artifacts/
        └── usecases/
            └── 001-payment/
                ├── usecase.md
                └── rules.md

.eases/
└── reverse-engineering/${RUN_ID}/               # 单次逆向分析过程
    ├── workplan.md                              # 全局断点续做状态
    └── domains/
        ├── 001-user-management/
        │   ├── analysis-report.md               # 原始分析报告
        │   └── workplan.md                      # Domain 级计划（可选）
        └── ...
```

**重要：** 
- 所有文档必须使用 Markdown 或 SQL 格式，禁止使用 JSON、YAML 等其他文件格式。
- **工作计划文件** `.eases/reverse-engineering/${RUN_ID}/workplan.md` 是执行断点续做的关键文件，必须妥善保存。

## 与 flow-1-analyze-brd 的关系

本命令与 `flow-1-analyze-brd` 命令形成闭环：

| 特性               | analyze-code                           | flow-1-analyze-brd                     |
| ------------------ | -------------------------------------- | -------------------------------------- |
| 输入源             | 源代码                                 | 业务需求文档                           |
| 适用场景           | 存量系统、无需求文档                   | 新项目、有需求文档                     |
| 输出目录           | `docs/domains/[编号]-[module_name]/` | `docs/domains/[编号]-[module_name]/` |
| 过程报告           | `.eases/reverse-engineering/${RUN_ID}/.../analysis-report.md` | `.eases/${CHANGE_ID}/flow-1-analyze/outputs/analysis-report.md` |
| 长期领域事实       | `docs/domains/${DOMAIN_ID}/domain-overview.md + usecases/` | `docs/domains/${DOMAIN_ID}/domain-overview.md + usecases/` |
| ease-spec 生命周期 | **不执行**                       | 完整执行                               |
| 目录结构           | **完全一致**                     | **完全一致**                     |

### 闭环工作流

```
存量系统（无需求文档）          新项目（有需求文档）
        │                              │
        ▼                              ▼
  analyze-code                   flow-1-analyze-brd
        │                              │
        ▼                              ▼
docs/domains/[编号]-[module_name]/    docs/domains/[编号]-[module_name]/
        │                              │
        └──────────┬───────────────────┘
                   ▼
          统一的领域模型目录结构
                   │
                   ▼
          后续可执行 ease-spec 生命周期
```

## 质量标准

- 领域模型必须覆盖所有核心业务概念
- 用例必须包含明确的参与者、目标和步骤
- 业务规则必须是可验证的
- 输出格式必须符合模板规范
- **所有目录和文件必须带三位编号**
- **目录结构必须与 flow-1-analyze-brd 保持一致**

## 示例

### 示例 1：Java 项目分析

输入：

```bash
/ease:analyze-code src/main/java/com/example
```

执行过程：

```
1. 语言检测: Java (检测到 pom.xml 和 *.java 文件)
2. 加载分析指南: references/code-analysis-java.md
3. 核心模块识别:
   - com.example.user → Domain: user-management
   - com.example.order → Domain: order-management
   - com.example.payment → Domain: payment-processing
   - com.example.common → 跳过（通用模块）
4. Domain 划分: 3 个独立 Domain
```

输出：

```
docs/domains/
├── 001-user-management/
│   ├── domain-overview.md                      # 审核确认后的领域事实
│   ├── artifacts/
│   │   ├── api-design.md
│   │   └── data-model.md
│   └── usecases/
│       ├── 001-authentication/
│       │   ├── usecase.md                      # 包含所有认证相关用例
│       │   └── rules.md                        # 包含所有认证相关规则
│       └── 002-registration/
│           ├── usecase.md
│           └── rules.md
├── 002-order-management/
│   ├── domain-overview.md
│   ├── artifacts/
│   └── usecases/
│       └── 001-order-lifecycle/
│           ├── usecase.md
│           └── rules.md
└── 003-payment-processing/
    ├── domain-overview.md
    ├── artifacts/
    └── usecases/
        └── 001-payment/
            ├── usecase.md
            └── rules.md

.eases/reverse-engineering/${RUN_ID}/
├── workplan.md                                 # 全局断点续做状态
└── domains/
    ├── 001-user-management/analysis-report.md
    ├── 002-order-management/analysis-report.md
    └── 003-payment-processing/analysis-report.md
```

**工作计划示例** (`.eases/reverse-engineering/${RUN_ID}/workplan.md`):

```markdown
# 代码分析工作计划 (Code Analysis Work Plan)

## 元数据 (Metadata)

- **生成时间**: 2024-01-15 10:30:00
- **项目语言**: java
- **源代码路径**: src/main/java/com/example
- **总 Domain 数**: 3
- **总 Subdomain 数**: 5
- **总用例任务数**: 12
- **执行状态**: in_progress
- **最后更新时间**: 2024-01-15 11:45:00

## 执行进度概览 (Progress Overview)

- **已完成 Domain**: 1 / 3
- **已完成 Subdomain**: 2 / 5
- **已完成用例**: 5 / 12
- **总体完成度**: 42%

## Domain 任务列表 (Domain Tasks)

### Domain 1: 001-user-management

- **状态**: completed
- **路径**: src/main/java/com/example/user
- **核心实体**: User, UserProfile, Role
- **Subdomain 数量**: 2
- **用例任务数量**: 5
- **开始时间**: 2024-01-15 10:35:00
- **完成时间**: 2024-01-15 11:30:00

#### Subdomain 1: 001-authentication

- **状态**: completed
- **目录路径**: `docs/domains/001-user-management/usecases/001-authentication/`
- **用例任务列表**:
  - [x] **任务 UC-001**: 密码登录
    - 状态: completed
    - 文件: `usecase.md`
    - 规则文件: `rules.md`
    - 依赖: 无
    - 开始时间: 2024-01-15 10:40:00
    - 完成时间: 2024-01-15 10:50:00
  - [x] **任务 UC-002**: SSO登录
    - 状态: completed
    - 文件: `usecase.md`
    - 规则文件: `rules.md`
    - 依赖: UC-001
    - 开始时间: 2024-01-15 10:51:00
    - 完成时间: 2024-01-15 11:00:00

#### Subdomain 2: 002-registration

- **状态**: completed
- **目录路径**: `docs/domains/001-user-management/usecases/002-registration/`
- **用例任务列表**:
  - [x] **任务 UC-003**: 邮箱注册
    - 状态: completed
    - 文件: `usecase.md`
    - 规则文件: `rules.md`
    - 依赖: 无
    - 开始时间: 2024-01-15 11:01:00
    - 完成时间: 2024-01-15 11:15:00

### Domain 2: 002-order-management

- **状态**: in_progress
- **路径**: src/main/java/com/example/order
- **核心实体**: Order, OrderItem, Payment
- **Subdomain 数量**: 1
- **用例任务数量**: 3
- **开始时间**: 2024-01-15 11:31:00
- **完成时间**: [进行中]

#### Subdomain 1: 001-order-lifecycle

- **状态**: in_progress
- **目录路径**: `docs/domains/002-order-management/usecases/001-order-lifecycle/`
- **用例任务列表**:
  - [x] **任务 UC-004**: 创建订单
    - 状态: completed
    - 文件: `usecase.md`
    - 规则文件: `rules.md`
    - 依赖: 无
    - 开始时间: 2024-01-15 11:35:00
    - 完成时间: 2024-01-15 11:40:00
  - [ ] **任务 UC-005**: 更新订单
    - 状态: in_progress
    - 文件: `usecase.md`
    - 规则文件: `rules.md`
    - 依赖: UC-004
    - 开始时间: 2024-01-15 11:41:00
    - 完成时间: [进行中]
  - [ ] **任务 UC-006**: 取消订单
    - 状态: pending
    - 文件: `usecase.md`
    - 规则文件: `rules.md`
    - 依赖: UC-004
    - 开始时间: [待开始]
    - 完成时间: [待完成]

### Domain 3: 003-payment-processing

- **状态**: pending
- **路径**: src/main/java/com/example/payment
- **核心实体**: Payment, Refund, Transaction
- **Subdomain 数量**: 1
- **用例任务数量**: 2
- **开始时间**: [待开始]
- **完成时间**: [待完成]

#### Subdomain 1: 001-payment

- **状态**: pending
- **目录路径**: `docs/domains/003-payment-processing/usecases/001-payment/`
- **用例任务列表**:
  - [ ] **任务 UC-007**: 处理支付
    - 状态: pending
    - 文件: `usecase.md`
    - 规则文件: `rules.md`
    - 依赖: 无
    - 开始时间: [待开始]
    - 完成时间: [待完成]
  - [ ] **任务 UC-008**: 退款处理
    - 状态: pending
    - 文件: `usecase.md`
    - 规则文件: `rules.md`
    - 依赖: UC-007
    - 开始时间: [待开始]
    - 完成时间: [待完成]
```

### 示例 2：Go 项目分析

输入：

```bash
/ease:analyze-code ./internal
```

执行过程：

```
1. 语言检测: Go (检测到 go.mod 和 *.go 文件)
2. 加载分析指南: references/code-analysis-go.md
3. 核心模块识别:
   - internal/user → Domain: user-management
   - internal/order → Domain: order-management
   - internal/pkg → 跳过（公共包）
4. Domain 划分: 2 个独立 Domain
```

### 示例 3：Python 项目分析

输入：

```bash
/ease:analyze-code ./apps
```

执行过程：

```
1. 语言检测: Python (检测到 requirements.txt 和 *.py 文件)
2. 加载分析指南: references/code-analysis-python.md
3. 核心模块识别:
   - apps/users → Domain: user-management
   - apps/orders → Domain: order-management
   - apps/common → 跳过（通用模块）
4. Domain 划分: 2 个独立 Domain
```

## 集成说明

本命令是存量系统领域初始化的关键入口，它：

1. **语言感知**：自动检测项目语言，加载对应的分析指南
2. **多 Domain 划分**：识别并划分多个独立的业务 Domain
3. **编号管理**：扫描现有目录获取最大编号，新增时自动 +1
4. **工作计划机制**：⭐ **新增** - 生成详细工作计划，确保大项目任务执行完整
5. **断点续做支持**：⭐ **新增** - 支持执行中断后从断点继续，避免重复工作
6. **实时状态更新**：⭐ **新增** - 每完成一个任务立即更新工作计划状态
7. **标准化输出**：确保所有分析结果都以一致的格式输出到 `docs/domains/`
8. **用例拆解**：从 ease-analysis 拆解用例到带编号的 `usecases/` 目录
9. **与 flow-1-analyze-brd 闭环**：目录结构完全一致，可无缝衔接

### 工作计划机制的价值

**解决的问题**：
- ✅ **大项目执行不完整**：通过详细工作计划确保所有任务都被执行
- ✅ **执行中断后重复工作**：支持断点续做，避免重复执行已完成的任务
- ✅ **任务依赖混乱**：明确任务依赖关系，按正确顺序执行
- ✅ **进度不透明**：实时更新进度，清晰了解执行状态

**工作机制**：
1. 在完成领域模型分析后，自动生成包含所有任务的工作计划
2. 每次执行前检查工作计划，识别未完成任务
3. 按工作计划顺序执行，每完成一个任务立即更新状态
4. 支持执行中断后从断点继续，无需重新开始

## 注意事项

- **禁止单一 Domain**：必须识别并划分多个独立的业务 Domain（不可协商）
- **必须先检测语言**：根据项目语言加载对应的分析指南（不可协商）
- **所有目录和文件必须带三位编号**（不可协商）
- **新增时必须扫描现有最大编号 +1**（不可协商）
- **必须生成工作计划**：在完成领域模型分析后，必须生成详细的工作计划（不可协商）
- **必须支持断点续做**：执行用例提取前必须检查工作计划，支持从断点继续（不可协商）
- **实时更新工作计划**：每完成一个任务必须立即更新工作计划状态（不可协商）
- 确保分析深度足够，覆盖代码中的所有业务逻辑
- 使用统一语言，保持术语一致性
- **usecases 必须从 ease-analysis 拆解**（不可协商）
- **目录结构必须与 flow-1-analyze-brd 保持一致**（不可协商）
- 本命令**不执行 ease-spec 生命周期**，如需执行请使用 `flow-1-analyze-brd` 命令

### 工作计划相关注意事项

- **工作计划是执行的核心**：所有用例提取任务必须严格按照工作计划执行
- **工作计划必须完整**：必须包含所有 Domain、Subdomain 和用例任务
- **状态更新必须及时**：每完成一个任务立即更新状态，避免重复执行
- **断点续做机制**：如果执行中断，下次执行时会自动从断点继续
- **工作计划文件位置**：`.eases/reverse-engineering/${RUN_ID}/workplan.md`，请勿删除或手动修改
- **验证机制**：对于状态为 `completed` 的任务，会验证文件是否存在，如果不存在会重置状态

## 语言分析指南

本命令依赖以下语言分析指南（位于 ease-analysis 技能包的 `references/` 目录）：

| 语言 | 指南文件 | 主要分析点 |
|-----|---------|-----------|
| Java | `code-analysis-java.md` | 包结构、Spring 注解、JPA 实体、Service 接口 |
| Go | `code-analysis-go.md` | 目录结构、接口定义、gRPC proto、GORM 模型 |
| Python | `code-analysis-python.md` | Django App、FastAPI Router、Pydantic 模型、SQLAlchemy |

如需支持其他语言，可在 `references/` 目录下创建对应的 `code-analysis-[language].md` 文件。

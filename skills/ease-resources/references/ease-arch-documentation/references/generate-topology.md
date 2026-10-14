# 拓扑发现与分析规范

本文档定义仓库拓扑的发现、分析与分类流程。作为架构文档生成的第一步，在索引构建之前执行。**无论单系统还是多子系统，都需要完成结构化分析**，分析结果写入 `metadata.json.topology` 供后续索引和文档生成阶段消费。

> **⚠️ 不可绕过**：拓扑发现是整个架构文档生成流程的必经入口。跳过此步骤会导致：
> - 单系统项目缺少架构风格和技术特征预分析，文档生成质量下降
> - 多子系统项目无法正确分发到子系统目录，所有内容混在一起
> - 增量更新无法映射变更文件到正确的子系统
> - 已有 `topology` 字段时，必须验证其与当前仓库结构的一致性（目录重命名、新增模块等），不一致时重新执行全量分析

## 1. 分析流程总览

```
Step 1: 仓库结构扫描      → 收集构建文件、目录布局、代码根
Step 2: 架构模式识别      → 判定单系统 / 多子系统，识别声明风格与实际依赖符合度
Step 3: 子系统筛选（多子系统时） → 区分真实子系统与公共依赖
Step 4: 关系图谱构建      → 依赖边、通信协议、共享资源
Step 5: 输出 topology     → 写入 metadata.json
```

---

## 2. Step 1: 仓库结构扫描

> **目标**：用最少的文件读取量，建立仓库的全貌认知。

### 2.1 必读文件（优先级从高到低）

| 文件 | 分析目的 | 关键信号 |
|------|----------|----------|
| `settings.gradle` / `settings.gradle.kts` | 识别 Gradle 多模块 | `include`、`includeBuild`、`projectDir` |
| `pom.xml` | 识别 Maven 多模块 | `<modules>`、`<parent>`、`<dependencyManagement>` |
| `package.json` | 识别 JS/TS monorepo | `workspaces`、`lerna` |
| `build.gradle`（根） | 识别根项目类型 | `subprojects`、`allprojects`、`plugins` |
| `go.mod` | 识别 Go 多模块 | `require`、`replace` |
| `Cargo.toml`（根） | 识别 Rust workspace | `[workspace]`、`members` |
| 目录结构（`ls -1` 根目录） | 识别聚合目录 | `services/`、`apps/`、`modules/`、`packages/`、`libs/` |

### 2.2 扫描策略

```bash
# 1. 根目录一览
ls -1

# 2. 构建文件探测
find . -maxdepth 3 -name "build.gradle" -o -name "pom.xml" -o -name "package.json" -o -name "go.mod" -o -name "Cargo.toml"

# 3. 入口类探测（Java/Spring 为例）
grep -rl "@SpringBootApplication\|public static void main" --include="*.java" .

# 4. 配置文件探测
find . -maxdepth 4 -name "application.properties" -o -name "application.yml" -o -name "application.yaml"

# 5. 部署文件探测
find . -maxdepth 3 -name "Dockerfile" -o -name "docker-compose*" -o -name "*.deployment.yaml"
```

### 2.3 产出物

将扫描结果整理为候选模块列表（尚未判定类型）：

```json
{
  "scan_result": {
    "build_tool": "gradle",
    "root_build_file": "build.gradle",
    "candidates": [
      { "path": "services/user", "has_build_file": true, "has_entry_class": true, "has_config": true },
      { "path": "services/order", "has_build_file": true, "has_entry_class": true, "has_config": true },
      { "path": "shared/common", "has_build_file": true, "has_entry_class": false, "has_config": false }
    ],
    "total_candidates": 3,
    "candidates_with_entry": 2
  }
}
```

---

## 3. Step 2: 架构模式识别

> **目标**：判定仓库是单系统还是多子系统，并识别架构风格。

### 3.1 输出路由与正交节点分类

`topology.type` 只决定文档输出路由，不等同于领域边界。每个候选节点还必须独立标注以下一个或多个类型：

- `repository_module`
- `build_module`
- `deployable`
- `runtime_process`
- `service`
- `bounded_context`
- `frontend_application`
- `shared_library`

按可独立部署单元判定输出路由：

```
发现 ≥2 个可独立部署单元？
├── 否 → single（一个文档集，内部仍可有多个模块/上下文）
└── 是 → multi_subsystem（按 deployable/业务作用域生成文档集）
```

**边界情况处理**：

| 场景 | 判定 | 理由 |
|------|------|------|
| Gradle 多模块但只有一个 `@SpringBootApplication` | 单系统 | 多模块是分层拆分（api/impl/web），不是独立子系统 |
| 没有构建工具声明，但有多个 `src/` 目录 | 候选 | 目录不是部署或业务边界证据，继续检查入口、产物和部署清单 |
| 所有模块都是共享库，无业务入口 | 单系统 | 从库的角度生成文档 |
| 单模块但有多个入口 | 候选 | 可能是工具、迁移程序或多进程，需要部署证据确认 |
| 前后端在同一仓库 | 候选多 deployable | 技术栈差异不自动等于业务子系统，按构建产物和部署边界分类 |

`bounded_context` 只能由领域文档、用例、批准设计或稳定业务语言证据确认；目录和技术栈最多形成 `inferred` 候选。

### 3.2 单系统架构风格识别

对单系统，进一步识别其架构风格，影响后续文档生成的侧重点：

| 架构风格 | 识别信号 | 文档侧重 |
|----------|----------|----------|
| **分层架构** | `web/controller/service/dao` 分层目录 | 各层职责 + 跨层调用链 |
| **DDD 分层** | `domain/application/infrastructure/interfaces` 目录 | 聚合 + 领域事件 + 限界上下文 |
| **六边形架构** | `adapter/port/application` 目录 | 端口与适配器 + 入站/出站 |
| **包按功能** | `user/order/product` 功能目录（每个含自己的 controller/service/dao） | 功能模块独立性 |
| **混合架构** | 上述模式混合 | 按实际结构说明 |

识别方法：
1. 扫描代码根下的一级和二级目录名，形成风格候选，不直接定案。
2. 从 import/call/build dependency 建立实际依赖方向，并定位入口、业务规则、出站适配器和状态访问。
3. 检查候选风格的关键约束是否存在执行证据，例如领域层是否反向依赖 Web/数据库框架、端口是否确实隔离适配器、分层是否被跨层调用绕过。
4. 分别记录 `declared_style`（批准文档）、`observed_style`（依赖图）和 `conformance`（`conformant/partial/violated/unknown`）；不能仅凭目录关键词声称实现了某种风格。
5. 无法匹配时标注为 `free_form` 并记录实际结构。

```json
{
  "architecture_style": {
    "declared_style": "layered",
    "observed_style": "layered",
    "conformance": "partial"
  },
  "style_evidence": [
    "src/main/java/.../web/ — 控制器层",
    "src/main/java/.../service/ — 业务服务层",
    "src/main/java/.../integration/dao/ — 数据访问层",
    "src/main/java/.../service/X.java:18 — service 直接依赖 web DTO，形成边界偏离"
  ]
}
```

### 3.3 单系统技术特征分析

对单系统，额外分析以下技术特征：

| 特征 | 分析方法 | 价值 |
|------|----------|------|
| **技术栈** | 读取 `build.gradle`/`pom.xml` 的依赖 | 01 系统概览的核心内容 |
| **接口协议** | `@RestController`、`@MumbleMessageService`、`@RabbitListener` 等 | 03 API 接口文档的分类依据 |
| **数据存储** | 数据库驱动依赖、`application.yml` 数据源配置 | 04 数据模型的存储层说明 |
| **中间件依赖** | Redis/MQ/配置中心等依赖 | 01 系统概览的中间件清单 |
| **部署形态** | 容器清单、IaC、部署脚本 | 01 部署与运行时章节 |

---

## 4. Step 3: 子系统筛选（仅多子系统）

> **目标**：从候选模块中筛选出真实子系统，排除公共依赖。

### 4.1 真实子系统判定

对每个候选模块，按以下**优先级递减**的信号判定：

**部署强信号（至少一项，且需独立构建产物或入口佐证）**：

1. **独立入口类**：包含 `@SpringBootApplication`、`main()`、`@IdeaBootApplication` 等
2. **独立部署单元**：包含 Dockerfile、K8s Deployment、`bootJar`/`war` 打包配置
3. **独立配置体系**：拥有自己的 `application.yml`（含 `server.port`、数据源等独立配置）

**业务作用域信号（用于命名和归属，不单独证明可部署）**：

4. **独立接口暴露**：包含 `@RestController` 或 `@MumbleMessageService`，且数量 ≥3
5. **独立业务领域**：拥有与公共模块无关的业务实体/DTO 集合
6. **独立数据存储**：连接独立的数据库或 Schema

**判定流程**：

```
有独立部署证据 + 构建产物/入口？ ──是──→ 标记为 deployable
      │
      否
      │
仅有入口/配置/目录信号？ ──是──→ 标记为 deployable_candidate
      │
      否
      │
无运行入口且只被复用？ ──是──→ 标记为 shared_library
      │
      否
      └──→ 保留 node types 与低置信待确认，不强行二分
```

### 4.2 公共依赖模块排除

以下模块**不视为**真实子系统，归类为公共依赖：

| 排除类型 | 识别信号 | 示例 |
|----------|----------|------|
| 纯工具库 | 只含 util/helper/constants 类 | `common-utils`、`tools` |
| 共享模型 | 只含 DTO/Entity/VO/Proto 定义 | `api-model`、`proto-definitions` |
| 接口契约 | 只含 interface/api 定义，无实现 | `contract-api`、`client-sdk` |
| 构建基础设施 | buildSrc、Gradle 插件、BOM | `build-plugins`、`bom` |
| 被广泛依赖的底层库 | 被所有其他模块依赖但自身无业务依赖 | `framework-core`、`base-lib` |

**关键区分**：被广泛依赖不等于公共库。若模块包含业务状态或业务规则，应同时记录 `shared_library` 风险和业务作用域，不得为了输出方便隐藏其业务耦合。

### 4.3 命名规则

子系统文档目录名使用子系统本身的名字（即业务/领域名），**不添加** `-service`、`-module`、`-app` 等技术后缀。

命名来源优先级：
1. 子系统目录名去掉技术后缀（如 `services/user-management/` → `user-management`，`user-service/` → `user`）
2. 构建文件中的 `project.name` 或 `artifactId`
3. 入口类所在包名的业务含义（如 `com.example.order` → `order`）

---

## 5. Step 4: 关系图谱构建

> **目标**：建立子系统间的依赖与通信关系，为 `00_TOPOLOGY.md` 提供数据。

### 5.1 构建时依赖

从构建文件提取模块间依赖关系：

| 构建工具 | 分析方法 |
|----------|----------|
| Gradle | `build.gradle` 中的 `implementation project(':xxx')`、`api project(':xxx')` |
| Maven | `pom.xml` 中的 `<dependency><groupId>${project.groupId}</groupId><artifactId>xxx</artifactId>` |
| npm/pnpm | `package.json` 中的 `"workspace:*"`、`"link:../xxx"` |

### 5.2 运行时通信

识别子系统间的运行时交互方式：

| 协议 | 识别信号 | 分析方法 |
|------|----------|----------|
| **HTTP/REST** | `RestTemplate`、`WebClient`、`FeignClient` | grep 调用方代码中的目标 URL 或服务名 |
| **RMB** | `@MumbleMessageService` serviceId 与调用方的 `rmbInvoke` | 匹配 serviceId 的提供方和消费方 |
| **消息队列** | `@RabbitListener`、`@KafkaListener`、`@RocketMQMessageListener` | 匹配 topic/queue 的生产者和消费者 |
| **共享数据库** | 多个子系统连接同一数据库实例 | 分析各子系统的 `application.yml` 数据源配置 |
| **共享缓存** | 多个子系统使用同一 Redis key 前缀 | 分析各子系统的 Redis key 命名模式 |
| **事件总线** | `@EventListener`、`ApplicationEventPublisher`（进程内） | 只在单进程内分析，跨进程需匹配消息协议 |

### 5.3 共享资源识别

分析子系统间共享的基础设施资源：

| 资源类型 | 识别方法 | 记录内容 |
|----------|----------|----------|
| 共享数据库 | 对比各子系统 `spring.datasource.url` | 共享的数据库名 + 使用方列表 |
| 共享 Redis | 对比各子系统 Redis 配置 | 共享的 Redis 集群 + key 前缀 |
| 共享消息 Topic | 匹配生产者和消费者的 topic 名 | topic 名 + 生产方 + 消费方 |
| 共享文件存储 | 对比 FPS/S3 配置 | 存储服务 + 使用方列表 |
| 共享配置中心 | 对比 WeConf/Apollo 配置引用 | 配置中心实例 + 共享的 namespace |

### 5.4 关系边结构

```json
{
  "dependency_edges": [
    {
      "from": "user",
      "to": "common",
      "type": "build_time",
      "evidence": "services/user/build.gradle:25 — implementation project(':shared:common')"
    },
    {
      "from": "user",
      "to": "order",
      "type": "runtime",
      "protocol": "RMB",
      "service_id": 130002,
      "description": "用户下单时查询订单状态",
      "evidence": "services/user/src/.../OrderClientService.java:15"
    },
    {
      "from": "user",
      "to": "notification",
      "type": "runtime",
      "protocol": "MQ",
      "topic": "user.created",
      "description": "用户创建后发送通知",
      "evidence": "services/user/src/.../UserEventPublisher.java:22"
    }
  ],
  "shared_resources": [
    {
      "type": "database",
      "name": "ecif_db",
      "used_by": ["user", "order"],
      "evidence": "services/user/src/main/resources/application.yml:10"
    }
  ]
}
```

### 5.5 边界、耦合与故障域分析

关系图不止回答“谁依赖谁”，还要为深度分析保留以下语义：

- `boundary_crossings`：进程、网络、信任、事务、数据所有权和团队边界。
- `coupling`：`structural/temporal/data/change/supply_chain`，以及证据可证明的同步性、顺序性或共同发布要求。
- `failure_domain`：共享进程、数据库、缓存、消息基础设施或配置控制面导致的共同失效范围。
- `blast_radius`：一条边失效时可能影响的 deployable、能力、消费者和数据；分析推导必须标 `inferred`。
- `enforcement`：架构边界由构建规则、端口接口、权限、数据库授权、测试还是人工约定维护。

对每个节点可计算 fan-in、fan-out、循环和共享资源数量，用作显著项筛选依据。指标只说明结构中心性，不直接等同于性能瓶颈、单点或坏设计。

---

## 6. Step 5: 输出 topology

### 6.1 单系统 topology

```json
{
  "topology": {
    "type": "single",
    "discovered_at": "2026-05-15T10:00:00",
    "architecture_style": {
      "declared_style": "unknown",
      "observed_style": "layered",
      "conformance": "partial"
    },
    "nodes": [
      {
        "id": "application",
        "types": ["repository_module", "build_module", "deployable", "runtime_process"],
        "state": "observed",
        "confidence": "high",
        "evidence": ["build-file:1", "deploy-file:1"]
      }
    ],
    "style_evidence": [
      "src/main/java/.../web/ — 控制器层",
      "src/main/java/.../service/ — 业务服务层",
      "src/main/java/.../integration/dao/ — 数据访问层"
    ],
    "tech_signals": {
      "framework": "spring-boot",
      "build_tool": "gradle",
      "api_protocols": ["HTTP", "RMB"],
      "data_storage": ["mysql", "redis"],
      "middleware": ["rmb", "gns", "fps", "weconf"]
    },
    "subsystems": [],
    "shared_libraries": [],
    "dependency_edges": []
  }
}
```

### 6.2 多子系统 topology

```json
{
  "topology": {
    "type": "multi_subsystem",
    "discovered_at": "2026-05-15T10:00:00",
    "discovery_strategy": "gradle_settings",
    "subsystems": [
      {
        "id": "user",
        "name": "用户管理",
        "root": "services/user",
        "types": ["repository_module", "build_module", "deployable", "service"],
        "entry_class": "com.example.user.Application",
        "architecture_style": {
          "declared_style": "unknown",
          "observed_style": "layered",
          "conformance": "partial"
        },
        "tech_stack": ["java", "spring-boot", "mybatis"],
        "depends_on": ["common"],
        "api_protocols": ["HTTP", "RMB"],
        "data_storage": ["mysql:ecif_user", "redis"],
        "evidence": {
          "entry_class": "services/user/src/.../Application.java:12",
          "build_file": "services/user/build.gradle:1",
          "config_file": "services/user/src/main/resources/application.yml:1"
        }
      }
    ],
    "shared_libraries": [
      {
        "id": "common",
        "name": "公共组件库",
        "root": "shared/common",
        "consumed_by": ["user", "order"],
        "content_type": "utilities",
        "evidence": "shared/common/build.gradle:1"
      }
    ],
    "dependency_edges": [
      { "from": "user", "to": "common", "type": "build_time", "evidence": "..." },
      { "from": "user", "to": "order", "type": "runtime", "protocol": "RMB", "service_id": 130002, "evidence": "..." }
    ],
    "shared_resources": [
      { "type": "database", "name": "ecif_db", "used_by": ["user", "order"], "evidence": "..." }
    ],
    "boundary_analysis": [
      {
        "edge": "user->order",
        "crosses": ["runtime_process", "network", "data_ownership"],
        "coupling": ["temporal"],
        "failure_domain": "order-runtime",
        "enforcement": ["contract:order-query"],
        "state": "inferred",
        "derived_from": ["edge:user->order", "contract:order-query"]
      }
    ]
  }
}
```

**`topology.type` 取值**：
- `"single"` — 单系统
- `"multi_subsystem"` — 多子系统

---

## 7. 生成顺序

**单系统**：直接进入索引构建和文档生成。

**多子系统**：
1. 按实际依赖分批，被依赖输入先就绪；同层独立子系统可按 `fan-out-workflow.md` 并行，循环依赖作为一个协调工作包。公共库提供共享证据，不单独生成文档集
2. 每个子系统独立走「索引 → 6 份文档 → 质量门禁」
3. 最后从各子系统 `metadata.json` 聚合生成 `00_TOPOLOGY.md`

---

## 8. 公共依赖模块的处理

公共依赖模块**不单独生成**文档集，但在以下位置体现：

1. **`00_TOPOLOGY.md`**：列出所有公共依赖模块及其被消费关系
2. **各子系统文档中**：
   - `01_SYSTEM_OVERVIEW.md` 的依赖说明中提及
   - `06_UTILS_LIBRARIES.md` 中说明从公共模块复用了哪些组件
   - `03_API_INTERFACE.md` 中标注来自公共模块的接口契约

---

## 9. 增量更新策略

**单系统**：由 `references/generate-project-index.md` 的增量策略处理。

**多子系统**：
1. `git diff --name-only <baseline>..HEAD` 获取变更文件
2. 将变更文件映射到子系统（根据 `root` 路径前缀）
3. 只对受影响的子系统执行增量更新
4. 公共依赖模块变更时，根据 `consumed_by` 找到消费方，评估影响范围
5. 子系统间接口变更时，同步更新 `00_TOPOLOGY.md`

---

## 10. 向后兼容

- 旧版 `metadata.json` 无 `topology` 字段：视为单系统
- 已有的 6 份文档结构和内容规范不变，仅作用域收窄到子系统内
- 单系统 `topology` 的 `tech_signals` 可为后续 `01_SYSTEM_OVERVIEW.md` 生成提供预分析素材

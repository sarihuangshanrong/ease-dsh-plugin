# E2E 技术适配规则（仅读取受影响部分）

根据 e2e-onboarding-split 的 Java/Go file-gen、authoring、onboarding 沙箱自检和 UI 指引提炼。规则适用于对应平台与 runner，项目其他平台按其实际文档验证；不凭模板假定运行环境。Ease 决定范围和预期，这里约束请求、配置和运行正确性。纯运行已有入口不要求重新生成或全量自检。

## Java：案例与模式

- 保留现有模式；首次接入 Java Gradle 优先 E（独立 Gradle/JUnit 工程），Maven/存量 executor 可用 A；后台任务可用 D。模式变化是设计决策，不因增量案例修改自动迁移。
- HTTP 请求按实际协议构造；WeService sourceSystemId 属于测试请求方，不能混用被测应用身份。版本、必填字段、序列化与 TC 对照，禁止套用其他项目常量。
- A/C 的 assertions 区分 json/text/bytes，bytes 仅 HTTP；NON_NULL 序列化不能要求必然不存在的 null 字段 exists。核对运行器实际输出 assertion_results，旧版静默忽略断言不能证明 TC。
- A/C 的 wemock 依赖与测试侧配置须保留。E 的测试不依赖 executor，并不等于应用无 wemock 启动依赖；WeService 的 SDK 配置/证书位于 gradle-test resources 时不得误删。
- E 保留 JUnit XML→`/logs/report.json` 的逐例汇总及原始 Gradle 退出状态；app 持续运行是正常情况，不要求应用容器退出才判通过。
- 修改打包先核对 Mumble SDK 版本：原指引中 >=4.1.9 已自动打包 e2e，不能再次添加重复 into('e2e')。其他版本检查实际产物再补齐。

## Go：请求与报告

- 增改 POST 案例时检查对应 handler 的绑定方式与请求契约：纯 URL 参数用 assert_api；JSON body 用 assert_api_body，并设置 application/json 和实际请求体。不能仅凭方法名或 POST 推断。
- 复用 shell/curl runner，保留失败累积、最终非零退出及 `/logs/report.json`；code=0 仅证明对应成功码，业务 TC 按预期补充结果或状态断言。
- 修改部署按 Go 的 configs/env/sit-e2e、二进制及实际容器路径处理，不套 Java tests/conf、JAR 或 JaCoCo。外部 Mock 是否需要按应用依赖判定，不因没有 executor 就一律删除 Mock。
- 使用 BSP 时核对应用解密与沙箱明文密码的一致性，使用隔离测试凭据，不复制其他项目密钥；变更构建确保当前产物身份唯一，避免旧镜像缓存冒充本次结果。

## UI：独立 runner

- UI 工程独立于后端 file-gen；原平台 runner 的 /workspace 只读且无 node_modules，不在那里 npm install 或写登录态。
- playwright.config 的间接本地依赖使用纯常量模块，不在这些模块中引入无法解析的第三方包。按现有 runner 的特殊加载约定验证，不能照搬普通本地 Playwright 环境。
- 原平台 storageState 写 `/reports/ui/.auth/user.json` 等明确可写的报告卷；SPA 登录成功使用本项目业务信号，不只依赖 URL 跳转。
- 使用 UM Mock 时核对当前 LoginResult 所需字段，避免缺字段导致解析失败。UI 请求发送仅能作为交互断言，业务 TC 还需验证其目标结果。
- 原平台从 e2e-ui 容器读取 `/reports/ui/results.json` 或 bundle；按实际 TTL 立即归档（原指引默认 1800 秒），不能等待临时产物失效。后端通过不能覆盖 UI 失败。

## 环境：仅检查本次影响面

- 变更部署/契约时以 Dockerfile、安装/启动脚本及实际容器路径相互核对，保留平台使用的 `e2e-constract.yaml` 拼写；未知路径不猜。端口/进程 readiness 与测试模式是两个独立维度，readiness 成功不等于业务通过。
- 配置变更检查三层一致性：应用 sit-e2e、测试请求方配置、e2e/config 运行时覆盖。身份区分调用方和被测方；DB 密码/库名、证书路径、Mock 地址和端口按实际沙箱一致，不把生产地址或凭据带入生成文件。
- 核对受影响的启动依赖、配置中心兜底与 Mock；数据 schema 与实际 DDL/mapper 匹配，种子数据满足 TC，执行间隔离且可清理。进程启动不能代替依赖链闭环。
- 原平台 exec readiness 的 app.ready 标记须遵循启动顺序；Java 阻塞 start.sh 需先后台启动再写标记并保持进程，Go 按现有 exec 前置标记机制处理，同时核对真实就绪条件，不能只靠标记证明业务可用。
- 仅 Java 的既有/批准覆盖率方案使用 JaCoCo，修改 JVM 参数时保留既有值并核对 classfiles 与当前构建；不强制给 Go/UI 注入 JaCoCo，不把采集失败写成零覆盖率或通过。
- 报告、日志卷及权限保持 runner 约定；原平台后端 `/logs/report.json`、UI `/reports/ui/results.json` 不因 Ease 归档而更名。

只读运行发现旧配置缺陷时报告具体失败，不为“符合模板”顺手改造整套环境。修改无法从这些规则及项目事实确定时，定向读取可用的对应原技能；仍有缺口按 Ease 任务记录阻塞，不臆造配置。

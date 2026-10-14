# MumbleSDK 框架验证清单（生成门槛）

用途：在“框架代码生成”完成后，按层逐项核验，确保 100% 符合 MumbleSDK 框架特征、文件类型与配置规范。此清单为合并/交付的强制门槛。

参考来源：
- **MumbleSDK 通用规范**：`references/mumblesdk/SKILL.md`
- **MumbleSDK 质量门槛**：`references/mumblesdk/references/quality-gates.md`
- **MumbleSDK 集成检查**：`references/mumblesdk/references/integration-checklist.md`
- **MumbleSDK 代码模板**：`references/mumblesdk/templates/*

---

## 0. 生成前必读（强制）- MumbleSDK 项目专用

本 checklist 仅适用于 **MumbleSDK 企业框架项目**。

- [ ] 已完整阅读 `references/mumblesdk/SKILL.md`（MumbleSDK 核心规范）
- [ ] 已阅读 `references/mumblesdk/references/quality-gates.md`（质量门槛）
- [ ] 已阅读 `references/mumblesdk/references/quickstart.md`（快速开始）
- [ ] 已明确设计来源（design_result.md 或等效），包含领域模型/用例/接口契约
- [ ] 已确认文件类型与配置格式约束（Java/.java、Properties/.properties、MyBatis/.xml、SQL/.sql；禁止 YAML）

---

## 1. Controller 层（100% 必须通过）
- [ ] Controller 类继承 MumbleAbstractBaseController
- [ ] 注解与映射：@RestController、@RequestMapping、@Slf4j 配置正确
- [ ] 注入 ThreadPoolTaskExecutor frontTaskExecutor、SeqService
- [ ] @Value 注入系统参数：mumbleSystemId、mumbleDcnNo（含默认值）
- [ ] 实现抽象方法：getFrontTaskExecutor / getBizSeqNo / getTxnSeqNo / getOrgSysId / getDcnNo / setMumbleContext
- [ ] setMumbleContext：生成 bizSeqNo（seqService.nextBizSeqNo）并设置客户端 IP、系统上下文
- [ ] 异步接口：使用 DeferredResult<WebMessage<T>>，业务执行通过 execute(...) 封装
- [ ] 统一响应：WebMessage + MumbleResponseStatus；成功码/超时/异常码一致
- [ ] 日志：包含 bizSeqNo，关键路径有审计性日志
- [ ] 全局异常处理：@ControllerAdvice 或 @RestControllerAdvice，@ExceptionHandler 针对业务/校验/系统异常返回统一格式

---

## 2. Service 层（100% 必须通过）
- [ ] @Service、@Slf4j 注解
- [ ] 注入依赖：SeqService、MumbleDistributedLock（若涉及并发控制）、DAO 组件
- [ ] 入口方法具备：
  - [ ] @MumbleMessageService，含 serviceIds、bizServiceIds、requestMessageClass、versions
  - [ ] 参数包含 @MumbleMessageObject request 与 BizErrors bizErrors
  - [ ] @Transactional(rollbackFor = Exception.class)
- [ ] 参数校验：YapiFieldValidationUtil.validate(request, bizErrors) 或等效
- [ ] 业务流水号：seqService.nextBizSeqNo 并设置到 MumbleContextUtil
- [ ] 异常处理：捕获 SQLException / BusinessException / Exception；使用 bizErrors.reject(...) 收集错误
- [ ] 日志：关键事件包含 bizSeqNo；异常路径包含上下文

---

## 3. DAO / MyBatis 层（100% 必须通过）
- [ ] DAO 接口：
  - [ ] 普通接口（无 @Mapper、无 BaseMapper 继承）
  - [ ] 所有方法声明 throws SQLException
- [ ] DAO 实现：
  - [ ] 类继承 AbstractSimpleDAO，标注 @Repository
  - [ ] 使用 try (MumbleSqlSession session = getSession()) 获取会话执行
- [ ] MyBatis XML：
  - [ ] Doctype 正确（mapper 3.0 DTD）
  - [ ] namespace 指向 DAO 接口全限定名
  - [ ] 定义 BaseResultMap（字段映射完整）
  - [ ] 定义 Base_Column_List（可复用字段列表）
  - [ ] 所有语句参数化：#{param,jdbcType=XXX}
  - [ ] 动态 SQL 规范：<if>、<trim> 等标签使用正确
- [ ] CRUD 命名与行为符合最佳实践

---

## 4. Entity 层（DTO/BO/VO，100% 必须通过）
- [ ] 包结构：pojo/dto、pojo/bo、pojo/vo/request、pojo/vo/response
- [ ] 继承：DTO/BO/VO 继承 BaseDTO（VO 如规范要求 FiaBaseDTO，需对齐具体版本约束）
- [ ] Lombok：@Data、@EqualsAndHashCode(callSuper = true)
- [ ] MyBatis：@TableName、@TableId、@TableField 等
- [ ] 校验注解：@NotBlank、@NotNull、@Length、@Pattern、@Min 等按设计约束配置
- [ ] 时间字段：统一 LocalDateTime；@JsonFormat("yyyy-MM-dd HH:mm:ss")
- [ ] 转换与业务辅助：fromBO()/toDTO()/validate()/isActive() 等实现合理

---

## 5. 配置与文件类型（100% 必须通过）
- [ ] application.properties 使用 Properties 格式（禁止 .yml/.yaml）
- [ ] MyBatis 映射使用 .xml；SQL 脚本使用 .sql；Java 源码使用 .java
- [ ] 多环境配置：application-dev.properties / application-test.properties / application-prod.properties（必要时）
- [ ] Spring Boot 配置类：
  - [ ] @Configuration、@EnableAutoConfiguration、@ComponentScan
  - [ ] @MapperScan 指向 DAO 包
  - [ ] @EnableAsync、@EnableScheduling
  - [ ] 线程池 Bean：frontTaskExecutor（前缀、队列、拒绝策略等）
  - [ ] 分布式锁 Bean、序列服务 Bean、事务管理器、Validator 存在且配置合理
- [ ] 日志配置：关键包日志级别、模式满足调试与审计需求

---

## 6. SQL / 数据库脚本（100% 必须通过）
- [ ] 字符集统一 utf8mb4；引擎 InnoDB
- [ ] 所有表与字段具备 COMMENT 注释
- [ ] 时间字段统一 datetime；状态字段 tinyint
- [ ] 主键、唯一键、联合索引等按查询场景设置
- [ ] DDL 具备默认值与 ON UPDATE（需时）
- [ ] 脚本按环境/版本管理（初始化/迁移）

---

## 7. 异常处理与可观测性（强制）
- [ ] 全局异常处理器覆盖：业务/校验/系统异常
- [ ] 错误码/消息一致性：与 WebMessage 响应码对齐（0000/9998/9999 等）
- [ ] 审计与可观测性：关键操作与错误路径记录 bizSeqNo，必要指标计数（按项目约定）

---

## 8. 验证流程（三阶段）
- 生成前：
  - [ ] 文档阅读与栈选择确认完毕（见第 0 节）
  - [ ] MumbleSDK 特征清单梳理完成
- 生成中：
  - [ ] 每文件/模块按第 1~6 节逐项标记
  - [ ] 发现不符合项立即停止，修复后继续
- 生成后：
  - [ ] 全量清单复核 100% 通过
  - [ ] 编译验证 0 错误
  - [ ] 依赖完整性检查
  - [ ] 配置/脚本/文件类型规范检查通过

---

## 9. 失败处理与回归
- [ ] 任一必检项失败立即停止生成/合并
- [ ] 记录失败项、原因与修复方案
- [ ] 如因模板缺陷导致，更新模板后重试
- [ ] 回归验证：仅对变更项重测不够，需进行全量关键路径复核

---

## 10. 常见反例（禁止）
- [ ] 使用 YAML（.yml/.yaml）作为 Spring 配置
- [ ] DAO 接口使用 @Mapper 或继承 BaseMapper
- [ ] Service 方法缺失 BizErrors 或 @MumbleMessageService
- [ ] Controller 未继承 MumbleAbstractBaseController 或未使用 execute/DeferredResult
- [ ] 时间字段使用 Date 而非 LocalDateTime
- [ ] MyBatis XML 缺失 BaseResultMap / Base_Column_List / 参数化查询
- [ ] 未设置 bizSeqNo 或日志不含流水号

---

## 11. 关联文档

**MumbleSDK 核心文档**：
- Main spec: `references/mumblesdk/SKILL.md`
- Quality gates: `references/mumblesdk/references/quality-gates.md`
- Quickstart: `references/mumblesdk/references/quickstart.md`
- Templates: `references/mumblesdk/templates/*`
- Examples: `references/mumblesdk/examples/*`

建议：将本清单纳入 CI 的门禁规则或 PR 审查模板，未勾选完成不得合入。

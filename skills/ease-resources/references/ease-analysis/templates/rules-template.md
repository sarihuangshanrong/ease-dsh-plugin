## 业务规则模板（Business Rules Template）

### 1. 头部与元数据（Header & Metadata）

* **子领域（Subdomain）：** [子领域名称，例如 "认证（Authentication）"]
* **版本（Version）：** [例如 1.0]
* **作者（Author）：** [你的姓名 / 团队]
* **最近更新（Last Updated）：** [日期]

---

### 2. 业务规则目录（Business Rules Catalog）

#### 2.1 约束规则（Constraints）

约束规则定义了阻止行为的限制条件。

| 规则 ID | 规则名称 | 规则描述 | 适用用例 | 来源 |
|---------|---------|---------|---------|------|
| BR-001-[rule-name] | [规则名称] | [完整的规则描述，避免含糊表述] | [UC-XXX, UC-YYY] | [代码/文档引用] |
| BR-002-[rule-name] | [规则名称] | [完整的规则描述] | [UC-XXX] | [代码/文档引用] |

> **注意**：规则 ID 必须遵循 `BR-[%03d]-[rule-name]` 格式，其中 `rule-name` 为 1-3 个具体业务词汇，如 `approval-limit`、`supplier-active`、`order-validation`。权威规范请参见 `terminology-glossary.md`。

**详细规则说明：**

##### BR-001-[rule-name]: [规则名称]

* **类型（Type）：** 约束（Constraint）
* **描述（Description）：** [完整的规则描述，包括条件、限制和影响范围]
* **触发条件（Trigger Conditions）：** [什么情况下此规则生效]
* **约束内容（Constraint Details）：** [具体的限制条件]
* **违反后果（Violation Consequences）：** [违反规则时的系统行为]
* **关联用例（Related Use Cases）：** [UC-XXX, UC-YYY]
* **代码引用（Code References）：** [源代码位置或文件路径]
* **备注（Notes）：** [其他相关信息]

**Java 伪代码实现（Java Pseudo-code Implementation）：**

> 注意：以下仅为规则实现的模式示例，实际代码应根据具体规则内容生成，**禁止直接复制模板代码及类名**。

```java
/**
 * 业务规则验证器 - 根据业务规则生成具体实现
 *
 * 要点：
 * - 类名应根据实际业务规则命名（如 ApprovalLimitValidator）
 * - 验证逻辑应根据规则描述具体实现
 * - 错误码应包含规则ID以便追踪
 */
public class BusinessRuleValidator {

    public ValidationResult validate(DomainEntity entity) {
        // 根据规则实现具体的验证逻辑
        if (/* 规则条件判断 */) {
            return ValidationResult.error(
                "BR-XXX-VIOLATION-CODE",
                "具体的错误消息，包含违反的原因",
                "BR-XXX-[rule-name]"
            );
        }
        return ValidationResult.success();
    }
}
```

**重要约束：**
- 验证器类名必须反映具体业务规则（如 `SupplierActiveValidator`，而非 `BR001Validator`）
- 常量/类名应根据实际业务语义命名
- 代码应从规则描述推导出具体逻辑，而非填充模板变量

---

#### 2.2 计算规则（Computations）

计算规则定义了如何计算值的公式或算法。

| 规则 ID | 规则名称 | 计算公式/算法 | 适用用例 | 来源 |
|---------|---------|--------------|---------|------|
| BR-001-[rule-name] | [规则名称] | [计算公式或算法描述] | [UC-XXX, UC-YYY] | [代码/文档引用] |
| BR-002-[rule-name] | [规则名称] | [计算公式或算法描述] | [UC-XXX] | [代码/文档引用] |

**详细规则说明：**

##### BR-001-[rule-name]: [规则名称]

* **类型（Type）：** 计算（Computation）
* **描述（Description）：** [完整的计算规则描述]
* **输入参数（Input Parameters）：** [计算所需的输入参数列表]
* **计算公式（Formula）：** [数学公式或算法步骤]
* **输出结果（Output）：** [计算结果及其含义]
* **边界条件（Boundary Conditions）：** [特殊情况的处理]
* **关联用例（Related Use Cases）：** [UC-XXX, UC-YYY]
* **代码引用（Code References）：** [源代码位置或文件路径]
* **备注（Notes）：** [其他相关信息]

**Java 伪代码实现示例（Java Pseudo-code Implementation Example）：**

> 注意：以下仅为计算规则实现的模式示例。

```java
/**
 * 计算规则服务 - 根据具体计算逻辑生成
 */
public class CalculationService {

    public CalculationResult calculate(CalculationInput input) {
        // 边界条件检查
        if (input == null || !isValidInput(input)) {
            return CalculationResult.defaultValue();
        }

        // 执行计算公式（根据规则描述推导）
        double result = applyCalculationFormula(input);

        // 结果范围校验
        return clampToValidRange(result);
    }
}
```

---

#### 2.3 推断规则（Inferences）

推断规则定义了 If-Then 形式的逻辑规则。

| 规则 ID | 规则名称 | 规则逻辑 | 适用用例 | 来源 |
|---------|---------|---------|---------|------|
| BR-001-[rule-name] | [规则名称] | [If-Then 逻辑描述] | [UC-XXX, UC-YYY] | [代码/文档引用] |
| BR-002-[rule-name] | [规则名称] | [If-Then 逻辑描述] | [UC-XXX] | [代码/文档引用] |

**详细规则说明：**

##### BR-001-[rule-name]: [规则名称]

* **类型（Type）：** 推断（Inference）
* **描述（Description）：** [完整的推断规则描述]
* **前提条件（Premise / If）：** [If 部分的条件]
* **结论（Conclusion / Then）：** [Then 部分的动作或状态]
* **优先级（Priority）：** [如果存在多个规则冲突时的优先级]
* **关联用例（Related Use Cases）：** [UC-XXX, UC-YYY]
* **代码引用（Code References）：** [源代码位置或文件路径]
* **备注（Notes）：** [其他相关信息]

**Java 伪代码实现示例（Java Pseudo-code Implementation Example）：**

> 注意：以下仅为推断规则实现的模式示例。

```java
/**
 * 推断规则服务 - If-Then 逻辑实现
 */
public class InferenceService {

    public void evaluateContext(BusinessContext context) {
        // 检查前提条件（根据规则描述）
        if (meetsPremiseConditions(context)) {
            // 执行结论动作（根据规则描述）
            executeInferredActions(context);
        }
    }
}
```

---

#### 2.4 动作触发规则（Action Enablers）

动作触发规则定义了触发后续动作的条件。

| 规则 ID | 规则名称 | 触发条件 | 触发动作 | 适用用例 | 来源 |
|---------|---------|---------|---------|---------|------|
| BR-001-[rule-name] | [规则名称] | [触发条件描述] | [触发的动作或事件] | [UC-XXX, UC-YYY] | [代码/文档引用] |
| BR-002-[rule-name] | [规则名称] | [触发条件描述] | [触发的动作或事件] | [UC-XXX] | [代码/文档引用] |

**详细规则说明：**

##### BR-001-[rule-name]: [规则名称]

* **类型（Type）：** 动作触发（Action Enabler）
* **描述（Description）：** [完整的触发规则描述]
* **触发条件（Trigger Conditions）：** [什么情况下触发]
* **触发动作（Triggered Actions）：** [被触发的具体动作或事件]
* **执行时机（Execution Timing）：** [立即执行、延迟执行等]
* **关联用例（Related Use Cases）：** [UC-XXX, UC-YYY]
* **代码引用（Code References）：** [源代码位置或文件路径]
* **备注（Notes）：** [其他相关信息]

---

### 3. 约束条件（Constraints）

#### 3.1 业务约束（Business Constraints）

* **[约束名称]：** [约束描述]
  * **影响范围：** [哪些用例或功能受影响]
  * **约束原因：** [为什么存在此约束]
  * **缓解措施：** [如何应对此约束]

#### 3.2 技术约束（Technical Constraints）

* **[约束名称]：** [约束描述]
  * **影响范围：** [哪些用例或功能受影响]
  * **约束原因：** [为什么存在此约束]
  * **缓解措施：** [如何应对此约束]

---

### 4. 成功标准（Success Criteria）

#### 4.1 功能成功标准（Functional Success Criteria）

* **[标准名称]：** [可量化的成功标准描述]
  * **测量指标：** [如何测量]
  * **目标值：** [期望达到的目标值]
  * **验证方法：** [如何验证是否达到标准]

#### 4.2 非功能成功标准（Non-Functional Success Criteria）

* **性能（Performance）：** [性能相关的成功标准]
* **安全（Security）：** [安全相关的成功标准]
* **可用性（Usability）：** [可用性相关的成功标准]
* **可维护性（Maintainability）：** [可维护性相关的成功标准]

---

### 5. 规则依赖关系（Rule Dependencies）

#### 5.1 规则依赖图（Rule Dependency Graph）

```
BR-001-[rule1] → BR-002-[rule2] → BR-003-[rule3]
BR-004-[rule4] → BR-005-[rule5]
BR-006-[rule6] → BR-001-[rule1]
```

#### 5.2 规则冲突（Rule Conflicts）

* **[冲突描述]：** [哪些规则存在冲突，如何解决]


---

### 6. 规则变更历史（Rule Change History）

| 版本 | 日期 | 变更内容 | 变更原因 | 变更人 |
|------|------|---------|---------|--------|
| 1.0 | [日期] | 初始版本 | - | [姓名] |
| 1.1 | [日期] | [变更描述] | [变更原因] | [姓名] |

---

### 7. 附录（Appendices）

#### 7.1 术语表（Glossary）

* **[术语]：** [定义]
* **[术语]：** [定义]

#### 7.2 参考文档（References）

* [相关文档链接或引用]


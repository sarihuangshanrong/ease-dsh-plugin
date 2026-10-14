## 用例模板（Use Case Template）
### 1. 头部与元数据（Header & Metadata）

* **用例 ID（Use Case ID）：** [唯一标识，例如 UC-001]
* **用例名称（Use Case Name）：** [以动作为导向的目标，例如 "提交采购订单（Submit Purchase Order）"]
* **版本（Version）：** [例如 1.0]
* **作者（Author）：** [你的姓名 / 团队]
* **最近更新（Last Updated）：** [日期]

### 2. 核心信息（Core Information）

* **主要参与者（Primary Actor）：** [发起用例的用户、角色或外部系统。例如 "采购经理（Procurement Manager）"]
* **次要参与者（Secondary Actors）：** [参与的其他参与者或系统，例如 "财务系统（Finance System）"]
* **目标（或范围）（Goal or Scope）：** [对参与者目标的简要 1–2 句描述。例如 "创建、校验并提交新的采购订单以供供应商审批。"]
* **层级（Level）：** [摘要（Summary）、用户目标（User-Goal）或子功能（Sub-function）。通常为 "User-Goal"]

### 3. 上下文与触发器（Context & Triggers）

* **触发器（Trigger）：** [启动用例的事件。例如 "采购经理选择 '创建新采购订单（Create New PO）'。"]
* **前置条件（Preconditions）：** [用例开始之前系统必须满足的状态。]
    * *示例：用户已通过认证，并拥有 "创建采购订单（Create PO）" 权限。*
    * *示例：供应商数据库可访问。*
* **后置条件（成功保证）（Postconditions / Success Guarantee）：** [用例成功完成后系统的状态。]
    * *示例：采购订单（PO）以 "已提交（Submitted）" 状态保存。*
    * *示例：向供应商的电子邮件通知已入队。*
    * *示例：审计日志条目已创建。*

---

### 4. 场景与流程（Scenarios & Flows）

#### 4.1 主成功场景（基础流程）（Main Success Scenario / Basic Flow）

[这是无错误与无偏离的“快乐路径”。使用清晰的“参与者动作（Actor Action）”→“系统响应（System Response）”格式。在流程步骤中需要应用业务规则的地方，必须明确标注。]

1.  **参与者（Actor）：** 点击“创建新采购订单（Create New Purchase Order）”。
2.  **系统（System）：** 显示新的采购订单（PO）表单，填充默认用户信息。（Use BR-001）
3.  **参与者（Actor）：** 从已批准列表中选择“供应商（Supplier）”。
4.  **系统（System）：** 校验该供应商的活动状态（Active）。
5.  **参与者（Actor）：** 添加一个或多个行项目（产品 ID、数量、价格）。
6.  **系统（System）：** 对每个行项目，校验产品 ID 并计算小计（subtotal）。
7.  **参与者（Actor）：** 点击“提交订单（Submit Order）”。
8.  **系统（System）：**
    a. 校验整张订单（例如：总金额在参与者的审批限额内）。
    b. 分配唯一的采购订单号（PO Number）。
    c. 以“已提交（Submitted）”状态将采购订单保存到数据库。
    d. 触发“通知供应商（Notify Supplier）”事件（参见用例 UC-002）。
    e. 向参与者显示“成功：PO-12345 已提交（Submitted）”消息。

#### 4.2 备选流程（Alternative Flows）

[这些是有效但不常见的路径，仍然以成功结束。使用主流程中发生分支的步骤编号进行引用。在流程步骤中需要应用业务规则的地方，必须明确标注。]

* **3a. 参与者搜索供应商：**
    1.  **参与者（Actor）：** 在“供应商（Supplier）”搜索框中输入部分名称。
    2.  **系统（System）：** 返回匹配的供应商列表。（Use BR-002）
    3.  **参与者（Actor）：** 从列表中选择供应商。
    4.  （流程回到主流程第 4 步）

* **7a. 参与者将订单保存为草稿：**
    1.  **参与者（Actor）：** 点击“保存为草稿（Save as Draft）”，而不是“提交（Submit）”。
    2.  **系统（System）：** 校验采购订单表单的完整性（草稿所需的最小字段）。
    3.  **系统（System）：** 以“草稿（Draft）”状态保存采购订单。
    4.  **系统（System）：** 显示“成功：PO-12346 已保存为草稿（Draft）。”。
    5.  （用例结束。）

#### 4.3 异常流程（错误处理）（Exception Flows / Error Handling）

[这些是目标未达成的错误条件。列出错误及系统的恢复步骤。在流程步骤中需要应用业务规则的地方，必须明确标注。]

* **4a. 供应商为非活动状态：**
    1.  **系统（System）：** 检测到所选供应商被标记为“非活动（Inactive）”。（Use BR-003）
    2.  **系统（System）：** 显示错误消息：“无法创建采购订单。供应商 [名称] 为非活动状态。”
    3.  （流程停留在采购订单表单上，等待用户更正。）

* **8a. 校验失败（审批限额）：**
    1.  **系统（System）：** 检测到采购订单总额（$50,000）超过参与者的审批限额（$25,000）。
    2.  **系统（System）：** 显示错误：“总额超过你的审批限额。请保存为草稿并提交给‘管理层（Management）’审批。”
    3.  （流程停留在采购订单表单上。）

* **8b. 数据库连接失败：**
    1.  **系统（System）：** 因数据库错误未能保存采购订单。
    2.  **系统（System）：** 记录关键错误（参见 NFR-Audit）。
    3.  **系统（System）：** 显示消息：“发生关键错误。请重试或联系支持。参考：ERR-915。”
    4.  （用例结束。）

---

### 5. 其他要求（Other Requirements）

* **关键业务规则（Key Business Rules）：** [列出在流程中引用的具体规则 ID。**重要：仅列出规则 ID，规则详细信息在 rules.md 中维护。这对开发者至关重要。**
    * **BR-001-approval-limit：** 参见 rules.md 中的详细规则描述
    * **BR-002-supplier-active：** 参见 rules.md 中的详细规则描述
    * **BR-003-order-validation：** 参见 rules.md 中的详细规则描述

> **注意**：规则 ID 必须遵循 `BR-[%03d]-[rule-name]` 格式，其中 `rule-name` 为 1-3 个具体业务词汇。权威规范请参见 `terminology-glossary.md`。

* **非功能性需求（NFRs / Non-Functional Requirements）：**
    * **性能（Performance）：** 供应商搜索（4a）必须在 < 2 秒内返回结果。
    * **安全（Security）：** 所有操作必须由已认证用户执行。用户的审批限额（BR-001-approval-limit）必须在服务器端校验，而非客户端。
    * **审计（Auditing）：** 所有成功（8e）与失败（8b）的提交尝试都必须记录到 `po_audit_log`，包括用户 ID、时间戳以及采购订单号（PO Number，若已生成）。
    * **可用性（Usability）：** 表单必须支持键盘导航。
* **未决问题 / 备注（Open Issues / Notes）：**
    * [例如：“需要明确数据库故障（8b）的具体重试策略。”]
    * [例如：“当用户填写表单期间产品价格发生变化时会怎样？”]

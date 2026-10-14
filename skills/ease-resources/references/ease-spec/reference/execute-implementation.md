---
description: 根据 tasks.md 中定义的所有任务处理并执行，实现技术实施计划
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
  ps: scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks
---

## 用户输入

```text
$ARGUMENTS
```

在继续之前（如不为空），你必须考虑用户输入。

## 契约与 Schema

- 引用：commands/contracts-unified.md
- 校验：commands/schemas/prerequisites.schema.json

## 大纲

1. 从仓库根目录运行 `{SCRIPT}` 并解析 JSON（遵循统一契约并校验 prerequisites.schema.json）获取 FEATURE_DIR 与 AVAILABLE_DOCS 列表。所有路径必须为绝对路径。对于类似 "I'm Groot" 的单引号参数，使用转义语法：例如 'I'\''m Groot'（或在可能情况下使用双引号："I'm Groot"）。

2. 检查清单状态（如果存在 FEATURE_DIR/checklists/）：
   - 扫描 checklists/ 目录中的所有清单文件
   - 对每个清单统计：
     - 总项目数：匹配 `- [ ]` 或 `- [X]` 或 `- [x]` 的所有行
     - 已完成项目数：匹配 `- [X]` 或 `- [x]` 的行
     - 未完成项目数：匹配 `- [ ]` 的行
   - 创建状态表：

     ```text
     | Checklist | Total | Completed | Incomplete | Status |
     |-----------|-------|-----------|------------|--------|
     | ux.md     | 12    | 12        | 0          | ✓ PASS |
     | test.md   | 8     | 5         | 3          | ✗ FAIL |
     | security.md | 6   | 6         | 0          | ✓ PASS |
     ```

   - 计算整体状态：
     - PASS：所有清单的未完成项目为 0
     - FAIL：一个或多个清单存在未完成项目

   - 若任一清单未完成：
     - 显示表格与未完成项目计数
     - 停止并询问：“存在未完成的清单。是否仍要继续实施？（yes/no）”
     - 在继续之前等待用户回应
     - 若用户回答 “no” 或 “wait” 或 “stop”，则停止执行
     - 若用户回答 “yes” 或 “proceed” 或 “continue”，继续到第 3 步

   - 若所有清单均为完成状态：
     - 显示所有清单通过的表格
     - 自动继续到第 3 步

3. 加载并分析实施上下文：
   - 必需：读取 tasks.md，获取完整任务列表与执行计划
   - 必需：读取 plan.md，获取技术栈、架构与文件结构
   - 若存在：读取 data-model.md，了解实体与关系
   - 若存在：读取 contracts/ 目录，了解 API 规范与测试需求
   - 若存在：读取 quickstart.md，了解集成场景

4. 项目设置核验：
   - 必需：基于实际项目设置创建/校验忽略文件

   检测与创建逻辑：
   - 优先依据 prerequisites JSON 的 HAS_GIT 字段判断是否为 git 仓库；
   - 若字段缺失或不可信，则通过如下命令判断（若是则创建/校验 .gitignore）：

     ```sh
     git rev-parse --git-dir 2>/dev/null
     ```

   - 检查是否存在 Dockerfile* 或 plan.md 中包含 Docker → 创建/校验 .dockerignore
   - 检查是否存在 .eslintrc* → 创建/校验 .eslintignore
   - 检查是否存在 eslint.config.* → 确保配置文件中的 `ignores` 条目覆盖所需模式
   - 检查是否存在 .prettierrc* → 创建/校验 .prettierignore
   - 检查是否存在 .npmrc 或 package.json → 创建/校验 .npmignore（若发布）
   - 检查是否存在 terraform 文件（*.tf）→ 创建/校验 .terraformignore
   - 检查是否需要 .helmignore（存在 helm charts）→ 创建/校验 .helmignore

   若忽略文件已存在：核验其包含关键模式，仅追加缺失的关键模式  
   若忽略文件缺失：基于检测到的技术栈创建完整模式集

   常见技术栈对应模式（来自 plan.md 的技术栈）：
   - Node.js/JavaScript/TypeScript：`node_modules/`、`dist/`、`build/`、`*.log`、`.env*`
   - Python：`__pycache__/`、`*.pyc`、`.venv/`、`venv/`、`dist/`、`*.egg-info/`
   - Java：`target/`、`*.class`、`*.jar`、`.gradle/`、`build/`
   - C#/.NET：`bin/`、`obj/`、`*.user`、`*.suo`、`packages/`
   - Go：`*.exe`、`*.test`、`vendor/`、`*.out`
   - Ruby：`.bundle/`、`log/`、`tmp/`、`*.gem`、`vendor/bundle/`
   - PHP：`vendor/`、`*.log`、`*.cache`、`.env`
   - Rust：`target/`、`debug/`、`release/`、`*.rs.bk`、`*.rlib`、`*.prof*`、`.idea/`、`*.log`、`.env*`
   - Kotlin：`build/`、`out/`、`.gradle/`、`.idea/`、`*.class`、`*.jar`、`*.iml`、`*.log`、`.env*`
   - C++：`build/`、`bin/`、`obj/`、`out/`、`*.o`、`*.so`、`*.a`、`*.exe`、`*.dll`、`.idea/`、`*.log`、`.env*`
   - C：`build/`、`bin/`、`obj/`、`out/`、`*.o`、`*.a`、`*.so`、`*.exe`、`Makefile`、`config.log`、`.idea/`、`*.log`、`.env*`
   - Swift：`.build/`、`DerivedData/`、`*.swiftpm/`、`Packages/`
   - R：`.Rproj.user/`、`.Rhistory`、`.RData`、`.Ruserdata`、`*.Rproj`、`packrat/`、`renv/`
   - 通用：`.DS_Store`、`Thumbs.db`、`*.tmp`、`*.swp`、`.vscode/`、`.idea/`

   工具特定模式：
   - Docker：`node_modules/`、`.git/`、`Dockerfile*`、`.dockerignore`、`*.log*`、`.env*`、`coverage/`
   - ESLint：`node_modules/`、`dist/`、`build/`、`coverage/`、`*.min.js`
   - Prettier：`node_modules/`、`dist/`、`build/`、`coverage/`、`package-lock.json`、`yarn.lock`、`pnpm-lock.yaml`
   - Terraform：`.terraform/`、`*.tfstate*`、`*.tfvars`、`.terraform.lock.hcl`
   - Kubernetes/k8s：`*.secret.yaml`、`secrets/`、`.kube/`、`kubeconfig*`、`*.key`、`*.crt`

5. 解析 tasks.md 结构并提取：
   - 任务阶段：Setup、Tests、Core、Integration、Polish
   - 任务依赖：顺序与并行执行规则
   - 任务细节：ID、描述、文件路径、并行标记 [P]
   - 执行流程：顺序与依赖要求

6. 按任务计划执行实施：
   - 分阶段执行：完成每一阶段后再进入下一阶段
   - 尊重依赖：顺序任务按序执行，并行任务 [P] 可同时执行
   - 遵循 TDD：在对应实现任务之前先执行测试任务
   - 基于文件的协调：影响同一文件的任务必须顺序执行
   - 校验检查点：验证每一阶段完成情况后再继续

7. 实施执行规则：
   - 先进行 Setup：初始化项目结构、依赖与配置
   - 测试先于代码：如需为契约、实体与集成场景编写测试
   - 核心开发：实现模型、服务、CLI 命令、端点
   - 集成工作：数据库连接、中间件、日志、外部服务
   - 打磨与验证：单元测试、性能优化、文档

8. 进度跟踪与错误处理：
   - 每完成一个任务报告一次进度
   - 若任一非并行任务失败则停止执行
   - 对于并行任务 [P]，继续执行成功的，报告失败的
   - 提供清晰的错误信息与调试上下文
   - 若无法继续实施，建议后续步骤
   - 重要：对已完成的任务，务必在任务文件中将该项标记为 [X]

9. 完成验证：
   - 验证所有必需任务均已完成
   - 检查已实现功能与原始规范的一致性
   - 验证测试通过且覆盖率达标
   - 确认实施符合技术计划
   - 输出最终状态与完成工作摘要

注意：此实现假定 tasks.md 已存在完整的任务分解。若任务不完整或缺失，建议先运行任务分解阶段（参考reference/generate-tasks.md）以重新生成任务列表。

## 运行原则
- 遵循统一契约字段命名、错误模型与退出码（见 contracts-unified.md）
- 只在仓库根目录运行脚本，所有路径以绝对路径输出

# ease-dsh-plugin 项目背景与进度

更新：2026-10-14。本文件记录背景与进度；任务范围以用户当前请求为准。

## 目标与最新决策

将 `../ease-cc-plugins` 中 Ease 的规范驱动开发流程迁移到 DeepSeek Harness。
用户已明确要求保留 `/ease:starter`、`/ease:xxx` 阶段入口；此前“合并为单一
/ease-flow”方案已被替代。当前实现为九个入口 + 同包共享资源 + DSH 冒号适配器。

DSH 原生技能名及斜杠解析不支持冒号，因此必须加载随包提供的 runtime overlay。
仅复制技能目录时使用 `/ease-starter` 等合法名称。不能声称冒号名称原生可发现。

## 当前完成情况

| 工作 | 状态 |
|---|---|
| Claude plugin / skill / command 与 DSH 实现核实 | 完成，见 CONVERSION.md |
| starter、4 个阶段命令转换 | 完成 |
| constitution / bootstrap-system / analyze-code / arch-docs | 转换完成 |
| 16 个领域资料与共享模板 | 已内化，仍有外部依赖报告 |
| 冒号命令适配与非持久化 profile overlay | 已实现并用实际 DSH 组件验证 |
| 可重复转换、复制安装、完整 ZIP 分发 | 已实现并测试 |
| BRD/TRD 全流程模型实测 | 未执行 |
| ease-tools / 云端异步 / 托管 Skills API | 未迁移 |

BRD 路线为 Flow 1→2→3；TRD 的 Flow 1 内置方案与任务，直接进入 Flow 3。
原入口对 TRD 强制经过阶段2的描述不再使用。

## 维护入口

- `scripts/convert.py`：转换器；源目录缺失时不删除旧产物。
- `entry/runtime.md`：手写运行约定真源。
- `runtime/aliases.mjs`：冒号命令 pre-step 适配器。
- `scripts/prepare-runtime.mjs`：根据本机 DSH 模块路径生成 `.runtime/` overlay。
- `skills/`：生成内容，不手工改。`ease-resources/conversion-report.json` 记录缺口。
- `tests/`：转换、安装、实际 DSH 发现及事件触发测试。
- `README.md`：启动和分发操作。

## 本轮对齐审计

已补齐 Flow 3 强制依赖 systematic-debugging 和技术验证 ease-poc；修复安装位置
导致的项目根与模板查找问题，明确只读第二遍不能被同会话自检替代。
新增 source-manifest.json 和 audit_alignment.py，可逐文件检查上游漂移与缺失资源。
9 个命令、199 个参考文件、14 个共享模板对齐检查通过；8 项 Python 测试通过。
见 ALIGNMENT.md。

## 后续重点

1. 在独立业务样例项目中走一轮 BRD 与 TRD，确认模型能按需读资源并遵守门禁。
2. 按外部引用报告修复源库历史失效引用，评估 ease-tools 的必需依赖。
3. 按真实执行结果优化长指令；不要仅为缩短文件而丢失源合同。
4. 如需 Web 自动补全或云端上传，分别设计 UI alias 与托管分发机制。

本次没有修改 DSH 源码、现有 profile、用户级技能或业务项目，也没有启动付费模型任务。

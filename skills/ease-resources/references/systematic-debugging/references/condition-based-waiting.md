# Condition Based Waiting — 用条件替代任意 sleep/timeout

很多“偶现”问题来自时序依赖：服务未就绪、异步任务未完成、最终一致性尚未收敛。

本参考文档提供一种可验证的等待策略：**等待条件成立**，而不是“睡一会儿祈祷它好了”。

> ⚠️ **铁律：禁止把任意 sleep 当作修复**。sleep 只能作为诊断实验的一部分，并且必须被条件等待替代。

## 适用场景

- CI/集成测试偶现失败
- 依赖服务启动慢
- 异步处理（队列/事件）导致最终一致性
- 外部依赖偶发抖动，需要重试但希望可控

## 核心原则

1. **条件可观测**：等待的条件必须可观测（HTTP health、文件出现、记录存在、状态机到达某状态）。
2. **有上限**：必须有最大等待时间与最大重试次数。
3. **可诊断**：每次等待/重试都记录关键上下文与当前状态。
4. **失败可解释**：超时后给出“最后观测到的状态”，而不是一句“timeout”。

## 通用伪代码

```text
deadline = now + MAX_WAIT
attempt = 0
while now < deadline:
  attempt += 1
  state = observe()
  if condition(state):
    return success
  sleep(backoff(attempt))
return timeout_with_last_state(state)
```

## 最小实践清单

- 定义 `observe()`：如何读取状态（调用接口、查 DB、读日志、查文件）
- 定义 `condition()`：状态达成的判定
- 选择退避策略：固定间隔 / 指数退避（推荐指数退避 + 上限）
- 记录：attempt、elapsed、state 摘要

## 常见错误

- 条件不可观测，只能凭感觉 sleep
- 没有上限导致卡死
- 只重试不记录状态，无法定位为什么一直不满足

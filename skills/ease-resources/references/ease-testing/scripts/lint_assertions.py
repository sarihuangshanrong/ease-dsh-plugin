#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Assertion / Determinism Lint — 把 ease-testing 的"断言硬禁令(B)"与"确定性硬禁令(C)"
落成可机械扫描的检查项。

设计原则（请先读）：
  这是**高信号、低误报**的"冒烟式"扫描器，不是编译器/AST 检查器。它只标记
  **几乎无歧义**的违规模式（字面恒真断言、`verify(any())`、裸 `assert_called_once()`、
  sleep、未 seed 的随机、`@Order` 等）。需要方法级语义判断的规则（如"某测试唯一断言
  是 L1 存在性"、"assertThrows 未断言 message/code"、"if 无 else 兜底"）误报率高，
  **不在本脚本范围**——它们仍由 SKILL.md 的 §6.5.5 / §7.3.5 人工门禁兜底。

  规则 ID 对齐 SKILL.md 禁令编号（B8/B4/C4/C5/C1 …）。命中 HIGH 即视为应改写。

用法：
  python3 lint_assertions.py path/to/test_file.py [more_paths...]   # 扫描测试文件
  python3 lint_assertions.py src/test/                              # 递归扫描目录（默认仅 .java/.go/.py/.ts …）
  python3 lint_assertions.py --markdown docs/                       # 额外扫描 .md 中的代码块
  python3 lint_assertions.py --selftest                             # 自检（证明规则会咬合）
  # CI：命中 HIGH 即退出码 1

  --markdown：提取 .md 的 fenced code block（仅 java/go/python/ts 等测试语言块）按行扫描，
  行号映射回 .md 真实行号。默认关闭——扫真实测试代码时不把 .md 拉进来；仅当要校验"skill
  文档里的 demo 代码本身是否合规"时启用（见 tests/claude-code/test-ease-testing-lint.sh）。
"""
import os
import re
import sys

# --------------------------------------------------------------------------- #
# 规则：(rule_id, severity, [patterns], message)
#   severity: HIGH = 明确违规应改写；MID = 需人工复核（可能是误报）
# --------------------------------------------------------------------------- #
RULES = [
    ("B8_LITERAL_TRUE", "HIGH",
     [r"assertTrue\s*\(\s*true\s*\)", r"assertFalse\s*\(\s*false\s*\)",
      r"expect\s*\(\s*true\s*\)\s*\.\s*toBe\s*\(\s*true\s*\)",
      r"expect\s*\(\s*true\s*\)\s*\.\s*toBeTruthy\s*\(\s*\)",
      r"^\s*assert\s+True\s*(#.*)?$", r"^\s*assert\s+False\s*(#.*)?$"],
     "恒真/空真断言：断言在行为出错时仍为真（B8），删除或改为断言具体值"),

    ("B4_VERIFY_ANY", "HIGH",
     [r"verify\s*\([^)]*\)\s*\.\s*\w+\s*\(\s*any\s*\(",   # verify(m).method(any(
      r"assert_called_once\s*\(\s*\)",                     # 无实参
      r"toHaveBeenCalled\s*\(\s*\)"],                      # 裸调用，无 With
     "交互只校验'被调过'未校验实参（B4/B6）：改 argThat/ArgumentCaptor/assert_called_once_with 精确实参"),

    ("B_NOOP_SOLO", "MID",
     [r"assertDoesNotThrow\s*\(",
      r"expect\s*\([^)]*\)\s*\.\s*not\s*\.\s*toThrow\s*\(\s*\)"],
     "'未抛异常'类断言常作为唯一验证（L0）：复核该测试是否还断言了状态/交互"),

    ("C3_REAL_CLOCK", "HIGH",
     [r"System\.currentTimeMillis", r"System\.nanoTime",
      # 只匹配已知系统时钟类型；timeProvider.now() 等注入式接口是合法的固定时间来源。
      r"\b(?:LocalDateTime|LocalDate|Instant|OffsetDateTime|ZonedDateTime)\.now\s*\(\s*\)",
      r"\bDate\.now\s*\(\s*\)",      # JavaScript Date.now()
      r"new\s+Date\s*\(\s*\)",       # new Date()
      r"time\.Now\s*\(\)",           # Go time.Now()
      r"datetime\.now\s*\(\s*\)"],   # Python datetime.now()
     "真实时钟（D3）：测试须注入 Clock.fixed/常量，禁止 now()/currentTimeMillis()/new Date()，断言不得含运行时时间表达式"),

    ("C4_SLEEP", "HIGH",
     [r"Thread\.sleep", r"time\.sleep", r"time\.Sleep", r"setTimeout"],
     "sleep 式同步（D5/C4）：改 CountDownLatch/Awaitility/同步 Executor/直接回调；超时值不得依赖机器性能（用 Awaitility atMost 而非固定 sleep）"),

    ("C5_RANDOM_UNSEEDED", "MID",
     [r"Math\.random", r"random\.random\b", r"random\.randint", r"random\.choice",
      r"random\.uniform", r"UUID\.randomUUID", r"uuid\.uuid4", r"math/rand"],
     "非确定性输入（D6/C5）：断言数据禁来自 Random/UUID.randomUUID()/自增序列；若确需随机须固定 seed 并注释"),

    ("C1_TEST_ORDER", "HIGH",
     [r"@Order\s*\(", r"@TestMethodOrder"],
     "测试顺序依赖（D1/C1）：删除排序注解，每个测试须能独立通过——必须能作为该类唯一被执行的测试而通过"),
]

_COMPILED = [(rid, sev, [re.compile(p) for p in pats], msg)
             for (rid, sev, pats, msg) in RULES]

_TEST_EXT = {".java", ".kt", ".go", ".py", ".ts", ".tsx", ".js", ".jsx"}

# .md fenced code block 的语言标记 → 扩展名，用于识别"文档里的 demo 代码"。
# 只有这些语言的代码块才扫；bash/text/json 等块跳过（避免误报命令行里的 sleep 等）。
_LANG_EXT = {
    "java": ".java", "kotlin": ".kt", "kt": ".kt",
    "go": ".go",
    "python": ".py", "python3": ".py", "py": ".py",
    "typescript": ".ts", "ts": ".ts", "tsx": ".tsx",
    "javascript": ".js", "js": ".js", "jsx": ".jsx",
}


def scan_file(path):
    """对单个文件逐行扫描，返回 [(line_no, rule_id, severity, message, line_text)]。"""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError:
        return []
    return _scan_numbered_lines(list(enumerate(lines, start=1)))


def _uses_jest_fake_timers(numbered_lines):
    """只有同时启用并推进 Jest fake timers 时，setTimeout 才是确定性调度而非真实等待。"""
    text = "\n".join(raw for _line_no, raw in numbered_lines)
    return (
        re.search(r"\bjest\.useFakeTimers\s*\(", text) is not None
        and re.search(
            r"\bjest\.(?:advanceTimersByTime|advanceTimersToNextTimer|runAllTimers|runOnlyPendingTimers)\s*\(",
            text,
        ) is not None
    )


def _scan_numbered_lines(numbered_lines):
    """扫描带真实行号的代码；对受 Jest fake timers 控制的 setTimeout 做上下文豁免。"""
    findings = []
    fake_timers = _uses_jest_fake_timers(numbered_lines)
    for i, raw in numbered_lines:
        if "lint:ignore" in raw:
            continue  # 行级显式豁免（如教学里有意展示的反例）
        for rid, sev, pats, msg in _COMPILED:
            if rid == "C4_SLEEP" and "setTimeout" in raw and fake_timers:
                continue
            for pat in pats:
                if pat.search(raw):
                    findings.append((i, rid, sev, msg, raw.rstrip()))
                    break  # 同一规则同一行只报一次
    return findings


def _scan_markdown_lines(lines):
    """对 .md 的行列表扫描其中的 fenced code block：仅测试语言块逐行扫，
    返回 [(line_no, rule_id, severity, message, line_text)]，行号为 .md 真实行号。"""
    in_block = False
    lang = ""
    block = []
    findings = []

    def _flush_block():
        if lang in _LANG_EXT:
            findings.extend(_scan_numbered_lines(block))

    for i, raw in enumerate(lines, start=1):
        fence = raw.lstrip()
        if fence.startswith("```"):
            if not in_block:
                rest = fence[3:].strip()
                lang = rest.split()[0].lower() if rest else ""
                in_block = True
                block = []
            else:
                _flush_block()
                in_block = False
                lang = ""
                block = []
            continue
        if in_block and lang in _LANG_EXT:
            block.append((i, raw))
    if in_block:
        _flush_block()
    return findings


def scan_markdown(path):
    """扫描单个 .md 文件中的代码块。"""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError:
        return []
    return _scan_markdown_lines(lines)


def scan_paths(paths, scan_md=False):
    """递归扫描路径，返回 [(file, line_no, rule_id, severity, message, line_text), ...] 与文件数。

    scan_md=True 时，额外扫描 .md 中的 fenced code block（用于校验文档里的 demo 代码）。"""
    rows = []
    files = 0

    def _scan_one(fp, ext):
        nonlocal files
        files += 1
        itr = scan_markdown(fp) if ext == ".md" else scan_file(fp)
        for (ln, rid, sev, msg, line) in itr:
            rows.append((fp, ln, rid, sev, msg, line))

    for p in paths:
        if os.path.isdir(p):
            for root, _dirs, fnames in os.walk(p):
                for fn in fnames:
                    ext = os.path.splitext(fn)[1]
                    if ext in _TEST_EXT or (scan_md and ext == ".md"):
                        _scan_one(os.path.join(root, fn), ext)
        elif os.path.isfile(p):
            ext = os.path.splitext(p)[1]
            if ext in _TEST_EXT or (scan_md and ext == ".md"):
                _scan_one(p, ext)
    return rows, files


def cli(argv):
    if "--selftest" in argv:
        return run_selftest()
    scan_md = "--markdown" in argv or "--md" in argv
    paths = [a for a in argv[1:] if not a.startswith("-")]
    if not paths:
        print(__doc__)
        print("错误：未给定扫描路径。示例：python3 lint_assertions.py src/test/")
        return 2
    rows, files = scan_paths(paths, scan_md=scan_md)
    high = sum(1 for r in rows if r[3] == "HIGH")
    for (fp, ln, rid, sev, msg, line) in rows:
        tag = "HIGH" if sev == "HIGH" else "MID "
        print("%s:%d: [%s|%s] %s" % (fp, ln, rid, tag, msg))
    print("\n扫描文件 %d 个，命中 %d 条（其中 HIGH %d 条）。" % (files, len(rows), high))
    return 1 if high > 0 else 0


# --------------------------------------------------------------------------- #
# 自检：把"已知坏片段"喂给规则，证明每条都会被咬；"已知好片段"不应误报。
# 这是本脚本"证明自己有用"的闭环——避免空规则。
# --------------------------------------------------------------------------- #
BAD_CASES = [
    ("assertTrue(true);", {"B8_LITERAL_TRUE"}),
    ("expect(true).toBe(true);", {"B8_LITERAL_TRUE"}),
    ("assert True", {"B8_LITERAL_TRUE"}),
    ("verify(repo).save(any());", {"B4_VERIFY_ANY"}),
    ("mock_repo.save.assert_called_once()", {"B4_VERIFY_ANY"}),
    ("expect(repo.save).toHaveBeenCalled();", {"B4_VERIFY_ANY"}),
    ("Thread.sleep(1000);", {"C4_SLEEP"}),
    ("time.sleep(2)", {"C4_SLEEP"}),
    ("setTimeout(done, 100);", {"C4_SLEEP"}),
    ("int id = (int)(Math.random()*1000);", {"C5_RANDOM_UNSEEDED"}),
    ("String uid = UUID.randomUUID().toString();", {"C5_RANDOM_UNSEEDED"}),
    ("@TestMethodOrder(OrderAnnotation.class)", {"C1_TEST_ORDER"}),
    ("System.currentTimeMillis()", {"C3_REAL_CLOCK"}),
    ("LocalDateTime.now()", {"C3_REAL_CLOCK"}),
    ("time.Now()", {"C3_REAL_CLOCK"}),
]
GOOD_CASES = [
    "assertThat(result.getStatus()).isEqualTo(OrderStatus.PAID);",
    "verify(repo).save(argThat(u -> u.getName().equals(\"John\")));",
    "mock_repo.save.assert_called_once_with(expected_user)",
    "expect(repo.save).toHaveBeenCalledWith({ id: 1 });",
    "await().atMost(2, SECONDS).until(() -> done);",
    "Random rnd = new Random(42L);  // 固定 seed",
    # 打桩（stub）用 any() 是合理的——只 verify(...) 用 any() 才该报。这行必须干净。
    "when(userRepository.save(any(User.class))).thenReturn(user);",
    # 带参 now(clock) 合法（注入时钟），不匹配无参 now()——不可误报。
    "LocalDateTime.now(clock);",
    # 注入式时间提供器不是系统真实时钟。
    "Instant actual = timeProvider.now();",
    # setTimeout 由 Jest fake timers 推进时不依赖墙上时间。
    "jest.useFakeTimers();\nsetTimeout(resolve, 10);\njest.advanceTimersByTime(10);",
]


def _scan_text(text):
    rows = _scan_numbered_lines(list(enumerate(text.splitlines(), start=1)))
    return {row[1] for row in rows}


def run_selftest():
    fails = 0
    for snippet, expected in BAD_CASES:
        got = _scan_text(snippet)
        if not (got & expected):
            print("  [MISS] 规则未咬合：%r 期望 %s 得 %s" % (snippet, expected, got))
            fails += 1
        else:
            print("  [OK]   %r -> %s" % (snippet, got & expected))
    for snippet in GOOD_CASES:
        got = _scan_text(snippet)
        if got:
            print("  [FALSE] 误报好片段：%r 被判 %s" % (snippet, got))
            fails += 1
        else:
            print("  [OK]   干净：%r" % snippet)
    # markdown 代码块扫描：.md 里测试语言块的违规要被扫到；非测试语言块/散文不扫
    MD_CASES = [
        ("```java\nverify(repo).save(any());\n```", {"B4_VERIFY_ANY"}),
        ("```python\nmock.save.assert_called_once()\n```", {"B4_VERIFY_ANY"}),
        ("```bash\nverify(repo).save(any());\n```", set()),     # bash 块不扫
        ("散文里的 verify(repo).save(any()); 不算代码", set()),  # 非代码块不扫
        ("```java\nverify(repo).save(any());  // lint:ignore\n```", set()),  # 行级豁免
        ("```typescript\njest.useFakeTimers();\nsetTimeout(done, 10);\njest.runAllTimers();\n```", set()),
    ]
    for md, expected in MD_CASES:
        got = set(r[1] for r in _scan_markdown_lines(md.splitlines(keepends=True)))
        if expected:
            if not (got & expected):
                print("  [MISS] markdown 未咬合：期望 %s 得 %s" % (expected, got))
                fails += 1
            else:
                print("  [OK]   markdown 命中：%s" % (got & expected))
        else:
            if got:
                print("  [FALSE] markdown 误报：%s" % got)
                fails += 1
            else:
                print("  [OK]   markdown 干净")
    print("\n自检结束。" + ("全部通过 ✅" if fails == 0 else "失败 %d 项 ❌" % fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(cli(sys.argv))

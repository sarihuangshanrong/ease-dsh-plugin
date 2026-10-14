# Project Type Detection (Optional)

This document is **optional**. Prefer using `Glob` and `Grep` directly in your current session.

## Goal

Detect language/framework quickly before implementing code:

1. Pick the correct language reference: `references/coding-*.md`
2. Detect whether this is a **MumbleSDK** project (if yes → **must use `mumblesdk` skill**)

## Preferred (Cross-platform) Checks

### Language detection (Glob)

| Language | Characteristic files |
|---|---|
| Java | `pom.xml` or `build.gradle` |
| Go | `go.mod` |
| Python | `requirements.txt` or `pyproject.toml` |
| TypeScript | `package.json` + `tsconfig.json` |

### MumbleSDK detection (Grep)

Use Grep to look for either:

- `mumble-sdk` dependency in build files
- Typical MumbleSDK base classes/DAO patterns in source

Examples of patterns (non-exhaustive):

- `mumble-sdk`
- `MumbleAbstractBaseController`
- `AbstractSimpleDAO`

## Optional Shell Snippet (If Available)

If your environment supports shell execution, the following snippet is a **convenience only** (not required):

```bash
IS_JAVA=$( [ -f "pom.xml" ] || [ -f "build.gradle" ] && echo true )
IS_MUMBLE=$( grep -q "mumble-sdk" pom.xml build.gradle 2>/dev/null || \
             grep -rq "MumbleAbstractBaseController\|AbstractSimpleDAO" src/ 2>/dev/null && echo true )
```

# Project Detection for Review

Use the requested review target first, then file extensions, then project markers.

| Target | Markers | Reference |
|---|---|---|
| Java | `pom.xml`, `build.gradle`, `.java` | `java.md` |
| Go | `go.mod`, `.go` | `go.md` |
| Python | `pyproject.toml`, `requirements.txt`, `.py` | `python.md` |
| TypeScript | `tsconfig.json`, `package.json`, `.ts`/`.tsx` | `typescript.md` |

Search Java targets for `mumble-sdk`, `MumbleAbstractBaseController`, or `AbstractSimpleDAO`; load `mumblesdk` constraints when detected. For mixed-language reviews, build a boundary map and apply each language reference only to matching files.

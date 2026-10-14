# Project Detection for Implementation

Use the user's explicit target first, then the edited file extension, then project markers.

| Target | Markers | Reference |
|---|---|---|
| Java | `pom.xml`, `build.gradle`, `.java` | `java.md` |
| Go | `go.mod`, `.go` | `go.md` |
| Python | `pyproject.toml`, `requirements.txt`, `.py` | `python.md` |
| TypeScript | `tsconfig.json`, `package.json`, `.ts`/`.tsx` | `typescript.md` |

Before implementation, search Java build files and source for `mumble-sdk`, `MumbleAbstractBaseController`, or `AbstractSimpleDAO`. If found, load `mumblesdk` before applying this skill.

For polyglot changes, choose the reference per edited file and document cross-language contracts. Do not infer the target solely from unrelated repository-root markers.

# POC 验证工具箱

本文档汇总 POC 验证中常用的工具，按语言、用途和验证类型分类。

## 性能测试工具

| 工具 | 用途 | 适用语言 | 使用说明 |
|------|------|----------|----------|
| JMH (Java Microbenchmark Harness) | 微基准测试 | Java | Maven/Gradle 集成，运行 `mvn package -Pjmh` |
| wrk | HTTP 压测 | 通用 | 命令行：`wrk -t4 -c100 -d30s http://example.com` |
| k6 | 现代压测工具 | 通用 | 编写 JS 脚本，`k6 run script.js` |
| Apache Bench (ab) | 简单压测 | 通用 | 命令行：`ab -n 1000 -c 10 http://example.com` |
| pytest-benchmark | 性能测试 | Python | 测试代码中添加 `@pytest.mark.benchmark` |
| go test -bench | 基准测试 | Go | 包含 `_test.go` 文件，运行 `go test -bench=. -benchmem` |

## 监控和诊断工具

| 工具 | 用途 | 适用语言 | 使用说明 |
|------|------|----------|----------|
| pprof | Go 性能分析 | Go | 运行时添加 `-cpuprofile`/`-memprofile` 参数 |
| arthas | Java 诊断 | Java | 下载 jar，`java -jar arthas-boot.jar` |
| py-spy | Python 性能分析 | Python | `py-spy top --pid <PID>` |
| VisualVM | Java 监控 | Java | JDK 内置，或下载独立版本 |
| tcpdump | 网络抓包 | 通用 | `tcpdump -i any -w capture.pcap` |

## 快速集成测试工具

| 工具 | 用途 | 适用场景 |
|------|------|----------|
| curl | 测试 HTTP API | REST API 调用 |
| jq | 处理 JSON | API 响应解析 |
| Docker Compose | 本地多容器验证 | 微服务集成 |
| Postman | API 测试 | HTTP/HTTPS 接口 |

## 数据库测试辅助

| 工具 | 用途 | 适用场景 |
|------|------|----------|
| docker | 快速启动数据库 | 临时数据库实例 |
| sqlcmd/mysql client | 直接 SQL 测试 | 数据库操作验证 |
| DBeaver | 数据库客户端 | 多数据库连接 |

## 架构验证工具

| 工具 | 用途 | 适用场景 | 使用说明 |
|------|------|----------|----------|
| Maven Dependency Tree | 依赖树分析 | Java 项目 | `mvn dependency:tree` |
| Gradle Dependencies | 依赖树分析 | Gradle 项目 | `gradle dependencies` |
| go mod graph | 依赖图分析 | Go 项目 | `go mod graph` |
| pipdeptree | 依赖树分析 | Python 项目 | `pip install pipdeptree && pipdeptree` |
| npm ls / pnpm ls | 依赖树分析 | Node.js 项目 | `npm ls --all` |
| jdeps | Java 依赖分析 | Java 模块依赖 | `jdeps -verbose:class target/*.jar` |
| ArchUnit | 架构规则验证 | Java | 编写架构规则测试 |
| Dependency-cruiser | 依赖规则验证 | JavaScript/TypeScript | 配置规则检查依赖方向 |

## 安全验证工具

| 工具 | 用途 | 适用场景 | 使用说明 |
|------|------|----------|----------|
| OWASP Dependency-Check | 依赖漏洞扫描 | Java/通用 | `mvn org.owasp:dependency-check-maven:check` |
| npm audit | 依赖安全审计 | Node.js | `npm audit` |
| pip-audit | 依赖安全审计 | Python | `pip install pip-audit && pip-audit` |
| govulncheck | Go 漏洞检查 | Go | `go install golang.org/x/vuln/cmd/govulncheck@latest` |
| Trivy | 容器/依赖扫描 | 通用 | `trivy image [image_name]` |
| Snyk | 安全扫描 | 通用 | `snyk test` |

## 技术栈检测参考

POC 启动时自动检测项目技术栈，以下为常见检测信号：

| 技术栈 | 检测文件 | 关键标志 |
|--------|----------|----------|
| Java/Maven | `pom.xml` | `<groupId>`, `<artifactId>`, `<version>` |
| Java/Gradle | `build.gradle` / `build.gradle.kts` | `plugins {}`, `dependencies {}` |
| Spring Boot | `pom.xml` + `application.yml` | `spring-boot-starter-*` |
| MumbleSDK | `pom.xml` | `mumblesdk-*` 依赖 |
| Go | `go.mod` | `module`, `go` 版本 |
| Python | `requirements.txt` / `pyproject.toml` | 依赖声明 |
| Node.js | `package.json` | `dependencies`, `devDependencies` |
| TypeScript | `tsconfig.json` | `compilerOptions` |

## 工具选用决策矩阵

### 按 POC 类型选用

| POC 类型 | 首选工具 | 辅助工具 |
|----------|----------|----------|
| Feasibility | 单元测试框架 | 依赖分析工具 |
| Performance | 语言专用基准工具 + wrk/k6 | 监控诊断工具 |
| Migration | 版本管理 + 差异对比 | 自动化测试框架 |
| Integration | curl/jq + Docker Compose | 抓包工具 |
| Security | OWASP 工具链 + 安全扫描 | 渗透测试工具 |
| Architecture Fit | 依赖分析 + 架构验证 | 文档生成工具 |

### 按语言选用性能测试工具

| 语言 | 微基准 | 压测 | 内存分析 |
|------|--------|------|----------|
| Java | JMH | wrk/k6 + JMeter | VisualVM/arthas |
| Go | go test -bench | wrk/k6 | pprof |
| Python | pytest-benchmark | locust/k6 | py-spy/memory_profiler |
| Node.js | benchmark.js | wrk/k6 | clinic/0x |

## 常用命令示例

### Java 性能基准
```bash
# 安装 JMH
mvn archetype:generate -DinteractiveMode=false \
  -DarchetypeGroupId=org.openjdk.jmh \
  -DarchetypeArtifactId=jmh-java-benchmark-archetype \
  -DarchetypeVersion=1.37

# 运行基准
mvn clean install
java -jar target/benchmarks.jar
```

### Java 依赖分析
```bash
# 依赖树
mvn dependency:tree

# 依赖冲突分析
mvn dependency:tree -Dverbose

# 安全扫描
mvn org.owasp:dependency-check-maven:check
```

### Python 性能测试
```bash
# 安装 pytest-benchmark
pip install pytest-benchmark

# 运行测试
pytest test_perf.py --benchmark-only
```

### Python 依赖分析
```bash
# 依赖树
pip install pipdeptree && pipdeptree

# 安全审计
pip install pip-audit && pip-audit
```

### Go 基准测试
```bash
# 运行所有基准测试
go test -bench=. -benchmem

# 运行指定测试
go test -bench=TestFunction -benchmem

# 显示内存分配
go test -bench=. -benchmem -memprofile=mem.prof

# 依赖图
go mod graph

# 漏洞检查
govulncheck ./...
```

### Node.js 依赖分析
```bash
# 依赖树
npm ls --all

# 安全审计
npm audit

# 依赖分析
npx dependency-cruiser src
```

### HTTP 压测
```bash
# wrk
wrk -t4 -c100 -d30s http://localhost:8080/api

# k6
k6 run --vus 100 --duration 30s script.js

# Apache Bench
ab -n 10000 -c 100 http://localhost:8080/api
```

## 容器化验证环境

### 快速启动数据库
```bash
# PostgreSQL
docker run -d --name poc-pg -e POSTGRES_PASSWORD=test -p 5432:5432 postgres:15

# Redis
docker run -d --name poc-redis -p 6379:6379 redis:7

# MySQL
docker run -d --name poc-mysql -e MYSQL_ROOT_PASSWORD=test -p 3306:3306 mysql:8
```

### Docker Compose 多服务验证
```yaml
version: '3'
services:
  app:
    build: .
    ports:
      - "8080:8080"
    depends_on:
      - db
      - cache
  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: test
  cache:
    image: redis:7
```

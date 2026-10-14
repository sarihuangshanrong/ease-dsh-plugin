#!/bin/bash
# Ease Spec Auto Integration Script
# 用于在 ease command 执行后自动触发 ease-spec 流程

set -euo pipefail

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示使用帮助
show_usage() {
    cat << EOF
Ease Spec Auto Integration Script

用法:
    $0 <docs_dir> [options]

参数:
    docs_dir        docs 目录路径 (如: docs/user-management)

选项:
    --auto          自动执行完整流程
    --prompt        提示用户是否继续
    --dry-run       只显示将要执行的命令
    --with-analyze  包含分析阶段
    --change-id ID  复用指定的单次变更标识；未提供时自动生成
    --desc TEXT     功能描述
    --tech TEXT     技术栈选择
    --debug         显示调试信息

示例:
    $0 docs/user-management --auto
    $0 docs/user-management --prompt --desc "用户认证系统"
    $0 docs/user-management --dry-run --tech "Spring Boot + JWT"
EOF
}

# 解析命令行参数
DOCS_DIR=""
AUTO_MODE=false
PROMPT_MODE=false
DRY_RUN=false
WITH_ANALYZE=false
FEATURE_DESC=""
TECH_STACK=""
CHANGE_ID=""
DEBUG=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --auto)
            AUTO_MODE=true
            shift
            ;;
        --prompt)
            PROMPT_MODE=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --with-analyze)
            WITH_ANALYZE=true
            shift
            ;;
        --desc)
            FEATURE_DESC="$2"
            shift 2
            ;;
        --tech)
            TECH_STACK="$2"
            shift 2
            ;;
        --change-id)
            CHANGE_ID="$2"
            shift 2
            ;;
        --debug)
            DEBUG=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            if [[ -z "$DOCS_DIR" ]]; then
                DOCS_DIR="$1"
            else
                print_error "未知参数: $1"
                show_usage
                exit 1
            fi
            shift
            ;;
    esac
done

# 验证参数
if [[ -z "$DOCS_DIR" ]]; then
    print_error "必须指定 docs 目录"
    show_usage
    exit 1
fi

# 规范化路径
DOCS_DIR=$(realpath "$DOCS_DIR")
DOCS_DIR_NAME=$(basename "$DOCS_DIR")

# 调试输出
if [[ "$DEBUG" == "true" ]]; then
    print_info "DOCS_DIR: $DOCS_DIR"
    print_info "DOCS_DIR_NAME: $DOCS_DIR_NAME"
    print_info "AUTO_MODE: $AUTO_MODE"
    print_info "PROMPT_MODE: $PROMPT_MODE"
fi

# 验证 docs 目录存在
if [[ ! -d "$DOCS_DIR" ]]; then
    print_error "docs 目录不存在: $DOCS_DIR"
    exit 1
fi

# 提取功能编号和名称
if [[ "$DOCS_DIR_NAME" =~ ^([0-9]+)-(.+)$ ]]; then
    FEATURE_NUM="${BASH_REMATCH[1]}"
    FEATURE_NAME="${BASH_REMATCH[2]}"
    DOMAIN_ID="${FEATURE_NUM}-${FEATURE_NAME}"
    if [[ -z "$CHANGE_ID" ]]; then
        CHANGE_ID="$(date +%Y%m%d%H%M%S)-${FEATURE_NAME}"
    fi
    EASES_DIR=".eases/${CHANGE_ID}"
else
    print_error "docs 目录名称格式不正确，应为: 编号-名称"
    exit 1
fi

print_info "检测到功能: ${FEATURE_NUM}-${FEATURE_NAME}"

# 检查是否有 ease-spec 技能
check_ease_spec() {
    # 查找 ease-spec 技能目录
    local skill_dirs=(
        "plugins/ease/skills/ease-spec"
        ".ease/skills/ease-spec"
        "skills/ease-spec"
    )

    for dir in "${skill_dirs[@]}"; do
        if [[ -d "$dir" ]]; then
            EASE_SPEC_DIR="$dir"
            return 0
        fi
    done

    return 1
}

# 构建 ease-spec 流程指引
build_ease_spec_command() {
    local guidance=""
    guidance+="# Ease Spec 流程指引（命令触发已过时）\n"
    guidance+="# 请参考以下文档手动执行：\n"
    guidance+="# \n"
    guidance+="# 1. 参考 reference/一键执行.md 文档\n"
    guidance+="# 2. 处理目录：docs/[module_name]\n"
    guidance+="# 3. 使用 --from-docs 参数进行目录映射\n"
    if [[ "$WITH_ANALYZE" == "true" ]]; then
        guidance+="# 4. 包含分析阶段：参考 reference/一致性分析.md\n"
    fi
    if [[ -n "$FEATURE_DESC" ]]; then
        guidance+="# 5. 功能描述：$FEATURE_DESC\n"
    fi
    guidance+="# \n"
    guidance+="# 详细步骤请参考 reference/一键执行.md 中的说明。\n"

    echo -e "$guidance"
}

# 执行 ease-spec 流程
execute_ease_spec() {
    local guidance=$(build_ease_spec_command)

    print_info "准备执行 ease-spec 流程..."
    print_info "指引:"
    echo -e "$guidance"

    if [[ "$DRY_RUN" == "true" ]]; then
        print_info "[DRY RUN] 将输出指引信息"
        return 0
    fi

    # 输出指引信息
    print_info "请根据以上指引手动执行 ease-spec 流程..."
    print_info "详细步骤请参考 reference/一键执行.md 文档。"
    print_success "指引已生成，请手动执行相应步骤。"
    print_success "生成的规范将位于: $EASES_DIR"
    return 0
}

# 生成报告
generate_report() {
    mkdir -p "$EASES_DIR/outputs"
    local report_file="$EASES_DIR/outputs/integration-report.md"

    cat > "$report_file" << EOF
# Ease Spec Integration Report

## 基本信息
- Docs 目录: \`docs/[module_name]\`（领域模块目录）
- Domain ID: \`${DOMAIN_ID}\`
- Change ID: \`${CHANGE_ID}\`
- Eases 目录: \`${EASES_DIR}\`
- 生成时间: $(date)

## 执行的 ease-spec 命令
\`\`\`bash
$(build_ease_spec_command)
\`\`\`

## 映射的文件

### 从 docs 到 eases
EOF

    # 添加文件映射信息
    if [[ -f "$EASES_DIR/flow-1-analyze/outputs/analysis-report.md" ]]; then
        echo "- \`flow-1-analyze/outputs/analysis-report.md\` → \`spec.md\` (业务需求部分)" >> "$report_file"
    elif [[ -f "$DOCS_DIR/analyze-brd-output.md" ]]; then
        echo "- legacy \`analyze-brd-output.md\` → \`spec.md\`（只读兼容，建议迁移）" >> "$report_file"
    fi

    if [[ -f "$DOCS_DIR/architecture-review-output.md" ]]; then
        echo "- \`architecture-review-output.md\` → \`plan.md\` (架构决策)" >> "$report_file"
    fi

    if [[ -d "$DOCS_DIR/artifacts" ]]; then
        echo "- \`artifacts/\` → \`contracts/\`" >> "$report_file"
    fi

    cat >> "$report_file" << EOF

## 下一步操作

1. 查看 .eases 目录中的规范文档
2. 根据需要修改计划
3. 继续执行实现

\`\`\`bash
# 查看生成的规范
ls -la ${EASES_DIR}/

# 继续执行（如果需要）
cd ${EASES_DIR}/
# 查看任务列表
cat tasks.md
\`\`\`
EOF

    print_success "集成报告已生成: $report_file"
}

# 主函数
main() {
    print_info "开始 Ease Spec 自动集成流程..."

    # 检查 ease-spec 技能
    if ! check_ease_spec; then
        print_error "未找到 ease-spec 技能"
        exit 1
    fi

    print_info "找到 ease-spec 技能: $EASE_SPEC_DIR"

    # 提示用户
    if [[ "$PROMPT_MODE" == "true" && "$AUTO_MODE" != "true" ]]; then
        echo
        echo "即将执行 ease-spec 流程，将："
        echo "1. 映射 docs/[module_name] 到 eases/[编号]-[功能名]"
        echo "2. 整合分析结果生成需求规范"
        echo "3. 创建技术实施计划"
        echo "4. 分解为可执行任务"
        echo
        read -p "是否继续？(y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "用户取消操作"
            exit 0
        fi
    fi

    # 执行 ease-spec
    if execute_ease_spec; then
        # 生成报告
        generate_report

        # 显示成功信息
        echo
        print_success "=== 集成完成 ==="
        echo
        echo "Docs 目录: $DOCS_DIR"
        echo "Eases 目录: $EASES_DIR"
        echo
        echo "查看生成的规范:"
        echo "  ls -la $EASES_DIR/"
        echo
        echo "继续开发流程:"
        echo "  cd $EASES_DIR"
        echo "  cat tasks.md  # 查看任务列表"
    else
        print_error "集成失败，请检查错误信息"
        exit 1
    fi
}

# 执行主函数
main

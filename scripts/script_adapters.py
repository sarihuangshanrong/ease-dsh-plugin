"""Explicit, drift-checked relocation patches for bundled upstream scripts."""

def adapt_script(relative, text):
    replacements = []
    if relative == 'ease-spec/scripts/bash/common.sh':
        replacements = [('''        # Fall back to script location for non-git repos
        local script_dir="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        (cd "$script_dir/../../.." && pwd)''', '''        # DSH: bundled scripts live outside the user's project.
        pwd -P''')]
    elif relative == 'ease-spec/scripts/bash/create-new-feature.sh':
        replacements = [('REPO_ROOT="$(find_repo_root "$SCRIPT_DIR")"', 'REPO_ROOT="$(pwd -P)"')]
    elif relative == 'ease-spec/scripts/powershell/common.ps1':
        replacements = [('return (Resolve-Path (Join-Path $PSScriptRoot "../../..")).Path', 'return (Get-Location).Path')]
    elif relative == 'ease-spec/scripts/powershell/create-new-feature.ps1':
        replacements = [('$fallbackRoot = (Find-RepositoryRoot -StartDir $PSScriptRoot)', '$fallbackRoot = (Get-Location).Path')]
    elif relative == 'ease-spec/scripts/auto-integrate.sh':
        replacements = [('    local skill_dirs=(', '    local skill_dirs=(\n        "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"')]
    for old, new in replacements:
        if text.count(old) != 1:
            raise ValueError(f'Upstream script changed; review adapter: {relative}')
        text = text.replace(old, new)
    # Preserve project-custom templates; fall back to the shipped template.
    if relative in ('ease-spec/scripts/bash/create-new-feature.sh', 'ease-spec/scripts/bash/setup-plan.sh'):
        import re
        text, count = re.subn(r'(TEMPLATE="\$REPO_ROOT/\.specify/templates/([\w-]+\.md)")',
            lambda m: m[1] + '\n' + f'[[ -f "$TEMPLATE" ]] || TEMPLATE="$SCRIPT_DIR/../../templates/{m[2]}"', text)
        expected = 2 if 'create-new-feature' in relative else 1
        if count != expected:
            raise ValueError(f'Upstream template lookup changed: {relative}')
    if relative in ('ease-spec/scripts/powershell/create-new-feature.ps1', 'ease-spec/scripts/powershell/setup-plan.ps1'):
        import re
        text, count = re.subn(r"(\$template = Join-Path \$(?:repoRoot|paths.REPO_ROOT) '\.(?:specify|ease)/templates/([\w-]+\.md)')",
            lambda m: m[1] + '\n' + f"if (-not (Test-Path $template)) {{ $template = Join-Path $PSScriptRoot '../../templates/{m[2]}' }}", text)
        expected = 2 if 'create-new-feature' in relative else 1
        if count != expected:
            raise ValueError(f'Upstream template lookup changed: {relative}')
    return text

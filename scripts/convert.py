#!/usr/bin/env python3
"""Build the Ease command suite for DSH; no source repository edits."""
from __future__ import annotations
import argparse
import json
import re
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMMANDS = ('starter', 'flow-1-analyze-brd', 'flow-1-analyze-trd',
            'flow-2-design', 'flow-3-implement', 'constitution',
            'bootstrap-system', 'analyze-code', 'arch-docs')
SKILLS = ('ease-analysis', 'ease-spec', 'ease-test-case-design',
          'ease-architecture', 'ease-architecture-design', 'ease-framework-code',
          'ease-system-bootstrap', 'ease-testing', 'ease-code-implement',
          'ease-coding', 'ease-code-review', 'ease-qa',
          'ease-arch-documentation', 'test-driven-development')


def split_frontmatter(text):
    match = re.match(r'\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)', text, re.S)
    if not match:
        return {}, text
    fields = dict(re.findall(r'^([\w-]+):[ \t]*(.*)$', match[1], re.M))
    return fields, text[match.end():].lstrip('\n')


def rewrite_paths(text):
    # Only explicit repository paths: local templates/ and references/ retain
    # their document-relative meaning. Never globally rewrite bare templates/.
    text = text.replace('plugins/ease/skills/', 'references/')
    text = text.replace('plugins/ease/templates/', 'templates/')
    text = text.replace('plugins/ease/commands/', 'commands/')
    text = text.replace('${DSH_SKILLS_ROOT}/', 'references/')
    return text


def build(src, out):
    plugin = src / 'plugins/ease'
    required = [plugin / 'commands' / f'{cmd}.md' for cmd in COMMANDS]
    required += [plugin / 'skills' / skill / 'SKILL.md' for skill in SKILLS]
    required += [plugin / 'templates', ROOT / 'entry/runtime.md']
    for path in required:
        if not path.exists():
            raise FileNotFoundError(f'Required source missing: {path}')
    # Build completely before replacing managed output, so missing inputs never
    # destroy the last usable conversion. Unrelated skill directories survive.
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.ease-build-', dir=out.parent) as tmp:
        stage = Path(tmp)
        resources = stage / 'ease-resources'
        resources.mkdir()
        shutil.copy(ROOT / 'entry/runtime.md', resources / 'runtime.md')
        for skill in SKILLS:
            shutil.copytree(plugin / 'skills' / skill, resources / 'references' / skill,
                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.DS_Store', 'node_modules'))
        shutil.copytree(plugin / 'templates', resources / 'templates')
        for path in resources.rglob('*.md'):
            text = path.read_text()
            if path.name == 'SKILL.md':
                # References aren't independent runtime skills. Remove the whole
                # YAML block, including nested handoffs/tools, not just key lines.
                _, text = split_frontmatter(text)
            path.write_text(rewrite_paths(text))
        (resources / 'commands').mkdir()
        for cmd in COMMANDS:
            fm, body = split_frontmatter((plugin / 'commands' / f'{cmd}.md').read_text())
            header = f'<!-- Converted from ease command: {cmd}. Read ../runtime.md first. -->\n'
            if 'argument-hint' in fm:
                header += f'\n参数提示：`{fm["argument-hint"]}`\n'
            dependencies = [s.strip() for s in fm.get('skills', '').split(',') if s.strip()]
            missing = set(dependencies) - set(SKILLS)
            if missing:
                raise ValueError(f'{cmd}: missing declared skills: {sorted(missing)}')
            if dependencies:
                header += '\n领域参考（按需读取）：' + '、'.join(f'`references/{s}/SKILL.md`' for s in dependencies) + '\n'
            if 'handoffs' in fm:
                header += '\nDSH 交接：阶段结束依据 ease-spec 的 checklist 契约完成清单；不调用源 frontmatter 的 agent。\n'
            (resources / 'commands' / f'{cmd}.md').write_text(header + '\n' + rewrite_paths(body))
            target = stage / f'ease-{cmd}'
            target.mkdir()
            description = fm.get('description', f'Ease {cmd}').strip('"\'')
            entry = f'''---
name: ease-{cmd}
description: {json.dumps(f'/ease:{cmd} — {description}', ensure_ascii=False)}
user-invocable: true
---

# /ease:{cmd}

先读取本技能目录的 `../ease-resources/runtime.md`，再读取
`../ease-resources/commands/{cmd}.md`，执行其中完整流程。
资源根为本技能目录的 `../ease-resources/`；所有 commands/、references/、templates/
绝对定位到该资源根。用户项目路径始终相对当前项目工作目录。
从用户消息中取得 `/ease:{cmd}`（或 `/ease-{cmd}`）之后的参数。
'''
            (target / 'SKILL.md').write_text(entry)
        report = []
        for path in sorted(resources.rglob('*.md')):
            for n, line in enumerate(path.read_text().splitlines(), 1):
                if re.search(r'plugins/|/ease-tools:|ease-poc|ease:async-task', line):
                    report.append({'file': str(path.relative_to(resources)), 'line': n, 'text': line.strip()})
        (resources / 'conversion-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        (stage / 'ease-manifest.json').write_text(json.dumps({
            'commands': {f'ease:{cmd}': f'ease-{cmd}' for cmd in COMMANDS},
            'resources': 'ease-resources', 'skills': list(SKILLS),
            'external_reference_occurrences': len(report),
        }, ensure_ascii=False, indent=2) + '\n')
        for path in sorted(stage.iterdir()):
            dest = out / path.name
            if dest.is_dir():
                shutil.rmtree(dest)
            elif dest.exists():
                dest.unlink()
            shutil.move(str(path), dest)
        legacy = out / 'ease-flow'
        if legacy.exists():
            shutil.rmtree(legacy)
    return len(report)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--src', type=Path, default=ROOT.parent / 'ease-cc-plugins')
    parser.add_argument('--out', type=Path, default=ROOT / 'skills')
    args = parser.parse_args()
    if args.out.resolve().is_relative_to(args.src.resolve()):
        parser.error('Output must not be inside the source repository')
    try:
        unresolved = build(args.src, args.out)
    except (OSError, ValueError) as exc:
        parser.exit(1, f'error: {exc}\n')
    print(f'Converted {len(COMMANDS)} commands, {len(SKILLS)} domain references; {unresolved} external-reference occurrences recorded.')

if __name__ == '__main__':
    main()

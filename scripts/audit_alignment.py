#!/usr/bin/env python3
"""Compare every converted command/resource with its current upstream source."""
import argparse
import hashlib
import json
from pathlib import Path
from convert import ROOT, COMMANDS, source_skills, split_frontmatter, rewrite_paths
from script_adapters import adapt_script


def audit(src, out):
    resources = out / 'ease-resources'
    errors = []
    counts = {'commands': 0, 'reference_files': 0, 'template_files': 0}
    def check(target, expected):
        if not target.is_file():
            errors.append(f'Missing: {target.relative_to(out)}')
        elif target.read_bytes() != expected:
            errors.append(f'Drift: {target.relative_to(out)}')
    for cmd in COMMANDS:
        path = src / 'plugins/ease/commands' / f'{cmd}.md'
        fm, body = split_frontmatter(path.read_text())
        converted = resources / 'commands' / path.name
        if not converted.is_file() or not converted.read_text().endswith('\n' + rewrite_paths(body)):
            errors.append(f'Command body lost or changed: {cmd}')
        for name in fm.get('skills', '').split(','):
            if name.strip() and not (resources / 'references' / name.strip() / 'SKILL.md').is_file():
                errors.append(f'Missing declared dependency: {cmd} -> {name}')
        counts['commands'] += 1
    for name, source in source_skills(src).items():
        for path in sorted(source.rglob('*')):
            if not path.is_file() or any(x in path.parts for x in ('node_modules', '__pycache__')) or path.name == '.DS_Store' or path.suffix == '.pyc':
                continue
            expected = path.read_bytes()
            rel = Path(name) / path.relative_to(source)
            if path.suffix == '.md':
                text = path.read_text()
                if path.name == 'SKILL.md':
                    _, text = split_frontmatter(text)
                expected = rewrite_paths(text).encode()
            elif path.suffix in ('.sh', '.ps1'):
                expected = adapt_script(str(rel), path.read_text()).encode()
            check(resources / 'references' / rel, expected)
            counts['reference_files'] += 1
    templates = src / 'plugins/ease/templates'
    for path in sorted(templates.rglob('*')):
        if path.is_file():
            expected = rewrite_paths(path.read_text()).encode() if path.suffix == '.md' else path.read_bytes()
            check(resources / 'templates' / path.relative_to(templates), expected)
            counts['template_files'] += 1
    for relative, digest in json.loads((resources / 'source-manifest.json').read_text()).items():
        source = src / relative
        if not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest() != digest:
            errors.append(f'Upstream changed since conversion: {relative}')
    return {'counts': counts, 'errors': errors, 'passed': not errors}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--src', type=Path, default=ROOT.parent / 'ease-cc-plugins')
    parser.add_argument('--out', type=Path, default=ROOT / 'skills')
    args = parser.parse_args()
    result = audit(args.src, args.out)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result['passed'] else 1)

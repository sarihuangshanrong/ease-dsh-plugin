#!/usr/bin/env python3
"""Validate durable TC definitions, pinned selections, and execution evidence; inventory legacy TCs."""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'scripts'))
from evidence_contract import check_graph, file_hash, git, read_json, safe_file, verify_snapshot

BLOCK = re.compile(r'```json tc\s*\n(.*?)\n```', re.S)
ID = re.compile(r'^TC-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)+$')


def case_files(root):
    return sorted(set(root.glob('docs/domains/*/testcases/**/*.md')) | set(root.glob('docs/qa/testcases/**/*.md')))


def load_cases(root):
    cases = {}
    for path in case_files(root):
        blocks = BLOCK.findall(path.read_text(encoding='utf-8'))
        if not blocks:
            if path.name == 'README.md':
                continue
            raise ValueError(f'{path}: missing json tc block')
        if len(blocks) != 1:
            raise ValueError(f'{path}: one TC per file required')
        tc = json.loads(blocks[0])
        if not isinstance(tc, dict) or not ID.fullmatch(str(tc.get('id', ''))):
            raise ValueError(f'{path}: invalid TC id')
        if tc['id'] in cases:
            raise ValueError(f'duplicate TC id: {tc["id"]}')
        for key in ('title', 'owner', 'given', 'when', 'then', 'level', 'environment', 'origin_change'):
            if not tc.get(key):
                raise ValueError(f'{tc["id"]}: missing {key}')
        if type(tc.get('revision')) is not int or tc['revision'] < 1:
            raise ValueError(f'{tc["id"]}: invalid revision')
        if tc.get('status') not in ('draft', 'active', 'deprecated'):
            raise ValueError(f'{tc["id"]}: invalid lifecycle status')
        if tc['level'] not in ('unit', 'integration', 'contract', 'system', 'static', 'manual', 'performance'):
            raise ValueError(f'{tc["id"]}: invalid test level')
        if not tc.get('basis') or not isinstance(tc['basis'], list):
            raise ValueError(f'{tc["id"]}: expected behavior needs approved basis')
        for ref in tc['basis']:
            if not isinstance(ref, dict) or not ref.get('id') or not ref.get('path'):
                raise ValueError(f'{tc["id"]}: invalid basis reference')
            source = safe_file(root, ref['path'])
            if ref['id'] not in source.read_text(encoding='utf-8'):
                raise ValueError(f'{tc["id"]}: unresolved basis id {ref["id"]}')
        tc['_path'] = path.relative_to(root).as_posix()
        tc['_hash'] = file_hash(path)
        cases[tc['id']] = tc
    check_graph(cases, 'supersedes')
    # Published identities survive moves and retirement; edits must advance revision.
    old_names = git(root, 'ls-tree', '-r', '--name-only', 'HEAD', '--', 'docs/domains', 'docs/qa/testcases').decode().splitlines()
    for name in old_names:
        if '/testcases/' not in name or not name.endswith('.md'):
            continue
        old_text = git(root, 'show', f'HEAD:{name}').decode()
        blocks = BLOCK.findall(old_text)
        if len(blocks) != 1:
            continue
        previous = json.loads(blocks[0])
        key = previous['id']
        if key not in cases:
            raise ValueError(f'{key}: published TC deleted; retain as deprecated')
        current = cases[key]
        if file_hash(safe_file(root, current['_path'])) != __import__('hashlib').sha256(old_text.encode()).hexdigest() and current['revision'] <= previous['revision']:
            raise ValueError(f'{key}: edited TC must advance revision')
    for key, item in cases.items():
        if item['status'] == 'active':
            for old in item.get('supersedes', []):
                if cases[old]['status'] != 'deprecated':
                    raise ValueError(f'{old}: active replacement requires deprecated predecessor')
    return cases


def validate_selection(root, cases, selection, admission=False):
    if selection.get('schema_version') != '1.0' or not selection.get('change_id'):
        raise ValueError('invalid selection schema/change_id')
    verify_snapshot(root, selection.get('snapshot'))
    selected = selection.get('cases')
    if not isinstance(selected, list) or not selected:
        raise ValueError('selection requires cases; use explicit workflow N/A for no persistent verification target')
    seen = set()
    for item in selected:
        tc_id = item['id']
        if tc_id in seen or tc_id not in cases:
            raise ValueError(f'duplicate or unknown selected TC: {tc_id}')
        seen.add(tc_id)
        tc = cases[tc_id]
        if tc['status'] == 'deprecated' or (admission and tc['status'] != 'active'):
            raise ValueError(f'{tc_id}: lifecycle not eligible')
        if any(item.get(k) != tc[v] for k, v in [('revision', 'revision'), ('path', '_path'), ('hash', '_hash')]):
            raise ValueError(f'{tc_id}: stale selection pin')
        if not item.get('reason') or type(item.get('required')) is not bool:
            raise ValueError(f'{tc_id}: selection needs reason and required boolean')
    obligations = selection.get('obligations')
    if not isinstance(obligations, list) or not obligations:
        raise ValueError('selection requires scoped requirements/architecture obligations')
    obligation_ids = set()
    for obligation in obligations:
        key = obligation.get('id')
        if not key or key in obligation_ids:
            raise ValueError('duplicate or missing obligation id')
        obligation_ids.add(key)
        ref = safe_file(root, obligation['source'])
        if file_hash(ref) != obligation.get('source_hash'):
            raise ValueError(f'{key}: stale obligation source')
        if key not in ref.read_text(encoding='utf-8'):
            raise ValueError(f'{key}: obligation not found in source')
        refs = obligation.get('tc_ids', [])
        if not refs or set(refs) - seen:
            raise ValueError(f'{key}: uncovered obligation')
        for tc_id in refs:
            if key not in {r['id'] for r in cases[tc_id]['basis']} | set(cases[tc_id].get('architecture_refs', [])):
                raise ValueError(f'{key}: TC does not trace obligation: {tc_id}')
    return seen


def validate_execution(root, cases, selection, report, snapshot_value):
    verify_snapshot(root, snapshot_value)
    if report.get('change_id') != selection['change_id'] or report.get('snapshot_id') != snapshot_value['id']:
        raise ValueError('execution belongs to another change/snapshot')
    rows = report.get('results', [])
    indexed = {}
    for row in rows:
        key = row.get('id')
        if key in indexed or key not in {x['id'] for x in selection['cases']}:
            raise ValueError(f'duplicate/unselected execution TC: {key}')
        indexed[key] = row
    for item in selection['cases']:
        tc = cases[item['id']]
        row = indexed.get(item['id'])
        if row is None:
            if item['required']:
                raise ValueError(f'{item["id"]}: required result missing')
            continue
        if row.get('revision') != tc['revision'] or row.get('case_hash') != tc['_hash']:
            raise ValueError(f'{item["id"]}: stale execution case')
        if row.get('result') not in ('pass', 'fail', 'blocked', 'skipped'):
            raise ValueError('invalid execution result')
        if item['required'] and row.get('result') != 'pass':
            raise ValueError(f'{item["id"]}: required test not passed')
        if row.get('result') == 'pass':
            if not row.get('method') or not row.get('environment') or not row.get('evidence'):
                raise ValueError('pass needs method, environment and evidence')
            for evidence in row['evidence']:
                if file_hash(safe_file(root, evidence['path'])) != evidence.get('hash'):
                    raise ValueError('execution evidence changed')
            if tc['level'] == 'manual' and (not row.get('executor') or not row.get('steps')):
                raise ValueError('manual pass needs executor and actual steps')
            if tc['level'] != 'manual':
                safe_file(root, row['method'].split('#', 1)[0])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path, default=Path.cwd())
    parser.add_argument('--selection', type=Path)
    parser.add_argument('--execution', type=Path)
    parser.add_argument('--execution-snapshot', type=Path)
    parser.add_argument('--admission', action='store_true')
    parser.add_argument('--inventory-legacy', action='store_true')
    args = parser.parse_args()
    root = args.repo_root.resolve()
    try:
        if args.inventory_legacy:
            result = []
            for path in sorted(root.glob('.eases/**/test-case-document.md')):
                ids = sorted(set(re.findall(r'\bTC-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)+', path.read_text(encoding='utf-8'))))
                result.append({'source': path.relative_to(root).as_posix(), 'hash': file_hash(path), 'ids': ids, 'status': 'needs-semantic-mapping'})
            print(json.dumps({'legacy_inventory': result}, ensure_ascii=False, indent=2))
            return 0
        cases = load_cases(root)
        if args.execution and not (args.selection and args.execution_snapshot):
            raise ValueError('execution requires selection and execution-snapshot')
        if args.selection:
            selection = read_json(args.selection)
            # At delivery the design snapshot is historical; check its identity, not current code.
            if args.execution:
                from evidence_contract import digest
                snap = selection.get('snapshot', {})
                if snap.get('id') != digest({k:v for k,v in snap.items() if k != 'id'}):
                    raise ValueError('invalid historical selection snapshot')
                current_selection = dict(selection, snapshot=read_json(args.execution_snapshot))
                validate_selection(root, cases, current_selection, True)
                validate_execution(root, cases, selection, read_json(args.execution), read_json(args.execution_snapshot))
            else:
                validate_selection(root, cases, selection, args.admission)
        print(json.dumps({'result': 'pass', 'cases': len(cases)}))
        return 0
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(json.dumps({'result': 'fail', 'error': str(exc)}, ensure_ascii=False))
        return 1

if __name__ == '__main__':
    raise SystemExit(main())

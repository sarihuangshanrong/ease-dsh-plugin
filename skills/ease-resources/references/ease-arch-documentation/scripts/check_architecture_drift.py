#!/usr/bin/env python3
"""Read-only snapshot, documentation impact and ADR realization checks."""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'scripts'))
from evidence_contract import changed_files, check_graph, digest, file_hash, git, read_json, safe_file, snapshot

ADR_BLOCK = re.compile(r'```json adr\s*\n(.*?)\n```', re.S)
STATES = {'Proposed', 'Accepted', 'Rejected', 'Deprecated', 'Superseded'}
REALIZATION = {'realized', 'partial', 'conflict', 'not_observed', 'unknown'}


def decisions(root, base=None):
    records, gaps = {}, []
    if base:
        git(root, 'rev-parse', '--verify', base + '^{commit}')
        previous = git(root, 'ls-tree', '-r', '--name-only', base, '--', 'docs/adr').decode().splitlines()
        for name in previous:
            if not re.fullmatch(r'docs/adr/\d{3}-.+\.md', name):
                continue
            if not (root / name).is_file():
                raise ValueError(f'decision record deleted: {name}; retain history and deprecate/supersede')
    for path in sorted(root.glob('docs/adr/[0-9][0-9][0-9]-*.md')):
        blocks = ADR_BLOCK.findall(path.read_text(encoding='utf-8'))
        if not blocks:
            gaps.append({'type': 'legacy_decision', 'path': path.relative_to(root).as_posix()})
            continue
        if len(blocks) != 1:
            raise ValueError(f'{path}: exactly one json adr block required')
        record = json.loads(blocks[0])
        key = record['id']
        if not re.fullmatch(r'ADR-\d{3}', key) or key in records:
            raise ValueError(f'duplicate/invalid ADR: {key}')
        if record.get('status') not in STATES or not record.get('scope'):
            raise ValueError(f'{key}: invalid status/scope')
        for field in ('decision', 'rationale', 'constraints'):
            if not record.get(field):
                raise ValueError(f'{key}: missing {field}')
        if record['status'] in ('Accepted', 'Superseded', 'Deprecated'):
            approval = record.get('approval', {})
            if not approval.get('by') or not approval.get('at'):
                raise ValueError(f'{key}: approval identity/time missing')
            safe_file(root, approval['source'])
        ids = set()
        for constraint in record['constraints']:
            cid = constraint['id']
            if cid in ids or not constraint.get('text') or not constraint.get('scope') or type(constraint.get('effective')) is not bool:
                raise ValueError(f'{key}: invalid constraint')
            ids.add(cid)
        if base:
            relative = path.relative_to(root).as_posix()
            try:
                old_text = git(root, 'show', f'{base}:{relative}').decode()
            except Exception as exc:
                import subprocess
                if not isinstance(exc, subprocess.CalledProcessError):
                    raise
                old_text = ''
            old_blocks = ADR_BLOCK.findall(old_text)
            if old_blocks:
                old = json.loads(old_blocks[0])
                if old.get('status') in ('Accepted', 'Superseded', 'Deprecated'):
                    for field in ('id', 'decision', 'rationale', 'constraints', 'scope'):
                        if old.get(field) != record.get(field):
                            raise ValueError(f'{key}: accepted decision body changed; create superseding ADR')
                    if record['status'] not in ('Accepted', 'Superseded', 'Deprecated'):
                        raise ValueError(f'{key}: invalid lifecycle regression')
        record['_path'] = path.relative_to(root).as_posix()
        record['_hash'] = file_hash(path)
        records[key] = record
    check_graph(records, 'supersedes')
    for key, record in records.items():
        for old in record.get('supersedes', []):
            if record['status'] == 'Accepted' and records[old]['status'] != 'Superseded':
                raise ValueError(f'{old}: accepted successor requires Superseded status')
        if record['status'] == 'Superseded' and not any(key in r.get('supersedes', []) for r in records.values()):
            raise ValueError(f'{key}: missing successor')
    return records, gaps


def assess_decisions(root, records, assessment, snap):
    if assessment and assessment.get('snapshot_id') != snap['id']:
        raise ValueError('ADR assessment is stale')
    rows = {}
    for row in assessment.get('decisions', []):
        key = (row['adr_id'], row['constraint_id'])
        if key in rows:
            raise ValueError('duplicate ADR assessment')
        rows[key] = row
    findings = []
    consumed = set()
    for adr_id, record in records.items():
        if record['status'] != 'Accepted':
            continue
        for constraint in record['constraints']:
            key = (adr_id, constraint['id'])
            row = rows.get(key, {})
            if row:
                consumed.add(key)
                if row.get('adr_hash') != record['_hash'] or row.get('status') not in REALIZATION:
                    raise ValueError(f'{key}: invalid/stale realization')
                if not row.get('reason') or not row.get('evidence'):
                    raise ValueError(f'{key}: realization needs reason/evidence')
                for evidence in row['evidence']:
                    if file_hash(safe_file(root, evidence['path'])) != evidence.get('hash'):
                        raise ValueError(f'{key}: stale realization evidence')
            status = row.get('status', 'unknown')
            findings.append({'id': f'{adr_id}:{constraint["id"]}', 'type': 'decision_conformance',
                             'status': status, 'effective': constraint['effective'], 'scope': constraint['scope'],
                             'blocking': constraint['effective'] and status != 'realized',
                             'reason': row.get('reason', 'No current realization assessment'), 'evidence': row.get('evidence', [])})
    if set(rows) - consumed:
        raise ValueError('assessment references unknown or inactive ADR constraints')
    return findings


def documentation_impact(root, changed, mode="worktree", head="HEAD"):
    assessments = []
    for path in sorted(root.glob('docs/system/**/metadata.json')):
        metadata = read_json(path)
        per_doc = metadata.get('last_generation', {}).get('per_doc', {})
        dependencies = metadata.get('document_dependencies', {})
        for doc, baseline in per_doc.items():
            commit = baseline.get('commit_id', metadata.get('last_generation', {}).get('commit_id'))
            try:
                doc_changes = changed_files(root, commit, mode, head) if commit else changed
            except Exception:
                assessments.append({'document': str(path.parent.relative_to(root) / doc), 'status': 'unknown', 'reason': 'Unresolvable document baseline'})
                continue
            sources = dependencies.get(doc, {}).get('sources', [])
            if isinstance(baseline.get('source_hashes'), dict):
                current_files = snapshot(root, mode, head)['files']
                current_sources = {name: value for name, value in current_files.items() if any(name == source or name.startswith(source.rstrip('/') + '/') for source in sources)}
                previous_sources = baseline['source_hashes']
                doc_changes = sorted(name for name in set(current_sources) | set(previous_sources) if current_sources.get(name) != previous_sources.get(name))
            touched = [name for name in doc_changes if any(name == source or name.startswith(source.rstrip('/') + '/') for source in sources)]
            assessments.append({'document': str(path.parent.relative_to(root) / doc),
                                'status': 'stale' if touched else ('unknown' if doc_changes and not sources else 'unchanged'),
                                'changed_sources': touched,
                                'reason': 'Source dependency changed' if touched else ('Missing dependency coverage' if doc_changes and not sources else 'No dependency changes')})
    return assessments


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path, default=Path.cwd())
    parser.add_argument('--base')
    parser.add_argument('--head', default='HEAD')
    parser.add_argument('--mode', choices=('worktree', 'commit'), default='worktree')
    parser.add_argument('--scope', nargs='+', default=['.'])
    parser.add_argument('--assessment', type=Path)
    parser.add_argument('--policy', choices=('warn', 'block'), default='warn')
    parser.add_argument('--snapshot-only', action='store_true')
    args = parser.parse_args()
    root = args.repo_root.resolve()
    try:
        snap = snapshot(root, args.mode, args.head, args.scope)
        if args.snapshot_only:
            print(json.dumps(snap, ensure_ascii=False, indent=2))
            return 0
        if args.mode == 'commit':
            # ADR/index content must match the inspected revision, not arbitrary checkout bytes.
            current = snapshot(root, 'worktree', args.head, args.scope)
            if current['files'] != snap['files']:
                raise ValueError('commit check requires checkout matching inspected commit; use worktree mode or isolated checkout')
        records, gaps = decisions(root, args.base or "HEAD")
        for record in records.values():
            if snap["files"].get(record["_path"]) != record["_hash"]:
                raise ValueError("ADR outside captured snapshot scope")
        decision_findings = assess_decisions(root, records, read_json(args.assessment) if args.assessment else {}, snap)
        changed = changed_files(root, args.base, args.mode, args.head) if args.base else []
        if args.base:
            git(root, 'rev-parse', '--verify', args.base + '^{commit}')
        blocked = bool(gaps) or any(f['blocking'] for f in decision_findings)
        print(json.dumps({'result': 'needs-review' if blocked else 'pass', 'snapshot': snap,
                          'changed_files': changed, 'documentation': documentation_impact(root, changed, args.mode, args.head),
                          'decision_findings': decision_findings, 'coverage_gaps': gaps}, ensure_ascii=False, indent=2))
        return 1 if args.policy == 'block' and blocked else 0
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(json.dumps({'result': 'fail', 'error': str(exc)}, ensure_ascii=False))
        return 1

if __name__ == '__main__':
    raise SystemExit(main())

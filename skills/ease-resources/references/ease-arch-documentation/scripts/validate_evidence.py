"""Strict architecture evidence contract (content schema 2.2)."""
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'scripts'))
from evidence_contract import check_graph, digest, file_hash, read_json, safe_file, verify_snapshot


def objects(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from objects(child)


def validate(root, docs_dir, metadata, targets, mode, review_path=None):
    snapshot = verify_snapshot(root, metadata.get('snapshot'))
    dependencies = metadata.get('document_dependencies', {})
    indexes = metadata.get('indexes')
    if not isinstance(indexes, dict) or not indexes:
        raise ValueError('nonempty indexes required')
    required = set()
    for doc in targets:
        entry = dependencies.get(doc)
        if not isinstance(entry, dict) or not entry.get('partitions') or not entry.get('claims') or not entry.get('sources'):
            raise ValueError(f'{doc}: partitions, claims and transitive sources required')
        required.update(entry['partitions'])
    if mode == 'full':
        required.update(indexes)
    # Explicit dependencies allow partial validation to avoid unrelated damaged indexes.
    queue = list(required)
    while queue:
        key = queue.pop()
        if key not in indexes or not isinstance(indexes[key], dict):
            raise ValueError(f'missing index: {key}')
        for dependency in indexes[key].get('depends_on', []):
            if dependency not in required:
                required.add(dependency)
                queue.append(dependency)
    if mode == 'full' and 'architecture_analysis_index' not in required:
        raise ValueError('full generation requires architecture analysis index and object coverage')
    nodes = {}
    input_hashes = {}
    for key in sorted(required):
        value = indexes[key]
        if 'file' in value:
            path = safe_file(root, value['file']) if str(value['file']).startswith('docs/') else safe_file(docs_dir, value['file'])
            if file_hash(path) != str(value.get('hash', '')).removeprefix('sha256:'):
                raise ValueError(f'{key}: index hash missing/mismatched')
            value = read_json(path)
        input_hashes[key] = digest(value)
        for node in objects(value):
            if 'id' not in node:
                continue
            identity = node['id']
            if not isinstance(identity, str) or identity in nodes:
                raise ValueError(f'duplicate/invalid claim id: {identity}')
            nodes[identity] = node
    if 'architecture_analysis_index' in required:
        value = indexes['architecture_analysis_index']
        if 'file' in value:
            value = read_json(safe_file(root, value['file']) if value['file'].startswith('docs/') else safe_file(docs_dir, value['file']))
        for collection in ('critical_paths', 'invariants', 'quality_scenarios', 'failure_propagations', 'evolution_hotspots', 'decision_realization'):
            if not isinstance(value.get(collection), list):
                raise ValueError(f'architecture analysis missing {collection}')
    if not nodes:
        raise ValueError('no indexed claims')
    check_graph(nodes)
    for key, node in nodes.items():
        if node.get('state') not in ('observed', 'approved_intent', 'inferred', 'unknown') or node.get('confidence') not in ('high', 'medium', 'low'):
            raise ValueError(f'{key}: missing state/confidence')
        if not node.get('derived_from') and not node.get('evidence'):
            raise ValueError(f'{key}: no source evidence')
        for evidence in node.get('evidence', []):
            location = evidence.get('location', '')
            match = re.fullmatch(r'(.+):(\d+)', location)
            if not match:
                raise ValueError(f'{key}: invalid evidence location')
            path = safe_file(root, match[1])
            lines = path.read_text(encoding='utf-8').splitlines()
            if not 1 <= int(match[2]) <= len(lines):
                raise ValueError(f'{key}: evidence line outside file')
            if snapshot['files'].get(match[1]) != file_hash(path):
                raise ValueError(f'{key}: evidence outside snapshot or changed')
        if node.get('realization_status') is not None:
            if node['realization_status'] not in ('realized', 'partial', 'conflict', 'not_observed', 'unknown') or not node.get('adr_id') or not node.get('constraint_id'):
                raise ValueError(f'{key}: invalid decision realization')
    # Realization entries must resolve to an actual ADR constraint, including approval state.
    if any('adr_id' in node for node in nodes.values()):
        from check_architecture_drift import decisions
        records, _ = decisions(root)
        for node in nodes.values():
            if 'adr_id' not in node:
                continue
            record = records.get(node['adr_id'])
            if not record or record['status'] != 'Accepted' or node.get('constraint_id') not in {c['id'] for c in record['constraints']}:
                raise ValueError('realization references missing/inactive ADR constraint')
    doc_hashes = {}
    for doc in targets:
        path = docs_dir / doc
        content = path.read_text(encoding='utf-8')
        doc_hashes[doc] = file_hash(path)
        for key in dependencies[doc]['claims']:
            if key not in nodes or key not in content:
                raise ValueError(f'{doc}: missing/unrendered claim {key}')
        for location, line in re.findall(r'来源:\s+(\S+):(\d+)', content):
            source = safe_file(root, location)
            if not 1 <= int(line) <= len(source.read_text(encoding='utf-8').splitlines()):
                raise ValueError(f'{doc}: invalid source line')
            if snapshot['files'].get(location) != file_hash(source):
                raise ValueError(f'{doc}: source outside snapshot')
    binding = {'snapshot_id': snapshot['id'], 'documents': doc_hashes, 'indexes': input_hashes}
    if review_path is None:
        return {'result': 'pending', 'binding': binding, 'reason': 'Independent semantic review required'}
    review = read_json(review_path)
    if review.get('binding') != binding or review.get('result') != 'pass' or not review.get('reviewer'):
        raise ValueError('semantic review missing, failed, or stale')
    checked = {row.get('id') for row in review.get('checks', []) if row.get('result') == 'pass' and row.get('evidence') and row.get('counterexample_search')}
    required_checks = {'claim-support', 'coverage-denominator', 'causal-consistency', 'decision-realization', 'mermaid-render'}
    if not required_checks <= checked:
        raise ValueError('semantic review lacks required evidence/counterexample checks')
    coverage = review.get('coverage', [])
    if not coverage:
        raise ValueError('semantic review needs object-based coverage matrix')
    for row in coverage:
        if row.get('object_id') not in nodes or not row.get('view_ids') or set(row['view_ids']) - nodes.keys():
            raise ValueError('invalid architecture coverage row')
    return {'result': 'pass', 'binding': binding}

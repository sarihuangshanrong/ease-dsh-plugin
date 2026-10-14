import hashlib
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('convert', ROOT / 'scripts/convert.py')
converter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(converter)

class ConversionTests(unittest.TestCase):
    def test_nested_frontmatter_removed(self):
        _, body = converter.split_frontmatter('---\nname: sample\nhandoffs:\n  - agent: a\n    prompt: b\n---\nBody\n')
        self.assertEqual(body, 'Body\n')

    def test_local_templates_not_redirected(self):
        text = '`templates/README.md` and `plugins/ease/templates/design/a.md`'
        self.assertEqual(converter.rewrite_paths(text), '`templates/README.md` and `templates/design/a.md`')

    def test_missing_source_preserves_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = root / 'out'
            out.mkdir()
            (out / 'sentinel').write_text('old build')
            with self.assertRaises(FileNotFoundError):
                converter.build(root / 'missing', out)
            self.assertEqual((out / 'sentinel').read_text(), 'old build')

    def test_generated_entrypoints_and_dependencies(self):
        root = ROOT / 'skills'
        manifest = json.loads((root / 'ease-manifest.json').read_text())
        self.assertEqual(len(manifest['commands']), 9)
        for alias, name in manifest['commands'].items():
            entry = (root / name / 'SKILL.md').read_text()
            self.assertIn(f'name: {name}', entry)
            self.assertIn(f'/'+alias, entry)
            self.assertTrue((root / 'ease-resources/commands' / (alias.split(':')[1] + '.md')).is_file())
        for skill in manifest['skills']:
            self.assertTrue((root / 'ease-resources/references' / skill / 'SKILL.md').is_file())
        self.assertFalse((root / 'ease-flow').exists())
        self.assertFalse(any(p.is_symlink() for p in root.rglob('*')))

    def test_install_preserves_unrelated_and_replaces_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / 'skills'
            dest.mkdir()
            (dest / 'unrelated').write_text('keep')
            for _ in range(2):
                subprocess.run(['python3', str(ROOT / 'scripts/install.py'), str(dest)], check=True, capture_output=True)
                stale = dest / 'ease-starter/stale.md'
                self.assertFalse(stale.exists())
                stale.write_text('obsolete')
            self.assertEqual((dest / 'unrelated').read_text(), 'keep')

    def test_repeat_build_identical(self):
        def hashes(root):
            return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in root.rglob('*') if p.is_file()}
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'skills'
            src = ROOT.parent / 'ease-cc-plugins'
            converter.build(src, out)
            first = hashes(out)
            converter.build(src, out)
            self.assertEqual(first, hashes(out))
            self.assertEqual(first, hashes(ROOT / 'skills'))

class AlignmentTests(unittest.TestCase):
    def test_upstream_alignment_and_missing_gate_detected(self):
        from audit_alignment import audit
        import shutil
        source = ROOT.parent / 'ease-cc-plugins'
        self.assertTrue(audit(source, ROOT / 'skills')['passed'])
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'skills'
            shutil.copytree(ROOT / 'skills', out)
            (out / 'ease-resources/references/ease-spec/gates/flow-3-delivery.md').unlink()
            result = audit(source, out)
            self.assertFalse(result['passed'])
            self.assertTrue(any('flow-3-delivery.md' in error for error in result['errors']))

    def test_detached_non_git_project_uses_shipped_templates(self):
        import os
        scripts = ROOT / 'skills/ease-resources/references/ease-spec/scripts/bash'
        with tempfile.TemporaryDirectory(prefix='ease-business-') as tmp:
            project = Path(tmp)
            env = dict(os.environ)
            for name in ('GIT_DIR', 'GIT_WORK_TREE', 'SPECIFY_FEATURE', 'EASE_FEATURE_DIR'):
                env.pop(name, None)
            subprocess.run(['bash', str(scripts / 'create-new-feature.sh'), '--json', '--feature-dir', '001-example/flow-1-analyze', 'example'],
                           cwd=project, env=env, check=True, capture_output=True)
            feature = project / '.eases/001-example/flow-1-analyze'
            expected = scripts.parent.parent / 'templates/spec-template.md'
            self.assertEqual((feature / 'spec.md').read_bytes(), expected.read_bytes())
            env['EASE_FEATURE_DIR'] = '001-example/flow-1-analyze'
            subprocess.run(['bash', str(scripts / 'setup-plan.sh'), '--json'], cwd=project, env=env, check=True, capture_output=True)
            self.assertEqual((feature / 'plan.md').read_bytes(), (scripts.parent.parent / 'templates/plan-template.md').read_bytes())
            # Project-specific overrides must still take precedence.
            custom = project / '.specify/templates'
            custom.mkdir(parents=True)
            (custom / 'plan-template.md').write_text('project plan')
            subprocess.run(['bash', str(scripts / 'setup-plan.sh'), '--json'], cwd=project, env=env, check=True, capture_output=True)
            self.assertEqual((feature / 'plan.md').read_text(), 'project plan')

if __name__ == '__main__':
    unittest.main()

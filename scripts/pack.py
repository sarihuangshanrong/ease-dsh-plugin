#!/usr/bin/env python3
"""Portable repository bundle, NOT a single-skill hosted API archive."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
root = Path(__file__).resolve().parent.parent
out = root / 'dist/ease-dsh-plugin.zip'
out.parent.mkdir(exist_ok=True)
with ZipFile(out, 'w', ZIP_DEFLATED) as archive:
    for name in ('skills', 'runtime', 'scripts', 'entry', 'tests', 'README.md', 'CONVERSION.md', 'PROJECT.md'):
        source = root / name
        paths = source.rglob('*') if source.is_dir() else [source]
        for path in sorted(paths):
            if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc':
                archive.write(path, Path('ease-dsh-plugin') / path.relative_to(root))
print(out)

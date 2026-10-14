#!/usr/bin/env python3
import json
import shutil
import sys
import tempfile
from pathlib import Path
src = Path(__file__).resolve().parent.parent / 'skills'
dest = Path(sys.argv[1]).resolve()
manifest = json.loads((src / 'ease-manifest.json').read_text())
names = [*manifest['commands'].values(), manifest['resources'], 'ease-manifest.json']
if dest == src.resolve() or src.resolve().is_relative_to(dest) or dest.is_relative_to(src.resolve()):
    raise SystemExit('Installation source and destination must be separate trees')
for name in names:
    if not (src / name).exists():
        raise SystemExit(f'Missing generated resource: {name}')
dest.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix='.ease-install-', dir=dest.parent) as tmp:
    stage = Path(tmp)
    for name in names:
        source = src / name
        if source.is_dir():
            shutil.copytree(source, stage / name)
        else:
            shutil.copy2(source, stage / name)
    for name in names:
        target = dest / name
        if target.is_symlink() or target.is_file():
            target.unlink()
        elif target.exists():
            shutil.rmtree(target)
        shutil.move(str(stage / name), target)
print(f'Installed {len(manifest["commands"])} skills and shared resources into {dest}')

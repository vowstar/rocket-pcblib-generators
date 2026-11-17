#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Normalize recorded STEP coordinates for KiCad without changing input files."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--library', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=Path('build/aligned'))
    parser.add_argument('--freecad', default='FreeCAD')
    parser.add_argument('--model', action='append', help='Input basename; default: all')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    manifest = root / 'transforms/kicad-alignment.json'
    spec = json.loads(manifest.read_text())
    models = [m for m in spec['models'] if not args.model or Path(m['input']).name in args.model]
    if not models or (args.model and set(args.model) - {Path(m['input']).name for m in models}):
        parser.error('Unknown model selection')
    for model in models:
        src = (args.library / model['input']).resolve()
        dst = (args.output / model['output']).resolve()
        if dst == src or (dst.exists() and dst.samefile(src)):
            parser.error('Output would overwrite an input model')
        if hashlib.sha256(src.read_bytes()).hexdigest() != model['sha256']:
            raise ValueError(f"Input hash mismatch: {model['input']}")
    tool_paths = (Path(__file__), root/'tools/align_models.FCMacro', root/'tools/geometry_checks.py', root/'tools/surface_cleanup.py', manifest)
    hashes = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in tool_paths}
    commit = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
    dirty = bool(subprocess.check_output(['git', '-C', str(root), 'status', '--porcelain'], text=True).strip())
    args.output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='model-align-') as tmp:
        work = Path(tmp)
        job = work / 'job.json'
        resolved = [dict(m, input=str((args.library / m['input']).resolve()),
                         output=str(work / m['output'])) for m in models]
        job.write_text(json.dumps([{'models': resolved}]))
        env = os.environ.copy()
        env['ROCKET_ALIGNMENT_JOB'] = str(job)
        command = [args.freecad, '--keep-deprecated-paths', '-u', str(work/'user.cfg'),
                   '-s', str(work/'system.cfg'), str(root/'tools/align_models.FCMacro')]
        if not env.get('DISPLAY'):
            command = ['xvfb-run', '-a', *command]
        proc = subprocess.run(command, env=env, capture_output=True, text=True, timeout=1800)
        (args.output/'freecad.log').write_text(proc.stdout+proc.stderr)
        receipt = job.with_suffix('.result.json')
        if not receipt.exists():
            raise RuntimeError(f'No alignment result (exit {proc.returncode})')
        result = json.loads(receipt.read_text())
        result['source_commit'] = commit
        result['source_dirty'] = dirty
        result['input_hashes'] = hashes
        if any(hashlib.sha256((root/p).read_bytes()).hexdigest() != digest for p,digest in hashes.items()):
            result.update(success=False, error='Source changed during alignment')
        (args.output/'result.json').write_text(json.dumps(result, indent=2)+'\n')
        if proc.returncode or not result['success']:
            raise RuntimeError(result.get('error', f'FreeCAD exit {proc.returncode}'))
        for model in models:
            dst = args.output / model['output']
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(work / model['output'], dst)
    print(f'Verified {len(models)} coordinate transforms: {args.output}')


if __name__ == '__main__':
    main()

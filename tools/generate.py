#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Generate and verify library models in an isolated FreeCAD process."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", action="append", help="Exact model name; default: all")
    parser.add_argument("--output", type=Path, default=Path("build"))
    parser.add_argument("--baseline", type=Path, help="Library checkout for geometric comparison")
    parser.add_argument("--freecad", default="FreeCAD")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    models = []
    for meta in sorted((root / "models").glob("*/*/model.toml")):
        model = tomllib.loads(meta.read_text())
        if args.model and model["name"] not in args.model:
            continue
        model["source"] = str(meta.parent / "generate.py")
        model["input_hashes"] = {
            str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(meta.parent.iterdir()) if p.is_file()
        }
        if args.baseline:
            baseline = (args.baseline / model["output"]).resolve()
            if hashlib.sha256(baseline.read_bytes()).hexdigest() != model["baseline_sha256"]:
                raise ValueError(f"Baseline hash mismatch: {model['name']}")
            model["baseline"] = str(baseline)
        models.append(model)
    if not models or (args.model and set(args.model) - {m["name"] for m in models}):
        parser.error("Unknown model selection")
    args.output.mkdir(parents=True, exist_ok=True)
    output = args.output.resolve()
    with tempfile.TemporaryDirectory(prefix="model-build-") as tmp:
        work = Path(tmp)
        spec = work / "job.json"
        spec.write_text(json.dumps({"root": str(root), "work": str(work), "models": models}))
        env = os.environ.copy()
        env["ROCKET_MODEL_JOB"] = str(spec)
        command = [args.freecad, "--keep-deprecated-paths", "-u", str(work / "user.cfg"),
                   "-s", str(work / "system.cfg"), str(root / "tools/runner.FCMacro")]
        if not env.get("DISPLAY"):
            command = ["xvfb-run", "-a", *command]
        proc = subprocess.run(command, env=env, capture_output=True, text=True, timeout=600)
        (output / "freecad.log").write_text(proc.stdout + proc.stderr)
        receipt = work / "result.json"
        if not receipt.exists():
            raise RuntimeError(f"FreeCAD produced no result (exit {proc.returncode}); see freecad.log")
        result = json.loads(receipt.read_text())
        if proc.returncode or not result["success"]:
            (output / "failed-result.json").write_text(json.dumps(result, indent=2) + "\n")
            raise RuntimeError(result.get("error", f"FreeCAD exit {proc.returncode}"))
        for model in models:
            for relative in (model["output"], "previews/" + model["name"] + ".png"):
                src, dst = work / relative, output / relative
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
        result["source_commit"] = subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
        result["source_dirty"] = bool(subprocess.check_output(
            ["git", "-C", str(root), "status", "--porcelain"], text=True).strip())
        result["tool_hashes"] = {
            str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((root / "tools").iterdir()) if p.is_file()
        }
        (output / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"Verified {len(models)} models: {output / 'result.json'}")


if __name__ == "__main__":
    main()

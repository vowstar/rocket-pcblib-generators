# rocket-pcblib-generators

Editable generator sources for [rocket-pcblib](https://github.com/chipsalliance/rocket-pcblib) models.
The library distributes STEP files. This repository contains their geometry construction code and dimensional references.

## Models

| Category | Model |
| --- | --- |
| Button_Switch_SMD | SAMZO C4B1802110 |
| Connector | Hirose FH12-32S-0.5SVA |
| Connector | Hirose FH34SRJ-24S-0.5SH |
| Connector | Hanrun HR911105A |
| Connector | Kangnex WJ15EDGRC-3.81-04P |
| LED | Worldsemi WS2812B-1313-V6 |
| Oscillator | YXC YSO230LR |
| Package_DFN_QFN | Espressif ESP32-S31 QFN-80 |
| Package_DFN_QFN | WCH CH347F |
| Package_DFN_QFN | TI RMQ0024A WQFN-24 |
| Package_SON | WSON-8, 6 x 5 mm |
| Package_SON | TI DQA0010A USON-10 |
| Package_SON | TECH PUBLIC DFN2510-10 |

Each model lives in `models/<library-category>/<model-name>/`.
`generate.py` constructs its geometry. `model.toml` records output paths, source provenance, and a baseline asset hash where available.
Dimensional references and visual simplifications are documented in the generator or its adjacent README.
Shared generation and verification code lives in `tools/`.

## Generate

Requires Python 3.11 or newer and FreeCAD 1.1 or newer with its GUI, Part, and Import modules.
FreeCAD must be available as `FreeCAD` on PATH, or selected with `--freecad`.
A desktop display or `xvfb-run` is required for GUI-based export and previews.
Validated with FreeCAD 1.1.3, Open CASCADE 7.8.1, and Python 3.14.10 on Linux.

```sh
python3 tools/generate.py --output build
```

Select one model by its exact directory name:

```sh
python3 tools/generate.py --model USON-10_2.5x1.0mm_P0.5mm --output build
```
Compare exports with a library checkout containing the recorded baseline files:

```sh
python3 tools/generate.py --baseline /path/to/rocket-pcblib --output build
```

For models with a recorded baseline, the command verifies SHA-256 hashes before geometric comparison.
New USON models are checked against explicit bounds and solid counts. Their manufacturer references document terminal geometry.
All exports are checked for valid solids and a Z=0 contact plane.
Baseline comparisons check bounds, solid volumes, face colors, and geometric differences.
The result also records volumes and colors for models without a baseline.
Exports and previews are copied from an isolated build directory only after successful verification.
The result is recorded in `build/result.json`, including tool versions, source revision, input hashes, and output hashes.
Failed generation returns a nonzero status. Build outputs are excluded from Git.

Geometric equivalence checks preserve the baseline model. They do not certify dimensions omitted from manufacturer drawings.
The models use documented package dimensions and visual simplifications.

## Coordinate normalization

`transforms/kicad-alignment.json` records rigid transforms for existing library models.
The source revision and input hashes identify the exact inputs.
Recorded cosmetic reliefs are removed within bounded surface regions before export.
Checks limit geometry changes to those regions and verify retained face colors.

```sh
python3 tools/align.py --library /path/to/baseline-rocket-pcblib --output build/aligned
```

Select one input filename with `--model <filename>`.
The tool preserves input files and their embedded notices.
It checks exported solids, face colors, dimensions, and geometric differences after re-import.
Invalid source solids can be repaired by removing zero-area faces and sewing their unchanged boundaries.
Other invalid solids fail verification. The result records the number of removed faces for each model.
Coincident full cylinders also receive an analytic geometry check when the CAD kernel returns an inconsistent Boolean difference.
Coordinate normalization does not reconstruct the original CAD source or change its license.

## License

Original project contributions use [Apache-2.0](LICENSE).
Imported sources retain their license and attribution.
Manufacturer documents are linked as dimensional references.

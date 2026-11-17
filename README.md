# rocket-pcblib-generators

Editable generator sources for [rocket-pcblib](https://github.com/chipsalliance/rocket-pcblib) models.
The library distributes STEP files. This repository contains their geometry construction code and dimensional references.

## Models

| Category | Model |
| --- | --- |
| Button_Switch_SMD | SAMZO C4B1802110 |
| Connector | Hirose FH12-32S-0.5SVA |
| Connector | Hirose FH34SRJ-24S-0.5SH |
| LED | Worldsemi WS2812B-1313-V6 |
| Oscillator | YXC YSO230LR |
| Package_DFN_QFN | WCH CH347F |
| Package_SON | WSON-8, 6 x 5 mm |

Each model lives in `models/<library-category>/<model-name>/`.
`generate.py` constructs its geometry. `model.toml` records output paths, source provenance, and the baseline asset hash.
Dimensional references and visual simplifications are documented in the generator or its adjacent README.
Shared generation and verification code lives in `tools/`.

## Generate

Requires Python 3.11 or newer and FreeCAD with its GUI, Part, and Import modules.
FreeCAD must be available as `FreeCAD` on PATH, or selected with `--freecad`.
A desktop display or `xvfb-run` is required for GUI-based export and previews.
Validated with FreeCAD 1.1.3, Open CASCADE 7.8.1, and Python 3.14.10 on Linux.

```sh
python3 tools/generate.py --output build
```

Select one model with `--model <model-name>`.
Compare exports with a library checkout containing the recorded baseline files:

```sh
python3 tools/generate.py --baseline /path/to/rocket-pcblib --output build
```

The command verifies baseline SHA-256 hashes before comparison.
It checks valid solids, contact plane, bounds, solid volumes, imported colors, and geometric differences.
Exports and previews are copied from an isolated build directory only after successful verification.
The result is recorded in `build/result.json`, including tool versions, source revision, input hashes, and output hashes.
Failed generation returns a nonzero status. Build outputs are excluded from Git.

Geometric equivalence checks preserve the baseline model. They do not certify dimensions omitted from manufacturer drawings.
The models use documented package dimensions and visual simplifications.

## License

Original project contributions use [Apache-2.0](LICENSE).
Imported sources retain their license and attribution.
Manufacturer documents are linked as dimensional references.

# SPDX-License-Identifier: Apache-2.0
"""Generate the nominal ALPS Alpine SKRTLBE010 side-push tactile switch."""
from pathlib import Path
import tomllib

import FreeCAD as App
import Part

from model_builder import ModelBuilder


def build(output):
    builder = ModelBuilder()
    box = builder.box
    materials = tomllib.loads(Path(__file__).with_name("model.toml").read_text())["materials"]
    colors = {name: tuple(finish["srgb"]) for name, finish in materials.items()}

    body = box(-2.25, -1.21, 0, 4.50, 2.56, 3.30)
    cap = Part.makeCylinder(1.0, 0.83, App.Vector(0, -2.04, 1.70), App.Vector(0, 1, 0))
    mount_left = box(-2.25, -1.30, 0, 0.80, 0.50, 0.15)
    mount_right = box(1.45, -1.30, 0, 0.80, 0.50, 0.15)

    plate = box(-2.25, -1.21, 0, 4.50, 0.175, 3.30)
    cheeks = [box(x, -1.21, 0, 0.17, 2.24, 3.30) for x in (-2.25, 2.08)]
    studs = [Part.makeCylinder(0.245, 0.21, App.Vector(x, -1.22, 2.84), App.Vector(0, 1, 0))
             for x in (-1.69, 1.69)]
    clip = plate.fuse([*cheeks, mount_left, mount_right]).cut(studs).removeSplitter()
    housing = body.cut(clip).removeSplitter()

    builder.add("Faceplate", clip, colors["faceplate"])
    builder.add("Housing", housing, colors["housing"])
    builder.add("Actuator", cap, colors["actuator"])
    for index, x in enumerate((-1.225, 0.0, 1.225), 1):
        terminal = box(x - 0.25, 1.35, 0, 0.50, 0.25, 0.15)
        builder.add(f"Terminal_{index}", terminal, colors["terminals"])

    builder.export(output)

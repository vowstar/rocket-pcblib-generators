# SPDX-License-Identifier: Apache-2.0
"""Generate the nominal Kangnex WJ15EDGRC-3.81-04P right-angle pluggable header."""
from pathlib import Path
import tomllib

import FreeCAD as App
import Part

from model_builder import ModelBuilder

POLES = 4
PITCH = 3.81
WIDTH = POLES * PITCH + 0.88
REAR = -1.20
FRONT = 8.00
HEIGHT = 7.25
WALL = 0.80
FLOOR = 1.00
ROOF = 0.90
CAVITY_DEPTH = 6.00
PIN = 0.80
PIN_Z = 3.60
PIN_TIP = 7.00
TAIL = 3.50


def build(output):
    builder = ModelBuilder()
    box = builder.box
    materials = tomllib.loads(Path(__file__).with_name("model.toml").read_text())["materials"]
    colors = {name: tuple(finish["srgb"]) for name, finish in materials.items()}
    xs = [(i - (POLES - 1) / 2) * PITCH for i in range(POLES)]

    # The mating face is +Y, towards the board edge. Pin 1 is at -X. Tails pass through the board.
    pins = []
    for x in xs:
        tail = box(x - PIN / 2, -PIN / 2, -TAIL, PIN, PIN, TAIL + PIN_Z + PIN / 2)
        arm = box(x - PIN / 2, -PIN / 2, PIN_Z - PIN / 2, PIN, PIN_TIP + PIN / 2, PIN)
        pins.append(tail.fuse(arm).removeSplitter())

    housing = box(-WIDTH / 2, REAR, 0, WIDTH, FRONT - REAR, HEIGHT)
    cavity_width = PITCH - WALL
    cavities = [box(x - cavity_width / 2, FRONT - CAVITY_DEPTH, FLOOR, cavity_width, CAVITY_DEPTH + 0.01,
                    HEIGHT - FLOOR - ROOF) for x in xs]
    housing = housing.cut(Part.makeCompound(cavities + pins)).removeSplitter()

    builder.add("Housing", housing, colors["housing"])
    for index, pin in enumerate(pins, 1):
        builder.add(f"Pin{index}", pin, colors["pins"])
    builder.export(output)

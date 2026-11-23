# SPDX-License-Identifier: Apache-2.0
"""Generate the nominal Hanrun HR911105A RJ45 jack with magnetics and LEDs."""
from pathlib import Path
import tomllib

import FreeCAD as App
import Part

from model_builder import ModelBuilder

X0, Y0 = -3.58, -17.26          # body corner in the footprint frame, mating face at -Y
WIDTH, DEPTH, HEIGHT = 16.04, 21.30, 13.50
SHIELD = 0.25
CENTER = 4.44                   # midpoint of contacts 1 and 8
OPEN_W, OPEN_Z, OPEN_H = 11.70, 3.00, 8.50
LATCH_W, LATCH_Z = 6.00, 1.80
CAVITY = 15.00
TAIL = 3.05
SIGNAL = [(0.0, 0.0), (1.26, 2.54), (2.54, 0.0), (3.80, 2.54),
          (5.08, 0.0), (6.34, 2.54), (7.62, 0.0), (8.88, 2.54)]
LED_PINS = [(-2.185, -11.26), (0.355, -11.26), (8.525, -11.26), (11.065, -11.26)]
TABS = [(-3.305, -3.31), (12.185, -3.31)]
PEGS = [(-1.275, -6.36), (10.155, -6.36)]


def build(output):
    builder = ModelBuilder()
    box = builder.box
    materials = tomllib.loads(Path(__file__).with_name("model.toml").read_text())["materials"]
    colors = {name: tuple(finish["srgb"]) for name, finish in materials.items()}

    opening = box(CENTER - OPEN_W / 2, Y0 - 0.1, OPEN_Z, OPEN_W, CAVITY + 0.1, OPEN_H)
    latch = box(CENTER - LATCH_W / 2, Y0 - 0.1, LATCH_Z, LATCH_W, CAVITY + 0.1, OPEN_Z - LATCH_Z + 0.01)
    leds = {"led_green": box(CENTER - 6.10, Y0, 0.70, 2.00, 1.20, 1.40),
            "led_yellow": box(CENTER + 4.10, Y0, 0.70, 2.00, 1.20, 1.40)}

    outer = box(X0, Y0, 0, WIDTH, DEPTH, HEIGHT)
    inner = box(X0 + SHIELD, Y0 + SHIELD, 0, WIDTH - 2 * SHIELD, DEPTH - 2 * SHIELD, HEIGHT - SHIELD)
    cuts = Part.makeCompound([opening, latch, *leds.values()])
    shield = outer.cut(inner).cut(cuts).removeSplitter()
    insert = inner.cut(cuts).removeSplitter()

    builder.add("Shield", shield, colors["shield"])
    builder.add("Insert", insert, colors["insert"])
    for name, led in leds.items():
        builder.add(name, led, colors[name])
    roof = OPEN_Z + OPEN_H
    for index in range(8):
        x = CENTER + (index - 3.5) * 1.02
        builder.add(f"Contact{index + 1}", box(x - 0.2, Y0 + 5.0, roof - 0.6, 0.4, 7.0, 0.6), colors["contacts"])
    for index, (x, y) in enumerate(SIGNAL + LED_PINS, 1):
        builder.add(f"Pin{index}", box(x - 0.25, y - 0.25, -TAIL, 0.5, 0.5, TAIL), colors["pins"])
    for index, (x, y) in enumerate(TABS, 1):
        builder.add(f"ShieldTab{index}", box(x - 0.15, y - 0.6, -TAIL, 0.3, 1.2, TAIL), colors["shield"])
    for index, (x, y) in enumerate(PEGS, 1):
        builder.add(f"Peg{index}", Part.makeCylinder(1.5, 2.0, App.Vector(x, y, -2.0)), colors["insert"])
    builder.export(output)

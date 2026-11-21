# SPDX-License-Identifier: Apache-2.0
"""Fugangs ST-C-16PCL-4.58, centred on the 14 mm body in the KiCad plane."""
from pathlib import Path
import tomllib

import FreeCAD as App
import Part

from model_builder import ModelBuilder


MOUTH = -7.0
PORT_CENTRE_Z = 4.58
STEEL_THICKNESS = 0.30


def obround_prism(width, height, length, start_y, centre_z):
    """Extrude a rounded capsule in XZ along the mating axis."""
    radius = width / 2
    low = centre_z - height / 2
    high = centre_z + height / 2
    direction = App.Vector(0, 1, 0)
    middle = ModelBuilder.box(-radius, start_y, low + radius, width, length, height - width)
    ends = (Part.makeCylinder(radius, length, App.Vector(0, start_y, z), direction)
            for z in (low + radius, high - radius))
    return middle.fuse(list(ends)).removeSplitter()


def build(output):
    builder = ModelBuilder()
    box, add = builder.box, builder.add
    materials = tomllib.loads(Path(__file__).with_name("model.toml").read_text())["materials"]
    colors = {name: tuple(finish["srgb"]) for name, finish in materials.items()}
    nickel, lcp = colors["nickel"], colors["black_lcp"]

    outside_width, outside_height = 3.16, 8.94
    shell = obround_prism(outside_width, outside_height, 14.0, MOUTH, PORT_CENTRE_Z)
    cavity = obround_prism(outside_width - 2 * STEEL_THICKNESS,
                           outside_height - 2 * STEEL_THICKNESS,
                           14.04, MOUTH - 0.02, PORT_CENTRE_Z)
    shell = shell.cut(cavity)
    # The raised rear support is exposed black LCP in the product photos.
    support = box(-1.8, -1.20, 8.65, 3.60, 8.20, 1.23)
    add("Shield", shell.cut(support).removeSplitter(), nickel)
    add("Rear_Support", support, lcp)

    # LCP supports the mating tongue and terminates at the board seating plane.
    rear = obround_prism(2.52, 8.28, 7.40, -0.58, PORT_CENTRE_Z)
    seating = box(-1.60, -1.20, 0, 3.20, 8.20, 0.50)
    # The two recessed SMT banks expose the formed solder tails.
    for x in (-1.09, 0.55):
        seating = seating.cut(box(x, -0.72, -0.01, 0.54, 6.50, 0.36))
    add("Housing", rear.fuse(seating).removeSplitter(), lcp)
    add("Tongue", obround_prism(0.70, 6.62, 5.32, -5.90, PORT_CENTRE_Z), lcp)

    # Stations derive from the dimensioned land pattern and its plotted terminal rows.
    stations = (5.45, 4.65, 3.90, 3.20, 2.50, 1.78, 1.08, 0.28)
    for side, ids in (
        (1, ("B1", "B4", "B5", "B6", "B7", "B8", "B9", "B12")),
        (-1, ("A12", "A9", "A8", "A7", "A6", "A5", "A4", "A1")),
    ):
        for index, (pin, y) in enumerate(zip(ids, stations, strict=True)):
            width = 0.40 if index in (0, 1, 6, 7) else 0.30
            x = 0.58 if side > 0 else -1.06
            foot = box(x, y - width / 2, 0, 0.48, width, 0.15)
            stem = box(x, y - width / 2, 0.10, 0.15, width, 0.36)
            add("Solder_" + pin, foot.fuse(stem).removeSplitter(), colors["gold_flash"])
        # The internal mating contacts are represented by eight separate inlays per bank.
        for index in range(8):
            z = PORT_CENTRE_Z - 2.68 + index * 0.75
            x = 0.31 if side > 0 else -0.40
            pad = box(x, -5.18, z, 0.09, 3.05, 0.27)
            add(f"Mating_{'B' if side > 0 else 'A'}_{index + 1}", pad, colors["contact_gold"])

    for y in (0.0, 6.10):
        for side in (-1, 1):
            x = 1.88 if side > 0 else -2.18
            tail = box(x, y - 0.50, -1.32, 0.30, 1.00, 1.76)
            shoulder = box(1.53 if side > 0 else -2.18, y - 0.50, 0.29, 0.65, 1.00, 0.22)
            add(f"Shield_Tab_{'R' if side > 0 else 'L'}_{int(y * 100)}",
                tail.fuse(shoulder).removeSplitter(), nickel)
    for index, y in enumerate((-0.70, 6.45), 1):
        # The locating-pin depth is nominal because the drawing specifies its diameter only.
        pin = Part.makeCylinder(0.30, 0.50, App.Vector(0, y, -0.45))
        add(f"Locator_{index}", pin, lcp)

    builder.export(output)

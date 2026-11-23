# SPDX-License-Identifier: Apache-2.0
"""Generate the nominal Espressif ESP32-S31 QFN-80 package."""
from pathlib import Path
import tomllib

import FreeCAD as App
import Part

from model_builder import ModelBuilder

BODY = 8.0
HEIGHT = 0.85
STANDOFF = 0.02
LEAD_WIDTH = 0.17
LEAD_LENGTH = 0.40
LEAD_THICKNESS = 0.203
PITCH = 0.35
PER_SIDE = 20
PAD = 6.5
PAD_CHAMFER = 0.30
MARK_RADIUS = 0.25
MARK_DEPTH = 0.02


def build(output):
    builder = ModelBuilder()
    box = builder.box
    materials = tomllib.loads(Path(__file__).with_name("model.toml").read_text())["materials"]
    colors = {name: tuple(finish["srgb"]) for name, finish in materials.items()}
    origin, axis = App.Vector(0, 0, 0), App.Vector(0, 0, 1)
    half = BODY / 2
    first = (PER_SIDE - 1) * PITCH / 2

    # Pin 1 is the top lead on the left side; numbering runs anticlockwise in top view.
    leads = []
    for side in range(4):
        for index in range(PER_SIDE):
            y = first - index * PITCH
            lead = box(-half, y - LEAD_WIDTH / 2, 0, LEAD_LENGTH, LEAD_WIDTH, LEAD_THICKNESS)
            lead.rotate(origin, axis, side * 90)
            leads.append((side * PER_SIDE + index + 1, lead))

    p = PAD / 2
    corner = [App.Vector(-p, p - PAD_CHAMFER, 0), App.Vector(-p + PAD_CHAMFER, p, 0), App.Vector(p, p, 0),
              App.Vector(p, -p, 0), App.Vector(-p, -p, 0)]
    pad = Part.Face(Part.makePolygon(corner + [corner[0]])).extrude(App.Vector(0, 0, LEAD_THICKNESS))

    mark_center = App.Vector(-half + 0.75, half - 0.75, HEIGHT - MARK_DEPTH)
    mark = Part.makeCylinder(MARK_RADIUS, MARK_DEPTH, mark_center)
    body = box(-half, -half, STANDOFF, BODY, BODY, HEIGHT - STANDOFF)
    body = body.cut(Part.makeCompound([lead for _, lead in leads] + [pad, mark])).removeSplitter()

    builder.add("Moulding", body, colors["moulding"])
    builder.add("Pin1Mark", mark, colors["mark"])
    builder.add("ExposedPad", pad, colors["terminals"])
    for number, lead in leads:
        builder.add(f"Lead{number}", lead, colors["terminals"])
    builder.export(output)

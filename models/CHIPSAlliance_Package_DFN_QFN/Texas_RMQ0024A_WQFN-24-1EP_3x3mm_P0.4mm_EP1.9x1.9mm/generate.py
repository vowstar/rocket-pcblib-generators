# SPDX-License-Identifier: Apache-2.0
"""Generate the nominal Texas Instruments RMQ0024A WQFN-24 package."""
from pathlib import Path
import tomllib

import FreeCAD as App
import Part

from model_builder import ModelBuilder

BODY = 3.0
HEIGHT = 0.75
STANDOFF = 0.02
LEAD_LENGTH = 0.25
LEAD_THICKNESS = 0.20
CORNER = 0.25
CORNER_GAP = 0.05
PAD = 1.9
PAD_CHAMFER = 0.25
MARK_RADIUS = 0.15
MARK_DEPTH = 0.02
# Pin 1 is the top lead on the left side; offsets in top view, anticlockwise.
SIDE_LEADS = ((0.9, 0.2), (0.5, 0.2), (0.0, 0.4), (-0.5, 0.2), (-0.9, 0.2))


def build(output):
    builder = ModelBuilder()
    box = builder.box
    materials = tomllib.loads(Path(__file__).with_name("model.toml").read_text())["materials"]
    colors = {name: tuple(finish["srgb"]) for name, finish in materials.items()}
    origin, axis = App.Vector(0, 0, 0), App.Vector(0, 0, 1)
    half = BODY / 2

    leads = []
    for side in range(4):
        for index, (y, width) in enumerate(SIDE_LEADS):
            lead = box(-half, y - width / 2, 0, LEAD_LENGTH, width, LEAD_THICKNESS)
            lead.rotate(origin, axis, side * 90)
            leads.append((side * 6 + index + 1, lead))
        corner = box(-half + CORNER_GAP, -half + CORNER_GAP, 0, CORNER, CORNER, LEAD_THICKNESS)
        corner.rotate(origin, axis, side * 90)
        leads.append((side * 6 + 6, corner))

    p = PAD / 2
    outline = [App.Vector(-p, p - PAD_CHAMFER, 0), App.Vector(-p + PAD_CHAMFER, p, 0), App.Vector(p, p, 0),
               App.Vector(p, -p, 0), App.Vector(-p, -p, 0)]
    pad = Part.Face(Part.makePolygon(outline + [outline[0]])).extrude(App.Vector(0, 0, LEAD_THICKNESS))

    mark = Part.makeCylinder(MARK_RADIUS, MARK_DEPTH, App.Vector(-half + 0.40, half - 0.40, HEIGHT - MARK_DEPTH))
    body = box(-half, -half, STANDOFF, BODY, BODY, HEIGHT - STANDOFF)
    body = body.cut(Part.makeCompound([lead for _, lead in leads] + [pad, mark])).removeSplitter()

    builder.add("Moulding", body, colors["moulding"])
    builder.add("Pin1Mark", mark, colors["mark"])
    builder.add("ExposedPad", pad, colors["terminals"])
    for number, lead in sorted(leads):
        builder.add(f"Lead{number}", lead, colors["terminals"])
    builder.export(output)

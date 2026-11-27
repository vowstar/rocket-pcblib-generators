# SPDX-License-Identifier: Apache-2.0
"""Build the Sunlord WPN252010U package using the Figure 3 envelope."""
import FreeCAD as App
import Part

from model_builder import ModelBuilder


def prism(outline, bottom, height):
    vertices = [App.Vector(x, y, bottom) for x, y in outline]
    return Part.Face(Part.makePolygon(vertices + vertices[:1])).extrude(
        App.Vector(0, 0, height)
    )


def build(output):
    model = ModelBuilder()
    body = [
        (-1.25, -0.86), (-1.05, -1.00), (1.05, -1.00), (1.25, -0.86),
        (1.25, 0.86), (1.05, 1.00), (-1.05, 1.00), (-1.25, 0.86),
    ]
    right_terminal = [
        (0.65, -1.00), (1.05, -1.00), (1.25, -0.86),
        (1.25, 0.86), (1.05, 1.00), (0.65, 1.00),
    ]
    left_terminal = [(-x, y) for x, y in right_terminal]
    model.add("Molded_body", prism(body, 0.10, 0.90), (0.26, 0.25, 0.24))
    for number, outline in enumerate((left_terminal, right_terminal), start=1):
        model.add(f"Terminal_{number}", prism(outline, 0.0, 0.10), (0.73, 0.73, 0.72))
    model.export(output)

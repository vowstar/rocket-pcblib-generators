# SPDX-License-Identifier: Apache-2.0
"""Construct ten-pin USON dimensional models with a 0.4 mm ground terminal pair."""
from pathlib import Path
import re
import FreeCAD as App
import ImportGui
import Part


def build_uson(output, *, height, standoff, lead_length, source):
    doc = App.newDocument('USON10')
    objects, pins = [], []
    metal, plastic = (0.75, 0.75, 0.75), (0.12, 0.12, 0.12)

    def add(name, shape, color):
        if not shape.isValid() or len(shape.Solids) != 1:
            raise ValueError(f'Invalid solid: {name}')
        obj = doc.addObject('PartDesign::Feature', name)
        obj.Shape = shape.copy()
        obj.ViewObject.ShapeColor = color
        obj.ViewObject.DiffuseColor = [color] * len(shape.Faces)
        objects.append(obj)
        return shape

    for number in range(1, 11):
        row = number - 1 if number <= 5 else 10 - number
        x = (row - 2) * 0.5
        width = 0.4 if number in (3, 8) else 0.2
        # Start with the -Y row. The other row is its XY mirror about X.
        shape = Part.makeBox(width, lead_length, 0.13, App.Vector(x-width/2, -0.5, 0))
        if number == 3:
            bump = Part.makeCylinder(0.125, 0.13, App.Vector(x, -0.5+lead_length, 0))
            shape = shape.fuse(bump).removeSplitter()
        elif number not in (1, 8):
            inner = -0.5 + lead_length
            edges = [e for e in shape.Edges if e.BoundBox.ZLength > 0.12
                     and abs(e.CenterOfMass.y-inner) < 1e-7]
            shape = shape.makeFillet(0.075, edges)
        if number > 5:
            shape.rotate(App.Vector(x, 0, 0), App.Vector(0, 0, 1), 180)
        pins.append(add(f'Pin_{number}', shape, metal))
    body = Part.makeBox(2.5, 1.0, height-standoff, App.Vector(-1.25, -0.5, standoff))
    body = body.cut(Part.makeCompound(pins)).removeSplitter()
    # The drawing specifies the index area, not its mark dimensions.
    mark = Part.makeCylinder(0.06, 0.02, App.Vector(-1.02, -0.30, height-0.01))
    add('Body', body.cut(mark).removeSplitter(), plastic)
    doc.recompute()
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    ImportGui.export(objects, str(output))
    note = ('/* SPDX-License-Identifier: Apache-2.0\n'
            f' * Dimensional reference: {source}\n'
            ' * Geometry generator: https://github.com/vowstar/rocket-pcblib-generators\n'
            ' * Pin mark dimensions and display colors are illustrative.\n */\n')
    text = re.sub(r"FILE_NAME\(\s*'[^']*'", "FILE_NAME('"+output.name+"'", output.read_text(), count=1)
    text = text.replace('HEADER;', 'HEADER;\n'+note, 1)
    output.write_text('\n'.join(line.rstrip() for line in text.splitlines())+'\n')
    App.closeDocument(doc.Name)

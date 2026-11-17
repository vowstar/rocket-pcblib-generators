# SPDX-License-Identifier: Apache-2.0
"""Shared FreeCAD construction and color-preserving export helpers."""
import FreeCAD as App
import ImportGui
import Part


class ModelBuilder:
    def __init__(self):
        self.document = App.newDocument("Model")
        self.objects = []

    @staticmethod
    def box(x, y, z, width, depth, height):
        return Part.makeBox(width, depth, height, App.Vector(x, y, z))

    def add(self, name, shape, color):
        if not shape.isValid() or len(shape.Solids) != 1:
            raise ValueError(f"Invalid solid: {name}")
        obj = self.document.addObject("PartDesign::Feature", name)
        obj.Shape = shape.copy()
        obj.ViewObject.ShapeColor = color
        self.objects.append(obj)
        return obj

    def export(self, output, translation=(0, 0, 0)):
        for obj in self.objects:
            obj.Placement.Base += App.Vector(*translation)
        self.document.recompute()
        output.parent.mkdir(parents=True, exist_ok=True)
        ImportGui.export(self.objects, str(output))
        App.closeDocument(self.document.Name)

# SPDX-License-Identifier: Apache-2.0
"""Nominal dimensional model. See README.md for dimensions and simplifications."""
import FreeCAD as App
import Part
from model_builder import ModelBuilder


def build(output):
    metal = (.72, .73, .75)
    black = (.10, .11, .12)
    cream = (.80, .77, .66)
    builder = ModelBuilder()
    box, add, V = builder.box, builder.add, App.Vector
    contacts=[]
    for side in range(4):
        for i in range(7):
            y=1.2-.4*i;s=box(-2,y-.1,0,.35,.2,.2);s.rotate(V(0,0,0),V(0,0,1),side*90);contacts.append(s);add('Lead'+str(side*7+i+1),s,metal)
    pts=[V(-1.35,1.10,0),V(-1.10,1.35,0),V(1.35,1.35,0),V(1.35,-1.35,0),V(-1.35,-1.35,0)];ep=Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,0,.2));add('ExposedPad',ep,metal)
    body=box(-2,-2,.025,4,4,.725).cut(Part.makeCompound(contacts+[ep]));add('Moulding',body,black)
    # Pin 1 top-view mark is a shallow recess, not an unsourced logo.
    dot=Part.makeCylinder(.12,.001,V(-1.55,1.55,.749));add('Pin1Mark',dot,(.33,.33,.33))
    builder.export(output, translation=(0, 0, 0))

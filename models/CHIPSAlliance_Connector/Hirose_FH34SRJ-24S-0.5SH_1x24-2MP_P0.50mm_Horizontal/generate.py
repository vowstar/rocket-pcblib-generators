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
    body=box(-7,-3,.05,14,3.8,.95).cut(box(-6.285,-3.01,.25,12.57,1.5,.4)).cut(box(-6.69,-.3,.65,13.38,1.1,.35))
    add('Housing',body,black);add('ClosedActuator',box(-6.69,-.3,.65,13.38,1.1,.35),cream)
    for i in range(24):add('Contact'+str(i+1),box(5.75-.5*i-.075,-.25,0,.15,.5,.15),metal)
    for x in [-6.75,6.75]:add('Fitting'+str(x),box(x-.15,-2.85,0,.3,.7,.15),metal)
    builder.export(output, translation=(0, 1.1, 0))

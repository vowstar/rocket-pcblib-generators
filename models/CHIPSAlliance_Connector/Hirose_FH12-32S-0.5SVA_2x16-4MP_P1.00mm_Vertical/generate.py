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
    body=box(-9.7,-1.8,.05,19.4,3.6,3.55).cut(box(-8.1,-.175,1.35,16.2,.35,2.26))
    add('Housing',body,cream)
    latch=box(-8.95,-1.75,3.6,17.9,3.5,1.25).cut(box(-8.1,-.175,3.59,16.2,.35,1.27));add('ClosedActuator',latch,black)
    for i in range(32):
        x=7.75-.5*i;sgn=1 if i%2==0 else -1
        foot=box(x-.1,1.1 if sgn>0 else -1.9,0,.2,.8,.15)
        stem=box(x-.1,1.1 if sgn>0 else -1.25,.1,.2,.15,3.4)
        add('Contact'+str(i+1),foot.fuse(stem).removeSplitter(),metal)
    for x in [-9.1,9.1]:
        for y in [-1.5,1.5]:add('Fitting'+str(x)+str(y),box(x-.3,y-.4,0,.6,.8,.2),metal)
    builder.export(output, translation=(0, 0, 0))

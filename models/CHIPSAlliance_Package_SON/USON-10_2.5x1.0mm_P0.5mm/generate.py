# SPDX-License-Identifier: Apache-2.0
"""TI DQA0010A. Height is the 0.55 mm maximum. Terminal length 0.365 mm is the midpoint of 0.30–0.43 mm. The drawing does not specify body standoff. The model uses 0.02 mm for display."""
from uson_builder import build_uson


def build(output):
    build_uson(output, height=0.55, standoff=0.02, lead_length=0.365,
               source='https://www.ti.com/lit/ds/symlink/tpd4e02b04.pdf')

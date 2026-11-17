# SPDX-License-Identifier: Apache-2.0
"""TECH PUBLIC RCLAMP0524P, page 5. Height 0.58 mm, body standoff 0.03 mm, metal thickness 0.13 mm, and terminal length 0.38 mm follow the dimensional table. The page 1 height summary differs from this table."""
from uson_builder import build_uson


def build(output):
    build_uson(output, height=0.58, standoff=0.03, lead_length=0.38,
               source='https://atta.szlcsc.com/upload/public/pdf/source/20210810/AE3DE9AC94AD2A317FD9BEA10653400F.pdf')

# SPDX-License-Identifier: Apache-2.0
"""STEP round-trip checks with an analytic test for closed circular cylinders."""
import math


def same_cylinder(a, b, tolerance=1e-6):
    """Recognize an identical full cylinder when OCCT fails a coincident seam cut."""
    records = []
    for shape in (a, b):
        if not shape.isValid() or len(shape.Faces) != 3:
            return False
        sides = [f for f in shape.Faces if type(f.Surface).__name__ == 'Cylinder']
        caps = [f for f in shape.Faces if type(f.Surface).__name__ == 'Plane']
        if len(sides) != 1 or len(caps) != 2:
            return False
        side = sides[0]
        radius, axis = side.Surface.Radius, side.Surface.Axis
        if abs(abs(side.ParameterRange[1]-side.ParameterRange[0])-2*math.pi) > tolerance:
            return False
        area = math.pi*radius**2
        height = shape.Volume/area
        center = shape.CenterOfMass
        if height <= 0 or any(abs(f.Area-area) > tolerance for f in caps):
            return False
        for cap in caps:
            delta = cap.CenterOfMass-center
            if delta.cross(axis).Length > tolerance or abs(abs(delta.dot(axis))-height/2) > tolerance:
                return False
            if cap.Surface.Axis.cross(axis).Length > tolerance:
                return False
        records.append((radius, height, axis, center))
    ar, ah, aa, ac = records[0]
    br, bh, ba, bc = records[1]
    return (abs(ar-br) <= tolerance and abs(ah-bh) <= tolerance
            and aa.cross(ba).Length <= tolerance and (ac-bc).Length <= tolerance)


def compare_solids(expected, actual):
    """Match solid positions and compare shape differences without fusing assemblies."""
    left, right = list(expected.Solids), list(actual.Solids)
    if len(left) != len(right):
        raise ValueError('Solid count mismatch')
    records = []
    for solid in left:
        center = solid.CenterOfMass
        index = min(range(len(right)), key=lambda i: (right[i].CenterOfMass-center).Length)
        other = right.pop(index)
        distance = (other.CenterOfMass-center).Length
        if distance > 1e-4:
            raise ValueError(f'Solid position mismatch: {distance} mm')
        raw = solid.cut((other,), 1e-6).Volume + other.cut((solid,), 1e-6).Volume
        tolerance = max(1e-5, abs(solid.Volume)*1e-6)
        analytic = raw > tolerance and same_cylinder(solid, other)
        if raw > tolerance and not analytic:
            raise ValueError(f'Geometry mismatch: {raw} mm3, volume {solid.Volume} mm3, center {tuple(center)}')
        records.append(dict(boolean_difference_mm3=raw, analytic_cylinder=analytic,
                            center_error_mm=distance, volume_mm3=solid.Volume))
    return records


def remove_empty_faces(shape):
    """Remove only zero-area faces from invalid solids, then sew their unchanged faces."""
    import Part
    solids, removed = [], 0
    for solid in shape.Solids:
        if solid.isValid():
            solids.append(solid)
            continue
        empty = [f for f in solid.Faces if f.Area <= 1e-12]
        if not empty or any(not f.isValid() and f.Area > 1e-12 for f in solid.Faces):
            raise ValueError('Invalid source has nonempty invalid faces')
        shell = Part.makeShell([f for f in solid.Faces if f.Area > 1e-12])
        shell.sewShape()
        healed = Part.makeSolid(shell)
        if (not healed.isValid() or not shell.isClosed() or healed.Volume <= 0
                or abs(healed.Volume-solid.Volume) > max(1e-5, abs(solid.Volume)*1e-6)
                or abs(healed.Area-solid.Area) > 1e-6):
            raise ValueError('Empty-face removal changed the solid boundary')
        solids.append(healed)
        removed += len(empty)
    result = Part.makeCompound(solids)
    if not result.isValid():
        raise ValueError('Invalid shape after empty-face removal')
    return result, removed


def colored_faces(objects):
    """Return area, exact bounds and surface type for each positive-area colored face."""
    rows = []
    for obj in objects:
        colors = list(obj.ViewObject.DiffuseColor)
        if len(colors) == 1:
            colors *= len(obj.Shape.Faces)
        if len(colors) != len(obj.Shape.Faces):
            raise ValueError('Face color count mismatch')
        for face, color in zip(obj.Shape.Faces, colors):
            if face.Area > 1e-12:
                b = face.optimalBoundingBox(False)
                bounds = (b.XMin, b.YMin, b.ZMin, b.XMax, b.YMax, b.ZMax)
                center = ((b.XMin+b.XMax)/2, (b.YMin+b.YMax)/2, (b.ZMin+b.ZMax)/2)
                rows.append((tuple(round(float(c), 5) for c in color),
                             type(face.Surface).__name__, face.Area, center, bounds))
    return rows


def compare_face_colors(before, after, tolerance=1e-3):
    """Match colored faces by surface and bounds within 1 micrometre."""
    # Exact bounds avoid integration-dependent centroids of tiny trimmed B-splines.
    # Solid geometry is independently checked by compare_solids.
    import itertools
    if len(before) != len(after):
        raise ValueError('Colored face count mismatch')
    buckets = {}
    for row in after:
        color, surface, area, center = row[:4]
        key = (color, surface, *(math.floor(v/tolerance) for v in center))
        buckets.setdefault(key, []).append(row)
    for expected in before:
        color, surface, area, center = expected[:4]
        position = tuple(math.floor(v/tolerance) for v in center)
        matched = False
        for delta in itertools.product((-1, 0, 1), repeat=3):
            key = (color, surface, *(v+d for v,d in zip(position, delta)))
            rows = buckets.get(key, [])
            for i, row in enumerate(rows):
                if (math.dist(row[3], center) <= tolerance
                        and (len(expected) < 5 or all(abs(a-b) <= tolerance for a,b in zip(expected[4], row[4])))):
                    rows.pop(i)
                    matched = True
                    break
            if matched:
                break
        if not matched:
            near = sorted((math.dist(row[3], center), row) for group in buckets.values() for row in group)[:3]
            raise ValueError(f'Face color/geometry mismatch at {center}, area {area}, color {color}, surface {surface}; nearest {near}')
    return len(before)

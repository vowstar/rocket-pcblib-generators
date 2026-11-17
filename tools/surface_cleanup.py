# SPDX-License-Identifier: Apache-2.0
"""Remove recorded nonmechanical surface reliefs from a hash-verified STEP input."""


def remove_surface_relief(shape, colors, spec):
    """Defeature the selected relief and verify that only its bounded volume changed."""
    original_faces = list(shape.Faces)
    if len(colors) != len(original_faces):
        raise ValueError('Face color count mismatch before surface cleanup')
    bounds = spec['bounds']
    color = spec['color']
    selected = [i for i, c in enumerate(colors)
                if all(abs(float(a)-b) < 1e-6 for a, b in zip(c[:3], color))]
    if len(selected) != spec['faces']:
        raise ValueError('Unexpected surface relief face count')

    def contained(box, tolerance=1e-6):
        values = (box.XMin, box.YMin, box.ZMin, box.XMax, box.YMax, box.ZMax)
        return all(values[i] >= bounds[i]-tolerance for i in range(3)) and all(
            values[i] <= bounds[i]+tolerance for i in range(3, 6))

    if any(not contained(shape.Faces[i].optimalBoundingBox(False)) for i in selected):
        raise ValueError('Surface relief falls outside its recorded region')
    cleaned = shape.defeaturing([shape.Faces[i] for i in selected])
    if not cleaned.isValid() or len(cleaned.Solids) != len(shape.Solids):
        raise ValueError('Invalid solid after surface cleanup')
    removed = shape.cut((cleaned,), 1e-7)
    added = cleaned.cut((shape,), 1e-7)
    if added.Volume > 1e-6 or not spec['volume_range'][0] <= removed.Volume <= spec['volume_range'][1]:
        raise ValueError('Unexpected volume change during surface cleanup')
    if added.Volume > 1e-12 and not contained(added.optimalBoundingBox(False)):
        raise ValueError('Surface cleanup added geometry outside its region')
    if not contained(removed.optimalBoundingBox(False)):
        raise ValueError('Surface cleanup changed mechanical geometry outside its region')

    # OCCT retains unchanged faces. Only the supporting plane is replaced.
    palette = []
    unchanged = 0
    for face in cleaned.Faces:
        matches = [i for i, old in enumerate(original_faces) if i not in selected and face.isSame(old)]
        if not matches:
            box = face.optimalBoundingBox(False)
            for i, old in enumerate(original_faces):
                if i in selected:
                    continue
                if type(face.Surface).__name__ != type(old.Surface).__name__ or abs(face.Area-old.Area) > 1e-6:
                    continue
                prior = old.optimalBoundingBox(False)
                if all(abs(getattr(box, k)-getattr(prior, k)) < 1e-6
                       for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')):
                    matches.append(i)
        if matches:
            if len({tuple(colors[i]) for i in matches}) != 1:
                raise ValueError('Ambiguous retained face color')
            palette.append(colors[matches[0]])
            unchanged += 1
        else:
            box = face.optimalBoundingBox(False)
            if (type(face.Surface).__name__ != 'Plane'
                    or abs(box.ZMin-spec['plane_z']) > 1e-6
                    or abs(box.ZMax-spec['plane_z']) > 1e-6):
                raise ValueError('Cleanup changed a face outside the supporting plane')
            palette.append(tuple(spec['surface_color']) + (1.0,))
    if any(all(abs(float(a)-b)<1e-6 for a,b in zip(c[:3],color)) for c in palette):
        raise ValueError('Removed relief color remains on the cleaned solid')
    if len(cleaned.Faces)-unchanged != 1:
        raise ValueError('Cleanup must replace exactly one supporting plane')
    before, after = shape.optimalBoundingBox(False), cleaned.optimalBoundingBox(False)
    for axis in ('XMin', 'YMin', 'ZMin', 'XMax', 'YMax'):
        if abs(getattr(before, axis)-getattr(after, axis)) > 1e-6:
            raise ValueError('Mechanical bounds changed during cleanup')
    if abs(after.ZMax-spec['plane_z']) > 1e-6:
        raise ValueError('Surface relief remains above the supporting plane')
    return cleaned, palette, dict(
        selected_faces=len(selected), removed_faces=len(shape.Faces)-len(cleaned.Faces),
        retained_faces=unchanged, replaced_supporting_planes=1,
        removed_volume_mm3=removed.Volume, added_volume_mm3=added.Volume,
        bounds=bounds, final_top_z_mm=after.ZMax,
        mechanical_xy_and_contact_bounds_unchanged=True)

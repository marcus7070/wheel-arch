import cadquery as cq
from types import SimpleNamespace as d
import math
from edge_tangent import makeTangentCircles
import castor_bearing as bearing_module
import leg as leg_module

dims = d()
dims.plate = d()
dims.plate.thick = 27
dims.tube_setback = 50
dims.tube_spacing = 115
dims.edge_thick = 10  # thickness around the outer edge of the bearings and tubes
dims.bearing_recess = bearing_module.dims.inner_edge_thick * 0.9
dims.chamfer = dims.edge_thick / 2


def signed_angle(vec0, vec1):
    vec0 = vec0.normalized()
    vec1 = vec1.normalized()
    sign = math.copysign(1, vec0.cross(vec1).dot(cq.Vector(0, 0, 1)))
    return sign * math.acos(vec0.dot(vec1))


def plate_ex(w0: cq.Wire):
    return cq.Solid.extrudeLinear(
        w0,
        [],
        cq.Vector(0, 0, dims.plate.thick),
    )

to_fuse = [plate_ex(cq.Wire.makeCircle(
    bearing_module.dims.od / 2,
    center=cq.Vector(0, 0, 0),
    normal=cq.Vector(0, 0, 1),
))]

for x0 in [-dims.tube_spacing / 2, dims.tube_spacing / 2]:
    tangent_edges = [
        makeTangentCircles(
            (0, 0),
            bearing_module.dims.od / 2,
            (x0, -dims.tube_setback),
            leg_module.dims.od / 2,
            sense,
            sense,
        ) for sense in ["outside", "inside"]
    ]
    points = []
    for e in tangent_edges:
        points.extend([e.startPoint(), e.endPoint()])

    avg_center = sum([p.Center() for p in points], cq.Vector()) / (len(points) + 1)
    points.sort(key=lambda e: signed_angle(e - avg_center, cq.Vector(1, 0, 0)))
    points.append(points[0])
    w0 = cq.Wire.makePolygon(points)
    to_fuse.append(plate_ex(w0))
    to_fuse.append(plate_ex(cq.Wire.makeCircle(
        leg_module.dims.od / 2,
        cq.Vector(x0, -dims.tube_setback),
        cq.Vector(0, 0, 1),
    )))

base = to_fuse.pop(0)
base = base.fuse(*to_fuse).clean()
base = cq.Solid(base.wrapped)

part = (
    cq.Workplane()
    .add(base)
    .tag("base")
    .faces(">Z")
    .workplane()
    .faces(">Z", tag="base")
    .wires()
    .toPending()
    .offset2D(dims.edge_thick)
    .extrude(-dims.plate.thick)
    .edges("|Z")
    .edges(cq.selectors.NearestToPointSelector((0, -bearing_module.dims.od / 2, 0)))
    .fillet(dims.edge_thick)
    .tag("base_part")
    .faces(">Z")
    .workplane()
    .hole(bearing_module.dims.od, dims.bearing_recess)
    .faces(">Z[-2]")
    .tag("upper_bearing_face")
    .end()
    .faces("<Z")
    .workplane()
    .hole(bearing_module.dims.od, dims.bearing_recess)
    .faces("<Z[-2]")
    .tag("lower_bearing_face")
    .end()
    .center(0, 0)
    .hole(bearing_module.dims.id + 0.4)
    .faces(">Z or <Z", tag="base_part")
    .wires()
    .chamfer(dims.chamfer)
)
for x0 in [-dims.tube_spacing / 2, dims.tube_spacing / 2]:
    part = (
        part
        .faces("<Z", tag="base")
        .workplane(origin=(x0, -dims.tube_setback, 0))
        .circle(leg_module.dims.od / 2)
        .circle(leg_module.dims.id / 2)
        .cutBlind(-(dims.plate.thick - dims.edge_thick))
        .center(0, 0)
        .hole(6, dims.plate.thick / 2)
    )
    tag = "left_leg" if x0 < 0 else "right_leg"
    part = (
        part
        .faces(cq.selectors.NearestToPointSelector(
            (x0, -dims.tube_setback, dims.plate.thick - dims.edge_thick)
        ))
        .faces(cq.selectors.AreaNthSelector(-1))
        .tag(tag)
        .end(2)
    )

# if "show_object" in locals():
#     show_object(part._getTagged("left_leg"), "left_leg")
#     show_object(part._getTagged("right_leg"), "right_leg")
